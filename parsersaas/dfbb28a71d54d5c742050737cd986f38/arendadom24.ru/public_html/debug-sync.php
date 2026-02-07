<?php
/**
 * Debug script - проверка синхронизации
 * URL: https://arendadom24.ru/debug-sync.php
 * УДАЛИТЕ ПОСЛЕ ИСПОЛЬЗОВАНИЯ!
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once __DIR__ . '/backend/config.php';

header('Content-Type: text/html; charset=utf-8');

echo "<h1>Debug Sync</h1>";

// 1. Проверяем подключение к БД
echo "<h2>1. База данных</h2>";
try {
    $db = Database::getInstance();
    echo "<p style='color:green'>✅ Подключение к БД работает</p>";
} catch (Exception $e) {
    echo "<p style='color:red'>❌ Ошибка БД: " . $e->getMessage() . "</p>";
    exit;
}

// 2. Проверяем пользователя
echo "<h2>2. Пользователи</h2>";
$users = $db->fetchAll("SELECT id, email, name FROM users LIMIT 5");
echo "<pre>" . print_r($users, true) . "</pre>";

// 3. Проверяем задачи парсинга
echo "<h2>3. Задачи парсинга (parsing_tasks)</h2>";
$tasks = $db->fetchAll("SELECT * FROM parsing_tasks ORDER BY id DESC LIMIT 5");
echo "<pre>" . print_r($tasks, true) . "</pre>";

// 4. Проверяем запуски
echo "<h2>4. Запуски парсинга (parsing_runs)</h2>";
$runs = $db->fetchAll("SELECT * FROM parsing_runs ORDER BY id DESC LIMIT 10");
echo "<pre>" . print_r($runs, true) . "</pre>";

// 5. Проверяем листинги
echo "<h2>5. Объявления (listings)</h2>";
$listings = $db->fetchAll("SELECT COUNT(*) as cnt FROM listings");
echo "<p>Всего объявлений: <strong>" . $listings[0]['cnt'] . "</strong></p>";

// 6. Проверяем Apify token
echo "<h2>6. Apify Config</h2>";
echo "<p>Token: " . substr(APIFY_TOKEN, 0, 15) . "...</p>";
echo "<p>Avito Actor: " . APIFY_AVITO_ACTOR . "</p>";
echo "<p>CIAN Actor: " . APIFY_CIAN_ACTOR . "</p>";

// Helper function - cURL GET (file_get_contents заблокирован на сервере)
function curlGet($url) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    $response = curl_exec($ch);
    $error = curl_error($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    return ['response' => $response, 'error' => $error, 'httpCode' => $httpCode];
}

// 7. Попробуем синхронизировать последний run
echo "<h2>7. Тест синхронизации (cURL)</h2>";
if (!empty($runs)) {
    foreach ($runs as $idx => $lastRun) {
        echo "<h3>Run #" . ($idx + 1) . "</h3>";
        echo "<p>Наш Run ID: <strong>" . $lastRun['id'] . "</strong></p>";
        echo "<p>Apify Run ID: <strong>" . ($lastRun['apify_run_id'] ?: 'НЕТ!') . "</strong></p>";
        echo "<p>Status в БД: <strong style='color:" . ($lastRun['status'] === 'completed' ? 'green' : 'orange') . "'>" . $lastRun['status'] . "</strong></p>";
        echo "<p>Items found: " . ($lastRun['items_found'] ?? 0) . "</p>";

        if (!empty($lastRun['apify_run_id'])) {
            // Проверим статус в Apify через cURL
            $apifyUrl = "https://api.apify.com/v2/actor-runs/{$lastRun['apify_run_id']}?token=" . APIFY_TOKEN;
            $result = curlGet($apifyUrl);

            if ($result['error']) {
                echo "<p style='color:red'>❌ cURL Error: " . $result['error'] . "</p>";
            } else {
                $data = json_decode($result['response'], true);
                $apifyStatus = $data['data']['status'] ?? 'UNKNOWN';
                echo "<p>Apify Status: <strong style='color:" . ($apifyStatus === 'SUCCEEDED' ? 'green' : 'blue') . "'>" . $apifyStatus . "</strong></p>";

                if ($apifyStatus === 'SUCCEEDED') {
                    // Получаем результаты
                    $datasetUrl = "https://api.apify.com/v2/actor-runs/{$lastRun['apify_run_id']}/dataset/items?token=" . APIFY_TOKEN;
                    $dataResult = curlGet($datasetUrl);
                    $items = json_decode($dataResult['response'], true) ?: [];

                    echo "<p>Результатов в Apify: <strong style='color:green'>" . count($items) . "</strong></p>";

                    if (!empty($items) && $lastRun['status'] !== 'completed') {
                        echo "<p>Первый результат:</p>";
                        echo "<pre style='max-height:200px;overflow:auto'>" . htmlspecialchars(print_r($items[0], true)) . "</pre>";

                        // Синхронизируем
                        echo "<h4>🔄 Синхронизация...</h4>";
                        $parser = new Parser();
                        $syncResult = $parser->processWebhook($lastRun['id'], $lastRun['user_id']);
                        echo "<pre style='color:green'>" . htmlspecialchars(print_r($syncResult, true)) . "</pre>";
                    } elseif ($lastRun['status'] === 'completed') {
                        echo "<p style='color:green'>✅ Уже синхронизирован</p>";
                    }
                }
            }
        } else {
            echo "<p style='color:red'>❌ Нет apify_run_id!</p>";
        }
        echo "<hr>";

        // Показываем только первые 3
        if ($idx >= 2) break;
    }
} else {
    echo "<p style='color:red'>❌ Нет запусков в БД</p>";
}

// 8. Проверяем объявления после синхронизации
echo "<h2>8. Объявления после синхронизации</h2>";
$listingsAfter = $db->fetchAll("SELECT COUNT(*) as cnt FROM listings");
echo "<p>Всего объявлений: <strong style='color:green'>" . $listingsAfter[0]['cnt'] . "</strong></p>";

$recentListings = $db->fetchAll("SELECT id, title, price, source, created_at FROM listings ORDER BY id DESC LIMIT 5");
if (!empty($recentListings)) {
    echo "<p>Последние объявления:</p>";
    echo "<table border='1' cellpadding='5'><tr><th>ID</th><th>Title</th><th>Price</th><th>Source</th><th>Created</th></tr>";
    foreach ($recentListings as $l) {
        echo "<tr><td>{$l['id']}</td><td>" . htmlspecialchars(substr($l['title'], 0, 50)) . "</td><td>{$l['price']}</td><td>{$l['source']}</td><td>{$l['created_at']}</td></tr>";
    }
    echo "</table>";
}

echo "<hr><p><strong>УДАЛИТЕ ЭТОТ ФАЙЛ ПОСЛЕ ИСПОЛЬЗОВАНИЯ!</strong></p>";
