/**
 * Parser SaaS - API Client
 * Подключить к dashboard страницам
 */

const API = {
    baseUrl: '/api',

    // Получить токен из cookie или localStorage
    getToken() {
        // Из cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'auth_token') return value;
        }
        // Из localStorage
        return localStorage.getItem('auth_token');
    },

    // Сохранить токен
    setToken(token) {
        localStorage.setItem('auth_token', token);
        document.cookie = `auth_token=${token}; path=/; max-age=${30 * 24 * 60 * 60}; secure; samesite=strict`;
    },

    // Удалить токен
    removeToken() {
        localStorage.removeItem('auth_token');
        document.cookie = 'auth_token=; path=/; max-age=0';
    },

    // Базовый запрос
    async request(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        const token = this.getToken();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Если 401 - редирект на логин
            if (response.status === 401) {
                this.removeToken();
                window.location.href = '/dashboard/login.html';
                return { success: false, error: 'Требуется авторизация' };
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: 'Ошибка сети' };
        }
    },

    // GET запрос
    get(endpoint, params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return this.request(url, { method: 'GET' });
    },

    // POST запрос
    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT запрос
    put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE запрос
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // ==================== AUTH ====================

    // Регистрация
    async register(email, password, firstName = '', lastName = '') {
        const result = await this.post('/auth/register', {
            email,
            password,
            first_name: firstName,
            last_name: lastName
        });

        if (result.success && result.token) {
            this.setToken(result.token);
        }

        return result;
    },

    // Вход
    async login(email, password) {
        const result = await this.post('/auth/login', { email, password });

        if (result.success && result.token) {
            this.setToken(result.token);
        }

        return result;
    },

    // Выход
    async logout() {
        await this.post('/auth/logout');
        this.removeToken();
        window.location.href = '/dashboard/login.html';
    },

    // Проверка авторизации
    isLoggedIn() {
        return !!this.getToken();
    },

    // ==================== USER ====================

    // Получить текущего пользователя
    getUser() {
        return this.get('/user/me');
    },

    // Обновить настройки
    updateSettings(settings) {
        return this.put('/user/settings', settings);
    },

    // Статистика
    getStats() {
        return this.get('/user/stats');
    },

    // ==================== TASKS ====================

    // Получить задачи
    getTasks() {
        return this.get('/tasks');
    },

    // Создать задачу
    createTask(taskData) {
        return this.post('/tasks', taskData);
    },

    // Запустить парсинг
    runTask(taskId) {
        return this.post(`/tasks/${taskId}/run`);
    },

    // Проверить статус
    checkRunStatus(runId) {
        return this.get(`/runs/${runId}/status`);
    },

    // ==================== LISTINGS ====================

    // Получить объявления
    getListings(limit = 50, offset = 0) {
        return this.get('/listings', { limit, offset });
    },

    // Экспорт в Excel
    exportExcel() {
        const token = this.getToken();
        window.open(`${this.baseUrl}/listings/export/excel?token=${token}`, '_blank');
    },

    // ==================== TELEGRAM ====================

    // Проверить токен бота
    verifyTelegramBot(botToken) {
        return this.post('/telegram/verify', { bot_token: botToken });
    },

    // Отправить тестовое сообщение
    sendTelegramTest(botToken, chatId) {
        return this.post('/telegram/test', { bot_token: botToken, chat_id: chatId });
    },

    // ==================== OTHER ====================

    // Получить города
    getCities() {
        return this.get('/cities');
    },

    // Получить тарифы
    getPlans() {
        return this.get('/plans');
    }
};

// Проверка авторизации при загрузке dashboard страниц
document.addEventListener('DOMContentLoaded', function() {
    // Если это dashboard страница (не login/register) - проверяем авторизацию
    const path = window.location.pathname;

    if (path.includes('/dashboard/') && !path.includes('login') && !path.includes('register')) {
        if (!API.isLoggedIn()) {
            window.location.href = '/dashboard/login.html';
        }
    }
});

// Экспортируем для использования
window.API = API;
