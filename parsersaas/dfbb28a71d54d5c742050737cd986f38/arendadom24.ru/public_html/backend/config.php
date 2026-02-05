<?php
/**
 * Parser SaaS - Конфигурация
 */

// Режим разработки
define('DEBUG', true);

// Домен сайта
define('SITE_URL', 'https://arendadom24.ru');
define('API_URL', SITE_URL . '/api');

// База данных MySQL (Beget)
// ВАЖНО: Замените на реальные данные на сервере!
define('DB_HOST', getenv('DB_HOST') ?: 'localhost');
define('DB_NAME', getenv('DB_NAME') ?: 'YOUR_DB_NAME');
define('DB_USER', getenv('DB_USER') ?: 'YOUR_DB_USER');
define('DB_PASS', getenv('DB_PASS') ?: 'YOUR_DB_PASS');

// Apify
define('APIFY_TOKEN', getenv('APIFY_TOKEN') ?: 'YOUR_APIFY_TOKEN');
define('APIFY_AVITO_ACTOR', 'D81KRIfXBnQ4hg8Bz');
define('APIFY_CIAN_ACTOR', 'CBn1BidHkyYcqYpPd');

// Google OAuth
define('GOOGLE_CLIENT_ID', getenv('GOOGLE_CLIENT_ID') ?: 'YOUR_GOOGLE_CLIENT_ID');
define('GOOGLE_CLIENT_SECRET', getenv('GOOGLE_CLIENT_SECRET') ?: 'YOUR_GOOGLE_CLIENT_SECRET');
define('GOOGLE_REDIRECT_URI', SITE_URL . '/api/auth/google/callback');

// Telegram Login
define('TELEGRAM_BOT_USERNAME', getenv('TELEGRAM_BOT_USERNAME') ?: 'ParsersaasBot');
define('TELEGRAM_BOT_TOKEN', getenv('TELEGRAM_BOT_TOKEN') ?: 'YOUR_TELEGRAM_BOT_TOKEN');

// JWT секрет для токенов
define('JWT_SECRET', getenv('JWT_SECRET') ?: 'CHANGE_THIS_TO_RANDOM_STRING');
define('JWT_EXPIRY', 86400 * 30);

// Email (SMTP)
define('SMTP_HOST', getenv('SMTP_HOST') ?: 'smtp.beget.com');
define('SMTP_PORT', 465);
define('SMTP_USER', getenv('SMTP_USER') ?: 'noreply@arendadom24.ru');
define('SMTP_PASS', getenv('SMTP_PASS') ?: 'YOUR_SMTP_PASS');
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
