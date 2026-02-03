# Parser SaaS - Инструкция по установке на Beget

## Структура файлов

После загрузки на сервер структура должна быть:

```
public_html/
├── api/
│   ├── .htaccess
│   └── index.php
├── classes/
│   ├── Database.php
│   ├── User.php
│   ├── Parser.php
│   └── Telegram.php
├── css/
│   └── styles.css
├── js/
│   ├── main.js
│   └── api.js
├── dashboard/
│   ├── index.html (главная дашборда)
│   ├── login.html
│   ├── register.html
│   └── ... другие страницы
├── config.php
└── index.html (лендинг)
```

## Шаги установки

### 1. Создайте базу данных MySQL

- Зайдите в панель Beget → MySQL
- База уже создана: `alexprz7_2026`

### 2. Выполните SQL скрипт

- Откройте phpMyAdmin: https://cp.beget.com/mysql → иконка "phpMyAdmin"
- Выберите базу `alexprz7_2026`
- Вкладка "SQL"
- Вставьте содержимое файла `database.sql`
- Нажмите "Выполнить"

### 3. Загрузите файлы на сервер

Через FTP или файловый менеджер Beget:

1. Загрузите папку `api/` в `public_html/api/`
2. Загрузите папку `classes/` в `public_html/classes/`
3. Загрузите `config.php` в `public_html/config.php`
4. Загрузите `js/api.js` в `public_html/js/api.js`

### 4. Настройте config.php

Откройте `public_html/config.php` и проверьте:

```php
// База данных (уже настроено)
define('DB_HOST', 'localhost');
define('DB_NAME', 'alexprz7_2026');
define('DB_USER', 'alexprz7_2026');
define('DB_PASS', 'Vitaha2026');

// Google OAuth (добавьте после создания)
define('GOOGLE_CLIENT_ID', 'ваш_client_id');
define('GOOGLE_CLIENT_SECRET', 'ваш_client_secret');

// Измените JWT секрет на случайную строку!
define('JWT_SECRET', 'случайная_строка_минимум_32_символа');
```

### 5. Подключите api.js к dashboard

В каждой странице dashboard добавьте перед `</body>`:

```html
<script src="/js/api.js"></script>
```

### 6. Обновите формы входа/регистрации

В `login.html` добавьте обработчик:

```html
<script>
document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;

    const result = await API.login(email, password);

    if (result.success) {
        window.location.href = '/dashboard/';
    } else {
        alert(result.error || 'Ошибка входа');
    }
});
</script>
```

В `register.html`:

```html
<script>
document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const firstName = document.querySelector('input[name="first_name"]').value;
    const lastName = document.querySelector('input[name="last_name"]').value;
    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;

    const result = await API.register(email, password, firstName, lastName);

    if (result.success) {
        window.location.href = '/dashboard/';
    } else {
        alert(result.error || 'Ошибка регистрации');
    }
});
</script>
```

### 7. Настройте Google OAuth

1. Создайте OAuth Client ID в Google Cloud Console
2. Добавьте Redirect URI: `https://arendadom24.ru/api/auth/google/callback`
3. Добавьте Client ID и Secret в `config.php`

Кнопка входа через Google:
```html
<a href="/api/auth/google" class="btn">
    <i class="fab fa-google"></i> Войти через Google
</a>
```

### 8. Настройте Telegram Login

1. Напишите @BotFather команду `/setdomain`
2. Укажите домен: `arendadom24.ru`

Виджет Telegram Login:
```html
<script async src="https://telegram.org/js/telegram-widget.js?22"
    data-telegram-login="ParsersaasBot"
    data-size="large"
    data-auth-url="https://arendadom24.ru/api/auth/telegram/callback"
    data-request-access="write">
</script>
```

## Проверка работы

1. Откройте `https://arendadom24.ru/api/plans` - должен вернуть JSON с тарифами
2. Откройте `https://arendadom24.ru/api/cities` - должен вернуть список городов
3. Попробуйте зарегистрироваться на сайте

## Частые проблемы

### Ошибка 500
- Проверьте права на файлы (644 для файлов, 755 для папок)
- Проверьте логи в панели Beget

### Ошибка подключения к БД
- Проверьте данные в config.php
- Убедитесь что база создана

### CORS ошибки
- Проверьте что .htaccess загружен в папку api/

## Контакты

Если нужна помощь - пишите!
