<?php
/**
 * Parser SaaS - Конфигурация
 * ВАЖНО: Замени значения на свои!
 */

// Режим разработки
define('DEBUG', false);

// Домен сайта
define('SITE_URL', 'https://arendadom24.ru');
define('API_URL', SITE_URL . '/api');

// База данных MySQL (Beget)
define('DB_HOST', 'localhost');
define('DB_NAME', 'alexprz7_2026');
define('DB_USER', 'alexprz7_2026');
define('DB_PASS', 'YOUR_DB_PASSWORD'); // Замени на свой пароль

// Apify
define('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'); // Замени на свой токен
define('APIFY_AVITO_ACTOR', 'D81KRIfXBnQ4hg8Bz');
define('APIFY_CIAN_ACTOR', 'CBn1BidHkyYcqYpPd');

// Google OAuth (получить на https://console.cloud.google.com/apis/credentials)
define('GOOGLE_CLIENT_ID', ''); // <-- ДОБАВЬ
define('GOOGLE_CLIENT_SECRET', ''); // <-- ДОБАВЬ
define('GOOGLE_REDIRECT_URI', SITE_URL . '/api/auth/google/callback');

// Telegram Login (https://core.telegram.org/widgets/login)
define('TELEGRAM_BOT_USERNAME', 'ParsersaasBot'); // Имя бота без @
define('TELEGRAM_BOT_TOKEN', ''); // Токен бота для проверки авторизации

// JWT секрет для токенов
define('JWT_SECRET', 'замени_на_случайную_строку_минимум_32_символа');
define('JWT_EXPIRY', 86400 * 30); // 30 дней

// Email (SMTP)
define('SMTP_HOST', 'smtp.beget.com');
define('SMTP_PORT', 465);
define('SMTP_USER', 'noreply@arendadom24.ru');
define('SMTP_PASS', ''); // <-- ДОБАВЬ
define('SMTP_FROM', 'noreply@arendadom24.ru');
define('SMTP_FROM_NAME', 'Parser SaaS');

// Лимиты по умолчанию
define('DEFAULT_DAILY_LIMIT', 100);

// Тарифы
$PLANS = [
    'free' => [
        'name' => 'Free',
        'price_monthly' => 0,
        'price_yearly' => 0,
        'daily_limit' => 100,
        'cities_limit' => 1,
        'features' => ['excel', 'telegram']
    ],
    'basic' => [
        'name' => 'Basic',
        'price_monthly' => 790,
        'price_yearly' => 7500,
        'daily_limit' => 1000,
        'cities_limit' => 5,
        'features' => ['excel', 'telegram', 'google_sheets', 'schedule', 'email_support']
    ],
    'pro' => [
        'name' => 'Pro',
        'price_monthly' => 1990,
        'price_yearly' => 19000,
        'daily_limit' => 10000,
        'cities_limit' => 999,
        'features' => ['excel', 'telegram', 'google_sheets', 'schedule', 'api', 'priority_support']
    ],
    'enterprise' => [
        'name' => 'Enterprise',
        'price_monthly' => 0, // По запросу
        'price_yearly' => 0,
        'daily_limit' => 999999,
        'cities_limit' => 999,
        'features' => ['all', 'dedicated', 'manager']
    ]
];

// Часовой пояс
date_default_timezone_set('Europe/Moscow');

// Обработка ошибок
if (DEBUG) {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
} else {
    error_reporting(0);
    ini_set('display_errors', 0);
}

// Автозагрузка классов
spl_autoload_register(function ($class) {
    $file = __DIR__ . '/classes/' . $class . '.php';
    if (file_exists($file)) {
        require_once $file;
    }
});
