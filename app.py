import threading
import asyncio
from flask import Flask
from bot import main

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return "OK", 200

def run_bot():
    asyncio.run(main())

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    threading.Thread(target=run_bot, daemon=True).start()
    # Запускаем Flask-сервер, чтобы Render видел открытый порт
    app.run(host="0.0.0.0", port=10000)

