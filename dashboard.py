from fastapi import FastAPI, Request, Form, Cookie, Response, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
import shutil

app = FastAPI(title="Alex Advanced Bot Control Center")

os.makedirs("static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_NAME = "dashboard_bots.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

CODE_ALEX_1 = '''import asyncio
import os
import random
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessConnection, LinkPreviewOptions
from aiohttp import web
import aiohttp

BOT_TOKEN = "8636464152:AAG_PzFg2JUqn6N0mPVrtbv574rXlIuwv6g"
WEB_APP_URL = "https://webapp-abar.onrender.com/api/log"

FIRST_STEP_MESSAGES = [
    "Привет, слушай ты искал работу в тик токе ?",
    "Привет! Слушай, ты искал работу в тик токе?",
]

FINAL_MESSAGE = "Тогда давай я тебе лучше скину ссылку, там тебе все расскажут и покажут\\n\\nhttps://t.me/+IxbHj9Wmox0zZmFi"

POSITIVE_KEYWORDS = ["да", "ага", "угу", "ну да", "вроде", "типа", "дап", "даа", "го", "+", "хочу", "ищу", "работу"]
NEGATIVE_KEYWORDS = ["нет", "не", "неа", "не-а", "мимо", "нет спасибо", "не интересует"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_log_to_web(lead_id, status_text, timer_sec, is_final_link=0, lead_username=""):
    data = {"token": BOT_TOKEN, "lead_id": str(lead_id), "lead_username": lead_username, "status_text": status_text, "timer_sec": timer_sec, "is_final_link": is_final_link}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEB_APP_URL, json=data) as resp: pass
    except Exception as e: print(f"Log Error: {e}")

@dp.business_message()
async def handle_business_message(message: Message):
    if message.from_user and message.from_user.is_bot: return
    conn_id = message.business_connection_id
    if not conn_id: return
    
    chat_id = message.chat.id
    u_name = message.from_user.username or ""
    
    await send_log_to_web(chat_id, "Инициализация диалога. Ожидание 10 минут...", 600, 0, u_name)
    await asyncio.sleep(600)
    await bot.send_message(chat_id=chat_id, text=random.choice(FIRST_STEP_MESSAGES), business_connection_id=conn_id)
    await send_log_to_web(chat_id, "Отправлен 1-й вопрос о работе", 0, 0, u_name)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''

CODE_ALEX_2 = CODE_ALEX_1.replace("8636464152:AAG_PzFg2JUqn6N0mPVrtbv574rXlIuwv6g", "8989087015:AAHAkK_e-fcIQFLkrfQgs4-ZhrKXcJft1G4")

CODE_SPANH_1 = '''import asyncio
import os
import random
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessConnection, LinkPreviewOptions
from aiohttp import web
import aiohttp

BOT_TOKEN = "8902861284:AAEUL5DImSMqKSYKWdJ_uqlbYdKgBfF9Bq4"
WEB_APP_URL = "https://webapp-abar.onrender.com/api/log"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_log_to_web(lead_id, status_text, timer_sec, is_final_link=0, lead_username=""):
    data = {"token": BOT_TOKEN, "lead_id": str(lead_id), "lead_username": lead_username, "status_text": status_text, "timer_sec": timer_sec, "is_final_link": is_final_link}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEB_APP_URL, json=data) as resp: pass
    except Exception as e: print(f"Log Error: {e}")

@dp.business_message()
async def handle_business_message(message: Message):
    if message.from_user and message.from_user.is_bot: return
    conn_id = message.business_connection_id
    if not conn_id: return
    
    chat_id = message.chat.id
    u_name = message.from_user.username or ""
    
    await send_log_to_web(chat_id, "Приветствие отправлено. Ожидание ответа...", 180, 0, u_name)
    await asyncio.sleep(180)
    await bot.send_message(chat_id=chat_id, text="Тогда держи ссылку: https://t.me/+52YuDrXyAok4ODc6", business_connection_id=conn_id)
    await send_log_to_web(chat_id, "Финиш: Ссылка успешно отправлена!", 0, 1, u_name)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''

CODE_SPANH_2 = CODE_SPANH_1.replace("8902861284:AAEUL5DImSMqKSYKWdJ_uqlbYdKgBfF9Bq4", "8833046723:AAG_el4XirqdoMZLVcZdNWypVzanJkETGnY")

CODE_FLASH = '''import asyncio
from aiogram import Bot, Dispatcher

BOT_TOKEN = "8586984485:AAE4m73JZGf3s5yfExriJP_C-otyiAWZu8I"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    print("Flash Manager Bot Started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''

def init_db():
    conn = get_db()
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
            lead_username TEXT DEFAULT '',
            status_text TEXT,
            timer_sec INTEGER,
            is_final_link INTEGER DEFAULT 0,
            status_code TEXT DEFAULT 'WAITING',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    default_bots = [
        ("Alex Bot 1", "8636464152:AAG_PzFg2JUqn6N0mPVrtbv574rXlIuwv6g", "Alex Group", CODE_ALEX_1, "@alex_acc_1", "Alex Manager 1"),
        ("Alex Bot 2", "8989087015:AAHAkK_e-fcIQFLkrfQgs4-ZhrKXcJft1G4", "Alex Group", CODE_ALEX_2, "@alex_acc_2", "Alex Manager 2"),
        ("Spanh Bot 1", "8902861284:AAEUL5DImSMqKSYKWdJ_uqlbYdKgBfF9Bq4", "Spanh Group", CODE_SPANH_1, "@spanh_acc_1", "Spanh Manager 1"),
        ("Spanh Bot 2", "8833046723:AAG_el4XirqdoMZLVcZdNWypVzanJkETGnY", "Spanh Group", CODE_SPANH_2, "@spanh_acc_2", "Spanh Manager 2"),
        ("Flash Manager Bot", "8586984485:AAE4m73JZGf3s5yfExriJP_C-otyiAWZu8I", "Общие", CODE_FLASH, "@flash_meneger", "Flash Manager")
    ]
    
    for name, token, group, code, o_user, o_name in default_bots:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO bots (name, token, group_name, code_content, owner_username, owner_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, token, group, code, o_user, o_name))
        except Exception:
            pass

    conn.commit()
    conn.close()

init_db()

async def self_ping_webapp():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://webapp-abar.onrender.com")
    await asyncio.sleep(20)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(render_url) as response: pass
            except Exception: pass
            await asyncio.sleep(300)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(self_ping_webapp())

async def get_bot_api_info(token: str):
    bot_info = {"username": "@bot", "name": "Telegram Bot"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.telegram.org/bot{token}/getMe") as resp:
                data = await resp.json()
                if data.get("ok"):
                    res = data["result"]
                    bot_info["username"] = f"@{res.get('username', 'bot')}"
                    bot_info["name"] = res.get('first_name', 'Bot')
    except Exception:
        pass
    return bot_info

class LogSchema(BaseModel):
    token: str
    lead_id: str
    lead_username: str = ""
    status_text: str
    timer_sec: int
    is_final_link: int = 0
    status_code: str = "WAITING"

@app.post("/api/log")
async def receive_bot_log(log: LogSchema):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bots WHERE token = ?", (log.token,))
    row = cursor.fetchone()
    if row:
        bot_id = row["id"]
        st_code = log.status_code
        if log.is_final_link == 1:
            st_code = "SUCCESS"
        elif "отказ" in log.status_text.lower() or "игнор" in log.status_text.lower():
            st_code = "REFUSAL"
            
        cursor.execute("""
            INSERT INTO bot_logs (bot_id, lead_id, lead_username, status_text, timer_sec, is_final_link, status_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (bot_id, log.lead_id, log.lead_username, log.status_text, log.timer_sec, log.is_final_link, st_code))
        conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/login", response_class=HTMLResponse)
async def login_page(response: Response, error: str = None):
    err_html = f'<div class="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs text-center mb-4">{error}</div>' if error else ''
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GOGOha Center | Авторизация</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen flex items-center justify-center p-4">
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-8 w-full max-w-sm shadow-2xl">
            <div class="text-center mb-6">
                <div class="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl mx-auto flex items-center justify-center text-2xl mb-3">⚡</div>
                <h1 class="text-xl font-bold text-white mb-1">Авторизация</h1>
                <p class="text-xs text-gray-400">Панель управления трафиком</p>
            </div>
            {err_html}
            <form action="/login" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Логин</label>
                    <input type="text" name="username" required placeholder="Gogoha" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-white focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Пароль</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-white focus:border-emerald-500">
                </div>
                <button type="submit" class="w-full bg-emerald-500 text-gray-950 font-bold py-3 rounded-xl text-sm hover:bg-emerald-400">Войти в кабинет</button>
            </form>
        </div>
    </body>
    </html>
    """
    res = HTMLResponse(content=html)
    res.delete_cookie("gogoha_strict_session")
    return res

@app.post("/login")
async def login_post(username: str = Form(...), password: str = Form(...)):
    if username == "Gogoha" and password == "05056978":
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="gogoha_strict_session", value="active_valid_session", max_age=86400, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Неверный логин или пароль", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("gogoha_strict_session")
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token, group_name FROM bots")
    bots = cursor.fetchall()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE date(updated_at) = ?", (today_str,))
    today_stats = cursor.fetchone()
    total_today = today_stats[0] or 0
    links_today = today_stats[1] or 0

    chart_labels, chart_messages, chart_links = [], [], []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        chart_labels.append((datetime.now() - timedelta(days=i)).strftime("%d.%m"))
        cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE date(updated_at) = ?", (d,))
        res = cursor.fetchone()
        chart_messages.append(res[0] or 0)
        chart_links.append(res[1] or 0)

    groups = {}
    for bot in bots:
        group = bot["group_name"]
        if group not in groups: groups[group] = []
        groups[group].append(bot)
    conn.close()

    groups_html = ""
    for group_name, g_bots in groups.items():
        bots_cards = ""
        for b in g_bots:
            bots_cards += f"""
            <div id="bot-card-{b['id']}" draggable="true" ondragstart="drag(event, {b['id']})" class="bg-gray-900 border border-gray-800 hover:border-emerald-500/50 rounded-2xl p-4 shadow-lg mb-3 flex justify-between items-center cursor-grab active:cursor-grabbing transition transform hover:-translate-y-0.5">
                <a href="/bot/{b['id']}" class="flex-grow">
                    <div class="flex justify-between items-start mb-1">
                        <h3 class="font-semibold text-emerald-400">🤖 {b['name']}</h3>
                        <span class="text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded-lg">Активен</span>
                    </div>
                    <p class="text-xs text-gray-500 font-mono truncate">Token: {b['token'][:10]}...</p>
                </a>
                <form action="/move-to-group" method="POST" class="ml-2">
                    <input type="hidden" name="bot_id" value="{b['id']}">
                    <input type="hidden" name="target_group" value="Общие">
                    {'<button type="submit" class="text-xs text-gray-500 hover:text-red-400 p-1" title="Сбросить в Общие">❌</button>' if group_name != 'Общие' else ''}
                </form>
            </div>
            """
        groups_html += f"""
        <div class="mb-6 drop-zone p-2 rounded-2xl transition border border-transparent" ondragover="allowDrop(event)" ondragleave="leaveDrop(event)" ondrop="drop(event, '{group_name}')">
            <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-bold text-gray-300">📁 {group_name} ({len(g_bots)})</span>
            </div>
            {bots_cards}
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Панель управления</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10 select-none">
        <div class="max-w-md mx-auto">
            <header class="flex justify-between items-center mb-4 pt-2">
                <div>
                    <h1 class="text-xl font-bold text-white">📱 Мои Боты</h1>
                    <p class="text-xs text-gray-400">Центр управления трафиком</p>
                </div>
                <div class="flex gap-2 items-center">
                    <a href="/logout" class="px-2.5 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl text-xs font-semibold border border-red-500/20">🚪 Выйти</a>
                    <button onclick="openGroupModal()" class="px-2.5 py-1.5 bg-gray-900 hover:bg-gray-800 text-gray-200 rounded-xl text-xs font-semibold border border-gray-800">+ Группа</button>
                    <button onclick="openModal()" class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold rounded-xl text-xs shadow-lg">+ Бот</button>
                </div>
            </header>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 shadow-xl">
                <h3 class="text-xs font-semibold text-gray-300 mb-3">📊 Статистика за сегодня</h3>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-950 p-3 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400">Лидов в обработке</div>
                        <div class="text-lg font-bold text-emerald-400">{total_today}</div>
                    </div>
                    <div class="bg-gray-950 p-3 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400">Успешно ссылок</div>
                        <div class="text-lg font-bold text-purple-400">{links_today}</div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-6 shadow-xl">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-xs font-semibold text-gray-300">📈 Динамика за 7 дней</h3>
                    <div class="flex gap-1 bg-gray-950 p-1 rounded-xl border border-gray-800">
                        <button onclick="filterChart('all')" id="filter-all" class="px-2 py-0.5 text-[10px] rounded-lg font-bold bg-emerald-500 text-gray-950">Все</button>
                        <button onclick="filterChart('leads')" id="filter-leads" class="px-2 py-0.5 text-[10px] rounded-lg font-semibold text-gray-400 hover:text-white">Лиды</button>
                        <button onclick="filterChart('links')" id="filter-links" class="px-2 py-0.5 text-[10px] rounded-lg font-semibold text-gray-400 hover:text-white">Ссылки</button>
                    </div>
                </div>
                <div class="relative h-48 w-full">
                    <canvas id="trafficChart"></canvas>
                </div>
            </div>

            {groups_html}

            <div id="addModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                <div class="bg-gray-900 border border-gray-800 rounded-3xl p-6 w-full max-w-sm shadow-2xl">
                    <h3 class="text-lg font-bold text-white mb-4">➕ Добавить бота</h3>
                    <form action="/add-bot" method="POST" class="space-y-3">
                        <input type="text" name="name" placeholder="Название" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white">
                        <input type="text" id="modalGroupName" name="group_name" value="Общие" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white">
                        <input type="text" name="token" placeholder="Token: 123456:ABC..." required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white">
                        <div class="flex gap-3 pt-2">
                            <button type="button" onclick="closeModal()" class="w-1/2 bg-gray-800 text-gray-300 py-3 rounded-xl text-sm font-medium">Отмена</button>
                            <button type="submit" class="w-1/2 bg-emerald-500 text-gray-950 font-bold py-3 rounded-xl text-sm">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>

            <div id="groupModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                <div class="bg-gray-900 border border-gray-800 rounded-3xl p-6 w-full max-w-sm shadow-2xl">
                    <h3 class="text-lg font-bold text-white mb-4">📁 Новая группа</h3>
                    <form action="/add-group" method="POST" class="space-y-3">
                        <input type="text" name="group_name" placeholder="Название группы" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white">
                        <div class="flex gap-3 pt-2">
                            <button type="button" onclick="closeGroupModal()" class="w-1/2 bg-gray-800 text-gray-300 py-3 rounded-xl text-sm font-medium">Отмена</button>
                            <button type="submit" class="w-1/2 bg-emerald-500 text-gray-950 font-bold py-3 rounded-xl text-sm">Создать</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                function allowDrop(ev) {{ ev.preventDefault(); ev.currentTarget.classList.add('border-emerald-500/50', 'bg-emerald-500/5'); }}
                function leaveDrop(ev) {{ ev.currentTarget.classList.remove('border-emerald-500/50', 'bg-emerald-500/5'); }}
                function drag(ev, botId) {{ ev.dataTransfer.setData("botId", botId); }}
                function drop(ev, targetGroup) {{
                    ev.preventDefault();
                    leaveDrop(ev);
                    const botId = ev.dataTransfer.getData("botId");
                    const form = document.createElement('form');
                    form.method = 'POST'; form.action = '/move-to-group';
                    const inputBot = document.createElement('input');
                    inputBot.type = 'hidden'; inputBot.name = 'bot_id'; inputBot.value = botId;
                    const inputGroup = document.createElement('input');
                    inputGroup.type = 'hidden'; inputGroup.name = 'target_group'; inputGroup.value = targetGroup;
                    form.appendChild(inputBot); form.appendChild(inputGroup);
                    document.body.appendChild(form); form.submit();
                }}

                const chartCtx = document.getElementById('trafficChart').getContext('2d');
                const trafficChart = new Chart(chartCtx, {{
                    type: 'line',
                    data: {{
                        labels: {chart_labels},
                        datasets: [
                            {{ label: 'Лиды', data: {chart_messages}, borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.15)', borderWidth: 2, tension: 0.4, fill: true }},
                            {{ label: 'Ссылки', data: {chart_links}, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.15)', borderWidth: 2, tension: 0.4, fill: true }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#9ca3af', font: {{ size: 10 }} }} }} }} }}
                }});

                function filterChart(type) {{
                    ['all', 'leads', 'links'].forEach(t => {{
                        document.getElementById('filter-' + t).className = 'px-2 py-0.5 text-[10px] rounded-lg font-semibold text-gray-400 hover:text-white';
                    }});
                    document.getElementById('filter-' + type).className = 'px-2 py-0.5 text-[10px] rounded-lg font-bold bg-emerald-500 text-gray-950';

                    if(type === 'all') {{
                        trafficChart.setDatasetVisibility(0, true);
                        trafficChart.setDatasetVisibility(1, true);
                    }} else if(type === 'leads') {{
                        trafficChart.setDatasetVisibility(0, true);
                        trafficChart.setDatasetVisibility(1, false);
                    }} else if(type === 'links') {{
                        trafficChart.setDatasetVisibility(0, false);
                        trafficChart.setDatasetVisibility(1, true);
                    }}
                    trafficChart.update();
                }}

                function openModal() {{ document.getElementById('addModal').classList.remove('hidden'); document.getElementById('addModal').classList.add('flex'); }}
                function closeModal() {{ document.getElementById('addModal').classList.add('hidden'); document.getElementById('addModal').classList.remove('flex'); }}
                function openGroupModal() {{ document.getElementById('groupModal').classList.remove('hidden'); document.getElementById('groupModal').classList.add('flex'); }}
                function closeGroupModal() {{ document.getElementById('groupModal').classList.add('hidden'); document.getElementById('groupModal').classList.remove('flex'); }}
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/bot/{bot_id}", response_class=HTMLResponse)
async def bot_detail(bot_id: int, gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
    bot = cursor.fetchone()
    
    if not bot:
        conn.close()
        return RedirectResponse(url="/", status_code=303)

    bot_api_info = await get_bot_api_info(bot['token'])

    cursor.execute("SELECT * FROM bot_logs WHERE bot_id = ? ORDER BY updated_at DESC", (bot_id,))
    logs = cursor.fetchall()

    cursor.execute("""
        SELECT lead_id, lead_username, status_text, timer_sec, is_final_link, status_code, MAX(updated_at) as last_time
        FROM bot_logs 
        WHERE bot_id = ? 
        GROUP BY lead_id, lead_username, status_text, timer_sec, is_final_link, status_code
        ORDER BY last_time DESC
    """, (bot_id,))
    users_summary = cursor.fetchall()

    daily_stats_html = ""
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        d_label = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
        cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE bot_id = ? AND date(updated_at) = ?", (bot_id, d))
        res = cursor.fetchone()
        daily_stats_html += f"""
        <div class="flex justify-between items-center bg-gray-900 border border-gray-800 rounded-2xl p-3 mb-2 text-xs">
            <span class="text-gray-300 font-semibold">📅 {d_label}</span>
            <div class="flex gap-3">
                <span class="text-emerald-400">Лидам: <b class="text-white">{res[0] or 0}</b></span>
                <span class="text-purple-400">Ссылки: <b class="text-white">{res[1] or 0}</b></span>
            </div>
        </div>
        """
    conn.close()

    logs_html = ""
    for l in logs:
        logs_html += f"""
        <div class="bg-gray-800/40 border border-gray-700/30 rounded-xl p-3 mb-2 text-xs">
            <div class="flex justify-between text-gray-400 mb-1">
                <span>Лид ID: <b class="text-white font-mono">{l['lead_id']}</b></span>
                <span class="text-emerald-400">⏱ {l['timer_sec']} сек</span>
            </div>
            <p class="text-gray-200">{l['status_text']}</p>
            <div class="text-[10px] text-gray-500 mt-1">{l['updated_at']}</div>
        </div>
        """
    if not logs:
        logs_html = """
        <div class="text-center py-8 bg-gray-900/50 border border-gray-800 rounded-2xl">
            <div class="text-2xl mb-2">📜</div>
            <p class="text-xs text-gray-400 font-medium">Логи пока пусты</p>
            <p class="text-[10px] text-gray-600 mt-1">Ожидание событий от запущенного бота...</p>
        </div>
        """

    users_html = ""
    for u in users_summary:
        st_code = u['status_code']
        is_link = u['is_final_link']
        
        if is_link == 1 or st_code == 'SUCCESS':
            badge = '<span class="px-2 py-1 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 font-semibold text-[11px]">✅ Ссылка отправлена</span>'
            status_dot = "🟢"
        elif st_code == 'REFUSAL':
            badge = '<span class="px-2 py-1 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 font-semibold text-[11px]">❌ Отказ</span>'
            status_dot = "🔴"
        else:
            badge = '<span class="px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 font-semibold text-[11px]">⚙️ В процессе</span>'
            status_dot = "🟠"

        user_disp = f"@{u['lead_username']}" if u['lead_username'] else f"ID: {u['lead_id']}"
        
        users_html += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-2xl p-3 mb-2 flex items-center justify-between shadow-md">
            <div class="flex items-center gap-2.5">
                <span class="text-base">{status_dot}</span>
                <div>
                    <div class="text-xs font-bold text-white font-mono">{user_disp}</div>
                    <div class="text-[10px] text-gray-400 truncate max-w-[180px]">{u['status_text']}</div>
                    <div class="text-[9px] text-gray-500 mt-0.5">{u['last_time']}</div>
                </div>
            </div>
            <div>{badge}</div>
        </div>
        """
    if not users_summary:
        users_html = """
        <div class="text-center py-8 bg-gray-900/50 border border-gray-800 rounded-2xl">
            <div class="text-2xl mb-2">👤</div>
            <p class="text-xs text-gray-400 font-medium">Список юзеров пока пуст</p>
            <p class="text-[10px] text-gray-600 mt-1">Здесь будут отображаться юзернеймы лидов и их статусы</p>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{bot['name']}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .code-editor::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            .code-editor::-webkit-scrollbar-track {{ background: #030712; border-radius: 8px; }}
            .code-editor::-webkit-scrollbar-thumb {{ background: #1f2937; border-radius: 8px; border: 2px solid #030712; }}
            .code-editor::-webkit-scrollbar-thumb:hover {{ background: #10b981; }}
        </style>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10">
        <div class="max-w-md mx-auto">
            <div class="flex items-center justify-between mb-4 pt-2">
                <a href="/" class="text-xs bg-gray-900 border border-gray-800 text-gray-300 px-3 py-1.5 rounded-xl">← Назад</a>
                <h1 class="font-bold text-base text-emerald-400">{bot['name']}</h1>
                <span class="text-xs text-gray-500">{bot['group_name']}</span>
            </div>

            <!-- ШАПКА: ЛИЧНЫЙ АККАУНТ + ПОДКЛЮЧЕННЫЙ TELEGRAM БОТ -->
            <div class="bg-gradient-to-r from-emerald-950/40 to-gray-900 border border-emerald-500/20 rounded-2xl p-4 mb-4 shadow-xl">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-[10px] text-gray-400 uppercase font-semibold tracking-wider">👥 Telegram Аккаунт & Бот</span>
                    <button onclick="toggleEditOwner()" class="text-[10px] text-emerald-400 hover:underline">Изменить фото</button>
                </div>
                
                <div id="owner-display" class="flex items-center gap-3 mb-3 pb-3 border-b border-gray-800">
                    <img src="{bot['owner_avatar']}" class="w-12 h-12 rounded-full border-2 border-emerald-500/40 object-cover shadow-md">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-sm font-bold text-white">{bot['owner_name']}</h2>
                            <span class="text-[9px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20">Владелец</span>
                        </div>
                        <p class="text-xs text-emerald-400 font-mono mt-0.5">{bot['owner_username']}</p>
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs bg-gray-950/80 p-2.5 rounded-xl border border-gray-800/80">
                    <div class="flex items-center gap-2.5">
                        <span class="text-lg">🤖</span>
                        <div>
                            <div class="text-white font-bold text-xs">{bot_api_info['name']}</div>
                            <div class="text-[11px] text-emerald-400 font-mono">{bot_api_info['username']}</div>
                        </div>
                    </div>
                    <span class="text-[10px] text-gray-400 font-mono bg-gray-900 px-2 py-1 rounded-lg border border-gray-800">Token: {bot['token'][:8]}...</span>
                </div>

                <form id="owner-form" action="/update-owner/{bot_id}" method="POST" enctype="multipart/form-data" class="hidden space-y-3 mt-3 pt-3 border-t border-gray-800">
                    <input type="text" name="owner_name" value="{bot['owner_name']}" placeholder="Имя аккаунта" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-white">
                    <input type="text" name="owner_username" value="{bot['owner_username']}" placeholder="@username аккаунта" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-white">
                    <input type="file" name="avatar_file" accept="image/*" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-gray-300">
                    <div class="flex gap-2">
                        <button type="submit" class="bg-emerald-500 text-gray-950 font-bold px-3 py-1.5 rounded-lg text-xs">Сохранить</button>
                        <button type="button" onclick="toggleEditOwner()" class="bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg text-xs">Отмена</button>
                    </div>
                </form>
            </div>

            <div class="grid grid-cols-4 gap-1 bg-gray-900 p-1 rounded-2xl mb-4 border border-gray-800">
                <button onclick="switchTab('users')" id="btn-users" class="py-2 px-1 rounded-xl text-[10px] font-semibold bg-emerald-500 text-gray-950 font-bold transition text-center">👤 Юзеры</button>
                <button onclick="switchTab('logs')" id="btn-logs" class="py-2 px-1 rounded-xl text-[10px] font-semibold text-gray-400 transition text-center">📊 Логи</button>
                <button onclick="switchTab('stats')" id="btn-stats" class="py-2 px-1 rounded-xl text-[10px] font-semibold text-gray-400 transition text-center">📈 Дни</button>
                <button onclick="switchTab('code')" id="btn-code" class="py-2 px-1 rounded-xl text-[10px] font-semibold text-gray-400 transition text-center">💻 Код</button>
            </div>

            <div id="tab-users" class="space-y-2">{users_html}</div>
            <div id="tab-logs" class="hidden space-y-2">{logs_html}</div>
            <div id="tab-stats" class="hidden space-y-2">{daily_stats_html}</div>

            <div id="tab-code" class="hidden space-y-3">
                <form id="code-form" action="/save-code/{bot_id}" method="POST" onsubmit="return confirmSaveCode()" class="space-y-3">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs text-gray-400"># Полный код бота</span>
                        <div class="flex gap-2">
                            <button type="button" onclick="cancelCodeEdit()" id="btn-cancel-code" class="hidden text-xs text-red-400 border border-red-500/30 px-2 py-1 rounded-lg bg-red-500/10">❌ Отмена</button>
                            <button type="button" onclick="enableCodeEdit()" id="btn-edit-code" class="text-xs text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded-lg bg-emerald-500/10">✏️ Изменить код</button>
                        </div>
                    </div>
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-2 shadow-lg">
                        <textarea id="code-area" readonly name="code_content" class="code-editor w-full h-[420px] bg-gray-950 border border-gray-800/80 rounded-xl p-3 text-xs font-mono text-emerald-400 focus:outline-none leading-relaxed resize-y whitespace-pre overflow-auto">{bot['code_content']}</textarea>
                    </div>
                    <button type="submit" id="btn-save-code" class="hidden w-full bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold py-3 rounded-xl text-sm shadow-lg shadow-emerald-500/20 transition">💾 Сохранить и обновить код</button>
                </form>
            </div>

            <script>
                const originalCodeContent = `{bot['code_content']}`;

                function enableCodeEdit() {{
                    if (confirm("Вы уверены, что хотите перейти в режим редактирования кода?")) {{
                        const area = document.getElementById('code-area');
                        area.removeAttribute('readonly');
                        area.focus();
                        document.getElementById('btn-edit-code').classList.add('hidden');
                        document.getElementById('btn-cancel-code').classList.remove('hidden');
                        document.getElementById('btn-save-code').classList.remove('hidden');
                    }}
                }}

                function cancelCodeEdit() {{
                    const area = document.getElementById('code-area');
                    area.value = originalCodeContent;
                    area.setAttribute('readonly', 'true');
                    document.getElementById('btn-edit-code').classList.remove('hidden');
                    document.getElementById('btn-cancel-code').classList.add('hidden');
                    document.getElementById('btn-save-code').classList.add('hidden');
                }}

                function confirmSaveCode() {{
                    return confirm("Вы уверены, что хотите сохранить изменения и обновить код бота?");
                }}

                function toggleEditOwner() {{
                    document.getElementById('owner-display').classList.toggle('hidden');
                    document.getElementById('owner-form').classList.toggle('hidden');
                }}

                function switchTab(tab) {{
                    if (tab !== 'code') {{
                        cancelCodeEdit();
                    }}

                    ['users', 'logs', 'stats', 'code'].forEach(t => {{
                        document.getElementById('tab-' + t).classList.add('hidden');
                        document.getElementById('btn-' + t).className = 'py-2 px-1 rounded-xl text-[10px] font-semibold text-gray-400 transition text-center';
                    }});
                    document.getElementById('tab-' + tab).classList.remove('hidden');
                    document.getElementById('btn-' + tab).className = 'py-2 px-1 rounded-xl text-[10px] font-semibold bg-emerald-500 text-gray-950 font-bold transition text-center';
                }}
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/move-to-group")
async def move_to_group(bot_id: int = Form(...), target_group: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET group_name = ? WHERE id = ?", (target_group, bot_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/add-bot")
async def add_bot(name: str = Form(...), token: str = Form(...), group_name: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bots (name, token, group_name, code_content, owner_username, owner_name) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, token.strip(), group_name.strip(), "", '@new_acc', 'New Manager'))
        conn.commit()
    except Exception: pass
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/add-group")
async def add_group(group_name: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-owner/{bot_id}")
async def update_owner(bot_id: int, owner_name: str = Form(...), owner_username: str = Form(...), avatar_file: UploadFile = File(None), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = get_db()
    cursor = conn.cursor()
    
    avatar_url = None
    if avatar_file and avatar_file.filename:
        file_ext = avatar_file.filename.split(".")[-1]
        file_name = f"avatar_{bot_id}_{int(datetime.now().timestamp())}.{file_ext}"
        file_path = os.path.join("static/avatars", file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar_file.file, buffer)
        avatar_url = f"/static/avatars/{file_name}"

    if avatar_url:
        cursor.execute("UPDATE bots SET owner_name = ?, owner_username = ?, owner_avatar = ? WHERE id = ?", (owner_name.strip(), owner_username.strip(), avatar_url, bot_id))
    else:
        cursor.execute("UPDATE bots SET owner_name = ?, owner_username = ? WHERE id = ?", (owner_name.strip(), owner_username.strip(), bot_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/bot/{bot_id}", status_code=303)

@app.post("/save-code/{bot_id}")
async def save_code(bot_id: int, code_content: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET code_content = ? WHERE id = ?", (code_content, bot_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/bot/{bot_id}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
