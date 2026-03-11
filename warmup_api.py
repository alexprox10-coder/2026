#!/usr/bin/env python3
"""
🔥 API для запуска прогрева лидов

Запускается как сервис, принимает webhook от n8n

Запуск:
python warmup_api.py

Эндпоинты:
- POST /warmup - запустить прогрев
- GET /status - статус последнего прогрева
- GET /health - проверка работоспособности
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uvicorn

load_dotenv()

# Импортируем основной скрипт
from warmup_sender import WarmupSender, CONFIG

app = FastAPI(title="Warmup API", version="1.0")

# Глобальное состояние
state = {
    "is_running": False,
    "last_run": None,
    "last_stats": None,
    "error": None
}


class WarmupRequest(BaseModel):
    limit: int = 10  # Сколько лидов обработать


class WarmupResponse(BaseModel):
    status: str
    message: str
    stats: dict = None


async def run_warmup(limit: int):
    """Фоновый запуск прогрева"""
    global state

    state["is_running"] = True
    state["error"] = None

    try:
        # Переопределяем лимит
        config = CONFIG.copy()
        config["daily_limit"] = limit

        sender = WarmupSender(config)

        if not sender.connect_sheets():
            raise Exception("Не удалось подключиться к Google Sheets")

        await sender.start()
        await sender.process_leads()
        await sender.notify_admin()
        await sender.stop()

        state["last_stats"] = sender.stats
        state["last_run"] = datetime.now().isoformat()

    except Exception as e:
        state["error"] = str(e)
        raise
    finally:
        state["is_running"] = False


@app.get("/health")
async def health():
    """Проверка работоспособности"""
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get("/status")
async def status():
    """Статус последнего прогрева"""
    return {
        "is_running": state["is_running"],
        "last_run": state["last_run"],
        "last_stats": state["last_stats"],
        "error": state["error"]
    }


@app.post("/warmup", response_model=WarmupResponse)
async def warmup(request: WarmupRequest, background_tasks: BackgroundTasks):
    """Запуск прогрева лидов"""

    if state["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Прогрев уже запущен"
        )

    # Запускаем в фоне
    background_tasks.add_task(run_warmup, request.limit)

    return WarmupResponse(
        status="started",
        message=f"Прогрев запущен, лимит: {request.limit} лидов"
    )


@app.post("/warmup/sync")
async def warmup_sync(request: WarmupRequest):
    """Синхронный запуск прогрева (ждёт завершения)"""

    if state["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Прогрев уже запущен"
        )

    await run_warmup(request.limit)

    return {
        "status": "completed",
        "stats": state["last_stats"]
    }


if __name__ == "__main__":
    port = int(os.getenv("WARMUP_API_PORT", "8001"))
    print(f"\n🚀 Warmup API запущен на http://0.0.0.0:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
