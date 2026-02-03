<?php
/**
 * Класс для работы с парсингом через Apify
 */
class Parser {
    private $db;
    private $apifyToken;

    public function __construct() {
        $this->db = Database::getInstance();
        $this->apifyToken = APIFY_TOKEN;
    }

    /**
     * Создать задачу парсинга
     */
    public function createTask($userId, $data) {
        $user = (new User())->getById($userId);

        // Проверяем лимит городов
        $taskCount = $this->db->fetch(
            "SELECT COUNT(*) as cnt FROM parsing_tasks WHERE user_id = ? AND status = 'active'",
            [$userId]
        )['cnt'];

        $plan = $GLOBALS['PLANS'][$user['plan']] ?? $GLOBALS['PLANS']['free'];
        if ($taskCount >= $plan['cities_limit']) {
            return ['success' => false, 'error' => 'Достигнут лимит задач для вашего тарифа'];
        }

        $taskId = $this->db->insert('parsing_tasks', [
            'user_id' => $userId,
            'name' => $data['name'] ?? 'Новая задача',
            'source' => $data['source'] ?? 'avito',
            'location' => $data['location'],
            'category' => $data['category'] ?? null,
            'operation_type' => $data['operation_type'] ?? 'rent',
            'price_min' => $data['price_min'] ?? null,
            'price_max' => $data['price_max'] ?? null,
            'rooms' => $data['rooms'] ?? null,
            'area_min' => $data['area_min'] ?? null,
            'area_max' => $data['area_max'] ?? null,
            'keywords' => $data['keywords'] ?? null,
            'max_items' => min($data['max_items'] ?? 100, $user['daily_limit'] - $user['daily_used']),
            'schedule_enabled' => $data['schedule_enabled'] ?? 0,
            'schedule_interval' => $data['schedule_interval'] ?? '1hour',
            'export_telegram' => $data['export_telegram'] ?? 1,
            'export_email' => $data['export_email'] ?? 0,
            'export_sheets' => $data['export_sheets'] ?? 0,
            'status' => 'active'
        ]);

        return [
            'success' => true,
            'task_id' => $taskId,
            'message' => 'Задача создана'
        ];
    }

    /**
     * Запустить парсинг
     */
    public function runTask($taskId, $userId) {
        $task = $this->db->fetch(
            "SELECT * FROM parsing_tasks WHERE id = ? AND user_id = ?",
            [$taskId, $userId]
        );

        if (!$task) {
            return ['success' => false, 'error' => 'Задача не найдена'];
        }

        // Проверяем лимит
        $userObj = new User();
        $user = $userObj->checkAndResetDailyLimit($userId);

        if ($user['daily_used'] >= $user['daily_limit']) {
            return ['success' => false, 'error' => 'Достигнут дневной лимит. Обновите тариф для увеличения лимита.'];
        }

        // Создаём запись о запуске
        $runId = $this->db->insert('parsing_runs', [
            'task_id' => $taskId,
            'user_id' => $userId,
            'status' => 'pending',
            'started_at' => date('Y-m-d H:i:s')
        ]);

        // Запускаем парсер на Apify
        $actorId = $task['source'] === 'cian' ? APIFY_CIAN_ACTOR : APIFY_AVITO_ACTOR;
        $input = $this->buildApifyInput($task);

        $result = $this->callApify($actorId, $input);

        if (!$result['success']) {
            $this->db->update('parsing_runs', [
                'status' => 'failed',
                'error_message' => $result['error']
            ], 'id = ?', [$runId]);
            return $result;
        }

        // Обновляем запись о запуске
        $this->db->update('parsing_runs', [
            'status' => 'running',
            'apify_run_id' => $result['run_id']
        ], 'id = ?', [$runId]);

        // Обновляем задачу
        $this->db->update('parsing_tasks', [
            'last_run_at' => date('Y-m-d H:i:s')
        ], 'id = ?', [$taskId]);

        return [
            'success' => true,
            'run_id' => $runId,
            'apify_run_id' => $result['run_id'],
            'message' => 'Парсинг запущен'
        ];
    }

    /**
     * Проверить статус и получить результаты
     */
    public function checkRunStatus($runId, $userId) {
        $run = $this->db->fetch(
            "SELECT r.*, t.source FROM parsing_runs r
             JOIN parsing_tasks t ON r.task_id = t.id
             WHERE r.id = ? AND r.user_id = ?",
            [$runId, $userId]
        );

        if (!$run) {
            return ['success' => false, 'error' => 'Запуск не найден'];
        }

        if ($run['status'] === 'completed' || $run['status'] === 'failed') {
            return [
                'success' => true,
                'status' => $run['status'],
                'items_found' => $run['items_found']
            ];
        }

        // Проверяем статус на Apify
        $status = $this->getApifyRunStatus($run['apify_run_id']);

        if ($status['status'] === 'SUCCEEDED') {
            // Получаем результаты
            $items = $this->getApifyResults($run['apify_run_id']);
            $this->processResults($run, $items);

            return [
                'success' => true,
                'status' => 'completed',
                'items_found' => count($items)
            ];
        } elseif ($status['status'] === 'FAILED') {
            $this->db->update('parsing_runs', [
                'status' => 'failed',
                'error_message' => 'Ошибка Apify'
            ], 'id = ?', [$runId]);

            return [
                'success' => true,
                'status' => 'failed',
                'error' => 'Ошибка парсинга'
            ];
        }

        return [
            'success' => true,
            'status' => 'running'
        ];
    }

    /**
     * Построить input для Apify
     */
    private function buildApifyInput($task) {
        if ($task['source'] === 'cian') {
            return [
                'maxItems' => (int)$task['max_items'],
                'location' => $task['location'],
                'operationType' => $task['operation_type'],
                'category' => $task['category'] ?? '',
                'shortTermRent' => false,
                'proxyConfiguration' => [
                    'useApifyProxy' => true,
                    'apifyProxyGroups' => ['RESIDENTIAL']
                ]
            ];
        } else {
            // Avito
            $url = "https://www.avito.ru/" . $this->transliterate($task['location']) . "/kvartiry/sdam";
            if ($task['operation_type'] === 'sale') {
                $url = "https://www.avito.ru/" . $this->transliterate($task['location']) . "/kvartiry/prodam";
            }

            return [
                'startUrls' => [['url' => $url]],
                'limit' => (int)$task['max_items']
            ];
        }
    }

    /**
     * Вызов Apify API
     */
    private function callApify($actorId, $input) {
        $url = "https://api.apify.com/v2/acts/{$actorId}/runs?token={$this->apifyToken}";

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($input));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 201) {
            return ['success' => false, 'error' => 'Ошибка запуска Apify: ' . $response];
        }

        $data = json_decode($response, true);

        return [
            'success' => true,
            'run_id' => $data['data']['id']
        ];
    }

    /**
     * Получить статус запуска Apify
     */
    private function getApifyRunStatus($runId) {
        $url = "https://api.apify.com/v2/actor-runs/{$runId}?token={$this->apifyToken}";

        $response = file_get_contents($url);
        $data = json_decode($response, true);

        return [
            'status' => $data['data']['status'] ?? 'UNKNOWN'
        ];
    }

    /**
     * Получить результаты Apify
     */
    private function getApifyResults($runId) {
        $url = "https://api.apify.com/v2/actor-runs/{$runId}/dataset/items?token={$this->apifyToken}";

        $response = file_get_contents($url);
        return json_decode($response, true) ?: [];
    }

    /**
     * Обработка результатов
     */
    private function processResults($run, $items) {
        $task = $this->db->fetch("SELECT * FROM parsing_tasks WHERE id = ?", [$run['task_id']]);
        $user = (new User())->getById($run['user_id']);

        $newItems = 0;

        foreach ($items as $item) {
            $externalId = $item['id'] ?? $item['url'] ?? md5(json_encode($item));

            // Проверяем дубликат
            $existing = $this->db->fetch(
                "SELECT id FROM listings WHERE user_id = ? AND source = ? AND external_id = ?",
                [$run['user_id'], $task['source'], $externalId]
            );

            if ($existing) continue;

            // Сохраняем
            $this->db->insert('listings', [
                'run_id' => $run['id'],
                'task_id' => $run['task_id'],
                'user_id' => $run['user_id'],
                'external_id' => $externalId,
                'source' => $task['source'],
                'title' => $item['title'] ?? '',
                'price' => $this->extractPrice($item),
                'location' => $item['location'] ?? $item['address'] ?? '',
                'address' => $item['address'] ?? '',
                'url' => $item['url'] ?? '',
                'image_url' => $item['image'] ?? $item['photos'][0] ?? '',
                'rooms' => $item['rooms'] ?? '',
                'area' => $item['area'] ?? null,
                'floor' => $item['floor'] ?? '',
                'phone' => $item['phone'] ?? '',
                'seller_name' => $item['seller'] ?? $item['sellerName'] ?? '',
                'raw_data' => json_encode($item)
            ]);

            $newItems++;
        }

        // Обновляем статистику
        $this->db->update('parsing_runs', [
            'status' => 'completed',
            'completed_at' => date('Y-m-d H:i:s'),
            'items_found' => count($items),
            'items_new' => $newItems
        ], 'id = ?', [$run['id']]);

        // Обновляем использование
        (new User())->incrementUsage($run['user_id'], $newItems);

        // Отправляем уведомления
        if ($task['export_telegram'] && $user['telegram_bot_token'] && $user['telegram_chat_id']) {
            $this->sendToTelegram($user, $items, $task);
        }
    }

    /**
     * Отправка в Telegram
     */
    private function sendToTelegram($user, $items, $task) {
        $telegram = new Telegram($user['telegram_bot_token']);

        $message = "🏠 *Новые объявления*\n";
        $message .= "📍 {$task['location']}\n";
        $message .= "📊 Найдено: " . count($items) . " шт.\n\n";

        $count = 0;
        foreach ($items as $item) {
            if ($count >= 10) {
                $message .= "\n... и ещё " . (count($items) - 10) . " объявлений";
                break;
            }

            $price = $this->extractPrice($item);
            $title = $item['title'] ?? 'Без названия';
            $url = $item['url'] ?? '';

            $message .= "• {$title}\n";
            $message .= "  💰 " . number_format($price, 0, '', ' ') . " ₽\n";
            if ($url) {
                $message .= "  🔗 [Открыть]({$url})\n";
            }
            $message .= "\n";

            $count++;
        }

        $telegram->sendMessage($user['telegram_chat_id'], $message);
    }

    /**
     * Извлечь цену
     */
    private function extractPrice($item) {
        $price = $item['price'] ?? $item['priceValue'] ?? 0;
        if (is_string($price)) {
            $price = preg_replace('/[^\d]/', '', $price);
        }
        return (float)$price;
    }

    /**
     * Транслитерация для URL
     */
    private function transliterate($text) {
        $converter = [
            'а' => 'a', 'б' => 'b', 'в' => 'v', 'г' => 'g', 'д' => 'd',
            'е' => 'e', 'ё' => 'e', 'ж' => 'zh', 'з' => 'z', 'и' => 'i',
            'й' => 'y', 'к' => 'k', 'л' => 'l', 'м' => 'm', 'н' => 'n',
            'о' => 'o', 'п' => 'p', 'р' => 'r', 'с' => 's', 'т' => 't',
            'у' => 'u', 'ф' => 'f', 'х' => 'h', 'ц' => 'c', 'ч' => 'ch',
            'ш' => 'sh', 'щ' => 'sch', 'ь' => '', 'ы' => 'y', 'ъ' => '',
            'э' => 'e', 'ю' => 'yu', 'я' => 'ya', ' ' => '_', '-' => '_'
        ];
        return strtr(mb_strtolower($text), $converter);
    }

    /**
     * Получить задачи пользователя
     */
    public function getUserTasks($userId) {
        return $this->db->fetchAll(
            "SELECT * FROM parsing_tasks WHERE user_id = ? ORDER BY created_at DESC",
            [$userId]
        );
    }

    /**
     * Получить результаты пользователя
     */
    public function getUserListings($userId, $limit = 50, $offset = 0) {
        return $this->db->fetchAll(
            "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            [$userId, $limit, $offset]
        );
    }
}
