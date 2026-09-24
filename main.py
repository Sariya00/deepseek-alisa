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

    print(f"USER TEXT: {user_text}")
    print(f"API KEY EXISTS: {bool(DEEPSEEK_API_KEY)}")
    print(f"API KEY PREFIX: {DEEPSEEK_API_KEY[:10] if DEEPSEEK_API_KEY else 'NONE'}")

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
            },
            timeout=30
        )
        
        print(f"DEEPSEEK STATUS: {response.status_code}")
        print(f"DEEPSEEK BODY: {response.text[:1000]}")
        
        data = response.json()
        
        # Проверяем, есть ли ошибка в ответе
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            error_code = data["error"].get("code", "unknown")
            print(f"DEEPSEEK ERROR: {error_code} - {error_msg}")
            answer = f"Ошибка API: {error_code}. Проверьте ключ и баланс."
        elif "choices" in data:
            answer = data["choices"][0]["message"]["content"]
        else:
            print(f"UNEXPECTED RESPONSE: {data}")
            answer = "Неожиданный ответ от сервиса."
            
    except requests.exceptions.Timeout:
        print("TIMEOUT")
        answer = "Превышено время ожидания."
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
        answer = "Произошла ошибка."

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }