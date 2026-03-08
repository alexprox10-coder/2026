const TelegramBot = require('node-telegram-bot-api');
const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const path = require('path');

// === НАСТРОЙКИ ===
const TOKEN = process.env.TELEGRAM_BOT_TOKEN || '8678730458:AAFR9QXWQr9HrCL_tCwj4IoRuWYPNqo3Ny8';
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || '';
const ALLOWED_USERS = [7984101063];

// Файл блокировки для предотвращения множественных запусков
const LOCK_FILE = '/tmp/claude-telegram-bot.lock';

// === ЗАЩИТА ОТ МНОЖЕСТВЕННЫХ ЗАПУСКОВ ===
function checkSingleInstance() {
  if (fs.existsSync(LOCK_FILE)) {
    try {
      const pid = parseInt(fs.readFileSync(LOCK_FILE, 'utf8').trim());
      // Проверяем, жив ли процесс
      process.kill(pid, 0);
      console.error(`Бот уже запущен (PID: ${pid}). Завершение.`);
      process.exit(1);
    } catch (e) {
      // Процесс не существует, удаляем старый lock файл
      fs.unlinkSync(LOCK_FILE);
    }
  }

  // Создаем lock файл с текущим PID
  fs.writeFileSync(LOCK_FILE, process.pid.toString());

  // Удаляем lock файл при завершении
  process.on('exit', () => {
    try { fs.unlinkSync(LOCK_FILE); } catch (e) {}
  });
  process.on('SIGINT', () => {
    try { fs.unlinkSync(LOCK_FILE); } catch (e) {}
    process.exit(0);
  });
  process.on('SIGTERM', () => {
    try { fs.unlinkSync(LOCK_FILE); } catch (e) {}
    process.exit(0);
  });
}

checkSingleInstance();

// === ИНИЦИАЛИЗАЦИЯ ANTHROPIC ===
const anthropic = new Anthropic({
  apiKey: ANTHROPIC_API_KEY,
});

// === ИНИЦИАЛИЗАЦИЯ TELEGRAM BOT ===
const bot = new TelegramBot(TOKEN, {
  polling: {
    interval: 300,
    autoStart: true,
    params: {
      timeout: 10
    }
  }
});

console.log('Claude Telegram Bot запущен (PID: ' + process.pid + ')');

// Хранилище истории диалогов (по userId)
const conversationHistory = new Map();
const MAX_HISTORY = 20; // Максимум сообщений в истории

// === КОМАНДА /start ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  bot.sendMessage(chatId,
    'Привет! Это бот для общения с Claude AI.\n\n' +
    `Ваш ID: ${userId}\n\n` +
    'Просто отправьте сообщение, и Claude ответит.\n\n' +
    'Команды:\n' +
    '/status - статус сервера\n' +
    '/clear - очистить историю диалога\n' +
    '/help - помощь'
  );
});

// === КОМАНДА /clear ===
bot.onText(/\/clear/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (!ALLOWED_USERS.includes(userId)) {
    return bot.sendMessage(chatId, `Доступ запрещен. Ваш ID: ${userId}`);
  }

  conversationHistory.delete(userId);
  bot.sendMessage(chatId, 'История диалога очищена.');
});

// === КОМАНДА /status ===
bot.onText(/\/status/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (!ALLOWED_USERS.includes(userId)) {
    return bot.sendMessage(chatId, `Доступ запрещен. Ваш ID: ${userId}`);
  }

  const uptime = process.uptime();
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = Math.floor(uptime % 60);

  const historySize = conversationHistory.get(userId)?.length || 0;

  bot.sendMessage(chatId,
    `Статус бота:\n` +
    `- PID: ${process.pid}\n` +
    `- Uptime: ${hours}ч ${minutes}м ${seconds}с\n` +
    `- Память: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB\n` +
    `- Сообщений в истории: ${historySize}\n` +
    `- API: Anthropic (Claude)`
  );
});

// === КОМАНДА /help ===
bot.onText(/\/help/, (msg) => {
  const chatId = msg.chat.id;

  bot.sendMessage(chatId,
    'Справка по боту:\n\n' +
    'Просто напишите сообщение, и Claude ответит.\n' +
    'Бот помнит контекст диалога (последние 20 сообщений).\n\n' +
    'Команды:\n' +
    '/start - начало работы\n' +
    '/status - статус сервера\n' +
    '/clear - очистить историю диалога\n' +
    '/help - эта справка'
  );
});

// === ОБРАБОТКА СООБЩЕНИЙ ===
bot.on('message', async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const text = msg.text;

  // Пропускаем команды
  if (!text || text.startsWith('/')) return;

  // Проверка доступа
  if (!ALLOWED_USERS.includes(userId)) {
    return bot.sendMessage(chatId, `Доступ запрещен.\nВаш ID: ${userId}\nДобавьте его в ALLOWED_USERS`);
  }

  // Отправляем статус "печатает"
  bot.sendChatAction(chatId, 'typing');

  const statusMsg = await bot.sendMessage(chatId, 'Claude думает...');

  try {
    // Получаем или создаем историю диалога
    if (!conversationHistory.has(userId)) {
      conversationHistory.set(userId, []);
    }
    const history = conversationHistory.get(userId);

    // Добавляем сообщение пользователя в историю
    history.push({
      role: 'user',
      content: text
    });

    // Ограничиваем историю
    while (history.length > MAX_HISTORY) {
      history.shift();
    }

    // Вызов Anthropic API
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      messages: history,
      system: 'Ты полезный ассистент. Отвечай на русском языке, если пользователь пишет на русском. Будь кратким и информативным.'
    });

    // Извлекаем ответ
    const assistantMessage = response.content[0].text;

    // Добавляем ответ в историю
    history.push({
      role: 'assistant',
      content: assistantMessage
    });

    // Удаляем статусное сообщение
    try {
      await bot.deleteMessage(chatId, statusMsg.message_id);
    } catch (e) {}

    // Telegram лимит 4096 символов - разбиваем на части
    const chunks = splitMessage(assistantMessage, 4000);

    for (const chunk of chunks) {
      await bot.sendMessage(chatId, chunk, { parse_mode: 'Markdown' }).catch(() => {
        // Если Markdown не парсится, отправляем как обычный текст
        bot.sendMessage(chatId, chunk);
      });
      await sleep(100);
    }

  } catch (error) {
    console.error('API Error:', error);

    // Удаляем статусное сообщение
    try {
      await bot.deleteMessage(chatId, statusMsg.message_id);
    } catch (e) {}

    let errorMsg = 'Произошла ошибка';

    if (error.status === 401) {
      errorMsg = 'Ошибка авторизации. Проверьте ANTHROPIC_API_KEY.';
    } else if (error.status === 429) {
      errorMsg = 'Слишком много запросов. Подождите немного.';
    } else if (error.status === 500) {
      errorMsg = 'Ошибка сервера Anthropic. Попробуйте позже.';
    } else if (error.message) {
      errorMsg = `Ошибка: ${error.message.slice(0, 200)}`;
    }

    bot.sendMessage(chatId, `${errorMsg}`);
  }
});

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

// Разбивка длинных сообщений
function splitMessage(text, maxLength) {
  const chunks = [];
  let current = '';

  const lines = text.split('\n');
  for (const line of lines) {
    if (current.length + line.length + 1 > maxLength) {
      if (current) chunks.push(current);
      current = line;
    } else {
      current += (current ? '\n' : '') + line;
    }
  }
  if (current) chunks.push(current);

  return chunks;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// === ОБРАБОТКА ОШИБОК ===
bot.on('polling_error', (error) => {
  if (error.code === 'ETELEGRAM' && error.message.includes('409 Conflict')) {
    console.error('CRITICAL: Другой экземпляр бота уже запущен! Завершение...');
    process.exit(1);
  }
  console.error('Polling error:', error.message);
});

bot.on('error', (error) => {
  console.error('Bot error:', error.message);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
});

console.log('Бот готов к работе!');
