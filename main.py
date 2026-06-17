import os
import json
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

DB_FILE = "database.json"

# Настоящие граждане из книги «Сказкалор дин Приднестровье»!
DEFAULT_DATA = {
    "1": {"name": "Ченушара (Фата ку ковтун)", "balance": 450, "history": []},
    "2": {"name": "Хансел (Куматрул мик)", "balance": 3200, "history": []},
    "3": {"name": "Гретел (Дештеаптэ)", "balance": 5000, "history": []},
    "4": {"name": "Алба-ка-Зэпада", "balance": 12500, "history": []},
    "5": {"name": "Аладдин (Омул ку лампа)", "balance": 150, "history": []}
}

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
        return DEFAULT_DATA
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return DEFAULT_DATA

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ЛК ГРАЖДАН
@app.get("/", response_class=HTMLResponse)
def citizen_login_view():
    db = load_db()
    options = "".join([f'<option value="{cid}">{data["name"]}</option>' for cid, data in db.items()])
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Приднестровье Банты-Банк</title>
        <style>
            body {{ background: linear-gradient(135deg, #060b14, #110e2e); color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 40px; max-width: 400px; width: 100%; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
            h1 {{ background: linear-gradient(90deg, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 20px 0; font-size: 1.8rem; }}
            select, button {{ width: 100%; padding: 14px; margin-top: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); font-size: 1rem; box-sizing: border-box; }}
            select {{ background: #000; color: white; }}
            button {{ background: linear-gradient(90deg, #38bdf8, #818cf8); color: white; border: none; font-weight: bold; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>БАНТЫ-БАНК 🏛️</h1>
            <p style="color: #64748b; font-size: 0.9rem;">Личный кабинет гражданина Приднестровья</p>
            <form action="/cabinet" method="get">
                <select name="citizen_id">
                    {options}
                </select>
                <button type="submit">Войти в систему ➔</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.get("/cabinet", response_class=HTMLResponse)
def citizen_cabinet(citizen_id: str):
    db = load_db()
    if citizen_id not in db:
        return RedirectResponse(url="/")
    user = db[citizen_id]
    history_rows = "".join([f"<li>⚠️ Изъято: <b>{h['amount']} PRB</b> — {h['reason']}</li>" for h in reversed(user["history"])])
    if not history_rows:
        history_rows = "<li style='color: #64748b;'>Транзакций нет. Правитель доволен вашей лояльностью!</li>"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Кабинет: {user['name']}</title>
        <style>
            body {{ background: linear-gradient(135deg, #060b14, #110e2e); color: #f8fafc; font-family: sans-serif; padding: 20px; display: flex; justify-content: center; }}
            .box {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 30px; max-width: 450px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
            .balance-card {{ background: rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; text-align: center; margin: 20px 0; border: 1px solid rgba(255,255,255,0.1); }}
            .amount {{ font-size: 2.8rem; font-weight: bold; color: #38bdf8; margin: 5px 0; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.2); padding: 12px; margin-bottom: 10px; border-radius: 10px; font-size: 0.95rem; }}
            .back-link {{ display: block; text-align: center; color: #64748b; text-decoration: none; margin-top: 20px; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Салют, {user['name']}!</h2>
            <p style="color: #64748b; margin: -10px 0 20px 0; font-size: 0.85rem;">Валюта: Приднестровский рубль (PRB)</p>
            <div class="balance-card">
                <div style="color: #94a3b8; font-size: 0.9rem;">Ваш баланс банты:</div>
                <div class="amount">{user['balance']} PRB</div>
            </div>
            <h3>История изъятий Правителя:</h3>
            <ul>{history_rows}</ul>
            <a href="/" class="back-link">← Выйти</a>
        </div>
    </body>
    </html>
    """

# ПАНЕЛЬ ПРАВИТЕЛЯ (АДМИНКА)
@app.get("/admin", response_class=HTMLResponse)
def admin_panel():
    db = load_db()
    rows = ""
    for cid, data in db.items():
        rows += f"""
        <tr>
            <td>ID: {cid}</td>
            <td><b>{data['name']}</b></td>
            <td style="color: #38bdf8; font-weight: bold; font-size: 1.2rem;">{data['balance']} PRB</td>
            <td>
                <form action="/charge" method="post" style="display: flex; gap: 8px;">
                    <input type="hidden" name="citizen_id" value="{cid}">
                    <input type="number" name="amount" placeholder="Сколько PRB" style="width: 110px; padding: 8px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff;" required>
                    <input type="text" name="reason" placeholder="Причина изъятия" style="width: 180px; padding: 8px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff;" required>
                    <button type="submit" style="background: #f43f5e; color: white; border: none; padding: 8px 15px; border-radius: 8px; font-weight: bold; cursor: pointer;">Списать</button>
                </form>
            </td>
        </tr>
        """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Контроль Банты-Банка</title>
        <style>
            body {{ background: linear-gradient(135deg, #090d16, #111827); color: #f8fafc; font-family: sans-serif; padding: 40px; display: flex; justify-content: center; }}
            .panel {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); border-radius: 24px; padding: 35px; max-width: 900px; width: 100%; box-shadow: 0 30px 60px rgba(0,0,0,0.4); }}
            h1 {{ background: linear-gradient(90deg, #f43f5e, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }}
            th {{ color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }}
        </style>
    </head>
    <body>
        <div class="panel">
            <h1>ПАНЕЛЬ ПРАВИТЕЛЯ 👑</h1>
            <p style="color: #64748b; margin: 5px 0 0 0;">Принудительное изъятие приднестровских рублей со счетов сказочных граждан</p>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Гражданин</th>
                        <th>Баланс банты</th>
                        <th>Карательное списание средств</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

# Защищенный обработчик POST-запроса формы
@app.post("/charge")
def charge_money(citizen_id: str = Form(...), amount: int = Form(...), reason: str = Form(...)):
    db = load_db()
    if citizen_id not in db:
        return RedirectResponse(url="/admin", status_code=303)
    
    db[citizen_id]["balance"] -= amount
    db[citizen_id]["history"].append({
        "amount": amount,
        "reason": reason
    })
    save_db(db)
    # Строго перенаправляем обратно в админку с кодом 303 (чтобы метод сбросился на GET)
    return RedirectResponse(url="/admin", status_code=303)

# На всякий случай обрабатываем GET на /charge, чтобы не было Not Found
@app.get("/charge")
def charge_get_redirect():
    return RedirectResponse(url="/admin")
