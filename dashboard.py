from fastapi import FastAPI, Request, Form, Cookie, Response, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os
import aiohttp
from datetime import datetime, timedelta
import shutil

app = FastAPI(title="Alex Advanced Bot Control Center")

os.makedirs("static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

def init_db():
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            token TEXT UNIQUE,
            group_name TEXT DEFAULT 'Общие',
            code_content TEXT DEFAULT '',
            owner_username TEXT DEFAULT '',
            owner_name TEXT DEFAULT '',
            owner_avatar TEXT DEFAULT 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER,
            lead_id TEXT,
            status_text TEXT,
            timer_sec INTEGER,
            is_final_link INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    full_code_alex = '''import asyncio
import os
import random
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessConnection, LinkPreviewOptions
from aiohttp import web
import aiohttp

BOT_TOKEN = "TOKEN_PLACEHOLDER"
WEB_APP_URL = "https://webapp-abar.onrender.com/api/log"

FIRST_STEP_MESSAGES = [
    "Привет, ты искал работу в тт ?",
    "привет! ты искал работу в ТТ?",
]

FINAL_MESSAGE = "Тогда давай я тебе лучше скину ссылку, там ты все увидишь\\n\\nhttps://t.me/+52YuDrXyAok4ODc6"

POSITIVE_KEYWORDS = [
    "да", "ага", "угу", "ну да", "вроде", "типа", "дап", "даа", "го", "+", 
    "было дело", "хочу", "просил", "кто", "возможно", "может", "хз", "помню", 
    "забыл", "какая", "что за", "а что", "зачем", "где", "как", "ищу", "работу",
    "интересно", "интересуюсь", "можно", "расскажи", "почему бы и нет",
    "работа", "что за работа", "какая работа", "расскажи подробнее"
]

NEGATIVE_KEYWORDS = [
    "нет", "не", "неа", "не-а", "мимо", "нет спасибо", "не интересует", 
    "нафиг", "пошел", "отвали", "не искал", "никакой"
]

user_stages = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_log_to_web(lead_id, status_text, timer_sec, is_final_link=0):
    data = {
        "token": BOT_TOKEN,
        "lead_id": str(lead_id),
        "status_text": status_text,
        "timer_sec": timer_sec,
        "is_final_link": is_final_link
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEB_APP_URL, json=data) as resp:
                pass
    except Exception as e:
        print(f"[WEB LOG] Ошибка: {e}")

async def handle_ping(request):
    return web.Response(text="Bot is active")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.
