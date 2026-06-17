import os
import json
from fastapi import FastAPI, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

DB_FILE = "database.json"

ADMIN_USERNAME = "admin"
ADMIN_PIN = "7777"

DEFAULT_DATA = {
    "citizens": {
        "1": {"name": "Маргарита", "balance": 1487, "pin": "1111", "banned": False, "history": ["Стартовый баланс: 1487 PRB"]},
        "2": {"name": "Братишкин", "balance": 1, "pin": "2222", "banned": False, "history": ["Стартовый баланс: 1 PRB"]},
        "3": {"name": "—", "balance": 0, "pin": "3333", "banned": False, "history": []},
        "4": {"name": "—", "balance": 0, "pin": "4444", "banned": False, "history": []},
        "5": {"name": "—", "balance": 0, "pin": "5555", "banned": False, "history": []},
        "6": {"name": "—", "balance": 0, "pin": "6666", "banned": False, "history": []},
        "7": {"name": "—", "balance": 0, "pin": "7778", "banned": False, "history": []},
        "8": {"name": "—", "balance": 0, "pin": "8888", "banned": False, "history": []},
        "9": {"name": "—", "balance": 0, "pin": "9999", "banned": False, "history": []},
        "10": {"name": "—", "balance": 0, "pin": "1010", "banned": False, "history": []},
        "11": {"name": "—", "balance": 0, "pin": "1112", "banned": False, "history": []},
        "12": {"name": "—", "balance": 0, "pin": "1212", "banned": False, "history": []},
        "13": {"name": "—", "balance": 0, "pin": "1313", "banned": False, "history": []},
        "14": {"name": "—", "balance": 0, "pin": "1414", "banned": False, "history": []},
        "15": {"name": "—", "balance": 0, "pin": "1515", "banned": False, "history": []}
    },
    "global_logs": ["База данных успешно инициализирована."]
}

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
        return DEFAULT_DATA
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if "citizens" not in data:
                return DEFAULT_DATA
            # Проверяем наличие параметра banned у пользователей
            updated = False
            for cid, cdata in data["citizens"].items():
                if "banned" not in cdata:
                    cdata["banned"] = False
                    updated = True
            if updated:
                save_db(data)
            return data
        except:
            return DEFAULT_DATA

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ================= ВХОД ДЛЯ ГРАЖДАН =================
@app.get("/", response_class=HTMLResponse)
def citizen_login_view(error: str = None):
    db = load_db()
    options = "".join([f'<option value="{cid}">{data["name"]} (ID: {cid})</option>' for cid, data in db["citizens"].items()])
    error_msg = f'<p style="color: #f43f5e; font-size: 0.9rem;">{error}</p>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZET БАНК</title>
        <style>
            body {{ background: linear-gradient(135deg, #0b0f19, #1a102f); color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 40px; max-width: 400px; width: 100%; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
            h1 {{ background: linear-gradient(90deg, #eab308, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 20px 0; font-size: 2.2rem; font-weight: 900; letter-spacing: 1px; }}
            select, input, button {{ width: 100%; padding: 14px; margin-top: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); font-size: 1rem; box-sizing: border-box; }}
            select, input {{ background: #000; color: white; }}
            button {{ background: linear-gradient(90deg, #eab308, #a855f7); color: white; border: none; font-weight: bold; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>ZET БАНК</h1>
            <p style="color: #94a3b8; font-size: 0.9rem;">Новое поколение цифровых рублей (PRB)</p>
            {error_msg}
            <form action="/login" method="post">
                <select name="citizen_id">
                    {options}
                </select>
                <input type="password" name="pin" placeholder="Введите PIN-код" maxlength="4" required>
                <button type="submit">Войти в систему</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login_process(citizen_id: str = Form(...), pin: str = Form(...)):
    db = load_db()
    if citizen_id in db["citizens"]:
        user = db["citizens"][citizen_id]
        if user["pin"] == pin:
            if user.get("banned", False):
                return RedirectResponse(url="/?error=Ваш аккаунт заблокирован!", status_code=303)
            return RedirectResponse(url=f"/cabinet?citizen_id={citizen_id}", status_code=303)
    return RedirectResponse(url="/?error=Неверный PIN-код!", status_code=303)

# ================= ЛИЧНЫЙ КАБИНЕТ ГРАЖДАН =================
@app.get("/cabinet", response_class=HTMLResponse)
def citizen_cabinet(citizen_id: str, error: str = None, success: str = None):
    db = load_db()
    if citizen_id not in db["citizens"]:
        return RedirectResponse(url="/")
    user = db["citizens"][citizen_id]
    if user.get("banned", False):
        return RedirectResponse(url="/?error=Ваш аккаунт заблокирован!", status_code=303)
    
    search_users = []
    for cid, data in db["citizens"].items():
        if cid != citizen_id and not data.get("banned", False):
            search_users.append({"id": cid, "name": data["name"]})
    search_users_json = json.dumps(search_users, ensure_ascii=False)

    history_rows = "".join([f"<li>{h}</li>" for h in reversed(user["history"])])
    if not history_rows:
        history_rows = "<li style='color: #64748b;'>Транзакций нет.</li>"
    status_msg = f'<p style="color: #f43f5e;">{error}</p>' if error else (f'<p style="color: #4ade80;">{success}</p>' if success else '')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZET Кабинет</title>
        <style>
            body {{ background: linear-gradient(135deg, #0b0f19, #1a102f); color: #f8fafc; font-family: sans-serif; padding: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }}
            .box {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 30px; max-width: 450px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
            .balance-card {{ background: rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; text-align: center; margin: 20px 0; border: 1px solid rgba(255,255,255,0.1); }}
            .amount {{ font-size: 2.5rem; font-weight: bold; color: #eab308; }}
            input, button {{ width: 100%; padding: 12px; margin-top: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #000; color: #fff; box-sizing: border-box; }}
            button {{ background: linear-gradient(90deg, #a855f7, #eab308); font-weight: bold; cursor: pointer; border: none; }}
            ul {{ list-style: none; padding: 0; max-height: 200px; overflow-y: auto; }}
            li {{ background: rgba(255,255,255,0.05); padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9rem; border-left: 4px solid #eab308; }}
            .back-link {{ display: block; text-align: center; color: #64748b; text-decoration: none; margin-top: 20px; }}
            
            .search-results {{ background: #000; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; max-height: 150px; overflow-y: auto; margin-top: 5px; display: none; padding: 0; list-style: none; text-align: left; }}
            .search-item {{ padding: 10px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.95rem; }}
            .search-item:hover {{ background: rgba(255,255,255,0.1); color: #eab308; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Салют, {user['name']}!</h2>
            {status_msg}
            <div class="balance-card">
                <div style="color: #94a3b8; font-size: 0.9rem;">Доступно средств:</div>
                <div class="amount">{user['balance']} PRB</div>
            </div>
            
            <h3>Перевод средств (Поиск получателя):</h3>
            <form action="/transfer" method="post" id="transferForm">
                <input type="hidden" name="sender_id" value="{citizen_id}">
                <input type="hidden" name="receiver_id" id="receiver_id" required>
                
                <input type="text" id="search_input" placeholder="Начните вводить имя получателя..." autocomplete="off" required>
                <ul class="search-results" id="search_results"></ul>
                
                <input type="number" name="amount" placeholder="Сумма в PRB" min="1" required>
                <button type="submit" id="submit_btn" style="opacity: 0.6; cursor: not-allowed;" disabled>Выберите получателя из поиска</button>
            </form>
            <a href="/" class="back-link">Выйти из системы</a>
        </div>
        
        <div class="box">
            <h3>История ZET-операций:</h3>
            <ul>{history_rows}</ul>
        </div>

        <script>
            const users = {search_users_json};
            const searchInput = document.getElementById('search_input');
            const searchResults = document.getElementById('search_results');
            const receiverIdInput = document.getElementById('receiver_id');
            const submitBtn = document.getElementById('submit_btn');

            searchInput.addEventListener('input', function() {{
                const query = this.value.toLowerCase().trim();
                searchResults.innerHTML = '';
                
                receiverIdInput.value = '';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.6';
                submitBtn.innerText = 'Выберите получателя из поиска';

                if (!query) {{
                    searchResults.style.display = 'none';
                    return;
                }}

                const filtered = users.filter(user => user.name.toLowerCase().includes(query));

                if (filtered.length > 0) {{
                    filtered.forEach(user => {{
                        const li = document.createElement('li');
                        li.className = 'search-item';
                        li.innerText = user.name;
                        li.addEventListener('click', function() {{
                            searchInput.value = user.name;
                            receiverIdInput.value = user.id;
                            searchResults.style.display = 'none';
                            
                            submitBtn.disabled = false;
                            submitBtn.style.opacity = '1';
                            submitBtn.style.cursor = 'pointer';
                            submitBtn.innerText = 'Перевести мгновенно';
                        }});
                        searchResults.appendChild(li);
                    }});
                    searchResults.style.display = 'block';
                }} else {{
                    const li = document.createElement('li');
                    li.className = 'search-item';
                    li.style.color = '#64748b';
                    li.style.cursor = 'default';
                    li.innerText = 'Никого не найдено';
                    searchResults.appendChild(li);
                    searchResults.style.display = 'block';
                }}
            }});

            document.addEventListener('click', function(e) {{
                if (e.target !== searchInput && e.target !== searchResults) {{
                    searchResults.style.display = 'none';
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.post("/transfer")
def process_transfer(sender_id: str = Form(...), receiver_id: str = Form(...), amount: int = Form(...)):
    db = load_db()
    if sender_id not in db["citizens"] or receiver_id not in db["citizens"]:
        return RedirectResponse(url="/", status_code=303)
    sender = db["citizens"][sender_id]
    receiver = db["citizens"][receiver_id]
    if sender.get("banned", False) or receiver.get("banned", False):
        return RedirectResponse(url=f"/cabinet?citizen_id={sender_id}&error=Операция заблокирована!", status_code=303)
    if sender["balance"] < amount:
        return RedirectResponse(url=f"/cabinet?citizen_id={sender_id}&error=Недостаточно PRB!", status_code=303)
    sender["balance"] -= amount
    receiver["balance"] += amount
    sender["history"].append(f"Перевод: -{amount} PRB для {receiver['name']}")
    receiver["history"].append(f"Получено: +{amount} PRB от {sender['name']}")
    db["global_logs"].append(f"{sender['name']} перевел {amount} PRB для {receiver['name']}")
    save_db(db)
    return RedirectResponse(url=f"/cabinet?citizen_id={sender_id}&success=Успешно отправлено!", status_code=303)


# ================= ПАНЕЛЬ ПРАВИТЕЛЯ (АДМИНКА) =================
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(error: str = None, success: str = None, ruler_session: str = Cookie(None)):
    if ruler_session == "ruler_authenticated_secret_token":
        db = load_db()
        rows = ""
        for cid, data in db["citizens"].items():
            status_text = "РАЗБАНЕН" if data.get("banned", False) else "ЗАБАНЕН"
            btn_color = "#10b981" if data.get("banned", False) else "#ef4444"
            status_badge = "<span style='color:#ef4444; font-weight:bold;'>БАН</span>" if data.get("banned", False) else "<span style='color:#10b981; font-weight:bold;'>АКТИВЕН</span>"
            
            rows += f"""
            <tr>
                <td>ID: {cid}</td>
                <td>
                    <form action="/admin/rename" method="post" style="display:inline-flex; gap:5px; margin:0;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <input type="text" name="new_name" value="{data['name']}" style="width: 120px; padding: 4px; background:#000; color:#fff; border:1px solid #333; border-radius:4px;">
                        <button type="submit" style="background:#4b5563; color:white; padding:4px 8px; border:none; border-radius:4px; cursor:pointer;">Сохранить</button>
                    </form>
                </td>
                <td style="color: #a855f7; font-weight: bold;">{data['pin']}</td>
                <td style="color: #eab308; font-weight: bold;">{data['balance']} PRB</td>
                <td>{status_badge}</td>
                <td>
                    <form action="/admin-action" method="post" style="display: inline-flex; gap: 5px; margin-bottom: 5px;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <input type="number" name="amount" placeholder="Сумма" style="width: 70px; padding: 6px; border-radius: 6px; border: 1px solid #333; background: #000; color: #fff;" required>
                        <input type="text" name="reason" placeholder="Причина" style="width: 100px; padding: 6px; border-radius: 6px; border: 1px solid #333; background: #000; color: #fff;" required>
                        <button type="submit" name="action" value="charge" style="background: #ef4444; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer;">Списать</button>
                        <button type="submit" name="action" value="give" style="background: #10b981; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer;">Начислить</button>
                    </form>
                    <br>
                    <form action="/change-pin" method="post" style="display: inline-flex; gap: 5px; margin-bottom: 5px;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <input type="text" name="new_pin" placeholder="Новый PIN" maxlength="4" style="width: 90px; padding: 6px; border-radius: 6px; border: 1px solid #444; background: #111; color: #fff;" required>
                        <button type="submit" style="background: #a855f7; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer;">Сменить PIN</button>
                    </form>
                    <form action="/admin/ban" method="post" style="display: inline-block; margin-left:5px;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <button type="submit" style="background: {btn_color}; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer;">{status_text}</button>
                    </form>
                </td>
            </tr>
            """
        log_rows = "".join([f"<li>{log}</li>" for log in reversed(db["global_logs"])])
        if not log_rows:
            log_rows = "<li style='color:#64748b;'>В системе тихо.</li>"

        status_top = f'<p style="color: #ef4444;">{error}</p>' if error else (f'<p style="color: #10b981;">{success}</p>' if success else '')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Управление ZET БАНК</title>
            <style>
                body {{ background: linear-gradient(135deg, #090d16, #111827); color: #f8fafc; font-family: sans-serif; padding: 40px; display: flex; flex-direction: column; align-items: center; gap: 30px; }}
                .panel {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 35px; max-width: 1100px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
                h1 {{ background: linear-gradient(90deg, #eab308, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }}
                th {{ color: #64748b; font-size: 0.85rem; text-transform: uppercase; }}
                ul {{ list-style: none; padding: 0; max-height: 250px; overflow-y: auto; }}
                li {{ background: rgba(0,0,0,0.3); padding: 10px; margin-bottom: 5px; border-radius: 6px; font-size: 0.9rem; border-left: 4px solid #eab308; }}
                .logout {{ float: right; background: #334155; color: white; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 0.9rem; font-weight: bold; }}
                .add-form input {{ padding: 10px; margin-right: 10px; border-radius: 6px; background:#000; color:#fff; border:1px solid #333; }}
            </style>
        </head>
        <body>
            <div class="panel">
                <a href="/admin-logout" class="logout">Выйти</a>
                <h1>ЦЕНТРАЛЬНЫЙ ОФИС ZET БАНК</h1>
                {status_top}
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Имя / Изменить</th>
                            <th>Текущий PIN</th>
                            <th>Баланс ZET-капитала</th>
                            <th>Статус</th>
                            <th>Действия Правителя</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                
                <div style="margin-top:25px; padding:20px; background:rgba(255,255,255,0.01); border-radius:12px; border:1px dashed #333;">
                    <h3>Добавить нового человека в базу</h3>
                    <form action="/admin/add-user" method="post" class="add-form">
                        <input type="text" name="name" placeholder="Имя жителя" required>
                        <input type="text" name="pin" placeholder="PIN (4 цифры)" maxlength="4" required>
                        <input type="number" name="balance" placeholder="Стартовый баланс" value="0" required>
                        <button type="submit" style="background:#10b981; color:white; padding:10px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Создать аккаунт</button>
                    </form>
                </div>
            </div>
            <div class="panel">
                <h2>МОНИТОРИНГ ZET-СИСТЕМЫ</h2>
                <ul>{log_rows}</ul>
            </div>
        </body>
        </html>
        """
    
    error_msg = f'<p style="color: #f43f5e; font-weight: bold;">{error}</p>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ZET Администрация</title>
        <style>
            body {{ background: #090514; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .login-box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.7); }}
            h2 {{ color: #eab308; margin-bottom: 20px; }}
            input, button {{ width: 100%; padding: 12px; margin-top: 15px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff; box-sizing: border-box; }}
            button {{ background: #eab308; color: #000; font-weight: bold; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Вход для Руководства ZET</h2>
            {error_msg}
            <form action="/admin-login" method="post">
                <input type="text" name="username" placeholder="Логин" required>
                <input type="password" name="pin" placeholder="PIN-код доступа" required>
                <button type="submit">Войти в панель</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/admin-login")
def admin_login_process(username: str = Form(...), pin: str = Form(...)):
    if username == ADMIN_USERNAME and pin == ADMIN_PIN:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="ruler_session", value="ruler_authenticated_secret_token", httponly=True)
        return response
    return RedirectResponse(url="/admin?error=Неверные данные доступа.", status_code=303)

@app.get("/admin-logout")
def admin_logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("ruler_session")
    return response

@app.post("/admin/rename")
def admin_rename_process(citizen_id: str = Form(...), new_name: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        old_name = db["citizens"][citizen_id]["name"]
        db["citizens"][citizen_id]["name"] = new_name
        db["global_logs"].append(f"Имя ID {citizen_id} изменено с {old_name} на {new_name}")
        save_db(db)
        return RedirectResponse(url="/admin?success=Имя успешно обновлено!", status_code=303)
    return RedirectResponse(url="/admin?error=Пользователь не найден.", status_code=303)

@app.post("/admin/ban")
def admin_ban_process(citizen_id: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        curr = db["citizens"][citizen_id].get("banned", False)
        db["citizens"][citizen_id]["banned"] = not curr
        status_txt = "заблокирован" if not curr else "разблокирован"
        db["global_logs"].append(f"Пользователь {db['citizens'][citizen_id]['name']} {status_txt}")
        save_db(db)
        return RedirectResponse(url="/admin?success=Статус бана изменен!", status_code=303)
    return RedirectResponse(url="/admin?error=Пользователь не найден.", status_code=303)

@app.post("/admin/add-user")
def admin_add_user_process(name: str = Form(...), pin: str = Form(...), balance: int = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    numeric_ids = [int(x) for x in db["citizens"].keys() if x.isdigit()]
    next_id = str(max(numeric_ids) + 1) if numeric_ids else "1"
    
    db["citizens"][next_id] = {
        "name": name,
        "balance": balance,
        "pin": pin,
        "banned": False,
        "history": [f"Аккаунт создан со стартовым балансом {balance} PRB"] if balance > 0 else []
    }
    db["global_logs"].append(f"Создан новый гражданин: {name} (ID: {next_id})")
    save_db(db)
    return RedirectResponse(url="/admin?success=Новый пользователь успешно создан!", status_code=303)

@app.post("/change-pin")
def change_pin_process(citizen_id: str = Form(...), new_pin: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        user = db["citizens"][citizen_id]
        user["pin"] = new_pin
        db["global_logs"].append(f"Установлен новый PIN для {user['name']}")
        save_db(db)
    return RedirectResponse(url="/admin?success=PIN-код изменен!", status_code=303)

@app.post("/admin-action")
def admin_action_process(citizen_id: str = Form(...), amount: int = Form(...), reason: str = Form(...), action: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        user = db["citizens"][citizen_id]
        if action == "charge":
            user["balance"] -= amount
            user["history"].append(f"Списание банка: -{amount} PRB — {reason}")
            db["global_logs"].append(f"Списано у {user['name']} {amount} PRB. Причина: {reason}")
        elif action == "give":
            user["balance"] += amount
            user["history"].append(f"Начисление банка: +{amount} PRB — {reason}")
            db["global_logs"].append(f"Начислено {user['name']} {amount} PRB. Причина: {reason}")
        save_db(db)
        return RedirectResponse(url="/admin?success=Баланс успешно откорректирован!", status_code=303)
    return RedirectResponse(url="/admin?error=Пользователь не найден.", status_code=303)        color: #f8fafc;
        display: flex; justify-content: center; align-items: center;
        min-height: 100vh; padding: 20px;
    }
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 35px;
        width: 100%; max-width: 900px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    h1, h2, h3 { text-align: center; color: #fff; text-shadow: 0 2px 10px rgba(255,255,255,0.1); }
    input, select, textarea {
        width: 100%; padding: 14px; margin: 10px 0;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; color: #fff; font-size: 16px;
        transition: 0.3s;
    }
    input:focus, select:focus {
        border-color: #38bdf8; background: rgba(255, 255, 255, 0.08); outline: none;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .btn {
        width: 100%; padding: 14px; margin-top: 15px;
        background: linear-gradient(135deg, #38bdf8, #0369a1);
        border: none; border-radius: 12px; color: white;
        font-size: 16px; font-weight: 600; cursor: pointer;
        transition: 0.3s; text-transform: uppercase; letter-spacing: 1px;
    }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(56, 189, 248, 0.4); }
    .btn-danger { background: linear-gradient(135deg, #ef4444, #b91c1c); }
    .btn-danger:hover { box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4); }
    .btn-secondary { background: linear-gradient(135deg, #22c55e, #15803d); }
    .btn-secondary:hover { box-shadow: 0 8px 20px rgba(34, 197, 94, 0.4); }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 14px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
    th { background: rgba(255,255,255,0.05); color: #38bdf8; }
    tr:hover { background: rgba(255,255,255,0.02); }
    .banned-row { opacity: 0.5; background: rgba(239, 68, 68, 0.05) !important; }
    .badge { padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .badge-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .flex-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .inline-form { display: inline-flex; gap: 5px; margin: 0; width: auto; }
    .inline-form input { width: 130px; padding: 6px 10px; margin: 0; font-size: 14px; }
    .inline-form .btn { width: auto; padding: 6px 12px; margin: 0; font-size: 12px; }
</style>
"""

# Вход в банк
@app.get("/", response_class=HTMLResponse)
async def login_page(msg: str = ""):
    error_html = f"<p style='color:#ef4444; text-align:center;'>{msg}</p>" if msg else ""
    return f"""
    <html>
    <head><title>PRB Bank - Авторизация</title>{BASE_STYLE}</head>
    <body>
        <div class="glass-panel" style="max-width: 400px;">
            <h1>PRB BANK</h1>
            {error_html}
            <form action="/login" method="post">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <input type="password" name="pin" placeholder="PIN-код" required>
                <button type="submit" class="btn">Войти</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/login")
async def login(user_id: str = Form(...), pin: str = Form(...)):
    db = load_db()
    if user_id == "admin" and pin == "7777":
        return RedirectResponse(url="/admin_panel", status_code=303)
    
    if user_id in db:
        if db[user_id]["pin"] == pin:
            if db[user_id].get("banned", False):
                return RedirectResponse(url="/?msg=Ваш аккаунт заблокирован администратором!", status_code=303)
            return RedirectResponse(url=f"/cabinet/{user_id}", status_code=303)
        
    return RedirectResponse(url="/?msg=Неверный ID или PIN!", status_code=303)

# Личный кабинет
@app.get("/cabinet/{user_id}", response_class=HTMLResponse)
async def cabinet(user_id: str, msg: str = ""):
    db = load_db()
    if user_id not in db or db[user_id].get("banned", False):
        return RedirectResponse(url="/", status_code=303)
    
    user = db[user_id]
    alert_html = f"<p style='color:#4ade80; text-align:center;'>{msg}</p>" if msg else ""
    
    history_html = ""
    for op in reversed(user.get("history", [])):
        history_html += f"<tr><td>{op['type']}</td><td>{op['amount']} PRB</td><td>{op['comment']}</td></tr>"
        
    options = "".join([f'<option value="{uid}">{uid} - {u["name"]}</option>' for uid, u in db.items() if uid != user_id and not u.get("banned", False)])

    return f"""
    <html>
    <head><title>Кабинет {user['name']}</title>{BASE_STYLE}</head>
    <body>
        <div class="glass-panel">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Личный кабинет</h2>
                <a href="/" style="color:#38bdf8; text-decoration:none;">Выйти</a>
            </div>
            <hr style="border-color:rgba(255,255,255,0.05); margin:20px 0;">
            <h3>Пользователь: <span style="color:#38bdf8;">{user['name']}</span> (ID: {user_id})</h3>
            <h1 style="font-size:48px; margin:10px 0; color:#4ade80;">{user['balance']} <span style="font-size:24px; color:#fff;">PRB</span></h1>
            
            {alert_html}
            
            <h3>Перевод средств</h3>
            <form action="/transfer/{user_id}" method="post">
                <select name="to_id" required>
                    <option value="" disabled selected>Выберите получателя</option>
                    {options}
                </select>
                <input type="number" name="amount" min="1" placeholder="Сумма (PRB)" required>
                <input type="text" name="comment" placeholder="Комментарий к платежу" required>
                <button type="submit" class="btn">Отправить перевод</button>
            </form>
            
            <h3>История операций</h3>
            <table>
                <tr><th>Тип</th><th>Сумма</th><th>Комментарий</th></tr>
                {history_html if history_html else "<tr><td colspan='3' style='text-align:center;'>История пуста</td></tr>"}
            </table>
        </div>
    </body>
    </html>
    """

@app.post("/transfer/{from_id}")
async def transfer(from_id: str, to_id: str = Form(...), amount: int = Form(...), comment: str = Form(...)):
    db = load_db()
    if from_id not in db or to_id not in db:
        return RedirectResponse(url=f"/cabinet/{from_id}?msg=Ошибка системы!", status_code=303)
    
    if db[from_id].get("banned", False) or db[to_id].get("banned", False):
        return RedirectResponse(url=f"/cabinet/{from_id}?msg=Один из участников забанен!", status_code=303)
        
    if db[from_id]["balance"] < amount:
        return RedirectResponse(url=f"/cabinet/{from_id}?msg=Недостаточно средств!", status_code=303)
        
    db[from_id]["balance"] -= amount
    db[to_id]["balance"] += amount
    
    db[from_id]["history"].append({"type": f"Перевод в ID {to_id}", "amount": -amount, "comment": comment})
    db[to_id]["history"].append({"type": f"Перевод от ID {from_id}", "amount": amount, "comment": comment})
    
    save_db(db)
    return RedirectResponse(url=f"/cabinet/{from_id}?msg=Перевод успешно выполнен!", status_code=303)

# Админ-панель
@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(msg: str = ""):
    db = load_db()
    alert_html = f"<p style='color:#38bdf8; text-align:center;'>{msg}</p>" if msg else ""
    
    rows = ""
    for uid, u in db.items():
        row_class = "class='banned-row'" if u.get("banned", False) else ""
        status_badge = "<span class='badge badge-danger'>BANNED</span>" if u.get("banned", False) else "<span class='badge badge-success'>ACTIVE</span>"
        ban_btn_text = "Разбанить" if u.get("banned", False) else "Бан"
        ban_btn_class = "btn-secondary" if u.get("banned", False) else "btn-danger"
        
        rows += f"""
        <tr {row_class}>
            <td><b>{uid}</b></td>
            <td>
                <!-- Форма изменения имени -->
                <form action="/admin/rename/{uid}" method="post" class="inline-form">
                    <input type="text" name="new_name" value="{u['name']}" required>
                    <button type="submit" class="btn" style="background:#475569;">✏️</button>
                </form>
            </td>
            <td><span style="color:#4ade80; font-weight:bold;">{u['balance']} PRB</span></td>
            <td><code>{u['pin']}</code></td>
            <td>{status_badge}</td>
            <td>
                <div class="flex-actions">
                    <!-- Изменение баланса -->
                    <form action="/admin/action/{uid}" method="post" class="inline-form">
                        <input type="number" name="amount" placeholder="Сумма" style="width:70px;" required>
                        <input type="text" name="comment" placeholder="Причина" required>
                        <button type="submit" name="act" value="add" class="btn btn-secondary">+</button>
                        <button type="submit" name="act" value="sub" class="btn btn-danger">-</button>
                    </form>
                    
                    <!-- Изменение PIN -->
                    <form action="/admin/pin/{uid}" method="post" class="inline-form">
                        <input type="text" name="new_pin" placeholder="Новый PIN" style="width:85px;" required>
                        <button type="submit" class="btn" style="background:#6366f1;">PIN</button>
                    </form>
                    
                    <!-- Кнопка Бана -->
                    <form action="/admin/ban/{uid}" method="post" style="margin:0;">
                        <button type="submit" class="btn {ban_btn_class}" style="padding: 6px 12px; font-size:12px; margin:0;">{ban_btn_text}</button>
                    </form>
                </div>
            </td>
        </tr>
        """
        
    return f"""
    <html>
    <head><title>Управление Банком</title>{BASE_STYLE}</head>
    <body>
        <div class="glass-panel" style="max-width: 1100px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>👑 Панель Управления Государством</h2>
                <a href="/" style="color:#ef4444; text-decoration:none; font-weight:bold;">Выйти</a>
            </div>
            
            {alert_html}
            
            <table>
                <tr>
                    <th>ID</th>
                    <th>Имя пользователя</th>
                    <th>Баланс</th>
                    <th>PIN</th>
                    <th>Статус</th>
                    <th>Действия</th>
                </tr>
                {rows}
            </table>
            
            <div style="margin-top: 30px; background: rgba(255,255,255,0.02); padding: 20px; border-radius:16px; border: 1px dashed rgba(255,255,255,0.1);">
                <h3>➕ Добавить нового пользователя в базу</h3>
                <form action="/admin/add_user" method="post" style="display:flex; gap:15px; align-items:center;">
                    <input type="text" name="name" placeholder="Имя нового жителя" required>
                    <input type="text" name="pin" placeholder="PIN-код (4 цифры)" max_length="4" required>
                    <input type="number" name="balance" placeholder="Стартовый баланс" value="0" required>
                    <button type="submit" class="btn btn-secondary" style="margin:0; width:auto; white-space:nowrap;">Создать аккаунт</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# Экшены админа: Начисление/Списание
@app.post("/admin/action/{uid}")
async def admin_action(uid: str, amount: int = Form(...), comment: str = Form(...), act: str = Form(...)):
    db = load_db()
    if uid in db:
        if act == "add":
            db[uid]["balance"] += amount
            db[uid]["history"].append({"type": "Казначейство (+)", "amount": amount, "comment": comment})
            msg = f"Успешно начислено {amount} PRB для ID {uid}"
        else:
            db[uid]["balance"] = max(0, db[uid]["balance"] - amount)
            db[uid]["history"].append({"type": "Штраф/Налог (-)", "amount": -amount, "comment": comment})
            msg = f"Успешно списано {amount} PRB у ID {uid}"
        save_db(db)
        return RedirectResponse(url=f"/admin_panel?msg={msg}", status_code=303)
    return RedirectResponse(url="/admin_panel?msg=Пользователь не найден", status_code=303)

# Экшен админа: Смена имени
@app.post("/admin/rename/{uid}")
async def admin_rename(uid: str, new_name: str = Form(...)):
    db = load_db()
    if uid in db:
        old_name = db[uid]["name"]
        db[uid]["name"] = new_name
        save_db(db)
        return RedirectResponse(url=f"/admin_panel?msg=ID {uid}: имя изменёно с '{old_name}' на '{new_name}'", status_code=303)
    return RedirectResponse(url="/admin_panel?msg=Пользователь не найден", status_code=303)

# Экшен админа: Смена PIN
@app.post("/admin/pin/{uid}")
async def admin_pin(uid: str, new_pin: str = Form(...)):
    db = load_db()
    if uid in db:
        db[uid]["pin"] = new_pin
        save_db(db)
        return RedirectResponse(url=f"/admin_panel?msg=PIN для ID {uid} изменен на {new_pin}", status_code=303)
    return RedirectResponse(url="/admin_panel?msg=Пользователь не найден", status_code=303)

# Экшен админа: Бан / Разбан
@app.post("/admin/ban/{uid}")
async def admin_ban(uid: str):
    db = load_db()
    if uid in db:
        current_status = db[uid].get("banned", False)
        db[uid]["banned"] = not current_status
        save_db(db)
        status_msg = "забанен" if not current_status else "разбанен"
        return RedirectResponse(url=f"/admin_panel?msg=Пользователь {db[uid]['name']} (ID {uid}) успешно {status_msg}!", status_code=303)
    return RedirectResponse(url="/admin_panel?msg=Пользователь не найден", status_code=303)

# Экшен админа: Добавить нового юзера (генерация авто-ID)
@app.post("/admin/add_user")
async def admin_add_user(name: str = Form(...), pin: str = Form(...), balance: int = Form(...)):
    db = load_db()
    
    # Автоматически вычисляем следующий свободный цифровой ID
    numeric_ids = [int(x) for x in db.keys() if x.isdigit()]
    next_id = str(max(numeric_ids) + 1) if numeric_ids else "1"
    
    db[next_id] = {
        "name": name,
        "balance": balance,
        "pin": pin,
        "banned": False,
        "history": [{"type": "Создание", "amount": balance, "comment": "Создан из панели управления"}] if balance > 0 else []
    }
    
    save_db(db)
    return RedirectResponse(url=f"/admin_panel?msg=Создан новый пользователь: {name} с ID {next_id}!", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)                </select>
                <input type="password" name="pin" placeholder="Введите PIN-код" maxlength="4" required>
                <button type="submit">Войти в систему ➔</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login_process(citizen_id: str = Form(...), pin: str = Form(...)):
    db = load_db()
    if citizen_id in db["citizens"] and db["citizens"][citizen_id]["pin"] == pin:
        return RedirectResponse(url=f"/cabinet?citizen_id={citizen_id}", status_code=303)
    return RedirectResponse(url="/?error=Неверный PIN-код!", status_code=303)

# ================= ЛИЧНЫЙ КАБИНЕТ ГРАЖДАН =================
@app.get("/cabinet", response_class=HTMLResponse)
def citizen_cabinet(citizen_id: str, error: str = None, success: str = None):
    db = load_db()
    if citizen_id not in db["citizens"]:
        return RedirectResponse(url="/")
    user = db["citizens"][citizen_id]
    
    # Подготовка списка пользователей для JavaScript поиска (исключая самого себя)
    search_users = []
    for cid, data in db["citizens"].items():
        if cid != citizen_id:
            search_users.append({"id": cid, "name": data["name"]})
    search_users_json = json.dumps(search_users, ensure_ascii=False)

    history_rows = "".join([f"<li>{h}</li>" for h in reversed(user["history"])])
    if not history_rows:
        history_rows = "<li style='color: #64748b;'>Транзакций нет.</li>"
    status_msg = f'<p style="color: #f43f5e;">{error}</p>' if error else (f'<p style="color: #4ade80;">{success}</p>' if success else '')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZET Кабинет</title>
        <style>
            body {{ background: linear-gradient(135deg, #0b0f19, #1a102f); color: #f8fafc; font-family: sans-serif; padding: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }}
            .box {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 30px; max-width: 450px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
            .balance-card {{ background: rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; text-align: center; margin: 20px 0; border: 1px solid rgba(255,255,255,0.1); }}
            .amount {{ font-size: 2.5rem; font-weight: bold; color: #eab308; }}
            input, button {{ width: 100%; padding: 12px; margin-top: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #000; color: #fff; box-sizing: border-box; }}
            button {{ background: linear-gradient(90deg, #a855f7, #eab308); font-weight: bold; cursor: pointer; border: none; }}
            ul {{ list-style: none; padding: 0; max-height: 200px; overflow-y: auto; }}
            li {{ background: rgba(255,255,255,0.05); padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9rem; border-left: 4px solid #eab308; }}
            .back-link {{ display: block; text-align: center; color: #64748b; text-decoration: none; margin-top: 20px; }}
            .logo-text {{ font-weight: 900; color: #eab308; }}
            
            /* Стили для выпадающего списка поиска */
            .search-results {{ background: #000; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; max-height: 150px; overflow-y: auto; margin-top: 5px; display: none; padding: 0; list-style: none; text-align: left; }}
            .search-item {{ padding: 10px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.95rem; }}
            .search-item:hover {{ background: rgba(255,255,255,0.1); color: #eab308; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Салют, {user['name']}!</h2>
            <p style="font-size: 0.85rem; color: #94a3b8;">Вы обслуживаетесь в <span class="logo-text">ZET БАНК</span></p>
            {status_msg}
            <div class="balance-card">
                <div style="color: #94a3b8; font-size: 0.9rem;">Доступно средств:</div>
                <div class="amount">{user['balance']} PRB</div>
            </div>
            
            <h3>Факэску Перевод (Поиск получателя):</h3>
            <form action="/transfer" method="post" id="transferForm">
                <input type="hidden" name="sender_id" value="{citizen_id}">
                <input type="hidden" name="receiver_id" id="receiver_id" required>
                
                <input type="text" id="search_input" placeholder="Начните вводить имя получателя..." autocomplete="off" required>
                <ul class="search-results" id="search_results"></ul>
                
                <input type="number" name="amount" placeholder="Сумма в PRB" min="1" required>
                <button type="submit" id="submit_btn" style="opacity: 0.6; cursor: not-allowed;" disabled>Выберите получателя из поиска</button>
            </form>
            <a href="/" class="back-link">← Выйти из системы</a>
        </div>
        
        <div class="box">
            <h3>История ZET-операций:</h3>
            <ul>{history_rows}</ul>
        </div>

        <script>
            const users = {search_users_json};
            const searchInput = document.getElementById('search_input');
            const searchResults = document.getElementById('search_results');
            const receiverIdInput = document.getElementById('receiver_id');
            const submitBtn = document.getElementById('submit_btn');

            searchInput.addEventListener('input', function() {{
                const query = this.value.toLowerCase().trim();
                searchResults.innerHTML = '';
                
                receiverIdInput.value = '';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.6';
                submitBtn.innerText = 'Выберите получателя из поиска';

                const filtered = users.filter(user => user.name.toLowerCase().includes(query));

                if (filtered.length > 0) {{
                    filtered.forEach(user => {{
                        const li = document.createElement('li');
                        li.className = 'search-item';
                        li.innerText = user.name;
                        li.addEventListener('click', function() {{
                            searchInput.value = user.name;
                            receiverIdInput.value = user.id;
                            searchResults.style.display = 'none';
                            
                            submitBtn.disabled = false;
                            submitBtn.style.opacity = '1';
                            submitBtn.style.cursor = 'pointer';
                            submitBtn.innerText = 'Перевести мгновенно ➔';
                        }});
                        searchResults.appendChild(li);
                    }});
                    searchResults.style.display = 'block';
                }} else {{
                    const li = document.createElement('li');
                    li.className = 'search-item';
                    li.style.color = '#64748b';
                    li.style.cursor = 'default';
                    li.innerText = 'Никого не найдено';
                    searchResults.appendChild(li);
                    searchResults.style.display = 'block';
                }}
            }});

            document.addEventListener('click', function(e) {{
                if (e.target !== searchInput && e.target !== searchResults) {{
                    searchResults.style.display = 'none';
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.post("/transfer")
def process_transfer(sender_id: str = Form(...), receiver_id: str = Form(...), amount: int = Form(...)):
    db = load_db()
    if sender_id not in db["citizens"] or receiver_id not in db["citizens"]:
        return RedirectResponse(url="/", status_code=303)
    sender = db["citizens"][sender_id]
    receiver = db["citizens"][receiver_id]
    if sender["balance"] < amount:
        return RedirectResponse(url=f"/cabinet?citizen_id={sender_id}&error=Недостаточно PRB!", status_code=303)
    sender["balance"] -= amount
    receiver["balance"] += amount
    sender["history"].append(f"💸 ZET-Перевод: <b>-{amount} PRB</b> для {receiver['name']}")
    receiver["history"].append(f"💰 ZET-Получено: <b>+{amount} PRB</b> от {sender['name']}")
    db["global_logs"].append(f"🔄 {sender['name']} перевел {amount} PRB для {receiver['name']}")
    save_db(db)
    return RedirectResponse(url=f"/cabinet?citizen_id={sender_id}&success=Успешно отправлено!", status_code=303)


# ================= ЗАЩИЩЕННАЯ ПАНЕЛЬ ПРАВИТЕЛЯ (АДМИНКА) =================
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(error: str = None, ruler_session: str = Cookie(None)):
    if ruler_session == "ruler_authenticated_secret_token":
        db = load_db()
        rows = ""
        for cid, data in db["citizens"].items():
            rows += f"""
            <tr>
                <td>ID: {cid}</td>
                <td><b>{data['name']}</b></td>
                <td style="color: #a855f7; font-weight: bold; font-size: 1.1rem;">{data['pin']}</td>
                <td style="color: #eab308; font-weight: bold; font-size: 1.2rem;">{data['balance']} PRB</td>
                <td>
                    <form action="/admin-action" method="post" style="display: inline-flex; gap: 5px; margin-bottom: 5px;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <input type="number" name="amount" placeholder="Сумма" style="width: 80px; padding: 6px; border-radius: 6px; border: 1px solid #333; background: #000; color: #fff;" required>
                        <input type="text" name="reason" placeholder="Причина" style="width: 120px; padding: 6px; border-radius: 6px; border: 1px solid #333; background: #000; color: #fff;" required>
                        <button type="submit" name="action" value="charge" style="background: #f43f5e; color: white; border: none; padding: 6px 10px; border-radius: 6px; font-weight: bold; cursor: pointer;">Списать</button>
                        <button type="submit" name="action" value="give" style="background: #10b981; color: white; border: none; padding: 6px 10px; border-radius: 6px; font-weight: bold; cursor: pointer;">Начислить</button>
                    </form>
                    <br>
                    <form action="/change-pin" method="post" style="display: inline-flex; gap: 5px;">
                        <input type="hidden" name="citizen_id" value="{cid}">
                        <input type="text" name="new_pin" placeholder="Новый PIN" maxlength="4" style="width: 110px; padding: 6px; border-radius: 6px; border: 1px solid #444; background: #111; color: #fff;" required>
                        <button type="submit" style="background: #a855f7; color: white; border: none; padding: 6px 10px; border-radius: 6px; font-weight: bold; cursor: pointer;">Сменить PIN</button>
                    </form>
                </td>
            </tr>
            """
        log_rows = "".join([f"<li>{log}</li>" for log in reversed(db["global_logs"])])
        if not log_rows:
            log_rows = "<li style='color:#64748b;'>В системе тихо.</li>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Управление ZET БАНК</title>
            <style>
                body {{ background: linear-gradient(135deg, #090d16, #111827); color: #f8fafc; font-family: sans-serif; padding: 40px; display: flex; flex-direction: column; align-items: center; gap: 30px; }}
                .panel {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 35px; max-width: 1050px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
                h1 {{ background: linear-gradient(90deg, #eab308, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }}
                th {{ color: #64748b; font-size: 0.85rem; text-transform: uppercase; }}
                ul {{ list-style: none; padding: 0; max-height: 250px; overflow-y: auto; }}
                li {{ background: rgba(0,0,0,0.3); padding: 10px; margin-bottom: 5px; border-radius: 6px; font-size: 0.9rem; border-left: 4px solid #eab308; }}
                .logout {{ float: right; background: #334155; color: white; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 0.9rem; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="panel">
                <a href="/admin-logout" class="logout">Выйти ×</a>
                <h1>ЦЕНТРАЛЬНЫЙ ОФИС ZET БАНК 👑</h1>
                <p style="color: #64748b; margin: 5px 0 0 0;">Регулирование ликвидности и контроль учетных записей</p>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Гражданин</th>
                            <th>Текущий PIN</th>
                            <th>Баланс ZET-капитала</th>
                            <th>Действия Регулятора</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            <div class="panel">
                <h2>👁️ МОНИТОРИНГ ZET-СИСТЕМЫ</h2>
                <ul>{log_rows}</ul>
            </div>
        </body>
        </html>
        """
    
    error_msg = f'<p style="color: #f43f5e; font-weight: bold;">{error}</p>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ZET Администрация</title>
        <style>
            body {{ background: #090514; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .login-box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; max-width: 360px; width: 100%; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.7); }}
            h2 {{ color: #eab308; margin-bottom: 20px; }}
            input, button {{ width: 100%; padding: 12px; margin-top: 15px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff; box-sizing: border-box; }}
            button {{ background: #eab308; color: #000; font-weight: bold; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Вход для Руководства ZET 👑</h2>
            {error_msg}
            <form action="/admin-login" method="post">
                <input type="text" name="username" placeholder="Логин" required>
                <input type="password" name="pin" placeholder="PIN-код доступа" required>
                <button type="submit">Войти в панель ➔</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/admin-login")
def admin_login_process(username: str = Form(...), pin: str = Form(...)):
    if username == ADMIN_USERNAME and pin == ADMIN_PIN:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="ruler_session", value="ruler_authenticated_secret_token", httponly=True)
        return response
    return RedirectResponse(url="/admin?error=Неверные данные доступа.", status_code=303)

@app.get("/admin-logout")
def admin_logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("ruler_session")
    return response

@app.post("/change-pin")
def change_pin_process(citizen_id: str = Form(...), new_pin: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        user = db["citizens"][citizen_id]
        old_pin = user["pin"]
        user["pin"] = new_pin
        db["global_logs"].append(f"🔑 Установлен новый PIN для {user['name']} (Был: {old_pin} -> Стал: {new_pin})")
        save_db(db)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin-action")
def admin_action_process(citizen_id: str = Form(...), amount: int = Form(...), reason: str = Form(...), action: str = Form(...), ruler_session: str = Cookie(None)):
    if ruler_session != "ruler_authenticated_secret_token":
        return RedirectResponse(url="/admin", status_code=303)
    db = load_db()
    if citizen_id in db["citizens"]:
        user = db["citizens"][citizen_id]
        if action == "charge":
            user["balance"] -= amount
            user["history"].append(f"⚠️ Списание ZET-Банка: <b>-{amount} PRB</b> — {reason}")
            db["global_logs"].append(f"🚨 Корректировка: Списано у {user['name']} {amount} PRB. Причина: {reason}")
        elif action == "give":
            user["balance"] += amount
            user["history"].append(f"🎁 Начисление ZET-Банка: <b>+{amount} PRB</b> — {reason}")
            db["global_logs"].append(f"💸 Эмиссия: Начислено {user['name']} {amount} PRB. Причина: {reason}")
        save_db(db)
    return RedirectResponse(url="/admin", status_code=303)
