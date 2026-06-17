import os
import json
from fastapi import FastAPI, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

DB_FILE = "database.json"

# Логин и секретный PIN-код самого Правителя
ADMIN_USERNAME = "admin"
ADMIN_PIN = "7777"

DEFAULT_DATA = {
    "citizens": {
        "1": {"name": "Ченушара (Фата ку ковтун)", "balance": 450, "pin": "1111", "history": []},
        "2": {"name": "Хансел (Куматрул мик)", "balance": 3200, "pin": "2222", "history": []},
        "3": {"name": "Гретел (Дештеаптэ)", "balance": 5000, "pin": "3333", "history": []},
        "4": {"name": "Алба-ка-Зэпада", "balance": 12500, "pin": "4444", "history": []},
        "5": {"name": "Аладдин (Омул ку лампа)", "balance": 150, "pin": "5555", "history": []}
    },
    "global_logs": []
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
    options = "".join([f'<option value="{cid}">{data["name"]}</option>' for cid, data in db["citizens"].items()])
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
            <h1>ZET БАНК ⚡</h1>
            <p style="color: #94a3b8; font-size: 0.9rem;">Новое поколение цифровых бант</p>
            {error_msg}
            <form action="/login" method="post">
                <select name="citizen_id">
                    {options}
                </select>
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
    recipients = "".join([f'<option value="{cid}">{data["name"]}</option>' for cid, data in db["citizens"].items() if cid != citizen_id])
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
            select, input, button {{ width: 100%; padding: 12px; margin-top: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #000; color: #fff; box-sizing: border-box; }}
            button {{ background: linear-gradient(90deg, #a855f7, #eab308); font-weight: bold; cursor: pointer; border: none; }}
            ul {{ list-style: none; padding: 0; max-height: 200px; overflow-y: auto; }}
            li {{ background: rgba(255,255,255,0.05); padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9rem; border-left: 4px solid #eab308; }}
            .back-link {{ display: block; text-align: center; color: #64748b; text-decoration: none; margin-top: 20px; }}
            .logo-text {{ font-weight: 900; color: #eab308; }}
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
            <h3>Факэску Перевод (Быстрый платеж):</h3>
            <form action="/transfer" method="post">
                <input type="hidden" name="sender_id" value="{citizen_id}">
                <select name="receiver_id">{recipients}</select>
                <input type="number" name="amount" placeholder="Сумма в PRB" min="1" required>
                <button type="submit">Перевести мгновенно ➔</button>
            </form>
            <a href="/" class="back-link">← Выйти из системы</a>
        </div>
        <div class="box">
            <h3>История ZET-операций:</h3>
            <ul>{history_rows}</ul>
        </div>
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
    
    # ФОРМА ВХОДА В АДМИНКУ СЕБЕ
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
        db["global_logs"].append(f"🔑 Установлен новый PIN для {user['name']} (Был: {old_pin} -> Став: {new_pin})")
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
