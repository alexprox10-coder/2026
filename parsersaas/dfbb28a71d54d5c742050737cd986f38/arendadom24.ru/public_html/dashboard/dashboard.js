// ========================================
// Dashboard JavaScript
// ========================================

// Configuration
// ВАЖНО: Настройте токены в личном кабинете или через переменные окружения
const CONFIG = {
    apifyToken: 'YOUR_APIFY_TOKEN', // Настраивается на сервере
    avitoActorId: 'D81KRIfXBnQ4hg8Bz',
    cianActorId: 'CBn1BidHkyYcqYpPd',
    telegramBotToken: 'YOUR_TELEGRAM_BOT_TOKEN', // Настраивается в личном кабинете
    telegramChatId: 'YOUR_TELEGRAM_CHAT_ID' // Настраивается в личном кабинете
};

// City URLs for Avito
const AVITO_CITIES = {
    moscow: 'moskva',
    spb: 'sankt-peterburg',
    kazan: 'kazan',
    novosibirsk: 'novosibirsk',
    ekb: 'ekaterinburg',
    krasnodar: 'krasnodar',
    nizhny: 'nizhniy_novgorod',
    blagoveshchensk: 'amurskaya_oblast_blagoveschensk'
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initSidebar();
    initRangeSlider();
    initParsing();
    loadSampleResults();
});

// Navigation between pages
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            showPage(page);

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

// Show specific page
function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // Update nav
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(nav => {
        nav.classList.toggle('active', nav.dataset.page === pageId);
    });
}

// Sidebar toggle for mobile
function initSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Close sidebar on page click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.menu-toggle')) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// Range slider
function initRangeSlider() {
    const range = document.getElementById('limitRange');
    const valueDisplay = document.getElementById('limitValue');

    if (range && valueDisplay) {
        range.addEventListener('input', () => {
            valueDisplay.textContent = range.value;
        });
    }
}

// Parsing functionality
function initParsing() {
    const startBtn = document.getElementById('startParsingBtn');

    if (startBtn) {
        startBtn.addEventListener('click', startParsing);
    }
}

// Start parsing
async function startParsing() {
    const statusContainer = document.getElementById('parserStatus');
    const statusLog = document.getElementById('statusLog');
    const startBtn = document.getElementById('startParsingBtn');

    // Get parameters
    const sources = Array.from(document.querySelectorAll('input[name="source"]:checked')).map(i => i.value);
    const city = document.getElementById('citySelect').value;
    const category = document.getElementById('categorySelect').value;
    const limit = document.getElementById('limitRange').value;
    const priceFrom = document.getElementById('priceFrom').value;
    const priceTo = document.getElementById('priceTo').value;
    const keywords = document.getElementById('keywords').value;

    if (sources.length === 0) {
        showNotification('Выберите хотя бы один источник', 'error');
        return;
    }

    // Update UI
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Парсинг...';

    statusContainer.innerHTML = `
        <div class="status-running">
            <div class="spinner"></div>
            <span>Парсинг запущен</span>
            <p>Собираем объявления...</p>
        </div>
    `;

    addLog('Запуск парсинга...', 'info');

    let allResults = [];

    try {
        // Parse Avito
        if (sources.includes('avito')) {
            addLog('Запуск парсера Avito...', 'info');
            const avitoResults = await parseAvito(city, category, limit);
            allResults = allResults.concat(avitoResults);
            addLog(`Avito: получено ${avitoResults.length} объявлений`, 'success');
        }

        // Parse CIAN
        if (sources.includes('cian')) {
            addLog('Запуск парсера ЦИАН...', 'info');
            const cianResults = await parseCian(city, limit);
            allResults = allResults.concat(cianResults);
            addLog(`ЦИАН: получено ${cianResults.length} объявлений`, 'success');
        }

        // Filter by price if specified
        if (priceFrom || priceTo) {
            allResults = filterByPrice(allResults, priceFrom, priceTo);
            addLog(`После фильтра по цене: ${allResults.length} объявлений`, 'info');
        }

        // Filter by keywords
        if (keywords) {
            allResults = filterByKeywords(allResults, keywords);
            addLog(`После фильтра по словам: ${allResults.length} объявлений`, 'info');
        }

        // Save results
        saveResults(allResults);
        updateResultsTable(allResults);

        statusContainer.innerHTML = `
            <div class="status-idle" style="color: var(--accent-green);">
                <i class="fas fa-check-circle"></i>
                <span>Парсинг завершён!</span>
                <p>Получено ${allResults.length} объявлений</p>
            </div>
        `;

        addLog(`Парсинг завершён. Всего: ${allResults.length} объявлений`, 'success');
        showNotification(`Парсинг завершён! Получено ${allResults.length} объявлений`, 'success');

    } catch (error) {
        console.error('Parsing error:', error);
        addLog(`Ошибка: ${error.message}`, 'error');
        showNotification('Ошибка при парсинге: ' + error.message, 'error');

        statusContainer.innerHTML = `
            <div class="status-idle" style="color: #ef4444;">
                <i class="fas fa-exclamation-circle"></i>
                <span>Ошибка парсинга</span>
                <p>${error.message}</p>
            </div>
        `;
    }

    // Reset button
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-play"></i> Запустить парсинг';
}

// Parse Avito via Apify
async function parseAvito(city, category, limit) {
    const citySlug = AVITO_CITIES[city] || city;

    // Build Avito URL
    let avitoUrl = `https://www.avito.ru/${citySlug}/kvartiry/`;
    if (category === 'rent') {
        avitoUrl += 'sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg';
    } else if (category === 'sale') {
        avitoUrl += 'prodam';
    }

    const payload = {
        startUrls: [{ url: avitoUrl }],
        limit: parseInt(limit),
        proxyConfiguration: {
            useApifyProxy: true,
            apifyProxyGroups: ['RESIDENTIAL']
        }
    };

    // For demo, return mock data
    // In production, make actual API call:
    /*
    const response = await fetch(
        `https://api.apify.com/v2/acts/${CONFIG.avitoActorId}/runs?token=${CONFIG.apifyToken}&waitForFinish=600`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }
    );
    const data = await response.json();
    // Then fetch results from dataset
    */

    // Demo: simulate API delay and return mock data
    await new Promise(resolve => setTimeout(resolve, 2000));
    return generateMockResults('Avito', parseInt(limit));
}

// Parse CIAN via Apify
async function parseCian(city, limit) {
    const payload = {
        maxItems: parseInt(limit),
        location: getCityName(city),
        operationType: 'rent',
        proxyConfiguration: {
            useApifyProxy: true,
            apifyProxyGroups: ['RESIDENTIAL']
        }
    };

    // Demo: simulate API delay and return mock data
    await new Promise(resolve => setTimeout(resolve, 2000));
    return generateMockResults('ЦИАН', parseInt(limit));
}

// Generate mock results for demo
function generateMockResults(source, count) {
    const results = [];
    const streets = ['ул. Ленина', 'ул. Пушкина', 'пр. Мира', 'ул. Советская', 'ул. Гагарина', 'ул. Строителей', 'пр. Победы'];
    const cities = ['Москва', 'СПб', 'Казань', 'Новосибирск', 'Екатеринбург'];
    const types = ['1-к квартира', '2-к квартира', '3-к квартира', 'Студия'];

    for (let i = 0; i < Math.min(count, 20); i++) {
        const type = types[Math.floor(Math.random() * types.length)];
        const area = 25 + Math.floor(Math.random() * 80);
        const floor = 1 + Math.floor(Math.random() * 20);
        const totalFloors = floor + Math.floor(Math.random() * 5);
        const price = (15000 + Math.floor(Math.random() * 70000));
        const street = streets[Math.floor(Math.random() * streets.length)];
        const houseNum = 1 + Math.floor(Math.random() * 150);
        const city = cities[Math.floor(Math.random() * cities.length)];

        results.push({
            id: `${source.toLowerCase()}-${Date.now()}-${i}`,
            title: `${type}, ${area} м², ${floor}/${totalFloors} эт.`,
            price: price,
            priceText: `${price.toLocaleString()} ₽/мес`,
            address: `${street}, ${houseNum}`,
            city: city,
            area: `${area} м²`,
            source: source,
            url: source === 'Avito'
                ? `https://www.avito.ru/moskva/kvartiry/${Date.now()}`
                : `https://www.cian.ru/rent/flat/${Date.now()}/`,
            date: new Date().toISOString(),
            image: `https://picsum.photos/seed/${i}/200/150`
        });
    }

    return results;
}

// Filter results by price
function filterByPrice(results, from, to) {
    return results.filter(item => {
        const price = item.price || 0;
        if (from && price < parseInt(from)) return false;
        if (to && price > parseInt(to)) return false;
        return true;
    });
}

// Filter results by keywords
function filterByKeywords(results, keywords) {
    const words = keywords.toLowerCase().split(',').map(w => w.trim());
    return results.filter(item => {
        const text = `${item.title} ${item.address}`.toLowerCase();
        return words.some(word => text.includes(word));
    });
}

// Get city name
function getCityName(cityCode) {
    const names = {
        moscow: 'Москва',
        spb: 'Санкт-Петербург',
        kazan: 'Казань',
        novosibirsk: 'Новосибирск',
        ekb: 'Екатеринбург',
        krasnodar: 'Краснодар',
        nizhny: 'Нижний Новгород',
        blagoveshchensk: 'Благовещенск'
    };
    return names[cityCode] || cityCode;
}

// Add log entry
function addLog(text, type = 'info') {
    const log = document.getElementById('statusLog');
    const time = new Date().toLocaleTimeString();

    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-text">${text}</span>
    `;

    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

// Save results to localStorage
function saveResults(results) {
    const existing = JSON.parse(localStorage.getItem('parserResults') || '[]');
    const combined = [...results, ...existing].slice(0, 1000); // Keep last 1000
    localStorage.setItem('parserResults', JSON.stringify(combined));
}

// Load sample results
function loadSampleResults() {
    let results = JSON.parse(localStorage.getItem('parserResults') || '[]');

    if (results.length === 0) {
        // Generate initial sample data
        results = [
            ...generateMockResults('Avito', 10),
            ...generateMockResults('ЦИАН', 10)
        ];
        localStorage.setItem('parserResults', JSON.stringify(results));
    }

    updateResultsTable(results);
}

// Update results table
function updateResultsTable(results) {
    const tbody = document.getElementById('resultsTableBody');
    if (!tbody) return;

    tbody.innerHTML = results.slice(0, 20).map((item, index) => `
        <tr>
            <td><input type="checkbox" data-id="${item.id}"></td>
            <td><div class="table-img" style="background: linear-gradient(135deg, hsl(${index * 30}, 70%, 60%) 0%, hsl(${index * 30 + 40}, 70%, 50%) 100%);"></div></td>
            <td>${item.title}</td>
            <td class="price">${item.priceText || item.price?.toLocaleString() + ' ₽'}</td>
            <td>${item.city}</td>
            <td><span class="source-badge ${item.source.toLowerCase()}">${item.source}</span></td>
            <td>${formatDate(item.date)}</td>
            <td>
                <div class="action-btns">
                    <button onclick="window.open('${item.url}', '_blank')" title="Открыть"><i class="fas fa-external-link-alt"></i></button>
                    <button onclick="sendToTelegram('${item.id}')" title="В Telegram"><i class="fab fa-telegram"></i></button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Только что';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} мин назад`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} ч назад`;
    if (diff < 172800000) return 'Вчера';

    return date.toLocaleDateString('ru-RU');
}

// Export functions
function exportData(format) {
    const results = JSON.parse(localStorage.getItem('parserResults') || '[]');

    if (results.length === 0) {
        showNotification('Нет данных для экспорта', 'error');
        return;
    }

    if (format === 'excel' || format === 'csv') {
        exportToCSV(results, format);
    } else if (format === 'json') {
        exportToJSON(results);
    }
}

// Export to CSV/Excel
function exportToCSV(results, format) {
    const headers = ['Заголовок', 'Цена', 'Адрес', 'Город', 'Источник', 'Дата', 'Ссылка'];
    const rows = results.map(item => [
        item.title,
        item.price,
        item.address,
        item.city,
        item.source,
        formatDate(item.date),
        item.url
    ]);

    let csvContent = '\uFEFF'; // BOM for Excel
    csvContent += headers.join(';') + '\n';
    csvContent += rows.map(row => row.map(cell => `"${cell}"`).join(';')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `parser_export_${Date.now()}.${format === 'excel' ? 'csv' : format}`;
    link.click();

    showNotification('Файл скачан!', 'success');
}

// Export to JSON
function exportToJSON(results) {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `parser_export_${Date.now()}.json`;
    link.click();

    showNotification('JSON файл скачан!', 'success');
}

// Send to Telegram
async function sendToTelegram(itemId) {
    const results = JSON.parse(localStorage.getItem('parserResults') || '[]');
    const item = results.find(r => r.id === itemId);

    if (!item) {
        showNotification('Объявление не найдено', 'error');
        return;
    }

    const text = `🏠 Новое предложение!\n\n📍 ${item.address}\n💰 ${item.priceText || item.price}\n🔗 Открыть объявление\n\nИсточник: ${item.source}\n\n${item.url}`;

    try {
        // For demo, just show notification
        // In production, make actual API call:
        /*
        const response = await fetch(
            `https://api.telegram.org/bot${CONFIG.telegramBotToken}/sendMessage`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: CONFIG.telegramChatId,
                    text: text,
                    link_preview_options: {
                        is_disabled: false,
                        prefer_large_media: true
                    }
                })
            }
        );
        */

        showNotification('Отправлено в Telegram!', 'success');
    } catch (error) {
        showNotification('Ошибка отправки в Telegram', 'error');
    }
}

// Connect Google Sheets
function connectGoogleSheets() {
    showNotification('Для подключения Google Sheets перейдите в настройки интеграций', 'info');
    showPage('integrations');
}

// Configure Email
function configureEmail() {
    const modal = document.getElementById('emailModal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Close modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Save email settings
function saveEmailSettings() {
    const email = document.getElementById('notificationEmail').value;
    const frequency = document.getElementById('emailFrequency').value;

    if (!email) {
        showNotification('Введите email', 'error');
        return;
    }

    localStorage.setItem('emailSettings', JSON.stringify({ email, frequency }));
    closeModal('emailModal');
    showNotification('Настройки email сохранены!', 'success');

    // Update integration status
    const emailStatus = document.querySelector('.integration-card:has(.fa-envelope) .integration-status');
    if (emailStatus) {
        emailStatus.innerHTML = '<i class="fas fa-check-circle"></i> Подключено';
        emailStatus.classList.add('connected');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        padding: 16px 24px;
        background: ${type === 'success' ? 'var(--accent-green)' : type === 'error' ? '#ef4444' : 'var(--accent-indigo)'};
        color: white;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(100px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100px); }
    }
`;
document.head.appendChild(style);

// Expose functions globally
window.showPage = showPage;
window.exportData = exportData;
window.sendToTelegram = sendToTelegram;
window.connectGoogleSheets = connectGoogleSheets;
window.configureEmail = configureEmail;
window.closeModal = closeModal;
window.saveEmailSettings = saveEmailSettings;


Copy


Search


Translate


Setting
Search for similar products on 1688


❯



