<?php
/**
 * Класс для работы с пользователями
 */
class User {
    private $db;

    public function __construct() {
        $this->db = Database::getInstance();
    }

    /**
     * Регистрация через email
     */
    public function register($email, $password, $firstName = '', $lastName = '') {
        // Проверяем существует ли пользователь
        $existing = $this->getByEmail($email);
        if ($existing) {
            return ['success' => false, 'error' => 'Пользователь с таким email уже существует'];
        }

        // Валидация email
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return ['success' => false, 'error' => 'Некорректный email'];
        }

        // Валидация пароля
        if (strlen($password) < 8) {
            return ['success' => false, 'error' => 'Пароль должен быть минимум 8 символов'];
        }

        // Создаём пользователя
        $verificationToken = bin2hex(random_bytes(32));
        $apiKey = bin2hex(random_bytes(32));

        $userId = $this->db->insert('users', [
            'email' => $email,
            'password_hash' => password_hash($password, PASSWORD_DEFAULT),
            'first_name' => $firstName,
            'last_name' => $lastName,
            'verification_token' => $verificationToken,
            'api_key' => $apiKey,
            'plan' => 'free',
            'daily_limit' => DEFAULT_DAILY_LIMIT,
            'daily_reset_at' => date('Y-m-d')
        ]);

        // Отправляем письмо подтверждения (опционально)
        // $this->sendVerificationEmail($email, $verificationToken);

        return [
            'success' => true,
            'user_id' => $userId,
            'message' => 'Регистрация успешна'
        ];
    }

    /**
     * Вход через email
     */
    public function login($email, $password) {
        $user = $this->getByEmail($email);

        if (!$user) {
            return ['success' => false, 'error' => 'Пользователь не найден'];
        }

        if (!password_verify($password, $user['password_hash'])) {
            return ['success' => false, 'error' => 'Неверный пароль'];
        }

        if (!$user['is_active']) {
            return ['success' => false, 'error' => 'Аккаунт заблокирован'];
        }

        // Обновляем время входа
        $this->db->update('users', ['last_login_at' => date('Y-m-d H:i:s')], 'id = ?', [$user['id']]);

        // Создаём сессию
        $token = $this->createSession($user['id']);

        return [
            'success' => true,
            'token' => $token,
            'user' => $this->sanitizeUser($user)
        ];
    }

    /**
     * Авторизация через Google
     */
    public function googleAuth($googleId, $email, $firstName, $lastName, $avatarUrl = null) {
        // Ищем по google_id
        $user = $this->db->fetch("SELECT * FROM users WHERE google_id = ?", [$googleId]);

        if ($user) {
            // Обновляем данные
            $this->db->update('users', [
                'last_login_at' => date('Y-m-d H:i:s'),
                'avatar_url' => $avatarUrl
            ], 'id = ?', [$user['id']]);
        } else {
            // Проверяем по email
            $user = $this->getByEmail($email);

            if ($user) {
                // Привязываем Google к существующему аккаунту
                $this->db->update('users', [
                    'google_id' => $googleId,
                    'avatar_url' => $avatarUrl,
                    'last_login_at' => date('Y-m-d H:i:s')
                ], 'id = ?', [$user['id']]);
            } else {
                // Создаём нового пользователя
                $apiKey = bin2hex(random_bytes(32));
                $userId = $this->db->insert('users', [
                    'email' => $email,
                    'google_id' => $googleId,
                    'first_name' => $firstName,
                    'last_name' => $lastName,
                    'avatar_url' => $avatarUrl,
                    'api_key' => $apiKey,
                    'is_verified' => 1,
                    'plan' => 'free',
                    'daily_limit' => DEFAULT_DAILY_LIMIT,
                    'daily_reset_at' => date('Y-m-d')
                ]);
                $user = $this->getById($userId);
            }
        }

        $token = $this->createSession($user['id']);

        return [
            'success' => true,
            'token' => $token,
            'user' => $this->sanitizeUser($user)
        ];
    }

    /**
     * Авторизация через Telegram
     */
    public function telegramAuth($telegramData) {
        // Проверяем подпись от Telegram
        if (!$this->verifyTelegramAuth($telegramData)) {
            return ['success' => false, 'error' => 'Неверная подпись Telegram'];
        }

        $telegramId = $telegramData['id'];
        $firstName = $telegramData['first_name'] ?? '';
        $lastName = $telegramData['last_name'] ?? '';
        $username = $telegramData['username'] ?? '';
        $photoUrl = $telegramData['photo_url'] ?? null;

        // Ищем по telegram_id
        $user = $this->db->fetch("SELECT * FROM users WHERE telegram_id = ?", [$telegramId]);

        if ($user) {
            $this->db->update('users', [
                'last_login_at' => date('Y-m-d H:i:s'),
                'telegram_username' => $username,
                'avatar_url' => $photoUrl
            ], 'id = ?', [$user['id']]);
        } else {
            // Создаём нового пользователя
            $apiKey = bin2hex(random_bytes(32));
            $userId = $this->db->insert('users', [
                'telegram_id' => $telegramId,
                'telegram_username' => $username,
                'first_name' => $firstName,
                'last_name' => $lastName,
                'avatar_url' => $photoUrl,
                'api_key' => $apiKey,
                'is_verified' => 1,
                'plan' => 'free',
                'daily_limit' => DEFAULT_DAILY_LIMIT,
                'daily_reset_at' => date('Y-m-d')
            ]);
            $user = $this->getById($userId);
        }

        $token = $this->createSession($user['id']);

        return [
            'success' => true,
            'token' => $token,
            'user' => $this->sanitizeUser($user)
        ];
    }

    /**
     * Проверка подписи Telegram
     */
    private function verifyTelegramAuth($data) {
        if (empty(TELEGRAM_BOT_TOKEN)) {
            return true; // Пропускаем проверку если токен не настроен
        }

        $checkHash = $data['hash'] ?? '';
        unset($data['hash']);

        $dataCheckArr = [];
        foreach ($data as $key => $value) {
            $dataCheckArr[] = $key . '=' . $value;
        }
        sort($dataCheckArr);
        $dataCheckString = implode("\n", $dataCheckArr);

        $secretKey = hash('sha256', TELEGRAM_BOT_TOKEN, true);
        $hash = hash_hmac('sha256', $dataCheckString, $secretKey);

        return $hash === $checkHash;
    }

    /**
     * Создание сессии
     */
    public function createSession($userId) {
        $token = bin2hex(random_bytes(32));
        $expiresAt = date('Y-m-d H:i:s', time() + JWT_EXPIRY);

        $this->db->insert('sessions', [
            'user_id' => $userId,
            'token' => $token,
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? null,
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? null,
            'expires_at' => $expiresAt
        ]);

        return $token;
    }

    /**
     * Проверка токена и получение пользователя
     */
    public function validateToken($token) {
        $session = $this->db->fetch(
            "SELECT * FROM sessions WHERE token = ? AND expires_at > NOW()",
            [$token]
        );

        if (!$session) {
            return null;
        }

        return $this->getById($session['user_id']);
    }

    /**
     * Выход
     */
    public function logout($token) {
        $this->db->delete('sessions', 'token = ?', [$token]);
        return ['success' => true];
    }

    /**
     * Получить по ID
     */
    public function getById($id) {
        return $this->db->fetch("SELECT * FROM users WHERE id = ?", [$id]);
    }

    /**
     * Получить по email
     */
    public function getByEmail($email) {
        return $this->db->fetch("SELECT * FROM users WHERE email = ?", [$email]);
    }

    /**
     * Обновить настройки пользователя
     */
    public function updateSettings($userId, $data) {
        $allowedFields = [
            'first_name', 'last_name', 'notification_email',
            'telegram_bot_token', 'telegram_chat_id',
            'google_sheets_url', 'google_sheets_id',
            'email_notifications', 'telegram_notifications'
        ];

        $updateData = [];
        foreach ($allowedFields as $field) {
            if (isset($data[$field])) {
                $updateData[$field] = $data[$field];
            }
        }

        if (empty($updateData)) {
            return ['success' => false, 'error' => 'Нет данных для обновления'];
        }

        $this->db->update('users', $updateData, 'id = ?', [$userId]);

        return ['success' => true, 'message' => 'Настройки обновлены'];
    }

    /**
     * Проверить и сбросить дневной лимит
     */
    public function checkAndResetDailyLimit($userId) {
        $user = $this->getById($userId);

        if ($user['daily_reset_at'] !== date('Y-m-d')) {
            $this->db->update('users', [
                'daily_used' => 0,
                'daily_reset_at' => date('Y-m-d')
            ], 'id = ?', [$userId]);
            $user['daily_used'] = 0;
        }

        return $user;
    }

    /**
     * Увеличить счётчик использования
     */
    public function incrementUsage($userId, $count = 1) {
        $this->db->query(
            "UPDATE users SET daily_used = daily_used + ? WHERE id = ?",
            [$count, $userId]
        );
    }

    /**
     * Очистить приватные данные
     */
    private function sanitizeUser($user) {
        unset($user['password_hash']);
        unset($user['verification_token']);
        unset($user['telegram_bot_token']); // Не показываем токен бота
        return $user;
    }
}
