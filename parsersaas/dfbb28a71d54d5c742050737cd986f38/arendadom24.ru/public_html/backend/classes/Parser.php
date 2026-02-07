<?php
class Parser {
    private $db;
    private $apifyToken;

    public function __construct() {
        $this->db = Database::getInstance();
        $this->apifyToken = APIFY_TOKEN;
    }

    /**
     * Выполнить GET запрос через cURL (file_get_contents заблокирован на сервере)
     */
    private function curlGet($url) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);
        $response = curl_exec($ch);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            return false;
        }
        return $response;
    }

    public function createTask($userId, $data) {
        $name = isset($data['name']) ? $data['name'] : 'Новая задача';
        $url = isset($data['url']) ? trim($data['url']) : '';
        $maxItems = isset($data['max_items']) ? (int)$data['max_items'] : 50;

        // Определяем источник по URL
        $source = 'avito';
        if (strpos($url, 'cian.ru') !== false) {
            $source = 'cian';
        }

        // Валидация URL
        if (empty($url)) {
            return array('success' => false, 'error' => 'Вставьте ссылку на страницу поиска');
        }
        
        if ($source === 'avito' && strpos($url, 'avito.ru') === false) {
            return array('success' => false, 'error' => 'Некорректная ссылка. Вставьте ссылку с avito.ru или cian.ru');
        }

        // Проверяем лимит
        $user = $this->db->fetch("SELECT * FROM users WHERE id = ?", array($userId));
        $dailyLimit = isset($user['daily_limit']) ? (int)$user['daily_limit'] : 100;
        $dailyUsed = isset($user['daily_used']) ? (int)$user['daily_used'] : 0;
        
        if ($dailyUsed >= $dailyLimit) {
            return array('success' => false, 'error' => 'Достигнут дневной лимит. Улучшите тариф.');
        }

        $maxItems = min($maxItems, $dailyLimit - $dailyUsed);

        $taskId = $this->db->insert('parsing_tasks', array(
            'user_id' => $userId,
            'name' => $name,
            'source' => $source,
            'url' => $url,
            'max_items' => $maxItems,
            'status' => 'active'
        ));

        return array(
            'success' => true,
            'task_id' => $taskId,
            'message' => 'Задача создана. Нажмите "Запустить" для начала парсинга.'
        );
    }

    public function runTask($taskId, $userId) {
        $task = $this->db->fetch(
            "SELECT * FROM parsing_tasks WHERE id = ? AND user_id = ?",
            array($taskId, $userId)
        );

        if (!$task) {
            return array('success' => false, 'error' => 'Задача не найдена');
        }

        $runId = $this->db->insert('parsing_runs', array(
            'task_id' => $taskId,
            'user_id' => $userId,
            'status' => 'running',
            'started_at' => date('Y-m-d H:i:s')
        ));

        $result = $this->startApifyActor($task);

        if ($result['success']) {
            $this->db->update('parsing_runs', array(
                'apify_run_id' => $result['run_id'],
                'status' => 'running'
            ), 'id = ?', array($runId));

            return array(
                'success' => true,
                'run_id' => $runId,
                'apify_run_id' => $result['run_id'],
                'message' => 'Парсинг запущен! Результаты появятся через 2-5 минут.'
            );
        } else {
            $this->db->update('parsing_runs', array(
                'status' => 'failed',
                'error_message' => $result['error']
            ), 'id = ?', array($runId));

            return $result;
        }
    }

    private function startApifyActor($task) {
        $source = $task['source'];
        $url = $task['url'];
        $maxItems = (int)$task['max_items'];

        if ($source === 'avito') {
            $actorId = APIFY_AVITO_ACTOR;

            $input = array(
                'startUrls' => array(array('url' => $url)),
                'maxItems' => $maxItems,
                'limit' => $maxItems
            );
        } else {
            $actorId = APIFY_CIAN_ACTOR;

            $input = array(
                'startUrls' => array(array('url' => $url)),
                'maxItems' => $maxItems
            );
        }

        // Запускаем актор (синхронизация результатов через кнопку в личном кабинете)
        $apiUrl = "https://api.apify.com/v2/acts/{$actorId}/runs?token={$this->apifyToken}";
        
        $ch = curl_init($apiUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($input));
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode === 201) {
            $data = json_decode($response, true);
            return array(
                'success' => true,
                'run_id' => $data['data']['id']
            );
        } else {
            return array(
                'success' => false,
                'error' => 'Ошибка запуска парсера: ' . $response
            );
        }
    }

    public function checkRunStatus($runId, $userId) {
        $run = $this->db->fetch(
            "SELECT * FROM parsing_runs WHERE id = ? AND user_id = ?",
            array($runId, $userId)
        );

        if (!$run) {
            return array('success' => false, 'error' => 'Запуск не найден');
        }

        if ($run['status'] === 'completed') {
            return array(
                'success' => true,
                'status' => 'completed',
                'items_found' => (int)$run['items_found']
            );
        }

        if (empty($run['apify_run_id'])) {
            return array('success' => true, 'status' => $run['status']);
        }

        $apiUrl = "https://api.apify.com/v2/actor-runs/{$run['apify_run_id']}?token={$this->apifyToken}";
        $response = $this->curlGet($apiUrl);
        $data = json_decode($response, true);

        $status = isset($data['data']['status']) ? $data['data']['status'] : 'UNKNOWN';

        if ($status === 'SUCCEEDED') {
            $items = $this->getApifyResults($run['apify_run_id']);
            $this->saveResults($run, $items);

            return array(
                'success' => true,
                'status' => 'completed',
                'items_found' => count($items)
            );
        } elseif ($status === 'FAILED' || $status === 'ABORTED') {
            $this->db->update('parsing_runs', array('status' => 'failed'), 'id = ?', array($runId));
            return array('success' => true, 'status' => 'failed');
        }

        return array('success' => true, 'status' => 'running');
    }

    private function getApifyResults($apifyRunId) {
        $apiUrl = "https://api.apify.com/v2/actor-runs/{$apifyRunId}/dataset/items?token={$this->apifyToken}";
        $response = $this->curlGet($apiUrl);
        return json_decode($response, true) ?: array();
    }

    private function saveResults($run, $items) {
        $count = 0;
        foreach ($items as $item) {
            $externalId = isset($item['id']) ? $item['id'] : (isset($item['url']) ? md5($item['url']) : md5(json_encode($item)));
            
            $existing = $this->db->fetch(
                "SELECT id FROM listings WHERE user_id = ? AND external_id = ?",
                array($run['user_id'], $externalId)
            );
            if ($existing) continue;

            // Определяем источник
            $source = 'avito';
            if (isset($item['url']) && strpos($item['url'], 'cian.ru') !== false) {
                $source = 'cian';
            }

            $this->db->insert('listings', array(
                'run_id' => $run['id'],
                'task_id' => $run['task_id'],
                'user_id' => $run['user_id'],
                'external_id' => $externalId,
                'source' => $source,
                'title' => isset($item['title']) ? $item['title'] : '',
                'price' => $this->extractPrice($item),
                'address' => isset($item['address']) ? $item['address'] : (isset($item['location']) ? $item['location'] : ''),
                'url' => isset($item['url']) ? $item['url'] : '',
                'image_url' => isset($item['image']) ? $item['image'] : (isset($item['images'][0]) ? $item['images'][0] : ''),
                'rooms' => isset($item['rooms']) ? $item['rooms'] : '',
                'area' => isset($item['area']) ? $item['area'] : '',
                'floor' => isset($item['floor']) ? $item['floor'] : '',
                'phone' => isset($item['phone']) ? $item['phone'] : '',
                'description' => isset($item['description']) ? mb_substr($item['description'], 0, 1000) : ''
            ));
            $count++;
        }

        $this->db->update('parsing_runs', array(
            'status' => 'completed',
            'completed_at' => date('Y-m-d H:i:s'),
            'items_found' => count($items),
            'items_new' => $count
        ), 'id = ?', array($run['id']));

        $this->db->query(
            "UPDATE users SET daily_used = daily_used + ? WHERE id = ?",
            array($count, $run['user_id'])
        );
    }

    private function extractPrice($item) {
        $price = isset($item['price']) ? $item['price'] : (isset($item['priceValue']) ? $item['priceValue'] : 0);
        if (is_string($price)) {
            $price = preg_replace('/[^\d]/', '', $price);
        }
        return (int)$price;
    }

    public function getUserTasks($userId) {
        return $this->db->fetchAll(
            "SELECT t.*, 
                (SELECT COUNT(*) FROM parsing_runs WHERE task_id = t.id) as runs_count,
                (SELECT COUNT(*) FROM listings WHERE task_id = t.id) as listings_count
             FROM parsing_tasks t 
             WHERE t.user_id = ? 
             ORDER BY t.created_at DESC",
            array($userId)
        );
    }

    public function getUserListings($userId, $limit = 50, $offset = 0) {
        return $this->db->fetchAll(
            "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            array($userId, $limit, $offset)
        );
    }

    /**
     * Обработка webhook от Apify - получение и сохранение результатов
     */
    public function processWebhook($runId, $userId) {
        $run = $this->db->fetch(
            "SELECT * FROM parsing_runs WHERE id = ? AND user_id = ?",
            array($runId, $userId)
        );

        if (!$run) {
            return array('success' => false, 'error' => 'Run not found');
        }

        // Если уже обработан - не обрабатываем повторно
        if ($run['status'] === 'completed') {
            return array(
                'success' => true,
                'status' => 'already_completed',
                'items_found' => (int)$run['items_found']
            );
        }

        if (empty($run['apify_run_id'])) {
            return array('success' => false, 'error' => 'No Apify run ID');
        }

        // Проверяем статус в Apify
        $apiUrl = "https://api.apify.com/v2/actor-runs/{$run['apify_run_id']}?token={$this->apifyToken}";
        $response = $this->curlGet($apiUrl);
        $data = json_decode($response, true);

        $status = isset($data['data']['status']) ? $data['data']['status'] : 'UNKNOWN';

        if ($status === 'SUCCEEDED') {
            $items = $this->getApifyResults($run['apify_run_id']);

            if (empty($items)) {
                $this->db->update('parsing_runs', array(
                    'status' => 'completed',
                    'completed_at' => date('Y-m-d H:i:s'),
                    'items_found' => 0,
                    'items_new' => 0
                ), 'id = ?', array($runId));

                return array(
                    'success' => true,
                    'status' => 'completed',
                    'items_found' => 0,
                    'message' => 'No items returned from Apify'
                );
            }

            $this->saveResults($run, $items);

            return array(
                'success' => true,
                'status' => 'completed',
                'items_found' => count($items)
            );
        } elseif ($status === 'RUNNING' || $status === 'READY') {
            return array('success' => true, 'status' => 'running');
        } else {
            $this->db->update('parsing_runs', array('status' => 'failed'), 'id = ?', array($runId));
            return array('success' => true, 'status' => 'failed', 'apify_status' => $status);
        }
    }

    /**
     * Получить все незавершённые запуски пользователя
     */
    public function getPendingRuns($userId) {
        return $this->db->fetchAll(
            "SELECT * FROM parsing_runs WHERE user_id = ? AND status = 'running' ORDER BY started_at DESC",
            array($userId)
        );
    }

    /**
     * Синхронизировать все незавершённые запуски
     */
    public function syncAllPendingRuns($userId) {
        // Получаем ВСЕ запуски со статусом running с apify_run_id
        $runs = $this->db->fetchAll(
            "SELECT * FROM parsing_runs
             WHERE user_id = ? AND apify_run_id IS NOT NULL AND apify_run_id != ''
             AND status = 'running'
             ORDER BY started_at DESC
             LIMIT 20",
            array($userId)
        );

        // Если нет running - попробуем последние 5 запусков (на случай если статус не обновился)
        if (empty($runs)) {
            $runs = $this->db->fetchAll(
                "SELECT * FROM parsing_runs
                 WHERE user_id = ? AND apify_run_id IS NOT NULL AND apify_run_id != ''
                 AND status != 'completed'
                 ORDER BY started_at DESC
                 LIMIT 5",
                array($userId)
            );
        }

        // Всё ещё нет? Берём последние запуски за сегодня
        if (empty($runs)) {
            $runs = $this->db->fetchAll(
                "SELECT * FROM parsing_runs
                 WHERE user_id = ? AND apify_run_id IS NOT NULL AND apify_run_id != ''
                 AND DATE(started_at) = CURDATE()
                 ORDER BY started_at DESC
                 LIMIT 5",
                array($userId)
            );
        }

        $results = array();

        foreach ($runs as $run) {
            // Пропускаем уже завершённые с результатами
            if ($run['status'] === 'completed' && (int)$run['items_found'] > 0) {
                continue;
            }

            $syncResult = $this->processWebhook($run['id'], $userId);
            $results[] = array(
                'run_id' => $run['id'],
                'apify_run_id' => $run['apify_run_id'],
                'db_status' => $run['status'],
                'result' => $syncResult
            );
        }

        return $results;
    }
}
