const TelegramBot = require('node-telegram-bot-api');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// === НАСТРОЙКИ ===
const TOKEN = process.env.TELEGRAM_BOT_TOKEN || '8678730458:AAFR9QXWQr9HrCL_tCwj4IoRuWYPNqo3Ny8';
const ALLOWED_USERS = [7984101063];
const CLAUDE_PATH = '/usr/bin/claude';
const TIMEOUT_MS = 120000; // 2 минуты (Claude CLI обычно отвечает быстро)

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

  bot.sendMessage(chatId, 'Claude CLI не хранит историю. Каждый запрос независим.');
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

  bot.sendMessage(chatId,
    `Статус бота:\n` +
    `- PID: ${process.pid}\n` +
    `- Uptime: ${hours}ч ${minutes}м ${seconds}с\n` +
    `- Память: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB\n` +
    `- Режим: Claude CLI\n` +
    `- Таймаут: ${TIMEOUT_MS / 1000} сек`
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
    // Вызов Claude CLI через spawn
    const response = await callClaudeCLI(text);

    // Удаляем статусное сообщение
    try {
      await bot.deleteMessage(chatId, statusMsg.message_id);
    } catch (e) {}

    // Telegram лимит 4096 символов - разбиваем на части
    const chunks = splitMessage(response, 4000);

    for (const chunk of chunks) {
      await bot.sendMessage(chatId, chunk, { parse_mode: 'Markdown' }).catch(() => {
        // Если Markdown не парсится, отправляем как обычный текст
        bot.sendMessage(chatId, chunk);
      });
      await sleep(100);
    }

  } catch (error) {
    console.error('CLI Error:', error);

    // Удаляем статусное сообщение
    try {
      await bot.deleteMessage(chatId, statusMsg.message_id);
    } catch (e) {}

    bot.sendMessage(chatId, `Ошибка: ${error.message || error}`);
  }
});

// === ВЫЗОВ CLAUDE CLI ===
function callClaudeCLI(prompt) {
  return new Promise((resolve, reject) => {
    let stdout = '';
    let stderr = '';

    // Экранируем кавычки для безопасности
    const safePrompt = prompt.replace(/"/g, '\\"').replace(/'/g, "\\'").replace(/\$/g, '\\$');

    const claude = spawn(CLAUDE_PATH, ['-p', prompt, '--output-format', 'text'], {
      env: {
        ...process.env,
        HOME: '/root',
        PATH: '/root/.local/bin:/root/.cargo/bin:/usr/local/go/bin:/opt/node22/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      timeout: TIMEOUT_MS
    });

    const timeoutId = setTimeout(() => {
      claude.kill('SIGKILL');
      reject(new Error('Таймаут (2 минуты). Попробуйте более короткий запрос.'));
    }, TIMEOUT_MS);

    claude.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    claude.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    claude.on('close', (code) => {
      clearTimeout(timeoutId);

      if (code === 0) {
        resolve(stdout.trim() || 'Пустой ответ');
      } else {
        reject(new Error(stderr || `Код ошибки: ${code}`));
      }
    });

    claude.on('error', (err) => {
      clearTimeout(timeoutId);
      reject(err);
    });
  });
}

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
