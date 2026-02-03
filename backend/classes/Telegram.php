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

    /**
     * Отправить сообщение
     */
    public function sendMessage($chatId, $text, $parseMode = 'Markdown') {
        return $this->request('sendMessage', [
            'chat_id' => $chatId,
            'text' => $text,
            'parse_mode' => $parseMode,
            'disable_web_page_preview' => true
        ]);
    }

    /**
     * Отправить фото
     */
    public function sendPhoto($chatId, $photoUrl, $caption = '') {
        return $this->request('sendPhoto', [
            'chat_id' => $chatId,
            'photo' => $photoUrl,
            'caption' => $caption,
            'parse_mode' => 'Markdown'
        ]);
    }

    /**
     * Отправить документ
     */
    public function sendDocument($chatId, $document, $caption = '') {
        return $this->request('sendDocument', [
            'chat_id' => $chatId,
            'document' => $document,
            'caption' => $caption
        ]);
    }

    /**
     * Получить информацию о боте
     */
    public function getMe() {
        return $this->request('getMe');
    }

    /**
     * Проверить валидность токена
     */
    public function isValidToken() {
        $result = $this->getMe();
        return $result['ok'] ?? false;
    }

    /**
     * Выполнить запрос к Telegram API
     */
    private function request($method, $params = []) {
        $url = $this->apiUrl . $this->token . '/' . $method;

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);

        $response = curl_exec($ch);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            return ['ok' => false, 'error' => $error];
        }

        return json_decode($response, true);
    }

    /**
     * Отправить список объявлений
     */
    public function sendListings($chatId, $listings, $taskName = '') {
        if (empty($listings)) {
            return $this->sendMessage($chatId, "📭 Новых объявлений не найдено.");
        }

        $header = "🏠 *Новые объявления*";
        if ($taskName) {
            $header .= "\n📋 Задача: {$taskName}";
        }
        $header .= "\n📊 Найдено: " . count($listings) . " шт.\n";

        $this->sendMessage($chatId, $header);

        // Отправляем по 5 объявлений
        $chunks = array_chunk($listings, 5);

        foreach ($chunks as $chunk) {
            $message = "";

            foreach ($chunk as $item) {
                $title = $item['title'] ?? 'Без названия';
                $price = number_format($item['price'] ?? 0, 0, '', ' ');
                $location = $item['location'] ?? $item['address'] ?? '';
                $url = $item['url'] ?? '';
                $rooms = $item['rooms'] ?? '';
                $area = $item['area'] ?? '';

                $message .= "━━━━━━━━━━━━━━━\n";
                $message .= "*{$title}*\n";
                $message .= "💰 {$price} ₽\n";

                if ($location) {
                    $message .= "📍 {$location}\n";
                }
                if ($rooms) {
                    $message .= "🚪 {$rooms} комн.\n";
                }
                if ($area) {
                    $message .= "📐 {$area} м²\n";
                }
                if ($url) {
                    $message .= "[🔗 Открыть объявление]({$url})\n";
                }
                $message .= "\n";
            }

            $this->sendMessage($chatId, $message);

            // Небольшая задержка чтобы не словить лимит
            usleep(500000); // 0.5 сек
        }

        return ['ok' => true, 'sent' => count($listings)];
    }
}
