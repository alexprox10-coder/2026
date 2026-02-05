<?php
class User {
    private $db;

    public function __construct() {
        $this->db = Database::getInstance();
    }

    public function register($email, $password, $firstName = '', $lastName = '') {
        if (empty($email) || empty($password)) {
            return array('success' => false, 'error' => 'Email и пароль обязательны');
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return array('success' => false, 'error' => 'Неверный формат email');
        }

        $existing = $this->db->fetch("SELECT id FROM users WHERE email = ?", array($email));
        if ($existing) {
            return array('success' => false, 'error' => 'Пользователь уже существует');
        }

        $userId = $this->db->insert('users', array(
            'email' => $email,
            'password_hash' => password_hash($password, PASSWORD_DEFAULT),
            'first_name' => $firstName,
            'last_name' => $lastName,
            'plan' => 'free',
            'daily_limit' => 100,
            'daily_used' => 0
        ));

        return array('success' => true, 'user_id' => $userId);
    }

    public function login($email, $password) {
        if (empty($email) || empty($password)) {
            return array('success' => false, 'error' => 'Email и пароль обязательны');
        }

        $user = $this->db->fetch("SELECT * FROM users WHERE email = ?", array($email));
        if (!$user || !password_verify($password, $user['password_hash'])) {
            return array('success' => false, 'error' => 'Неверный email или пароль');
        }

        $token = $this->createSession($user['id']);
        return array('success' => true, 'token' => $token, 'user' => $this->sanitizeUser($user));
    }

    public function googleAuth($googleId, $email, $firstName, $lastName, $picture) {
        if (empty($email)) {
            return array('success' => false, 'error' => 'Email не получен от Google');
        }

        $user = $this->db->fetch("SELECT * FROM users WHERE email = ? OR google_id = ?", array($email, $googleId));

        if ($user) {
            if (empty($user['google_id'])) {
                $this->db->update('users', array(
                    'google_id' => $googleId,
                    'avatar_url' => $picture
                ), 'id = ?', array($user['id']));
            }
        } else {
            $userId = $this->db->insert('users', array(
                'email' => $email,
                'google_id' => $googleId,
                'first_name' => $firstName,
                'last_name' => $lastName,
                'avatar_url' => $picture,
                'plan' => 'free',
                'daily_limit' => 100,
                'daily_used' => 0
            ));
            $user = $this->db->fetch("SELECT * FROM users WHERE id = ?", array($userId));
        }

        $token = $this->createSession($user['id']);
        return array('success' => true, 'token' => $token, 'user' => $this->sanitizeUser($user));
    }

    public function createSession($userId) {
        $token = bin2hex(openssl_random_pseudo_bytes(32));
        $hashedToken = hash('sha256', $token);
        $expiresAt = date('Y-m-d H:i:s', time() + 86400 * 30);

        $this->db->insert('sessions', array(
            'user_id' => $userId,
            'token' => $hashedToken,
            'expires_at' => $expiresAt
        ));

        return $token;
    }

    public function validateToken($token) {
        if (empty($token)) return null;

        $hashedToken = hash('sha256', $token);
        $session = $this->db->fetch(
            "SELECT * FROM sessions WHERE token = ? AND expires_at > NOW()",
            array($hashedToken)
        );

        if (!$session) return null;

        return $this->db->fetch("SELECT * FROM users WHERE id = ?", array($session['user_id']));
    }

    public function logout($token) {
        $hashedToken = hash('sha256', $token);
        $this->db->query("DELETE FROM sessions WHERE token = ?", array($hashedToken));
    }

    public function getById($userId) {
        return $this->db->fetch("SELECT * FROM users WHERE id = ?", array($userId));
    }

    private function sanitizeUser($user) {
        unset($user['password_hash']);
        return $user;
    }
}
