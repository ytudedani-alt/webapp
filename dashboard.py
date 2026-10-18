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
import psutil

app = FastAPI(title="Alex Advanced Bot Control Center")

os.makedirs("static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_NAME = "dashboard_bots.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

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
            owner_avatar TEXT DEFAULT '/static/avatars/default.png'
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

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
        elif log.timer_sec > 0:
            st_code = "WAITING"
            
        cursor.execute("""
            INSERT INTO bot_logs (bot_id, lead_id, lead_username, status_text, timer_sec, is_final_link, status_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (bot_id, log.lead_id, log.lead_username, log.status_text, log.timer_sec, log.is_final_link, st_code))
        conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/server-status")
async def server_status():
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "hostname": "striped-black",
        "ip": "194.76.136.240",
        "cpu_usage": cpu_usage,
        "ram_total": round(ram.total / (1024**3), 2),
        "ram_used": round(ram.used / (1024**3), 2),
        "disk_percent": disk.percent
    }

@app.post("/api/tiktok/add")
async def add_tiktok_link(url: str = Form(...)):
    url = url.strip()
    if not url:
        return RedirectResponse(url="/?tab=tiktok&msg=empty", status_code=303)
    if "tiktok.com" not in url.lower():
        return RedirectResponse(url="/?tab=tiktok&msg=invalid_domain", status_code=303)
    try:
        conn = get_db()
        conn.execute("INSERT INTO tiktok_links (url) VALUES (?)", (url,))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/?tab=tiktok&msg=added", status_code=303)
    except sqlite3.IntegrityError:
        return RedirectResponse(url="/?tab=tiktok&msg=exists", status_code=303)

@app.post("/api/tiktok/check")
async def check_tiktok_link(data: dict):
    url = data.get("url", "").strip()
    if not url:
        return {"exists": False, "message": "Введите ссылку"}
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tiktok_links WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"exists": True, "message": "❌ Данная ссылка уже обрабатывалась!"}
    return {"exists": False, "message": "✅ Ссылки нет в базе (можно использовать)"}

@app.post("/api/tiktok/delete")
async def delete_tiktok_link(link_id: int = Form(...)):
    conn = get_db()
    conn.execute("DELETE FROM tiktok_links WHERE id = ?", (link_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/?tab=tiktok&msg=deleted", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(error: str = None):
    err_html = f'<div class="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs text-center mb-4">{error}</div>' if error else ''
    html = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>GOGOha Center | Авторизация</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen flex items-center justify-center p-4">
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-8 w-full max-w-sm shadow-2xl">
            <div class="text-center mb-6">
                <div class="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl mx-auto flex items-center justify-center text-2xl mb-3">⚡</div>
                <h1 class="text-xl font-bold text-white mb-1">Авторизация</h1>
            </div>
            {err_html}
            <form action="/login" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Логин</label>
                    <input type="text" name="username" required placeholder="Gogoha" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-white">
                </div>
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Пароль</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-white">
                </div>
                <button type="submit" class="w-full bg-emerald-500 text-gray-950 font-bold py-3 rounded-xl text-sm hover:bg-emerald-400">Войти в кабинет</button>
            </form>
        </div>
    </body>
    </html>"""
    return HTMLResponse(content=html)

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
async def dashboard(request: Request, gogoha_strict_session: str = Cookie(None), filter_target: str = "all", tab: str = "bots", msg: str = None):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token, group_name, owner_username, owner_name, owner_avatar FROM bots")
    bots = cursor.fetchall()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    if filter_target.startswith("bot_"):
        b_id = filter_target.split("_")[1]
        cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE bot_id = ? AND date(updated_at) = ?", (b_id, today_str))
    elif filter_target.startswith("group_"):
        g_name = filter_target.split("_")[1]
        cursor.execute("""
            SELECT COUNT(DISTINCT l.lead_id), COALESCE(SUM(l.is_final_link), 0) 
            FROM bot_logs l JOIN bots b ON l.bot_id = b.id 
            WHERE b.group_name = ? AND date(l.updated_at) = ?
        """, (g_name, today_str))
    else:
        cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE date(updated_at) = ?", (today_str,))
        
    today_stats = cursor.fetchone()
    total_today = today_stats[0] or 0
    links_today = today_stats[1] or 0

    chart_labels, chart_messages, chart_links = [], [], []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        chart_labels.append((datetime.now() - timedelta(days=i)).strftime("%d.%m"))
        
        if filter_target.startswith("bot_"):
            cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE bot_id = ? AND date(updated_at) = ?", (b_id, d))
        elif filter_target.startswith("group_"):
            cursor.execute("""
                SELECT COUNT(DISTINCT l.lead_id), COALESCE(SUM(l.is_final_link), 0) 
                FROM bot_logs l JOIN bots b ON l.bot_id = b.id 
                WHERE b.group_name = ? AND date(l.updated_at) = ?
            """, (g_name, d))
        else:
            cursor.execute("SELECT COUNT(DISTINCT lead_id), COALESCE(SUM(is_final_link), 0) FROM bot_logs WHERE date(updated_at) = ?", (d,))
            
        res = cursor.fetchone()
        chart_messages.append(res[0] or 0)
        chart_links.append(res[1] or 0)

    cursor.execute("SELECT * FROM tiktok_links ORDER BY created_at DESC")
    tiktok_links = cursor.fetchall()
    conn.close()

    groups = {}
    for bot in bots:
        group = bot["group_name"]
        if group not in groups: groups[group] = []
        groups[group].append(bot)

    filter_options = '<option value="all" ' + ('selected' if filter_target=='all' else '') + '>🌐 Вся система (Все боты)</option>'
    for g_name in groups.keys():
        filter_options += f'<option value="group_{g_name}" ' + ('selected' if filter_target==f'group_{g_name}' else '') + f'>📁 Папка: {g_name}</option>'
    for bot in bots:
        filter_options += f'<option value="bot_{bot["id"]}" ' + ('selected' if filter_target==f'bot_{bot["id"]}' else '') + f'>🤖 Бот: {bot["name"]}</option>'

    groups_html = ""
    for group_name, g_bots in groups.items():
        bots_cards = ""
        for b in g_bots:
            avatar = b['owner_avatar'] if b['owner_avatar'] else '/static/avatars/default.png'
            b_id = b['id']
            b_name = b['name']
            b_owner_name = b['owner_name']
            b_owner_username = b['owner_username']
            b_token = b['token']
            bots_cards += f"""
            <div class="bg-gray-900 border border-gray-800 hover:border-emerald-500/50 rounded-2xl p-4 shadow-lg mb-3 flex items-center justify-between transition">
                <a href="/bot/{b_id}" class="flex items-center gap-3 flex-grow">
                    <img src="{avatar}" class="w-10 h-10 rounded-xl object-cover border border-gray-700">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-semibold text-white text-sm">{b_name}</h3>
                            <span class="text-[10px] text-green-400 bg-green-500/10 px-2 py-0.5 rounded-lg">Активен</span>
                        </div>
                        <div class="text-[11px] text-gray-400">{b_owner_name} ({b_owner_username})</div>
                        <div class="text-[10px] text-gray-500 font-mono mt-0.5 truncate max-w-[200px]">Token: {b_token}</div>
                    </div>
                </a>
            </div>"""
        groups_html += f"""
        <div class="mb-6">
            <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-bold text-gray-300">📁 {group_name} ({len(g_bots)})</span>
            </div>
            {bots_cards}
        </div>"""

    tiktok_rows_html = ""
    for link in tiktok_links:
        l_id = link['id']
        l_url = link['url']
        l_date = link['created_at']
        tiktok_rows_html += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-2 flex justify-between items-center text-xs">
            <span class="text-emerald-400 font-mono truncate max-w-[200px]">{l_url}</span>
            <div class="flex items-center gap-2">
                <span class="text-[10px] text-gray-500">{l_date}</span>
                <form action="/api/tiktok/delete" method="POST" class="inline">
                    <input type="hidden" name="link_id" value="{l_id}">
                    <button type="submit" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 px-2 py-1 rounded-lg text-[10px] border border-red-500/20 font-bold">🗑️ Удалить</button>
                </form>
            </div>
        </div>"""

    msg_box = ""
    if msg == "added":
        msg_box = '<div class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-2.5 rounded-xl text-xs text-center mb-3 font-bold">✅ Ссылка успешно добавлена!</div>'
    elif msg == "exists":
        msg_box = '<div class="bg-red-500/10 border border-red-500/30 text-red-400 p-2.5 rounded-xl text-xs text-center mb-3 font-bold">❌ Данная ссылка уже обрабатывалась!</div>'
    elif msg == "invalid_domain":
        msg_box = '<div class="bg-amber-500/10 border border-amber-500/30 text-amber-400 p-2.5 rounded-xl text-xs text-center mb-3 font-bold">⚠️ Введите только прямую ссылку TikTok!</div>'
    elif msg == "deleted":
        msg_box = '<div class="bg-gray-800 text-gray-300 p-2.5 rounded-xl text-xs text-center mb-3 font-bold">🗑️ Ссылка удалена</div>'

    html = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Панель управления</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10">
        <div class="max-w-md mx-auto">
            <header class="flex justify-between items-center mb-4">
                <div>
                    <h1 class="text-xl font-bold text-white">📱 Мои Боты</h1>
                    <p class="text-xs text-gray-400">Центр управления трафиком</p>
                </div>
                <a href="/logout" class="px-2.5 py-1.5 bg-red-500/10 text-red-400 rounded-xl text-xs font-semibold border border-red-500/20">🚪 Выйти</a>
            </header>

            <div class="flex bg-gray-900 border border-gray-800 rounded-2xl p-1 mb-4">
                <button onclick="switchTab('bots')" id="tab-btn-bots" class="flex-1 py-2 text-center text-xs font-bold rounded-xl bg-emerald-500 text-gray-950">🤖 Боты</button>
                <button onclick="switchTab('server')" id="tab-btn-server" class="flex-1 py-2 text-center text-xs font-semibold text-gray-400">🖥️ Сервер</button>
                <button onclick="switchTab('tiktok')" id="tab-btn-tiktok" class="flex-1 py-2 text-center text-xs font-semibold text-gray-400">🎵 Тик Ток</button>
            </div>

            <div id="section-bots" class="{'hidden' if tab != 'bots' else ''}">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-3 mb-4 shadow-xl">
                    <label class="block text-[11px] text-gray-400 mb-1">🔍 Выбрать источник для статистики:</label>
                    <select onchange="changeFilter(this.value)" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-emerald-400 font-semibold focus:border-emerald-500">
                        {filter_options}
                    </select>
                </div>

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
                    <h3 class="text-xs font-semibold text-gray-300 mb-3">📈 Динамика за 7 дней</h3>
                    <div class="relative h-48 w-full">
                        <canvas id="trafficChart"></canvas>
                    </div>
                </div>

                {groups_html}
            </div>

            <div id="section-server" class="{'hidden' if tab != 'server' else ''}">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-4 shadow-xl">
                    <div class="flex justify-between items-center mb-4 pb-3 border-b border-gray-800">
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="text-base font-bold text-white">🇸🇪 striped-black</span>
                                <span class="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-lg">SWE-PROMO</span>
                            </div>
                            <div class="text-xs text-gray-400 font-mono mt-0.5">IP: 194.76.136.240</div>
                        </div>
                    </div>
                    <div class="space-y-3 pt-2">
                        <div>
                            <div class="flex justify-between text-xs mb-1">
                                <span class="text-gray-400">Загрузка CPU</span>
                                <span id="srv-cpu" class="font-mono text-emerald-400">--%</span>
                            </div>
                            <div class="w-full bg-gray-950 h-2 rounded-full overflow-hidden border border-gray-800">
                                <div id="srv-cpu-bar" class="bg-emerald-500 h-full w-0 transition-all duration-500"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs mb-1">
                                <span class="text-gray-400">Оперативная память (RAM)</span>
                                <span id="srv-ram" class="font-mono text-purple-400">-- / 4 GB</span>
                            </div>
                            <div class="w-full bg-gray-950 h-2 rounded-full overflow-hidden border border-gray-800">
                                <div id="srv-ram-bar" class="bg-purple-500 h-full w-0 transition-all duration-500"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="section-tiktok" class="{'hidden' if tab != 'tiktok' else ''}">
                {msg_box}
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4">
                    <h3 class="text-xs font-bold text-white mb-3">➕ Добавить ссылку TikTok</h3>
                    <form action="/api/tiktok/add" method="POST" class="flex gap-2">
                        <input type="text" name="url" required placeholder="https://www.tiktok.com/@..." class="flex-grow bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-white">
                        <button type="submit" class="bg-emerald-500 text-gray-950 font-bold px-4 py-2.5 rounded-xl text-xs">Добавить</button>
                    </form>
                </div>

                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4">
                    <h3 class="text-xs font-bold text-white mb-3">🔍 Проверка ссылки</h3>
                    <input type="text" id="check-url-input" placeholder="Ссылка TikTok..." class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-white mb-2">
                    <button type="button" onclick="checkTikTokUrl()" class="w-full bg-purple-600 text-white font-bold py-2.5 rounded-xl text-xs">Проверить</button>
                    <div id="check-result-box" class="hidden p-3 rounded-xl border text-xs text-center font-bold mt-2"></div>
                </div>

                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4">
                    <h3 class="text-xs font-bold text-gray-300 mb-3">📋 Сохраненные ссылки</h3>
                    {tiktok_rows_html}
                </div>
            </div>

            <script>
                function switchTab(tab) {{
                    ['bots', 'server', 'tiktok'].forEach(t => {{
                        document.getElementById('section-' + t).classList.add('hidden');
                        document.getElementById('tab-btn-' + t).className = 'flex-1 py-2 text-center text-xs font-semibold text-gray-400';
                    }});
                    document.getElementById('section-' + tab).classList.remove('hidden');
                    document.getElementById('tab-btn-' + tab).className = 'flex-1 py-2 text-center text-xs font-bold rounded-xl bg-emerald-500 text-gray-950';
                    if (tab === 'server') fetchServerStatus();
                }}
                function changeFilter(val) {{ window.location.href = "/?filter_target=" + val + "&tab=bots"; }}
                async function fetchServerStatus() {{
                    try {{
                        const res = await fetch('/api/server-status');
                        const data = await res.json();
                        document.getElementById('srv-cpu').innerText = data.cpu_usage + '%';
                        document.getElementById('srv-cpu-bar').style.width = data.cpu_usage + '%';
                        document.getElementById('srv-ram').innerText = data.ram_used + ' / ' + data.ram_total + ' GB';
                        document.getElementById('srv-ram-bar').style.width = ((data.ram_used / data.ram_total) * 100) + '%';
                    }} catch(e) {{}}
                }}
                async function checkTikTokUrl() {{
                    const url = document.getElementById('check-url-input').value.trim();
                    const box = document.getElementById('check-result-box');
                    if (!url) return;
                    const res = await fetch('/api/tiktok/check', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    const data = await res.json();
                    box.classList.remove('hidden', 'bg-red-500/10', 'text-red-400', 'bg-emerald-500/10', 'text-emerald-400');
                    box.classList.add(data.exists ? 'bg-red-500/10' : 'bg-emerald-500/10', data.exists ? 'text-red-400' : 'text-emerald-400');
                    box.innerText = data.message;
                }}
                const urlParams = new URLSearchParams(window.location.search);
                const activeTab = urlParams.get('tab');
                if (activeTab) switchTab(activeTab);

                const ctx = document.getElementById('trafficChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {chart_labels},
                        datasets: [
                            {{ label: 'Лиды', data: {chart_messages}, borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.3 }},
                            {{ label: 'Ссылки', data: {chart_links}, borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.1)', fill: true, tension: 0.3 }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#9ca3af', font: {{ size: 10 }} }} }} }} }}
                }});
            </script>
        </div>
    </body>
    </html>"""
    return HTMLResponse(content=html)

@app.get("/bot/{bot_id}", response_class=HTMLResponse)
async def bot_detail_page(request: Request, bot_id: int, gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
    bot = cursor.fetchone()
    if not bot:
        conn.close()
        return RedirectResponse(url="/", status_code=303)

    # Логи действий бота
    cursor.execute("SELECT * FROM bot_logs WHERE bot_id = ? ORDER BY updated_at DESC LIMIT 50", (bot_id,))
    logs = cursor.fetchall()

    # Уникальные лиды для Юзов
    cursor.execute("""
        SELECT lead_id, lead_username, status_text, timer_sec, is_final_link, status_code, max(updated_at) as updated_at 
        FROM bot_logs WHERE bot_id = ? GROUP BY lead_id ORDER BY updated_at DESC
    """, (bot_id,))
    leads = cursor.fetchall()

    # Личная статистика бота по дням
    cursor.execute("""
        SELECT date(updated_at) as d, COUNT(DISTINCT lead_id) as cnt, COALESCE(SUM(is_final_link), 0) as links
        FROM bot_logs WHERE bot_id = ? GROUP BY date(updated_at) ORDER BY d DESC LIMIT 7
    """, (bot_id,))
    bot_stats_days = cursor.fetchall()
    conn.close()

    bot_name = bot['name']
    bot_group = bot['group_name']
    owner_name = bot['owner_name']
    owner_username = bot['owner_username']
    bot_token = bot['token']
    avatar = bot['owner_avatar'] if bot['owner_avatar'] else '/static/avatars/default.png'

    # Раздел 2: Логи
    logs_rows = ""
    for l in logs:
        l_username = l['lead_username'] or f"id_{l['lead_id']}"
        logs_rows += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-2 text-xs shadow-md">
            <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-emerald-400">@{l_username}</span>
                <span class="text-[11px] font-mono text-gray-400">{l['updated_at']}</span>
            </div>
            <div class="text-gray-300 text-[11px]">{l['status_text']}</div>
        </div>"""
    if not logs:
        logs_rows = '<div class="text-center py-6 text-xs text-gray-500">Логов пока нет</div>'

    # Раздел 1: Юзы
    leads_rows = ""
    for lead in leads:
        lead_uname = lead['lead_username'] or f"id_{lead['lead_id']}"
        lead_st_text = lead['status_text']
        st_badge = '<span class="text-[10px] bg-amber-500/10 text-amber-400 font-bold px-2 py-0.5 rounded-lg">В процессе</span>'
        if lead['is_final_link'] == 1:
            st_badge = '<span class="text-[10px] bg-emerald-500/10 text-emerald-400 font-bold px-2 py-0.5 rounded-lg">Ссылка отправлена</span>'
        elif "отказ" in lead_st_text.lower():
            st_badge = '<span class="text-[10px] bg-red-500/10 text-red-400 font-bold px-2 py-0.5 rounded-lg">Отказ</span>'
            
        leads_rows += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-2 text-xs shadow-md">
            <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-emerald-400">@{lead_uname}</span>
                <span class="text-[10px] text-gray-400">{lead['updated_at']}</span>
            </div>
            <div class="flex justify-between items-center mt-1">
                <span class="text-gray-300 text-[11px] truncate max-w-[180px]">{lead_st_text}</span>
                {st_badge}
            </div>
        </div>"""
    if not leads:
        leads_rows = '<div class="text-center py-6 text-xs text-gray-500">Нет пользователей</div>'

    # Раздел 3: Очередь (фильтруем строго ожидание отправки ссылки, ожидание 1 вопроса и отказы)
    queue_waiting, queue_first, queue_refusal = "", "", ""
    for lead in leads:
        lead_uname = lead['lead_username'] or f"id_{lead['lead_id']}"
        st_text = lead['status_text'].lower()
        
        card = f"""
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-2 text-xs shadow-md flex justify-between items-center">
            <div>
                <span class="font-bold text-emerald-400">@{lead_uname}</span>
                <div class="text-gray-300 text-[11px] mt-0.5">{lead['status_text']}</div>
            </div>
            <span class="text-[10px] text-gray-400 font-mono">{lead['updated_at']}</span>
        </div>"""
        
        if lead['is_final_link'] == 1:
            continue
        elif "отказ" in st_text or "игнор" in st_text:
            queue_refusal += card
        elif "ссылк" in st_text or "ожидание" in st_text and ("ч." in st_text or "мин" in st_text or "сек" in st_text or lead['timer_sec'] > 0):
            queue_waiting += card
        else:
            queue_first += card

    # Раздел 4: Статистика по дням
    stats_rows = ""
    for row in bot_stats_days:
        stats_rows += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-3 mb-2 text-xs flex justify-between items-center">
            <span class="font-mono text-gray-300 font-bold">{row['d']}</span>
            <div class="flex gap-4">
                <span class="text-emerald-400">👤 Лидов: <b>{row['cnt']}</b></span>
                <span class="text-purple-400">🔗 Ссылок: <b>{row['links']}</b></span>
            </div>
        </div>"""
    if not bot_stats_days:
        stats_rows = '<div class="text-center py-6 text-xs text-gray-500">Нет данных статистики</div>'

    html = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{bot_name} | Управление</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10">
        <div class="max-w-md mx-auto">
            <header class="flex justify-between items-center mb-4 pt-2">
                <a href="/" class="px-3 py-1.5 bg-gray-900 text-gray-200 rounded-xl text-xs font-semibold border border-gray-800">← Назад</a>
                <h1 class="text-base font-bold text-white">{bot_name}</h1>
                <span class="text-xs text-gray-400">{bot_group}</span>
            </header>

            <!-- ШАПКА -->
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 shadow-xl flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <img src="{avatar}" class="w-12 h-12 rounded-xl object-cover border border-emerald-500/30">
                    <div>
                        <h3 class="font-bold text-white text-sm">{owner_name}</h3>
                        <p class="text-xs text-emerald-400">{owner_username}</p>
                    </div>
                </div>
                <button onclick="openEditModal()" class="px-2.5 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-xs font-bold border border-emerald-500/30">
                    ✏️ Изменить
                </button>
            </div>

            <!-- 4 ОСНОВНЫЕ ВКЛАДКИ -->
            <div class="flex bg-gray-900 border border-gray-800 rounded-2xl p-1 mb-4 gap-1">
                <button onclick="switchSubTab('users')" id="subtab-btn-users" class="flex-1 py-2 text-center text-xs font-bold rounded-xl bg-emerald-500 text-gray-950">👥 Юзы</button>
                <button onclick="switchSubTab('logs')" id="subtab-btn-logs" class="flex-1 py-2 text-center text-xs font-semibold text-gray-400">📜 Логи</button>
                <button onclick="switchSubTab('queue')" id="subtab-btn-queue" class="flex-1 py-2 text-center text-xs font-semibold text-gray-400">⏳ Очередь</button>
                <button onclick="switchSubTab('stats')" id="subtab-btn-stats" class="flex-1 py-2 text-center text-xs font-semibold text-gray-400">📊 Стат</button>
            </div>

            <!-- 1. ЮЗЫ -->
            <div id="subtab-users">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-gray-300 mb-3">👥 Обработанные пользователи</h3>
                    {leads_rows}
                </div>
            </div>

            <!-- 2. ЛОГИ -->
            <div id="subtab-logs" class="hidden">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-gray-300 mb-3">📜 Логи действий бота</h3>
                    {logs_rows}
                </div>
            </div>

            <!-- 3. ОЧЕРЕДЬ (С МИНИ-ПОДВКЛАДКАМИ) -->
            <div id="subtab-queue" class="hidden space-y-4">
                <div class="flex bg-gray-900 border border-gray-800 rounded-xl p-1 gap-1">
                    <button onclick="switchQueueTab('waiting')" id="qbtn-waiting" class="flex-1 py-1.5 text-center text-[11px] font-bold rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">⏳ Ожидание ссылки</button>
                    <button onclick="switchQueueTab('first')" id="qbtn-first" class="flex-1 py-1.5 text-center text-[11px] font-semibold rounded-lg text-gray-400 hover:text-white">💬 1-й вопрос</button>
                    <button onclick="switchQueueTab('refusal')" id="qbtn-refusal" class="flex-1 py-1.5 text-center text-[11px] font-semibold rounded-lg text-gray-400 hover:text-white">❌ Отказы</button>
                </div>

                <div id="qsec-waiting" class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-amber-400 mb-2">⏳ Ожидают отправки ссылки</h3>
                    {queue_waiting if queue_waiting else '<div class="text-xs text-gray-500 py-4 text-center">Нет лидов в ожидании ссылки</div>'}
                </div>

                <div id="qsec-first" class="hidden bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-blue-400 mb-2">💬 Ждут ответа на 1-й вопрос</h3>
                    {queue_first if queue_first else '<div class="text-xs text-gray-500 py-4 text-center">Нет лидов</div>'}
                </div>

                <div id="qsec-refusal" class="hidden bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-red-400 mb-2">❌ Полные отказы</h3>
                    {queue_refusal if queue_refusal else '<div class="text-xs text-gray-500 py-4 text-center">Нет отказов</div>'}
                </div>
            </div>

            <!-- 4. СТАТИСТИКА -->
            <div id="subtab-stats" class="hidden">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-xl">
                    <h3 class="text-xs font-bold text-gray-300 mb-3">📊 Статистика по дням</h3>
                    {stats_rows}
                </div>
            </div>

            <!-- МОДАЛЬНОЕ ОКНО РЕДАКТИРОВАНИЯ -->
            <div id="editModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                <div class="bg-gray-900 border border-gray-800 rounded-3xl p-6 w-full max-w-sm shadow-2xl">
                    <h3 class="text-lg font-bold text-white mb-4">✏️ Редактировать бота</h3>
                    <form action="/bot/{bot_id}/update" method="POST" enctype="multipart/form-data" class="space-y-3">
                        <div>
                            <label class="block text-[11px] text-gray-400 mb-1">Название бота</label>
                            <input type="text" name="name" value="{bot_name}" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-white">
                        </div>
                        <div>
                            <label class="block text-[11px] text-gray-400 mb-1">Имя менеджера</label>
                            <input type="text" name="owner_name" value="{owner_name}" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-white">
                        </div>
                        <div>
                            <label class="block text-[11px] text-gray-400 mb-1">Юзернейм (@)</label>
                            <input type="text" name="owner_username" value="{owner_username}" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-xs text-white">
                        </div>
                        <div>
                            <label class="block text-[11px] text-gray-400 mb-1">Аватарка</label>
                            <input type="file" name="avatar" accept="image/*" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 text-xs text-gray-400">
                        </div>
                        <div class="flex gap-3 pt-2">
                            <button type="button" onclick="closeEditModal()" class="w-1/2 bg-gray-800 text-gray-300 py-2.5 rounded-xl text-xs">Отмена</button>
                            <button type="submit" class="w-1/2 bg-emerald-500 text-gray-950 font-bold py-2.5 rounded-xl text-xs">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                function switchSubTab(tab) {{
                    ['users', 'logs', 'queue', 'stats'].forEach(t => {{
                        document.getElementById('subtab-' + t).classList.add('hidden');
                        document.getElementById('subtab-btn-' + t).className = 'flex-1 py-2 text-center text-xs font-semibold text-gray-400';
                    }});
                    document.getElementById('subtab-' + tab).classList.remove('hidden');
                    document.getElementById('subtab-btn-' + tab).className = 'flex-1 py-2 text-center text-xs font-bold rounded-xl bg-emerald-500 text-gray-950';
                }}

                function switchQueueTab(q) {{
                    ['waiting', 'first', 'refusal'].forEach(item => {{
                        document.getElementById('qsec-' + item).classList.add('hidden');
                        document.getElementById('qbtn-' + item).className = 'flex-1 py-1.5 text-center text-[11px] font-semibold rounded-lg text-gray-400 hover:text-white';
                    }});
                    document.getElementById('qsec-' + q).classList.remove('hidden');
                    let activeClass = 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
                    if (q === 'first') activeClass = 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
                    if (q === 'refusal') activeClass = 'bg-red-500/20 text-red-400 border border-red-500/30';
                    document.getElementById('qbtn-' + q).className = 'flex-1 py-1.5 text-center text-[11px] font-bold rounded-lg ' + activeClass;
                }}

                function openEditModal() {{ document.getElementById('editModal').classList.remove('hidden'); document.getElementById('editModal').classList.add('flex'); }}
                function closeEditModal() {{ document.getElementById('editModal').classList.add('hidden'); document.getElementById('editModal').classList.remove('flex'); }}
            </script>
        </div>
    </body>
    </html>"""
    return HTMLResponse(content=html)

@app.post("/bot/{bot_id}/update")
async def update_bot_profile(bot_id: int, name: str = Form(...), owner_name: str = Form(...), owner_username: str = Form(...), avatar: UploadFile = File(None)):
    conn = get_db()
    cursor = conn.cursor()
    
    avatar_path = None
    if avatar and avatar.filename:
        os.makedirs("static/avatars", exist_ok=True)
        filename = f"bot_{bot_id}_{avatar.filename}"
        real_path = f"static/avatars/{filename}"
        with open(real_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        avatar_path = f"/static/avatars/{filename}"

    if avatar_path:
        cursor.execute("UPDATE bots SET name = ?, owner_name = ?, owner_username = ?, owner_avatar = ? WHERE id = ?", (name, owner_name, owner_username, avatar_path, bot_id))
    else:
        cursor.execute("UPDATE bots SET name = ?, owner_name = ?, owner_username = ? WHERE id = ?", (name, owner_name, owner_username, bot_id))
        
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/bot/{bot_id}", status_code=303)
