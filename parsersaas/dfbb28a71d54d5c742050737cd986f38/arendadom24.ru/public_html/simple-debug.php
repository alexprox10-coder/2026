<?php
/**
 * Simple Debug - минимальный тест
 * УДАЛИТЕ ПОСЛЕ ИСПОЛЬЗОВАНИЯ!
 */
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>Simple Debug</h1>";

// 1. PHP работает
echo "<p>✅ PHP работает</p>";
echo "<p>PHP версия: " . phpversion() . "</p>";

// 2. Проверяем наличие файлов
echo "<h2>Проверка файлов:</h2>";

$files = [
    '/backend/config.php',
    '/backend/classes/Database.php',
    '/backend/classes/User.php',
    '/backend/classes/Parser.php',
    '/backend/api/index.php'
];

foreach ($files as $file) {
    $path = __DIR__ . $file;
    if (file_exists($path)) {
        echo "<p>✅ " . $file . " - существует (" . filesize($path) . " bytes)</p>";
    } else {
        echo "<p>❌ " . $file . " - НЕ НАЙДЕН!</p>";
    }
}

// 3. Попробуем подключить config
echo "<h2>Подключение config.php:</h2>";
try {
    require_once __DIR__ . '/backend/config.php';
    echo "<p>✅ config.php загружен</p>";
    echo "<p>DB_HOST: " . (defined('DB_HOST') ? DB_HOST : 'не определён') . "</p>";
    echo "<p>APIFY_TOKEN: " . (defined('APIFY_TOKEN') ? substr(APIFY_TOKEN, 0, 10) . '...' : 'не определён') . "</p>";
} catch (Exception $e) {
    echo "<p>❌ Ошибка: " . $e->getMessage() . "</p>";
}

// 4. Попробуем подключиться к БД напрямую
echo "<h2>Тест подключения к БД:</h2>";
try {
    if (defined('DB_HOST') && defined('DB_NAME') && defined('DB_USER') && defined('DB_PASS')) {
        $pdo = new PDO(
            "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4",
            DB_USER,
            DB_PASS
        );
        echo "<p>✅ Подключение к MySQL успешно!</p>";

        // Проверяем таблицы
        $tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
        echo "<p>Таблицы: " . implode(', ', $tables) . "</p>";

        // Проверяем parsing_runs
        $runs = $pdo->query("SELECT id, task_id, user_id, status, apify_run_id, started_at FROM parsing_runs ORDER BY id DESC LIMIT 5")->fetchAll(PDO::FETCH_ASSOC);
        echo "<h3>Последние 5 запусков:</h3>";
        echo "<pre>" . print_r($runs, true) . "</pre>";

        // Проверяем listings
        $count = $pdo->query("SELECT COUNT(*) FROM listings")->fetchColumn();
        echo "<p>Объявлений в БД: <strong>" . $count . "</strong></p>";

    } else {
        echo "<p>❌ Константы БД не определены</p>";
    }
} catch (PDOException $e) {
    echo "<p>❌ Ошибка БД: " . $e->getMessage() . "</p>";
}

echo "<hr><p><strong>УДАЛИТЕ ЭТОТ ФАЙЛ!</strong></p>";
