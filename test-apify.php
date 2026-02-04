<?php
/**
 * Test Apify actors for CIAN and Avito
 * URL: arendadom24.ru/test-apify.php
 */

require_once __DIR__ . '/backend/config.php';

header('Content-Type: text/html; charset=UTF-8');

// Default test parameters
$testCian = [
    'maxItems' => 10,
    'location' => 'Москва',
    'operationType' => 'rent',
    'category' => '',
    'shortTermRent' => false,
    'includeStudio' => false,
    'withNeighbors' => false,
    'proxyConfiguration' => [
        'useApifyProxy' => true,
        'apifyProxyGroups' => ['RESIDENTIAL']
    ]
];

$testAvito = [
    'startUrls' => [
        ['url' => 'https://www.avito.ru/amurskaya_oblast_blagoveschensk/kvartiry/sdam']
    ],
    'limit' => 20
];

/**
 * Call Apify API
 */
function callApify($actorId, $input, $token, $sync = false) {
    $endpoint = $sync ? 'run-sync-get-dataset-items' : 'runs';
    $url = "https://api.apify.com/v2/acts/{$actorId}/{$endpoint}?token={$token}";

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($input));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, $sync ? 300 : 30);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);

    return [
        'http_code' => $httpCode,
        'response' => $response,
        'error' => $error,
        'data' => json_decode($response, true)
    ];
}

/**
 * Get run status
 */
function getRunStatus($runId, $token) {
    $url = "https://api.apify.com/v2/actor-runs/{$runId}?token={$token}";
    $response = @file_get_contents($url);
    return json_decode($response, true);
}

/**
 * Get dataset items
 */
function getDatasetItems($runId, $token) {
    $url = "https://api.apify.com/v2/actor-runs/{$runId}/dataset/items?token={$token}";
    $response = @file_get_contents($url);
    return json_decode($response, true) ?: [];
}

// Process form submission
$result = null;
$actor = $_POST['actor'] ?? $_GET['actor'] ?? null;
$action = $_POST['action'] ?? $_GET['action'] ?? null;
$runId = $_GET['run_id'] ?? null;

if ($action === 'start' && $actor) {
    $actorId = $actor === 'cian' ? APIFY_CIAN_ACTOR : APIFY_AVITO_ACTOR;
    $input = $actor === 'cian' ? $testCian : $testAvito;

    // Override with custom params if provided
    if ($actor === 'cian' && !empty($_POST['location'])) {
        $input['location'] = $_POST['location'];
    }
    if ($actor === 'cian' && !empty($_POST['operationType'])) {
        $input['operationType'] = $_POST['operationType'];
    }
    if ($actor === 'avito' && !empty($_POST['url'])) {
        $input['startUrls'] = [['url' => $_POST['url']]];
    }
    if (!empty($_POST['limit'])) {
        if ($actor === 'cian') {
            $input['maxItems'] = (int)$_POST['limit'];
        } else {
            $input['limit'] = (int)$_POST['limit'];
        }
    }

    $result = callApify($actorId, $input, APIFY_TOKEN);
    $result['actor'] = $actor;
    $result['input'] = $input;
}

if ($action === 'status' && $runId) {
    $result = getRunStatus($runId, APIFY_TOKEN);
}

if ($action === 'results' && $runId) {
    $result = getDatasetItems($runId, APIFY_TOKEN);
}
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Apify - CIAN & Avito</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h2 {
            margin-top: 0;
            color: #667;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        label { display: block; margin: 10px 0 5px; font-weight: 500; }
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }
        button:hover { background: #0056b3; }
        button.cian { background: #ff6600; }
        button.cian:hover { background: #cc5200; }
        button.avito { background: #00a859; }
        button.avito:hover { background: #008547; }
        .result {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
        }
        .result pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 12px;
        }
        .status { padding: 5px 10px; border-radius: 4px; font-weight: 500; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.pending { background: #fff3cd; color: #856404; }
        .config-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .config-info code {
            background: #d0e8ff;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .item-card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            background: white;
        }
        .item-card img {
            max-width: 150px;
            max-height: 100px;
            border-radius: 4px;
        }
        .item-title { font-weight: bold; color: #333; }
        .item-price { color: #28a745; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🔍 Test Apify Actors</h1>

    <div class="config-info">
        <strong>Configuration:</strong><br>
        CIAN Actor: <code><?= APIFY_CIAN_ACTOR ?></code><br>
        Avito Actor: <code><?= APIFY_AVITO_ACTOR ?></code><br>
        Token: <code><?= substr(APIFY_TOKEN, 0, 10) ?>...</code>
        <?php if (APIFY_TOKEN === 'YOUR_APIFY_TOKEN'): ?>
            <br><span style="color: red;">⚠️ WARNING: APIFY_TOKEN not configured!</span>
        <?php endif; ?>
    </div>

    <div class="grid">
        <!-- CIAN Form -->
        <div class="card">
            <h2>🏢 CIAN Scraper</h2>
            <form method="POST">
                <input type="hidden" name="actor" value="cian">
                <input type="hidden" name="action" value="start">

                <label>Город:</label>
                <input type="text" name="location" value="Москва" placeholder="Москва">

                <label>Тип операции:</label>
                <select name="operationType">
                    <option value="rent">Аренда (rent)</option>
                    <option value="sale">Продажа (sale)</option>
                </select>

                <label>Лимит объявлений:</label>
                <input type="number" name="limit" value="10" min="1" max="100">

                <button type="submit" class="cian">🚀 Запустить CIAN</button>
            </form>

            <div style="margin-top: 15px; font-size: 12px; color: #666;">
                <strong>Input JSON:</strong>
                <pre><?= json_encode($testCian, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?></pre>
            </div>
        </div>

        <!-- Avito Form -->
        <div class="card">
            <h2>🛒 Avito Scraper</h2>
            <form method="POST">
                <input type="hidden" name="actor" value="avito">
                <input type="hidden" name="action" value="start">

                <label>URL страницы:</label>
                <input type="text" name="url" value="https://www.avito.ru/amurskaya_oblast_blagoveschensk/kvartiry/sdam" placeholder="https://www.avito.ru/...">

                <label>Лимит объявлений:</label>
                <input type="number" name="limit" value="20" min="1" max="3000">

                <button type="submit" class="avito">🚀 Запустить Avito</button>
            </form>

            <div style="margin-top: 15px; font-size: 12px; color: #666;">
                <strong>Input JSON:</strong>
                <pre><?= json_encode($testAvito, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?></pre>
            </div>
        </div>
    </div>

    <?php if ($result): ?>
    <div class="card">
        <h2>📊 Result</h2>

        <?php if (isset($result['http_code'])): ?>
            <p>
                <strong>HTTP Code:</strong>
                <span class="status <?= $result['http_code'] === 201 ? 'success' : 'error' ?>">
                    <?= $result['http_code'] ?>
                </span>
            </p>

            <?php if ($result['error']): ?>
                <p><strong>cURL Error:</strong> <?= htmlspecialchars($result['error']) ?></p>
            <?php endif; ?>

            <?php if (isset($result['data']['data']['id'])): ?>
                <p>
                    <strong>Run ID:</strong>
                    <code><?= $result['data']['data']['id'] ?></code>
                </p>
                <p>
                    <strong>Status:</strong>
                    <span class="status pending"><?= $result['data']['data']['status'] ?? 'STARTED' ?></span>
                </p>
                <p>
                    <a href="?action=status&run_id=<?= $result['data']['data']['id'] ?>">Check Status</a> |
                    <a href="?action=results&run_id=<?= $result['data']['data']['id'] ?>">Get Results</a>
                </p>
            <?php endif; ?>

            <p><strong>Actor:</strong> <?= strtoupper($result['actor'] ?? 'unknown') ?></p>
            <p><strong>Input sent:</strong></p>
            <div class="result">
                <pre><?= json_encode($result['input'] ?? [], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?></pre>
            </div>
        <?php endif; ?>

        <p><strong>Full Response:</strong></p>
        <div class="result">
            <pre><?= json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?></pre>
        </div>
    </div>
    <?php endif; ?>

    <?php if ($action === 'results' && is_array($result) && count($result) > 0): ?>
    <div class="card">
        <h2>📋 Dataset Items (<?= count($result) ?>)</h2>
        <?php foreach (array_slice($result, 0, 20) as $item): ?>
            <div class="item-card">
                <?php if (!empty($item['image']) || !empty($item['photos'][0])): ?>
                    <img src="<?= htmlspecialchars($item['image'] ?? $item['photos'][0] ?? '') ?>" alt="">
                <?php endif; ?>
                <div class="item-title"><?= htmlspecialchars($item['title'] ?? 'No title') ?></div>
                <div class="item-price">
                    <?php
                    $price = $item['price'] ?? $item['priceValue'] ?? 0;
                    echo number_format((float)preg_replace('/[^\d]/', '', $price), 0, '', ' ') . ' ₽';
                    ?>
                </div>
                <div style="font-size: 12px; color: #666;">
                    <?= htmlspecialchars($item['address'] ?? $item['location'] ?? '') ?>
                </div>
                <?php if (!empty($item['url'])): ?>
                    <a href="<?= htmlspecialchars($item['url']) ?>" target="_blank" style="font-size: 12px;">Open →</a>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <div class="card">
        <h2>📖 API Documentation</h2>
        <p><strong>CIAN Actor:</strong>
            <a href="https://console.apify.com/actors/<?= APIFY_CIAN_ACTOR ?>/input" target="_blank">
                console.apify.com/actors/<?= APIFY_CIAN_ACTOR ?>
            </a>
        </p>
        <p><strong>Avito Actor:</strong>
            <a href="https://console.apify.com/actors/<?= APIFY_AVITO_ACTOR ?>/source" target="_blank">
                console.apify.com/actors/<?= APIFY_AVITO_ACTOR ?>
            </a>
        </p>
        <p><strong>Apify API Docs:</strong>
            <a href="https://docs.apify.com/api/v2" target="_blank">docs.apify.com/api/v2</a>
        </p>
    </div>
</body>
</html>
