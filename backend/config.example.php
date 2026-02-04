<?php
/**
 * Parser SaaS - Конфигурация (ШАБЛОН)
 * Скопируй этот файл в config.php и заполни свои данные
 */

// Режим разработки
define('DEBUG', true);

// Домен сайта
define('SITE_URL', 'https://arendadom24.ru');
define('API_URL', SITE_URL . '/api');

// База данных MySQL
define('DB_HOST', 'localhost');
define('DB_NAME', 'your_db_name');
define('DB_USER', 'your_db_user');
define('DB_PASS', 'your_db_password');

// Apify - https://console.apify.com/account/integrations
define('APIFY_TOKEN', 'your_apify_token');
define('APIFY_AVITO_ACTOR', 'voyager_/avito-parser');
define('APIFY_CIAN_ACTOR', 'igolaizola/cian-scraper');

// Google OAuth - https://console.cloud.google.com/apis/credentials
define('GOOGLE_CLIENT_ID', 'your_google_client_id');
define('GOOGLE_CLIENT_SECRET', 'your_google_client_secret');
define('GOOGLE_REDIRECT_URI', SITE_URL . '/api/auth/google/callback');

// Telegram Login - https://core.telegram.org/widgets/login
define('TELEGRAM_BOT_USERNAME', 'YourBotUsername');
define('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token');

// JWT секрет для токенов (сгенерируй случайную строку 40+ символов)
define('JWT_SECRET', 'your_random_jwt_secret_at_least_40_chars');
define('JWT_EXPIRY', 86400 * 30);

// Email (SMTP)
define('SMTP_HOST', 'smtp.beget.com');
define('SMTP_PORT', 465);
define('SMTP_USER', 'noreply@yourdomain.ru');
define('SMTP_PASS', 'your_smtp_password');
define('SMTP_FROM', 'noreply@yourdomain.ru');
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
