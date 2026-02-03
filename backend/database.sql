-- =============================================
-- Parser SaaS - Структура базы данных
-- Выполнить в phpMyAdmin на Beget
-- =============================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) UNIQUE,
    `password_hash` VARCHAR(255),
    `first_name` VARCHAR(100),
    `last_name` VARCHAR(100),
    `avatar_url` VARCHAR(500),

    -- OAuth данные
    `google_id` VARCHAR(255) UNIQUE,
    `telegram_id` VARCHAR(255) UNIQUE,
    `telegram_username` VARCHAR(255),

    -- Настройки Telegram бота клиента
    `telegram_bot_token` VARCHAR(255),
    `telegram_chat_id` VARCHAR(255),

    -- Настройки Google Sheets
    `google_sheets_url` VARCHAR(500),
    `google_sheets_id` VARCHAR(255),

    -- Email для уведомлений
    `notification_email` VARCHAR(255),
    `email_notifications` TINYINT(1) DEFAULT 1,
    `telegram_notifications` TINYINT(1) DEFAULT 1,

    -- Тариф
    `plan` ENUM('free', 'basic', 'pro', 'enterprise') DEFAULT 'free',
    `plan_expires_at` DATETIME,
    `daily_limit` INT DEFAULT 100,
    `daily_used` INT DEFAULT 0,
    `daily_reset_at` DATE,

    -- API
    `api_key` VARCHAR(64) UNIQUE,

    -- Статус
    `is_active` TINYINT(1) DEFAULT 1,
    `is_verified` TINYINT(1) DEFAULT 0,
    `verification_token` VARCHAR(64),

    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `last_login_at` TIMESTAMP,

    INDEX `idx_email` (`email`),
    INDEX `idx_google_id` (`google_id`),
    INDEX `idx_telegram_id` (`telegram_id`),
    INDEX `idx_api_key` (`api_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица тарифов
CREATE TABLE IF NOT EXISTS `plans` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `slug` VARCHAR(50) UNIQUE NOT NULL,
    `price_monthly` DECIMAL(10,2) DEFAULT 0,
    `price_yearly` DECIMAL(10,2) DEFAULT 0,
    `daily_limit` INT DEFAULT 100,
    `cities_limit` INT DEFAULT 1,
    `features` JSON,
    `is_active` TINYINT(1) DEFAULT 1,
    `sort_order` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Базовые тарифы
INSERT INTO `plans` (`name`, `slug`, `price_monthly`, `price_yearly`, `daily_limit`, `cities_limit`, `features`, `sort_order`) VALUES
('Free', 'free', 0, 0, 100, 1, '{"excel": true, "telegram": true, "google_sheets": false, "api": false, "schedule": false, "support": "chat"}', 1),
('Basic', 'basic', 790, 7500, 1000, 5, '{"excel": true, "telegram": true, "google_sheets": true, "api": false, "schedule": true, "support": "email"}', 2),
('Pro', 'pro', 1990, 19000, 10000, 999, '{"excel": true, "telegram": true, "google_sheets": true, "api": true, "schedule": true, "support": "priority"}', 3),
('Enterprise', 'enterprise', 0, 0, 999999, 999, '{"excel": true, "telegram": true, "google_sheets": true, "api": true, "schedule": true, "support": "manager"}', 4);

-- Таблица задач парсинга
CREATE TABLE IF NOT EXISTS `parsing_tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `name` VARCHAR(255),

    -- Источник
    `source` ENUM('avito', 'cian') NOT NULL,

    -- Параметры парсинга
    `location` VARCHAR(255) NOT NULL,
    `category` VARCHAR(100),
    `operation_type` ENUM('rent', 'sale') DEFAULT 'rent',
    `price_min` INT,
    `price_max` INT,
    `rooms` VARCHAR(50),
    `area_min` INT,
    `area_max` INT,
    `keywords` TEXT,
    `max_items` INT DEFAULT 100,

    -- Расписание
    `schedule_enabled` TINYINT(1) DEFAULT 0,
    `schedule_interval` ENUM('15min', '30min', '1hour', '3hours', '6hours', '12hours', '24hours') DEFAULT '1hour',
    `last_run_at` TIMESTAMP,
    `next_run_at` TIMESTAMP,

    -- Экспорт
    `export_telegram` TINYINT(1) DEFAULT 1,
    `export_email` TINYINT(1) DEFAULT 0,
    `export_sheets` TINYINT(1) DEFAULT 0,

    -- Статус
    `status` ENUM('active', 'paused', 'completed', 'error') DEFAULT 'active',
    `error_message` TEXT,

    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_next_run` (`next_run_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица запусков парсинга
CREATE TABLE IF NOT EXISTS `parsing_runs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `task_id` INT NOT NULL,
    `user_id` INT NOT NULL,

    -- Apify данные
    `apify_run_id` VARCHAR(255),
    `apify_dataset_id` VARCHAR(255),

    -- Результаты
    `items_found` INT DEFAULT 0,
    `items_new` INT DEFAULT 0,
    `items_exported` INT DEFAULT 0,

    -- Статус
    `status` ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    `started_at` TIMESTAMP,
    `completed_at` TIMESTAMP,
    `error_message` TEXT,

    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`task_id`) REFERENCES `parsing_tasks`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица результатов (объявления)
CREATE TABLE IF NOT EXISTS `listings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `run_id` INT NOT NULL,
    `task_id` INT NOT NULL,
    `user_id` INT NOT NULL,

    -- Уникальный ID объявления
    `external_id` VARCHAR(255) NOT NULL,
    `source` ENUM('avito', 'cian') NOT NULL,

    -- Данные объявления
    `title` VARCHAR(500),
    `price` DECIMAL(15,2),
    `price_currency` VARCHAR(10) DEFAULT 'RUB',
    `location` VARCHAR(255),
    `address` VARCHAR(500),
    `url` VARCHAR(1000),
    `image_url` VARCHAR(1000),

    -- Характеристики
    `rooms` VARCHAR(20),
    `area` DECIMAL(10,2),
    `floor` VARCHAR(20),
    `total_floors` INT,

    -- Контакты
    `phone` VARCHAR(50),
    `seller_name` VARCHAR(255),

    -- Полные данные JSON
    `raw_data` JSON,

    -- Статус
    `is_sent_telegram` TINYINT(1) DEFAULT 0,
    `is_sent_email` TINYINT(1) DEFAULT 0,
    `is_sent_sheets` TINYINT(1) DEFAULT 0,

    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`run_id`) REFERENCES `parsing_runs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`task_id`) REFERENCES `parsing_tasks`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_listing` (`user_id`, `source`, `external_id`),
    INDEX `idx_user_source` (`user_id`, `source`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица сессий
CREATE TABLE IF NOT EXISTS `sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `token` VARCHAR(64) UNIQUE NOT NULL,
    `ip_address` VARCHAR(45),
    `user_agent` VARCHAR(500),
    `expires_at` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token` (`token`),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица платежей
CREATE TABLE IF NOT EXISTS `payments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `plan_slug` VARCHAR(50) NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `currency` VARCHAR(10) DEFAULT 'RUB',
    `period` ENUM('monthly', 'yearly') DEFAULT 'monthly',
    `payment_method` VARCHAR(50),
    `payment_id` VARCHAR(255),
    `status` ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица городов
CREATE TABLE IF NOT EXISTS `cities` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `name_en` VARCHAR(255),
    `region` VARCHAR(255),
    `avito_slug` VARCHAR(255),
    `cian_id` INT,
    `is_active` TINYINT(1) DEFAULT 1,
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Популярные города
INSERT INTO `cities` (`name`, `name_en`, `region`, `avito_slug`) VALUES
('Москва', 'Moscow', 'Москва', 'moskva'),
('Санкт-Петербург', 'Saint Petersburg', 'Санкт-Петербург', 'sankt-peterburg'),
('Новосибирск', 'Novosibirsk', 'Новосибирская область', 'novosibirsk'),
('Екатеринбург', 'Yekaterinburg', 'Свердловская область', 'ekaterinburg'),
('Казань', 'Kazan', 'Республика Татарстан', 'kazan'),
('Нижний Новгород', 'Nizhny Novgorod', 'Нижегородская область', 'nizhniy_novgorod'),
('Краснодар', 'Krasnodar', 'Краснодарский край', 'krasnodar'),
('Самара', 'Samara', 'Самарская область', 'samara'),
('Ростов-на-Дону', 'Rostov-on-Don', 'Ростовская область', 'rostov-na-donu'),
('Челябинск', 'Chelyabinsk', 'Челябинская область', 'chelyabinsk'),
('Уфа', 'Ufa', 'Республика Башкортостан', 'ufa'),
('Воронеж', 'Voronezh', 'Воронежская область', 'voronezh'),
('Красноярск', 'Krasnoyarsk', 'Красноярский край', 'krasnoyarsk'),
('Пермь', 'Perm', 'Пермский край', 'perm'),
('Волгоград', 'Volgograd', 'Волгоградская область', 'volgograd'),
('Благовещенск', 'Blagoveshchensk', 'Амурская область', 'blagoveschensk');
