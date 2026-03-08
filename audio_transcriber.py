"""
Сервис транскрипции аудио в текст
Использует OpenAI Whisper
"""

import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import whisper

app = FastAPI(title="Audio Transcriber")

# Загружаем модель при старте (medium — баланс скорости и качества)
model = whisper.load_model("medium")


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "ru"):
    """
    Принимает аудио файл, возвращает текст
    Поддерживает: mp3, wav, m4a, ogg, flac
    """

    # Проверяем расширение
    allowed_ext = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_ext:
        raise HTTPException(400, f"Формат {ext} не поддерживается. Используй: {allowed_ext}")

    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Транскрибируем
        result = model.transcribe(tmp_path, language=language)

        return {
            "status": "ok",
            "text": result["text"],
            "language": result.get("language", language),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result.get("segments", [])
            ]
        }

    except Exception as e:
        raise HTTPException(500, f"Ошибка транскрипции: {str(e)}")

    finally:
        # Удаляем временный файл
        os.unlink(tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok", "model": "whisper-medium"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
