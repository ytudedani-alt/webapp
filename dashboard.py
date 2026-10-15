from fastapi import FastAPI, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import sqlite3
import os
import aiohttp
from datetime import datetime, timedelta

app = FastAPI(title="Alex Advanced Bot Control Center")

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
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessConnection, LinkPreviewOptions
from aiohttp import web
import aiohttp

BOT_TOKEN = "TOKEN_PLACEHOLDER"
print("Bot initialized")'''

    default_bots = [
        ("Alex Bot 1", "8636464152:AAG_PzFg2JUqn6N0mPVrtbv574rXlIuwv6g", "Alex Group", full_code_alex, "@alex_acc_1", "Alex Manager 1"),
        ("Alex Bot 2", "8989087015:AAHAkK_e-fcIQFLkrfQgs4-ZhrKXcJft1G4", "Alex Group", full_code_alex, "@alex_acc_2", "Alex Manager 2"),
        ("Spanh Bot 1", "8902861284:AAEUL5DImSMqKSYKWdJ_uqlbYdKgBfF9Bq4", "Spanh Group", full_code_alex, "@spanh_acc_1", "Spanh Manager 1"),
        ("Spanh Bot 2", "8833046723:AAG_el4XirqdoMZLVcZdNWypVzanJkETGnY", "Spanh Group", full_code_alex, "@spanh_acc_2", "Spanh Manager 2"),
        ("Flash Manager Bot", "8586984485:AAE4m73JZGf3s5yfExriJP_C-otyiAWZu8I", "Общие", full_code_alex, "@flash_meneger", "Flash Meneger")
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

@app.get("/login", response_class=HTMLResponse)
async def login_page(response: Response, error: str = None):
    err_html = f'<div class="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs text-center mb-4">{error}</div>' if error else ''
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>GOGOha Center | Авторизация</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{
                background-color: #030712;
                overflow: hidden;
            }}
            canvas {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                pointer-events: none;
            }}
            .login-container {{
                position: relative;
                z-index: 10;
            }}
        </style>
    </head>
    <body class="text-gray-100 min-h-screen flex items-center justify-center p-4 select-none">
        
        <canvas id="particleCanvas"></canvas>

        <div class="absolute inset-0 pointer-events-none overflow-hidden z-0">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px]"></div>
        </div>

        <div class="login-container bg-gray-900/85 backdrop-blur-2xl border border-gray-800/80 rounded-3xl p-8 w-full max-w-sm shadow-2xl shadow-emerald-950/20">
            <div class="text-center mb-6">
                <div class="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl mx-auto flex items-center justify-center text-2xl mb-3 shadow-lg shadow-emerald-500/10">
                    ⚡
                </div>
                <h1 class="text-xl font-bold text-white mb-1">Добро пожаловать</h1>
                <p class="text-xs text-gray-400">Панель управления трафиком</p>
            </div>
            {err_html}
            <form action="/login" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Логин</label>
                    <input type="text" name="username" required placeholder="Введите логин" class="w-full bg-gray-950/80 border border-gray-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500 transition">
                </div>
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Пароль</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full bg-gray-950/80 border border-gray-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500 transition">
                </div>
                <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold py-3 rounded-xl text-sm shadow-lg shadow-emerald-500/20 transition transform active:scale-95">Войти в кабинет</button>
            </form>
        </div>

        <script>
            const canvas = document.getElementById('particleCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }}
            window.addEventListener('resize', resize);
            resize();

            const particles = [];
            const count = 1200;
            let angle = 0;

            for (let i = 0; i < count; i++) {{
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos((Math.random() * 2) - 1);
                particles.push({{
                    theta: theta,
                    phi: phi,
                    radius: 130 + Math.random() * 20
                }});
            }}

            const rings = [];
            for (let i = 0; i < 3; i++) {{
                rings.push({{
                    radiusX: 220 + i * 50,
                    radiusY: 70 + i * 20,
                    tilt: 0.3 + i * 0.2,
                    speed: 0.005 + i * 0.002
                }});
            }}

            function animate() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const cx = canvas.width / 2;
                const cy = canvas.height / 2 + 50;

                angle += 0.008;

                ctx.fillStyle = 'rgba(52, 211, 153, 0.6)';
                particles.forEach(p => {{
                    const currentTheta = p.theta + angle;
                    const x = p.radius * Math.sin(p.phi) * Math.cos(currentTheta);
                    const y = p.radius * Math.sin(p.phi) * Math.sin(currentTheta);
                    const z = p.radius * Math.cos(p.phi);

                    const rotX = x;
                    const rotY = y * Math.cos(0.4) - z * Math.sin(0.4);
                    const rotZ = y * Math.sin(0.4) + z * Math.cos(0.4);

                    const scale = 300 / (300 + rotZ);
                    const px = cx + rotX * scale;
                    const py = cy + rotY * scale;

                    if (rotZ > -200) {{
                        const size = Math.max(1, scale * 1.5);
                        ctx.globalAlpha = Math.min(1, (rotZ + 200) / 250);
                        ctx.fillRect(px, py, size, size);
                    }}
                }});

                rings.forEach(ring => {{
                    ctx.strokeStyle = 'rgba(52, 211, 153, 0.25)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    for (let a = 0; a < Math.PI * 2; a += 0.05) {{
                        const rx = Math.cos(a) * ring.radiusX;
                        const ry = Math.sin(a) * ring.radiusY;
                        
                        const rotX = rx * Math.cos(angle * ring.speed * 10) - ry * Math.sin(angle * ring.speed * 10);
                        const rotY = (rx * Math.sin(angle * ring.speed * 10) + ry * Math.cos(angle * ring.speed * 10)) * Math.cos(ring.tilt);

                        const px = cx + rotX;
                        const py = cy + rotY;

                        if (a === 0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }}
                    ctx.stroke();
                }});

                requestAnimationFrame(animate);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    res = HTMLResponse(content=html)
    # Сбрасываем старые куки при каждом переходе на логин
    res.delete_cookie("auth_token")
    res.delete_cookie("gogoha_strict_session")
    return res

@app.post("/login")
async def login_post(username: str = Form(...), password: str = Form(...)):
    if username == "Gogoha" and password == "05056978":
        response = RedirectResponse(url="/", status_code=303)
        # Сохраняем сессию на 15 минут
        response.set_cookie(key="gogoha_strict_session", value="active_valid_session", max_age=900, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Неверный логин или пароль", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("gogoha_strict_session")
    response.delete_cookie("auth_token")
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)

    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token, group_name FROM bots")
    bots = cursor.fetchall()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*), SUM(is_final_link) FROM bot_logs WHERE date(updated_at) = ?", (today_str,))
    today_stats = cursor.fetchone()
    total_today = today_stats[0] or 0
    links_today = today_stats[1] or 0

    chart_labels = []
    chart_messages = []
    chart_links = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        d_label = (datetime.now() - timedelta(days=i)).strftime("%d.%m")
        chart_labels.append(d_label)
        cursor.execute("SELECT COUNT(*), SUM(is_final_link) FROM bot_logs WHERE date(updated_at) = ?", (d,))
        res = cursor.fetchone()
        chart_messages.append(res[0] or 0)
        chart_links.append(res[1] or 0)

    groups = {}
    for bot_id, name, token, group in bots:
        if group not in groups:
            groups[group] = []
        groups[group].append((bot_id, name, token))
        
    conn.close()

    groups_html = ""
    for group_name, g_bots in groups.items():
        bots_cards = ""
        for b_id, b_name, b_token in g_bots:
            remove_btn = f"""
            <form action="/remove-from-group" method="POST" class="inline">
                <input type="hidden" name="bot_id" value="{b_id}">
                <button type="submit" class="text-xs text-gray-500 hover:text-red-400 p-1" title="Убрать из папки">❌</button>
            </form>
            """ if group_name != "Общие" else ""

            bots_cards += f"""
            <div class="bg-gray-900 border border-gray-800 hover:border-emerald-500/50 rounded-2xl p-4 shadow-lg mb-3 transition flex justify-between items-center">
                <a href="/bot/{b_id}" class="flex-grow">
                    <div class="flex justify-between items-start mb-1">
                        <h3 class="font-semibold text-emerald-400">🤖 {b_name}</h3>
                        <span class="text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded-lg">Активен</span>
                    </div>
                    <p class="text-xs text-gray-500 font-mono truncate">Token: {b_token[:10]}...</p>
                </a>
                <div class="ml-3">{remove_btn}</div>
            </div>
            """
        
        action_buttons = f"""
        <div class="flex items-center gap-1">
            <button onclick="openAddModalToGroup('{group_name}')" class="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-lg font-bold" title="Добавить бота">+</button>
            <form action="/delete-group" method="POST" onsubmit="return confirm('Удалить папку {group_name}?');" class="inline">
                <input type="hidden" name="group_name" value="{group_name}">
                <button type="submit" class="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-lg" title="Удалить">🗑</button>
            </form>
        </div>
        """ if group_name != "Общие" else ""

        groups_html += f"""
        <div class="mb-6">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                    <span class="text-sm font-bold text-gray-300">📁 {group_name}</span>
                    <span class="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">{len(g_bots)}</span>
                </div>
                {action_buttons}
            </div>
            {bots_cards}
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Панель управления</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#030712">
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
                    <button onclick="openGroupModal()" class="px-2.5 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl text-xs font-semibold border border-gray-700">+ Группа</button>
                    <button onclick="openModal()" class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold rounded-xl text-xs shadow-lg shadow-emerald-500/20">+ Бот</button>
                </div>
            </header>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 shadow-xl">
                <h3 class="text-xs font-semibold text-gray-300 mb-3">📊 Статистика за сегодня</h3>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-950 p-3 rounded-xl border border-gray-800/80">
                        <div class="text-xs text-gray-400">Отписал лидам</div>
                        <div class="text-lg font-bold text-emerald-400">{total_today}</div>
                    </div>
                    <div class="bg-gray-950 p-3 rounded-xl border border-gray-800/80">
                        <div class="text-xs text-gray-400">Отправлено ссылок</div>
                        <div class="text-lg font-bold text-purple-400">{links_today}</div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-6 shadow-xl">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-xs font-semibold text-gray-300">📈 Динамика трафика</h3>
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
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Название</label>
                            <input type="text" name="name" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Группа / Папка</label>
                            <input type="text" id="modalGroupName" name="group_name" value="Общие" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Token</label>
                            <input type="text" name="token" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500" placeholder="123456:ABC...">
                        </div>
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
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Название группы</label>
                            <input type="text" name="group_name" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500">
                        </div>
                        <div class="flex gap-3 pt-2">
                            <button type="button" onclick="closeGroupModal()" class="w-1/2 bg-gray-800 text-gray-300 py-3 rounded-xl text-sm font-medium">Отмена</button>
                            <button type="submit" class="w-1/2 bg-emerald-500 text-gray-950 font-bold py-3 rounded-xl text-sm">Создать</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                const ctx = document.getElementById('trafficChart').getContext('2d');
                const trafficChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {chart_labels},
                        datasets: [
                            {{
                                label: 'Отписано лидам',
                                data: {chart_messages},
                                borderColor: '#34d399',
                                backgroundColor: 'rgba(52, 211, 153, 0.1)',
                                borderWidth: 2,
                                tension: 0.4,
                                pointBackgroundColor: '#34d399',
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                fill: true
                            }},
                            {{
                                label: 'Ссылки отправлены',
                                data: {chart_links},
                                borderColor: '#38bdf8',
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                tension: 0.4,
                                pointBackgroundColor: '#38bdf8',
                                pointRadius: 3,
                                fill: false
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ boxWidth: 12, font: {{ size: 10 }}, color: '#9ca3af' }} }},
                            tooltip: {{ backgroundColor: '#111827', titleFont: {{ size: 12 }}, bodyFont: {{ size: 11 }}, borderColor: '#374151', borderWidth: 1 }}
                        }},
                        scales: {{
                            x: {{ grid: {{ color: '#1f2937', display: true }}, ticks: {{ color: '#9ca3af', font: {{ size: 10 }} }} }},
                            y: {{ grid: {{ color: '#1f2937' }}, ticks: {{ color: '#9ca3af', font: {{ size: 10 }}, stepSize: 1 }} }}
                        }}
                    }}
                }});

                function openModal() {{ document.getElementById('modalGroupName').value = 'Общие'; document.getElementById('addModal').classList.remove('hidden'); document.getElementById('addModal').classList.add('flex'); }}
                function openAddModalToGroup(groupName) {{ document.getElementById('modalGroupName').value = groupName; document.getElementById('addModal').classList.remove('hidden'); document.getElementById('addModal').classList.add('flex'); }}
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

    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, token, group_name, code_content, owner_username, owner_name, owner_avatar FROM bots WHERE id = ?", (bot_id,))
    bot = cursor.fetchone()
    
    cursor.execute("SELECT lead_id, status_text, timer_sec, updated_at FROM bot_logs WHERE bot_id = ?", (bot_id,))
    logs = cursor.fetchall()
    conn.close()

    if not bot:
        return RedirectResponse(url="/", status_code=303)

    name, token, group_name, code_content, owner_username, owner_name, owner_avatar = bot
    bot_api_info = await get_bot_api_info(token)

    logs_html = ""
    for lead_id, status_text, timer_sec, updated_at in logs:
        logs_html += f"""
        <div class="bg-gray-800/40 border border-gray-700/30 rounded-xl p-3 mb-2 text-xs">
            <div class="flex justify-between text-gray-400 mb-1">
                <span>Лид ID: <b class="text-white font-mono">{lead_id}</b></span>
                <span class="text-emerald-400">⏱ {timer_sec} сек</span>
            </div>
            <p class="text-gray-200">{status_text}</p>
        </div>
        """
    if not logs:
        logs_html = "<p class='text-center text-gray-500 text-xs py-4'>Активных переписок в логах пока нет</p>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{name}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10">
        <div class="max-w-md mx-auto">
            <div class="flex items-center justify-between mb-4 pt-2">
                <a href="/" class="text-xs bg-gray-900 border border-gray-800 text-gray-300 px-3 py-1.5 rounded-xl">← Назад</a>
                <h1 class="font-bold text-base text-emerald-400">{name}</h1>
                <span class="text-xs text-gray-500">{group_name}</span>
            </div>

            <div class="bg-gradient-to-r from-emerald-950/40 to-gray-900 border border-emerald-500/20 rounded-2xl p-4 mb-4 shadow-xl">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">👥 Telegram Аккаунт & Бот</span>
                    <button onclick="toggleEditOwner()" class="text-[10px] text-emerald-400 hover:underline">Изменить аккаунт</button>
                </div>
                
                <div id="owner-display" class="flex items-center gap-3 mb-3 pb-3 border-b border-gray-800">
                    <img src="{owner_avatar}" class="w-12 h-12 rounded-full border-2 border-emerald-500/40 object-cover shadow-md">
                    <div class="overflow-hidden">
                        <div class="flex items-center gap-2">
                            <h2 class="text-sm font-bold text-white truncate">{owner_name}</h2>
                            <span class="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-semibold">Рассылает</span>
                        </div>
                        <p class="text-xs text-emerald-400 font-mono mt-0.5">{owner_username}</p>
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs text-gray-400">
                    <div class="flex items-center gap-2">
                        <span class="text-base">🤖</span>
                        <div>
                            <div class="text-white font-medium">{bot_api_info['name']}</div>
                            <div class="text-[11px] text-gray-500 font-mono">{bot_api_info['username']}</div>
                        </div>
                    </div>
                    <span class="text-[10px] bg-gray-800 text-gray-300 px-2 py-1 rounded-lg font-mono">Token: {token[:8]}...</span>
                </div>

                <form id="owner-form" action="/update-owner/{bot_id}" method="POST" class="hidden space-y-2 mt-2 pt-2 border-t border-gray-800">
                    <div>
                        <label class="block text-[10px] text-gray-400 mb-1">Имя аккаунта</label>
                        <input type="text" name="owner_name" value="{owner_name}" required class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-white">
                    </div>
                    <div>
                        <label class="block text-[10px] text-gray-400 mb-1">Юзернейм аккаунта (@username)</label>
                        <input type="text" name="owner_username" value="{owner_username}" required class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-white">
                    </div>
                    <div>
                        <label class="block text-[10px] text-gray-400 mb-1">Ссылка на аватарку (фото)</label>
                        <input type="text" name="owner_avatar" value="{owner_avatar}" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-white">
                    </div>
                    <div class="flex gap-2 pt-1">
                        <button type="submit" class="bg-emerald-500 text-gray-950 font-bold px-3 py-1.5 rounded-lg text-xs">Сохранить</button>
                        <button type="button" onclick="toggleEditOwner()" class="bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg text-xs">Отмена</button>
                    </div>
                </form>
            </div>

            <div class="flex bg-gray-900 p-1 rounded-2xl mb-4 border border-gray-800">
                <button onclick="switchTab('logs')" id="btn-logs" class="w-1/2 py-2 rounded-xl text-xs font-semibold bg-emerald-500 text-gray-950 font-bold transition">📊 Трафик и логи</button>
                <button onclick="trySwitchToCode()" id="btn-code" class="w-1/2 py-2 rounded-xl text-xs font-semibold text-gray-400 transition">💻 Редактор кода</button>
            </div>

            <div id="tab-logs" class="space-y-3">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-lg">
                    <h3 class="text-xs font-semibold text-gray-300 mb-3 uppercase tracking-wider">👥 Текущие переписки и таймеры</h3>
                    {logs_html}
                </div>
            </div>

            <div id="tab-code" class="hidden">
                <form action="/save-code/{bot_id}" method="POST" onsubmit="return confirmSave();" class="space-y-3">
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-lg">
                        <label class="block text-xs text-gray-400 mb-2">Полный исходный код бота (Python / Aiogram)</label>
                        <textarea name="code_content" class="w-full h-96 bg-gray-950 border border-gray-800 rounded-xl p-3 text-xs font-mono text-emerald-400 focus:outline-none focus:border-emerald-500 leading-relaxed overflow-y-auto">{code_content}</textarea>
                    </div>
                    <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold py-3 rounded-xl text-sm shadow-lg shadow-emerald-500/20">💾 Сохранить и применить код</button>
                </form>
            </div>

            <script>
                function toggleEditOwner() {{
                    const display = document.getElementById('owner-display');
                    const form = document.getElementById('owner-form');
                    if (form.classList.contains('hidden')) {{
                        form.classList.remove('hidden');
                        display.classList.add('hidden');
                    }} else {{
                        form.classList.add('hidden');
                        display.classList.remove('hidden');
                    }}
                }}

                function trySwitchToCode() {{
                    if (confirm("Вы точно хотите редактировать код?")) {{
                        document.getElementById('tab-code').classList.remove('hidden');
                        document.getElementById('tab-logs').classList.add('hidden');
                        document.getElementById('btn-code').className = 'w-1/2 py-2 rounded-xl text-xs font-semibold bg-emerald-500 text-gray-950 font-bold transition';
                        document.getElementById('btn-logs').className = 'w-1/2 py-2 rounded-xl text-xs font-semibold text-gray-400 transition';
                    }}
                }}

                function confirmSave() {{
                    return confirm("Вы точно хотите сохранить изменения в коде?");
                }}

                function switchTab(tab) {{
                    if (tab === 'logs') {{
                        document.getElementById('tab-logs').classList.remove('hidden');
                        document.getElementById('tab-code').classList.add('hidden');
                        document.getElementById('btn-logs').className = 'w-1/2 py-2 rounded-xl text-xs font-semibold bg-emerald-500 text-gray-950 font-bold transition';
                        document.getElementById('btn-code').className = 'w-1/2 py-2 rounded-xl text-xs font-semibold text-gray-400 transition';
                    }}
                }}
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/update-owner/{bot_id}")
async def update_owner(bot_id: int, owner_name: str = Form(...), owner_username: str = Form(...), owner_avatar: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET owner_name = ?, owner_username = ?, owner_avatar = ? WHERE id = ?", 
                   (owner_name.strip(), owner_username.strip(), owner_avatar.strip(), bot_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/bot/{bot_id}", status_code=303)

@app.post("/add-bot")
async def add_bot(name: str = Form(...), token: str = Form(...), group_name: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bots (name, token, group_name, code_content, owner_username, owner_name) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, token.strip(), group_name.strip(), '# Новый бот\nprint("Started")', '@new_acc', 'New Manager'))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/add-group")
async def add_group(group_name: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-group")
async def delete_group(group_name: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET group_name = 'Общие' WHERE group_name = ?", (group_name,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/remove-from-group")
async def remove_from_group(bot_id: int = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET group_name = 'Общие' WHERE id = ?", (bot_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/save-code/{bot_id}")
async def save_code(bot_id: int, code_content: str = Form(...), gogoha_strict_session: str = Cookie(None)):
    if gogoha_strict_session != "active_valid_session":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET code_content = ? WHERE id = ?", (code_content, bot_id))
    cursor.execute("INSERT INTO bot_logs (bot_id, lead_id, status_text, timer_sec, is_final_link) VALUES (?, ?, ?, ?, ?)", 
                   (bot_id, "SYSTEM", "Код успешно обновлен через Web IDE. Бот переведен в рабочий режим.", 0, 0))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/bot/{bot_id}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
