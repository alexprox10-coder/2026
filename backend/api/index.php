<?php
/**
 * Parser SaaS - API Router
 */

// CORS заголовки
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

// Preflight запрос
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Подключаем конфигурацию
require_once __DIR__ . '/../config.php';

// Получаем путь
$requestUri = $_SERVER['REQUEST_URI'];
$basePath = '/api';
$path = str_replace($basePath, '', parse_url($requestUri, PHP_URL_PATH));
$path = trim($path, '/');
$method = $_SERVER['REQUEST_METHOD'];

// Получаем данные запроса
$input = json_decode(file_get_contents('php://input'), true) ?? [];
$input = array_merge($_GET, $_POST, $input);

// Функция ответа
function response($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

// Функция получения текущего пользователя
function getCurrentUser() {
    $token = null;

    // Из заголовка
    $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (preg_match('/Bearer\s+(.+)/', $authHeader, $matches)) {
        $token = $matches[1];
    }

    // Из cookie
    if (!$token && isset($_COOKIE['auth_token'])) {
        $token = $_COOKIE['auth_token'];
    }

    if (!$token) {
        return null;
    }

    $user = new User();
    return $user->validateToken($token);
}

// Требовать авторизацию
function requireAuth() {
    $user = getCurrentUser();
    if (!$user) {
        response(['success' => false, 'error' => 'Требуется авторизация'], 401);
    }
    return $user;
}

// ==================== РОУТИНГ ====================

// AUTH: Регистрация
if ($path === 'auth/register' && $method === 'POST') {
    $user = new User();
    $result = $user->register(
        $input['email'] ?? '',
        $input['password'] ?? '',
        $input['first_name'] ?? '',
        $input['last_name'] ?? ''
    );

    if ($result['success']) {
        // Автоматически входим после регистрации
        $loginResult = $user->login($input['email'], $input['password']);
        response($loginResult);
    }

    response($result, $result['success'] ? 200 : 400);
}

// AUTH: Вход
if ($path === 'auth/login' && $method === 'POST') {
    $user = new User();
    $result = $user->login($input['email'] ?? '', $input['password'] ?? '');
    response($result, $result['success'] ? 200 : 401);
}

// AUTH: Выход
if ($path === 'auth/logout' && $method === 'POST') {
    $token = null;
    $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (preg_match('/Bearer\s+(.+)/', $authHeader, $matches)) {
        $token = $matches[1];
    }

    if ($token) {
        $user = new User();
        $user->logout($token);
    }

    response(['success' => true]);
}

// AUTH: Google OAuth
if ($path === 'auth/google' && $method === 'GET') {
    if (empty(GOOGLE_CLIENT_ID)) {
        response(['success' => false, 'error' => 'Google OAuth не настроен'], 500);
    }

    $params = http_build_query([
        'client_id' => GOOGLE_CLIENT_ID,
        'redirect_uri' => GOOGLE_REDIRECT_URI,
        'response_type' => 'code',
        'scope' => 'email profile',
        'access_type' => 'offline'
    ]);

    header('Location: https://accounts.google.com/o/oauth2/auth?' . $params);
    exit;
}

// AUTH: Google OAuth callback
if ($path === 'auth/google/callback' && $method === 'GET') {
    $code = $_GET['code'] ?? '';

    if (!$code) {
        header('Location: ' . SITE_URL . '/dashboard/login.html?error=google_failed');
        exit;
    }

    // Получаем токен
    $tokenResponse = file_get_contents('https://oauth2.googleapis.com/token', false, stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/x-www-form-urlencoded',
            'content' => http_build_query([
                'code' => $code,
                'client_id' => GOOGLE_CLIENT_ID,
                'client_secret' => GOOGLE_CLIENT_SECRET,
                'redirect_uri' => GOOGLE_REDIRECT_URI,
                'grant_type' => 'authorization_code'
            ])
        ]
    ]));

    $tokenData = json_decode($tokenResponse, true);
    $accessToken = $tokenData['access_token'] ?? '';

    if (!$accessToken) {
        header('Location: ' . SITE_URL . '/dashboard/login.html?error=google_token_failed');
        exit;
    }

    // Получаем данные пользователя
    $userInfo = json_decode(file_get_contents(
        'https://www.googleapis.com/oauth2/v2/userinfo?access_token=' . $accessToken
    ), true);

    $user = new User();
    $result = $user->googleAuth(
        $userInfo['id'],
        $userInfo['email'],
        $userInfo['given_name'] ?? '',
        $userInfo['family_name'] ?? '',
        $userInfo['picture'] ?? null
    );

    if ($result['success']) {
        // Устанавливаем cookie и редиректим
        setcookie('auth_token', $result['token'], time() + JWT_EXPIRY, '/', '', true, true);
        header('Location: ' . SITE_URL . '/dashboard/');
    } else {
        header('Location: ' . SITE_URL . '/dashboard/login.html?error=google_auth_failed');
    }
    exit;
}

// AUTH: Telegram callback
if ($path === 'auth/telegram/callback' && $method === 'GET') {
    $user = new User();
    $result = $user->telegramAuth($_GET);

    if ($result['success']) {
        setcookie('auth_token', $result['token'], time() + JWT_EXPIRY, '/', '', true, true);
        header('Location: ' . SITE_URL . '/dashboard/');
    } else {
        header('Location: ' . SITE_URL . '/dashboard/login.html?error=telegram_auth_failed');
    }
    exit;
}

// USER: Получить текущего пользователя
if ($path === 'user/me' && $method === 'GET') {
    $user = requireAuth();
    unset($user['password_hash']);
    response(['success' => true, 'user' => $user]);
}

// USER: Обновить настройки
if ($path === 'user/settings' && $method === 'PUT') {
    $currentUser = requireAuth();
    $user = new User();
    $result = $user->updateSettings($currentUser['id'], $input);
    response($result);
}

// USER: Статистика
if ($path === 'user/stats' && $method === 'GET') {
    $currentUser = requireAuth();
    $db = Database::getInstance();

    $stats = [
        'daily_used' => $currentUser['daily_used'],
        'daily_limit' => $currentUser['daily_limit'],
        'plan' => $currentUser['plan'],
        'total_listings' => $db->fetch(
            "SELECT COUNT(*) as cnt FROM listings WHERE user_id = ?",
            [$currentUser['id']]
        )['cnt'],
        'active_tasks' => $db->fetch(
            "SELECT COUNT(*) as cnt FROM parsing_tasks WHERE user_id = ? AND status = 'active'",
            [$currentUser['id']]
        )['cnt'],
        'today_runs' => $db->fetch(
            "SELECT COUNT(*) as cnt FROM parsing_runs WHERE user_id = ? AND DATE(created_at) = CURDATE()",
            [$currentUser['id']]
        )['cnt']
    ];

    response(['success' => true, 'stats' => $stats]);
}

// TASKS: Получить список задач
if ($path === 'tasks' && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $tasks = $parser->getUserTasks($user['id']);
    response(['success' => true, 'tasks' => $tasks]);
}

// TASKS: Создать задачу
if ($path === 'tasks' && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->createTask($user['id'], $input);
    response($result, $result['success'] ? 201 : 400);
}

// TASKS: Запустить парсинг
if (preg_match('/^tasks\/(\d+)\/run$/', $path, $matches) && $method === 'POST') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->runTask($matches[1], $user['id']);
    response($result);
}

// TASKS: Проверить статус
if (preg_match('/^runs\/(\d+)\/status$/', $path, $matches) && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $result = $parser->checkRunStatus($matches[1], $user['id']);
    response($result);
}

// LISTINGS: Получить результаты
if ($path === 'listings' && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $limit = (int)($input['limit'] ?? 50);
    $offset = (int)($input['offset'] ?? 0);
    $listings = $parser->getUserListings($user['id'], $limit, $offset);
    response(['success' => true, 'listings' => $listings]);
}

// LISTINGS: Экспорт в Excel
if ($path === 'listings/export/excel' && $method === 'GET') {
    $user = requireAuth();
    $parser = new Parser();
    $listings = $parser->getUserListings($user['id'], 10000, 0);

    // Генерируем CSV (простой Excel-совместимый формат)
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="listings_' . date('Y-m-d') . '.csv"');

    $output = fopen('php://output', 'w');
    fprintf($output, chr(0xEF).chr(0xBB).chr(0xBF)); // BOM для UTF-8

    // Заголовки
    fputcsv($output, ['Название', 'Цена', 'Адрес', 'Комнаты', 'Площадь', 'Источник', 'Ссылка', 'Дата']);

    foreach ($listings as $item) {
        fputcsv($output, [
            $item['title'],
            $item['price'],
            $item['address'],
            $item['rooms'],
            $item['area'],
            $item['source'],
            $item['url'],
            $item['created_at']
        ]);
    }

    fclose($output);
    exit;
}

// TELEGRAM: Проверить токен бота
if ($path === 'telegram/verify' && $method === 'POST') {
    $user = requireAuth();
    $botToken = $input['bot_token'] ?? '';

    if (!$botToken) {
        response(['success' => false, 'error' => 'Укажите токен бота']);
    }

    $telegram = new Telegram($botToken);
    $result = $telegram->getMe();

    if ($result['ok'] ?? false) {
        response([
            'success' => true,
            'bot' => $result['result']
        ]);
    }

    response(['success' => false, 'error' => 'Неверный токен бота']);
}

// TELEGRAM: Отправить тестовое сообщение
if ($path === 'telegram/test' && $method === 'POST') {
    $user = requireAuth();

    $botToken = $input['bot_token'] ?? $user['telegram_bot_token'];
    $chatId = $input['chat_id'] ?? $user['telegram_chat_id'];

    if (!$botToken || !$chatId) {
        response(['success' => false, 'error' => 'Укажите токен бота и chat_id']);
    }

    $telegram = new Telegram($botToken);
    $result = $telegram->sendMessage($chatId, "✅ Тестовое сообщение от Parser SaaS!\n\nВаш бот успешно подключен.");

    response([
        'success' => $result['ok'] ?? false,
        'error' => $result['description'] ?? null
    ]);
}

// CITIES: Получить список городов
if ($path === 'cities' && $method === 'GET') {
    $db = Database::getInstance();
    $cities = $db->fetchAll("SELECT id, name, region FROM cities WHERE is_active = 1 ORDER BY name");
    response(['success' => true, 'cities' => $cities]);
}

// PLANS: Получить тарифы
if ($path === 'plans' && $method === 'GET') {
    $db = Database::getInstance();
    $plans = $db->fetchAll("SELECT * FROM plans WHERE is_active = 1 ORDER BY sort_order");
    response(['success' => true, 'plans' => $plans]);
}

// 404
response(['success' => false, 'error' => 'Endpoint not found'], 404);
