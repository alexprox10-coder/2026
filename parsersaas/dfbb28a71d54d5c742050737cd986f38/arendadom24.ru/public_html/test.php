<?php
echo "PHP работает!<br>";
echo "Версия: " . phpversion() . "<br>";

// Проверим config.php
$configFile = __DIR__ . '/backend/config.php';
echo "<br>Config файл: " . ($configFile) . "<br>";
echo "Существует: " . (file_exists($configFile) ? 'ДА' : 'НЕТ') . "<br>";

if (file_exists($configFile)) {
    echo "Размер: " . filesize($configFile) . " bytes<br>";
    echo "<br><b>Первые 500 символов config.php:</b><br>";
    echo "<pre>" . htmlspecialchars(substr(file_get_contents($configFile), 0, 500)) . "</pre>";
}
