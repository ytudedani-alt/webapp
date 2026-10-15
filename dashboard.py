from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import sqlite3
import os

app = FastAPI(title="Alex Multi-Bot Dashboard")

def init_dashboard_db():
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            token TEXT UNIQUE
        )
    """)
    conn.commit()

    # Автоматически добавляем все 5 твоих рабочих ботов
    default_bots = [
        ("Alex Bot 1", "8636464152:AAG_PzFg2JUqn6N0mPVrtbv574rXlIuwv6g"),
        ("Alex Bot 2", "8989087015:AAHAkK_e-fcIQFLkrfQgs4-ZhrKXcJft1G4"),
        ("Spanh Bot 1", "8902861284:AAEUL5DImSMqKSYKWdJ_uqlbYdKgBfF9Bq4"),
        ("Spanh Bot 2", "8833046723:AAG_el4XirqdoMZLVcZdNWypVzanJkETGnY"),
        ("Flash Manager Bot", "8586984485:AAE4m73JZGf3s5yfExriJP_C-otyiAWZu8I")
    ]
    for name, token in default_bots:
        try:
            cursor.execute("INSERT OR IGNORE INTO bots (name, token) VALUES (?, ?)", (name, token))
        except Exception:
            pass
            
    conn.commit()
    conn.close()

init_dashboard_db()

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "Alex Bots Control",
        "short_name": "Bots",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#030712",
        "theme_color": "#030712",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/6134/6134346.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = sqlite3.connect("dashboard_bots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token FROM bots")
    bots = cursor.fetchall()
    conn.close()

    bots_html = ""
    for bot_id, name, token in bots:
        bots_html += f"""
        <div class="bg-gray-900 border border-gray-800 rounded-2xl p-4 shadow-lg mb-3">
            <div class="flex justify-between items-start mb-2">
                <h2 class="font-semibold text-blue-400">🤖 {name}</h2>
                <span class="text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded-lg">Активен</span>
            </div>
            <p class="text-xs text-gray-400 font-mono truncate mb-2">Token: {token[:10]}...</p>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Управление ботами</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="theme-color" content="#030712">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen p-4 pb-10 select-none">
        <div class="max-w-md mx-auto">
            <header class="flex justify-between items-center mb-6 pt-2">
                <div>
                    <h1 class="text-xl font-bold text-white">📱 Мои Боты</h1>
                    <p class="text-xs text-gray-400">Центр управления аккаунтами ({len(bots)} шт.)</p>
                </div>
                <button onclick="openModal()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/30 flex items-center gap-1">
                    + Добавить
                </button>
            </header>

            <div class="space-y-3 mb-6">
                {bots_html}
            </div>

            <div id="addModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                <div class="bg-gray-900 border border-gray-800 rounded-3xl p-6 w-full max-w-sm shadow-2xl">
                    <h3 class="text-lg font-bold text-white mb-4">➕ Новый бот / аккаунт</h3>
                    <form action="/add-bot" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Название (например, Бот 6)</label>
                            <input type="text" name="name" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-blue-500">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Telegram Bot Token</label>
                            <input type="text" name="token" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-blue-500" placeholder="123456:ABC-DEF...">
                        </div>
                        <div class="flex gap-3 pt-2">
                            <button type="button" onclick="closeModal()" class="w-1/2 bg-gray-800 hover:bg-gray-700 text-gray-300 py-3 rounded-xl text-sm font-medium">Отмена</button>
                            <button type="submit" class="w-1/2 bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl text-sm font-medium shadow-lg shadow-blue-600/30">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                function openModal() {{
                    document.getElementById('addModal').classList.remove('hidden');
                    document.getElementById('addModal').classList.add('flex');
                }}
                function closeModal() {{
                    document.getElementById('addModal').classList.add('hidden');
                    document.getElementById('addModal').classList.remove('flex');
                }}
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/add-bot")
async def add_bot(name: str = Form(...), token: str = Form(...)):
    try:
        conn = sqlite3.connect("dashboard_bots.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bots (name, token) VALUES (?, ?)", (name, token.strip()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка добавления: {e}")
    
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
