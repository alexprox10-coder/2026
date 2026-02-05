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

// 7. Попробуем синхронизировать последний run
echo "<h2>7. Тест синхронизации</h2>";
if (!empty($runs)) {
    $lastRun = $runs[0];
    echo "<p>Последний run ID: " . $lastRun['id'] . "</p>";
    echo "<p>Apify Run ID: " . ($lastRun['apify_run_id'] ?: 'НЕТ!') . "</p>";
    echo "<p>Status: " . $lastRun['status'] . "</p>";

    if (!empty($lastRun['apify_run_id'])) {
        // Проверим статус в Apify
        $apifyUrl = "https://api.apify.com/v2/actor-runs/{$lastRun['apify_run_id']}?token=" . APIFY_TOKEN;
        $response = @file_get_contents($apifyUrl);
        $data = json_decode($response, true);

        echo "<p>Apify Status: <strong>" . ($data['data']['status'] ?? 'UNKNOWN') . "</strong></p>";

        if (isset($data['data']['status']) && $data['data']['status'] === 'SUCCEEDED') {
            // Попробуем получить результаты
            $datasetUrl = "https://api.apify.com/v2/actor-runs/{$lastRun['apify_run_id']}/dataset/items?token=" . APIFY_TOKEN;
            $items = json_decode(@file_get_contents($datasetUrl), true);

            echo "<p>Результатов в Apify: <strong>" . count($items) . "</strong></p>";

            if (!empty($items)) {
                echo "<p>Первый результат:</p>";
                echo "<pre>" . print_r($items[0], true) . "</pre>";

                // Попробуем сохранить
                echo "<h3>Сохранение в БД...</h3>";
                $parser = new Parser();
                $result = $parser->processWebhook($lastRun['id'], $lastRun['user_id']);
                echo "<pre>" . print_r($result, true) . "</pre>";
            }
        }
    } else {
        echo "<p style='color:red'>❌ У последнего запуска нет apify_run_id!</p>";
    }
} else {
    echo "<p style='color:red'>❌ Нет запусков в БД</p>";
}

echo "<hr><p><strong>УДАЛИТЕ ЭТОТ ФАЙЛ ПОСЛЕ ИСПОЛЬЗОВАНИЯ!</strong></p>";
