import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
            },
            timeout=30  # Добавляем таймаут, чтобы запрос не "висел"
        )
        
        # Проверяем статус ответа перед парсингом JSON
        if response.status_code != 200:
            # Логируем ошибку для диагностики (но не показываем пользователю детали)
            print(f"DeepSeek API error: {response.status_code} - {response.text[:200]}")
            answer = "Извините, сервис временно недоступен. Попробуйте позже."
        else:
            answer = response.json()["choices"][0]["message"]["content"]
            
    except requests.exceptions.Timeout:
        print("DeepSeek API request timed out")
        answer = "Превышено время ожидания ответа. Попробуйте еще раз."
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        answer = "Произошла ошибка при обращении к сервису."
    except (KeyError, IndexError, ValueError) as e:
        print(f"Unexpected response format: {e}")
        answer = "Получен неожиданный ответ от сервиса."

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }