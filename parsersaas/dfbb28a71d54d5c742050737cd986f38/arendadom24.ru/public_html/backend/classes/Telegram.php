<?php
/**
 * Класс для работы с Telegram Bot API
 */
class Telegram {
    private $token;
    private $apiUrl = 'https://api.telegram.org/bot';

    public function __construct($token) {
        $this->token = $token;
    }

    public function sendMessage($chatId, $text, $parseMode = 'HTML') {
        return $this->request('sendMessage', [
            'chat_id' => $chatId,
            'text' => $text,
            'parse_mode' => $parseMode,
            'disable_web_page_preview' => true
        ]);
    }

    public function sendPhoto($chatId, $photoUrl, $caption = '') {
        return $this->request('sendPhoto', [
            'chat_id' => $chatId,
            'photo' => $photoUrl,
            'caption' => $caption,
            'parse_mode' => 'HTML'
        ]);
    }

    public function getMe() {
        return $this->request('getMe');
    }

    public function setWebhook($url) {
        return $this->request('setWebhook', ['url' => $url]);
    }

    private function request($method, $params = []) {
        $url = $this->apiUrl . $this->token . '/' . $method;

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30
        ]);

        $response = curl_exec($ch);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            return ['ok' => false, 'error' => $error];
        }

        return json_decode($response, true);
    }

    /**
     * Проверка данных авторизации Telegram Login Widget
     */
    public static function verifyLoginData($authData, $botToken) {
        $checkHash = $authData['hash'];
        unset($authData['hash']);

        $dataCheckArr = [];
        foreach ($authData as $key => $value) {
            $dataCheckArr[] = $key . '=' . $value;
        }
        sort($dataCheckArr);
        $dataCheckString = implode("\n", $dataCheckArr);

        $secretKey = hash('sha256', $botToken, true);
        $hash = hash_hmac('sha256', $dataCheckString, $secretKey);

        if (strcmp($hash, $checkHash) !== 0) {
            return false;
        }

        // Проверяем что данные не старше 24 часов
        if ((time() - $authData['auth_date']) > 86400) {
            return false;
        }

        return true;
    }
}
