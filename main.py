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
        print(f"DEEPSEEK RESPONSE: {response.text[:500]}")
        
        if response.status_code != 200:
            answer = "Сервис временно недоступен. Попробуйте позже."
        else:
            answer = response.json()["choices"][0]["message"]["content"]
            
    except Exception as e:
        print(f"ERROR: {e}")
        answer = "Произошла ошибка. Попробуйте позже."

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }