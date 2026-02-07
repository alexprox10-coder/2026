<?php
// Отключаем вывод ошибок в HTML - все ответы должны быть JSON
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);

// Обработчик ошибок - возвращаем JSON
set_error_handler(function($errno, $errstr, $errfile, $errline) {
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array(
        'success' => false,
        'error' => 'Server error: ' . $errstr,
        'file' => basename($errfile),
        'line' => $errline
    ), JSON_UNESCAPED_UNICODE);
    exit;
});

// Обработчик исключений
set_exception_handler(function($e) {
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array(
        'success' => false,
        'error' => 'Exception: ' . $e->getMessage(),
        'file' => basename($e->getFile()),
        'line' => $e->getLine()
    ), JSON_UNESCAPED_UNICODE);
    exit;
});

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/../config.php';

$requestUri = $_SERVER['REQUEST_URI'];
$path = str_replace('/api', '', parse_url($requestUri, PHP_URL_PATH));
$path = trim($path, '/');
$method = $_SERVER['REQUEST_METHOD'];

$inputRaw = file_get_contents('php://input');
$input = json_decode($inputRaw, true);
if (!is_array($input)) $input = array();
$input = array_merge($_GET, $_POST, $input);

function response($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function getCurrentUser() {
    $token = null;
    $authHeader = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
    if (preg_match('/Bearer\s+(.+)/', $authHeader, $matches)) {
        $token = $matches[1];
    }
    if (!$token && isset($_COOKIE['auth_token'])) {
        $token = $_COOKIE['auth_token'];
    }
    if (!$token) return null;
    
    $user = new User();
    return $user->validateToken($token);
}

function requireAuth() {
    $user = getCurrentUser();
    if (!$user) {
        response(array('success' => false, 'error' => 'Требуется авторизация'), 401);
    }
    return $user;
}

// API Info
if ($path === '' && $method === 'GET') {
    response(array('status' => 'Parser SaaS API v1.0'));
}

// Register
if ($path === 'auth/register' && $method === 'POST') {
    $user = new User();
    // Поддержка обоих вариантов: name или first_name/last_name
    $name = isset($input['name']) ? $input['name'] : '';
    $firstName = isset($input['first_name']) ? $input['first_name'] : '';
    $lastName = isset($input['last_name']) ? $input['last_name'] : '';

    // Если передан name, разбиваем его на first_name и last_name
    if ($name && !$firstName) {
        $parts = explode(' ', $name, 2);
        $firstName = $parts[0];
        $lastName = isset($parts[1]) ? $parts[1] : '';
    }

    $result = $user->register(
        isset($input['email']) ? $input['email'] : '',
        isset($input['password']) ? $input['password'] : '',
        $firstName,
        $lastName
    );
    if ($result['success']) {
        $loginResult = $user->login($input['email'], $input['password']);
        response($loginResult);
    }
    response($result, 400);
}

// Login
if ($path === 'auth/login' && $method === 'POST') {
    $user = new User();
    $result = $user->login(
        isset($input['email']) ? $input['email'] : '',
        isset($input['password']) ? $input['password'] : ''
    );
    response($result, $result['success'] ? 200 : 401);
}

// Logout
if ($path === 'auth/logout' && $method === 'POST') {
    response(array('success' => true));
}

// Google OAuth
if ($path === 'auth/google' && $method === 'GET') {
    $params = http_build_query(array(
        'client_id' => GOOGLE_CLIENT_ID,
        'redirect_uri' => GOOGLE_REDIRECT_URI,
        'response_type' => 'code',
        'scope' => 'email profile',
        'access_type' => 'offline'
    ));
    header('Location: https://accounts.google.com/o/oauth2/auth?' . $params);
    exit;
}

// Google Callback
if ($path === 'auth/google/callback' && $method === 'GET') {
    $code = isset($_GET['code']) ? $_GET['code'] : '';
    if (!$code) {
        header('Location: ' . SITE_URL . '/login.html?error=no_code');
        exit;
    }

    // Проверяем что credentials не placeholder
    if (GOOGLE_CLIENT_ID === 'YOUR_GOOGLE_CLIENT_ID' || GOOGLE_CLIENT_SECRET === 'YOUR_GOOGLE_CLIENT_SECRET') {
        echo '<pre>GOOGLE OAUTH ERROR: Google credentials not configured in config.php</pre>';
        exit;
    }

    // Используем cURL вместо file_get_contents (file_get_contents заблокирован для HTTPS)
    $ch = curl_init('https://oauth2.googleapis.com/token');
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
        'code' => $code,
        'client_id' => GOOGLE_CLIENT_ID,
        'client_secret' => GOOGLE_CLIENT_SECRET,
        'redirect_uri' => GOOGLE_REDIRECT_URI,
        'grant_type' => 'authorization_code'
    )));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/x-www-form-urlencoded'));

    $tokenResponse = curl_exec($ch);
    $curlError = curl_error($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($curlError || $httpCode !== 200) {
        echo '<pre>GOOGLE TOKEN ERROR: httpCode=' . $httpCode . ' curlError=' . $curlError . ' response=' . $tokenResponse . '</pre>';
        exit;
    }

    $tokenData = json_decode($tokenResponse, true);
    $accessToken = isset($tokenData['access_token']) ? $tokenData['access_token'] : '';

    if (!$accessToken) {
        echo '<pre>GOOGLE TOKEN ERROR: No access_token in response. Response: ' . $tokenResponse . '</pre>';
        exit;
    }

    // Получаем данные пользователя
    $ch2 = curl_init('https://www.googleapis.com/oauth2/v2/userinfo?access_token=' . $accessToken);
    curl_setopt($ch2, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch2, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch2, CURLOPT_SSL_VERIFYHOST, false);
    $userInfoResponse = curl_exec($ch2);
    curl_close($ch2);

    $userInfo = json_decode($userInfoResponse, true);

    if (!isset($userInfo['email'])) {
        echo '<pre>GOOGLE USER ERROR: No email in response. Response: ' . $userInfoResponse . '</pre>';
        exit;
    }

    $user = new User();
    $result = $user->googleAuth(
        $userInfo['id'],
        $userInfo['email'],
        isset($userInfo['given_name']) ? $userInfo['given_name'] : '',
        isset($userInfo['family_name']) ? $userInfo['family_name'] : '',
        isset($userInfo['picture']) ? $userInfo['picture'] : null
    );

    if ($result['success']) {
        setcookie('auth_token', $result['token'], time() + 86400 * 30, '/', '', false, true);
        header('Location: ' . SITE_URL . '/dashboard/index.html?token=' . $result['token']);
    } else {
        header('Location: ' . SITE_URL . '/login.html?error=auth_failed');
    }
    exit;
}

// User Me
if ($path === 'user/me' && $method === 'GET') {
    $user = requireAuth();
    unset($user['password_hash']);
    response(array('success' => true, 'user' => $user));
}

// User Stats
if ($path === 'user/stats' && $method === 'GET') {
    $user = requireAuth();
    response(array('success' => true, 'stats' => array(
        'daily_used' => (int)$user['daily_used'],
        'daily_limit' => (int)$user['daily_limit'],
        'plan' => $user['plan']
    )));
}

// User Settings
if ($path === 'user/settings' && $method === 'PUT') {
    $user = requireAuth();
    $updates = array();
    if (isset($input['telegram_bot_token'])) $updates['telegram_bot_token'] = $input['telegram_bot_token'];
    if (isset($input['telegram_chat_id'])) $updates['telegram_chat_id'] = $input['telegram_chat_id'];
    if (!empty($updates)) {
        $db = Database::getInstance();
        $db->update('users', $updates, 'id = ?', array($user['id']));
    }
    response(array('success' => true));
}

// Get Tasks
if ($path === 'tasks' && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $tasks = $parser->getUserTasks($user['id']);
    response(array('success' => true, 'tasks' => $tasks));
}

// Create Task
if ($path === 'tasks' && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->createTask($user['id'], $input);
    response($result, $result['success'] ? 201 : 400);
}

// Delete Task
if (preg_match('/^tasks\/(\d+)$/', $path, $matches) && $method === 'DELETE') {
    $user = requireAuth();
    $taskId = (int)$matches[1];
    $db = Database::getInstance();

    // Проверяем что задача принадлежит пользователю
    $task = $db->fetch("SELECT id FROM parsing_tasks WHERE id = ? AND user_id = ?", array($taskId, $user['id']));
    if (!$task) {
        response(array('success' => false, 'error' => 'Задача не найдена'), 404);
    }

    // Удаляем связанные данные
    $db->query("DELETE FROM listings WHERE task_id = ?", array($taskId));
    $db->query("DELETE FROM parsing_runs WHERE task_id = ?", array($taskId));
    $db->query("DELETE FROM parsing_tasks WHERE id = ?", array($taskId));

    response(array('success' => true, 'message' => 'Задача удалена'));
}

// Run Task
if (preg_match('/^tasks\/(\d+)\/run$/', $path, $matches) && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->runTask($matches[1], $user['id']);
    response($result);
}

// Check Run Status
if (preg_match('/^runs\/(\d+)\/status$/', $path, $matches) && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->checkRunStatus($matches[1], $user['id']);
    response($result);
}

// Get Listings
if ($path === 'listings' && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $limit = isset($input['limit']) ? (int)$input['limit'] : 50;
    $offset = isset($input['offset']) ? (int)$input['offset'] : 0;
    $listings = $parser->getUserListings($user['id'], $limit, $offset);
    response(array('success' => true, 'listings' => $listings));
}

// Sync all pending runs - синхронизировать все незавершённые запуски
if ($path === 'runs/sync-all' && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $results = $parser->syncAllPendingRuns($user['id']);
    response(array('success' => true, 'synced' => $results));
}

// Export to Excel/CSV
if ($path === 'export/excel' && $method === 'GET') {
    $token = isset($_GET['token']) ? $_GET['token'] : null;
    if (!$token) {
        response(array('success' => false, 'error' => 'Token required'), 401);
    }

    $user = new User();
    $userData = $user->validateToken($token);
    if (!$userData) {
        response(array('success' => false, 'error' => 'Invalid token'), 401);
    }

    $parser = new Parser();
    $listings = $parser->getUserListings($userData['id'], 10000, 0);

    if (empty($listings)) {
        response(array('success' => false, 'error' => 'No data to export'));
    }

    // Generate CSV
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="parser_export_' . date('Y-m-d_H-i') . '.csv"');

    // BOM for Excel
    echo "\xEF\xBB\xBF";

    // Headers
    echo "Заголовок;Цена;Адрес;Комнаты;Площадь;Этаж;Телефон;Источник;Ссылка;Дата\n";

    // Data
    foreach ($listings as $item) {
        $row = array(
            str_replace(array('"', ';', "\n"), array("'", ',', ' '), $item['title'] ?: ''),
            $item['price'] ?: '',
            str_replace(array('"', ';', "\n"), array("'", ',', ' '), $item['address'] ?: ''),
            $item['rooms'] ?: '',
            $item['area'] ?: '',
            $item['floor'] ?: '',
            $item['phone'] ?: '',
            $item['source'] ?: 'avito',
            $item['url'] ?: '',
            $item['created_at'] ?: ''
        );
        echo '"' . implode('";"', $row) . "\"\n";
    }
    exit;
}

// Telegram Verify
if ($path === 'telegram/verify' && $method === 'POST') {
    $user = requireAuth();
    $botToken = isset($input['bot_token']) ? $input['bot_token'] : '';
    if (!$botToken) response(array('success' => false, 'error' => 'Нет токена'));
    $telegram = new Telegram($botToken);
    $result = $telegram->getMe();
    response(array('success' => isset($result['ok']) && $result['ok'], 'bot' => isset($result['result']) ? $result['result'] : null));
}

// Telegram Test
if ($path === 'telegram/test' && $method === 'POST') {
    $user = requireAuth();
    $botToken = isset($input['bot_token']) ? $input['bot_token'] : '';
    $chatId = isset($input['chat_id']) ? $input['chat_id'] : '';
    if (!$botToken || !$chatId) response(array('success' => false, 'error' => 'Нет данных'));
    $telegram = new Telegram($botToken);
    $result = $telegram->sendMessage($chatId, "Тест от Parser SaaS! Бот подключен.");
    response(array('success' => isset($result['ok']) && $result['ok']));
}

// Apify Webhook - автоматическое получение результатов
if ($path === 'webhook/apify' && $method === 'POST') {
    // Логируем входящий webhook
    $logFile = __DIR__ . '/../../logs/apify_webhook.log';
    $logDir = dirname($logFile);
    if (!is_dir($logDir)) mkdir($logDir, 0755, true);

    file_put_contents($logFile, date('Y-m-d H:i:s') . " Webhook received\n", FILE_APPEND);
    file_put_contents($logFile, "Input: " . $inputRaw . "\n\n", FILE_APPEND);

    // Получаем данные из webhook
    $runId = isset($input['runId']) ? $input['runId'] : (isset($input['resource']['id']) ? $input['resource']['id'] : null);
    $status = isset($input['status']) ? $input['status'] : (isset($input['resource']['status']) ? $input['resource']['status'] : null);
    $eventType = isset($input['eventType']) ? $input['eventType'] : null;

    // Также проверяем GET параметры (для совместимости)
    if (!$runId && isset($_GET['run_id'])) $runId = $_GET['run_id'];
    if (!$runId && isset($_GET['apify_run_id'])) $runId = $_GET['apify_run_id'];

    file_put_contents($logFile, "RunId: $runId, Status: $status, Event: $eventType\n", FILE_APPEND);

    if (!$runId) {
        response(array('success' => false, 'error' => 'No run ID provided'));
    }

    // Ищем запуск в нашей БД по apify_run_id
    $db = Database::getInstance();
    $run = $db->fetch("SELECT * FROM parsing_runs WHERE apify_run_id = ?", array($runId));

    if (!$run) {
        file_put_contents($logFile, "Run not found in DB for apify_run_id: $runId\n", FILE_APPEND);
        response(array('success' => false, 'error' => 'Run not found'));
    }

    // Если статус SUCCEEDED - забираем результаты
    if ($status === 'SUCCEEDED' || $eventType === 'ACTOR.RUN.SUCCEEDED') {
        $parser = new Parser();
        $result = $parser->processWebhook($run['id'], $run['user_id']);
        file_put_contents($logFile, "Processed: " . json_encode($result) . "\n", FILE_APPEND);
        response($result);
    }

    response(array('success' => true, 'message' => 'Webhook received', 'status' => $status));
}

// Manual sync - принудительная синхронизация результатов
if (preg_match('/^runs\/(\d+)\/sync$/', $path, $matches) && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->processWebhook($matches[1], $user['id']);
    response($result);
}

// 404
response(array('success' => false, 'error' => 'Not found: ' . $path), 404);
