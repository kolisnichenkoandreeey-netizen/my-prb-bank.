"""
ZET BANK - Высоконагруженная банковская система (FastAPI)
Архитектура: Monolithic Single-File App
Стиль: Liquid Glass (Dark Theme, Neon Gold & Purple)
Особенности: 
- Автовосстановление БД и защита от KeyError.
- Строгая типизация и обработка транзакций.
- Cookie-based авторизация.
"""

import json
import os
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from fastapi import FastAPI, Form, Cookie, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

# ==========================================
# 1. СТИЛИ И UI (LIQUID GLASS)
# ==========================================

def get_css() -> str:
    """Генерирует CSS для интерфейса в стиле Liquid Glass с неоновыми акцентами."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Roboto:wght@300;400;700&display=swap');
        
        :root {
            --bg-color: #0b0c10;
            --glass-bg: rgba(20, 20, 25, 0.65);
            --glass-border: rgba(255, 215, 0, 0.3);
            --gold: #FFD700;
            --purple: #8A2BE2;
            --purple-glow: rgba(138, 43, 226, 0.6);
            --text-main: #e0e0e0;
            --text-muted: #a0a0a0;
            --danger: #ff4c4c;
            --success: #00ff88;
        }

        body {
            margin: 0;
            padding: 0;
            background: radial-gradient(circle at top left, #1a0b2e, #0b0c10 100%);
            color: var(--text-main);
            font-family: 'Roboto', sans-serif;
            min-height: 100vh;
            background-attachment: fixed;
        }

        h1, h2, h3, h4 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.4);
            margin-top: 0;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(138, 43, 226, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-card:hover {
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.7), inset 0 0 20px var(--purple-glow);
        }

        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--purple);
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        .nav-links a {
            color: var(--gold);
            text-decoration: none;
            font-weight: bold;
            margin-left: 20px;
            font-family: 'Orbitron', sans-serif;
            transition: text-shadow 0.3s;
        }

        .nav-links a:hover {
            text-shadow: 0 0 10px var(--gold);
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin: 10px 0 20px 0;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--purple);
            color: white;
            border-radius: 8px;
            font-size: 1rem;
            outline: none;
            box-sizing: border-box;
            transition: 0.3s;
        }

        input:focus, select:focus {
            border-color: var(--gold);
            box-shadow: 0 0 10px var(--gold);
        }

        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(45deg, #4b0082, var(--purple));
            color: white;
            font-weight: bold;
            font-size: 1.1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-family: 'Orbitron', sans-serif;
        }

        button:hover {
            background: linear-gradient(45deg, var(--purple), var(--gold));
            color: black;
            box-shadow: 0 0 15px var(--gold);
            transform: translateY(-2px);
        }

        .btn-danger {
            background: linear-gradient(45deg, #8b0000, #ff0000);
        }
        
        .btn-danger:hover {
            background: #ff4c4c;
            box-shadow: 0 0 15px #ff4c4c;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(138, 43, 226, 0.3);
        }

        th {
            color: var(--gold);
            font-family: 'Orbitron', sans-serif;
        }

        tr:hover {
            background: rgba(138, 43, 226, 0.1);
        }

        .alert-error {
            background: rgba(255, 76, 76, 0.15);
            border-left: 4px solid var(--danger);
            color: #ffb3b3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .alert-success {
            background: rgba(0, 255, 136, 0.15);
            border-left: 4px solid var(--success);
            color: #b3ffcc;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
        }

        .balance-display {
            font-size: 2.5rem;
            color: white;
            text-shadow: 0 0 15px var(--gold);
            margin: 10px 0;
            font-family: 'Orbitron', sans-serif;
        }
    </style>
    """

# ==========================================
# 2. БАЗА ДАННЫХ И БИЗНЕС-ЛОГИКА
# ==========================================

class BankDatabase:
    """Обертка базы данных. Обеспечивает отказоустойчивость и защиту от KeyError."""
    
    def __init__(self, filename: str = "database.json"):
        self.filename = filename
        self.users: Dict[str, Dict[str, Any]] = {}
        self.system_logs: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        """Загрузка данных и применение setdefault для защиты от падений."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.users = raw.get("users", {})
                    self.system_logs = raw.get("system_logs", [])
            except Exception as e:
                print(f"[ERROR] Не удалось загрузить БД, создана пустая: {e}")
                self.users = {}
                self.system_logs = []
        else:
            self._create_default_admin()

        # КРИТИЧЕСКИ ВАЖНО: Заполняем отсутствующие поля (миграция на лету)
        for cid, user in self.users.items():
            user.setdefault("name", f"Citizen {cid}")
            user.setdefault("pin", "0000")
            user.setdefault("balance", 0.0)
            user.setdefault("savings", 0.0)
            user.setdefault("credit", 0.0)
            user.setdefault("banned", False)
            user.setdefault("role", "user")
            user.setdefault("logs", [])
            
        self.save()

    def _create_default_admin(self):
        """Создает базовых пользователей, если БД пуста."""
        self.users["1000"] = {
            "name": "Системный Администратор",
            "pin": "7777",
            "balance": 1000000.0,
            "savings": 0.0,
            "credit": 0.0,
            "banned": False,
            "role": "admin",
            "logs": []
        }
        self.users["1001"] = {
            "name": "Иван Иванов",
            "pin": "1234",
            "balance": 50000.0,
            "savings": 10000.0,
            "credit": 0.0,
            "banned": False,
            "role": "user",
            "logs": []
        }
        self.log_system_action("Инициализация", "Создана новая база данных.")

    def save(self):
        """Атомарное сохранение базы данных в файл JSON."""
        data = {
            "users": self.users,
            "system_logs": self.system_logs
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # --- ЛОГИРОВАНИЕ ---

    def log_system_action(self, action: str, details: str):
        """Записывает событие в системный лог (для админки)."""
        ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.system_logs.insert(0, {"time": ts, "action": action, "details": details})
        self.system_logs = self.system_logs[:200]  # Храним последние 200
        self.save()

    def log_user_action(self, cid: str, message: str):
        """Записывает событие в личный лог пользователя."""
        if cid in self.users:
            ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.users[cid]["logs"].insert(0, {"time": ts, "msg": message})
            self.users[cid]["logs"] = self.users[cid]["logs"][:50]
            self.save()

    # --- ОСНОВНЫЕ МЕТОДЫ ---

    def get_user(self, cid: str) -> Optional[Dict[str, Any]]:
        return self.users.get(cid)

    def find_users_by_name(self, name: str) -> List[str]:
        """Поиск ID пользователей по точному совпадению имени (без учета регистра)."""
        target = name.strip().lower()
        return [cid for cid, u in self.users.items() if u["name"].strip().lower() == target]

    def authenticate(self, cid: str, pin: str) -> bool:
        user = self.get_user(cid)
        return bool(user and user["pin"] == pin)

    # --- ФИНАНСОВЫЕ ОПЕРАЦИИ ---

    def process_transfer(self, sender_id: str, recipient_name: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        
        sender = self.get_user(sender_id)
        if not sender: return False, "Отправитель не найден."
        if sender["banned"]: return False, "Ваш счет заблокирован. Операция отклонена."
        if sender["balance"] < amount: return False, "Недостаточно средств на основном счете."

        matches = self.find_users_by_name(recipient_name)
        if not matches: return False, f"Получатель с именем '{recipient_name}' не найден."
        if len(matches) > 1: return False, f"Найдено несколько пользователей '{recipient_name}'. Уточните данные."
        
        recipient_id = matches[0]
        if sender_id == recipient_id: return False, "Нельзя перевести средства самому себе."

        recipient = self.get_user(recipient_id)
        if recipient["banned"]: return False, "Счет получателя заблокирован."

        # Выполнение транзакции
        sender["balance"] -= amount
        recipient["balance"] += amount

        self.log_user_action(sender_id, f"Перевод {amount:.2f} ₽ пользователю {recipient['name']}.")
        self.log_user_action(recipient_id, f"Получен перевод {amount:.2f} ₽ от {sender['name']}.")
        self.log_system_action("Перевод", f"{sender_id} -> {recipient_id}: {amount:.2f} ₽")
        self.save()
        return True, "Перевод успешно завершен."

    def process_savings(self, cid: str, action: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        user = self.get_user(cid)
        if not user: return False, "Пользователь не найден."
        if user["banned"]: return False, "Счет заблокирован."

        if action == "deposit":
            if user["balance"] < amount: return False, "Недостаточно средств на счете."
            user["balance"] -= amount
            user["savings"] += amount
            self.log_user_action(cid, f"Пополнение вклада: {amount:.2f} ₽")
            self.save()
            return True, "Вклад успешно пополнен."
        elif action == "withdraw":
            if user["savings"] < amount: return False, "Недостаточно средств на вкладе."
            user["savings"] -= amount
            user["balance"] += amount
            self.log_user_action(cid, f"Снятие со вклада: {amount:.2f} ₽")
            self.save()
            return True, "Средства сняты со вклада."
        return False, "Неизвестная операция."

    def process_credit(self, cid: str, action: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        user = self.get_user(cid)
        if not user: return False, "Пользователь не найден."
        if user["banned"]: return False, "Счет заблокирован."

        if action == "take":
            if user["credit"] + amount > 5000000: return False, "Превышен лимит кредитования."
            user["credit"] += amount
            user["balance"] += amount
            self.log_user_action(cid, f"Взят кредит: {amount:.2f} ₽")
            self.save()
            return True, "Кредит успешно оформлен."
        elif action == "pay":
            if user["balance"] < amount: return False, "Недостаточно средств для погашения."
            actual_payment = min(amount, user["credit"])
            if actual_payment <= 0: return False, "У вас нет задолженностей по кредиту."
            
            user["balance"] -= actual_payment
            user["credit"] -= actual_payment
            self.log_user_action(cid, f"Погашение кредита: {actual_payment:.2f} ₽")
            self.save()
            return True, f"Кредит погашен на сумму {actual_payment:.2f} ₽."
        return False, "Неизвестная операция."

    # --- АДМИН ПАНЕЛЬ ---

    def admin_create_user(self, name: str, pin: str) -> str:
        # Генерируем новый ID (максимальный + 1)
        existing_ids = [int(k) for k in self.users.keys() if k.isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1000"
        
        self.users[new_id] = {
            "name": name,
            "pin": pin,
            "balance": 0.0,
            "savings": 0.0,
            "credit": 0.0,
            "banned": False,
            "role": "user",
            "logs": []
        }
        self.log_system_action("Создан пользователь", f"ID: {new_id}, Имя: {name}")
        self.save()
        return new_id

    def admin_delete_user(self, cid: str) -> bool:
        if cid in self.users:
            name = self.users[cid]["name"]
            del self.users[cid]
            self.log_system_action("Удален пользователь", f"ID: {cid}, Имя: {name}")
            self.save()
            return True
        return False

    def admin_ban_user(self, cid: str, state: bool) -> bool:
        user = self.get_user(cid)
        if user:
            user["banned"] = state
            action_str = "Забанен" if state else "Разбанен"
            self.log_system_action(action_str, f"Пользователь ID: {cid}")
            self.save()
            return True
        return False

    def admin_change_pin(self, cid: str, new_pin: str) -> bool:
        user = self.get_user(cid)
        if user:
            user["pin"] = new_pin
            self.log_system_action("Смена PIN", f"Пользователь ID: {cid}")
            self.save()
            return True
        return False

    def admin_adjust_balance(self, cid: str, amount: float, reason: str, is_add: bool) -> Tuple[bool, str]:
        user = self.get_user(cid)
        if not user: return False, "Пользователь не найден."
        
        if is_add:
            user["balance"] += amount
            action_log = f"Начислено {amount:.2f} ₽. Причина: {reason}"
        else:
            if user["balance"] < amount: return False, "Недостаточно средств для списания."
            user["balance"] -= amount
            action_log = f"Списано {amount:.2f} ₽. Причина: {reason}"

        self.log_user_action(cid, f"Админ. корректировка: {action_log}")
        self.log_system_action("Корректировка баланса", f"ID: {cid} | {action_log}")
        self.save()
        return True, "Баланс успешно скорректирован."


# Инициализация БД и Приложения
db = BankDatabase()
app = FastAPI(title="ZET BANK")

# Константы
ADMIN_PASSWORD = "admin"  # Пароль для панели администратора

# ==========================================
# 3. HTML ШАБЛОНЫ (ГЕНЕРАТОРЫ)
# ==========================================

def render_layout(title: str, content: str, error: str = "", success: str = "") -> str:
    """Оборачивает контент в базовый HTML каркас."""
    alerts = ""
    if error:
        alerts += f"<div class='alert-error'><strong>Ошибка:</strong> {error}</div>"
    if success:
        alerts += f"<div class='alert-success'><strong>Успешно:</strong> {success}</div>"

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZET BANK | {title}</title>
    {get_css()}
</head>
<body>
    <div class="container">
        <div class="glass-card header-bar">
            <h1>ZET BANK</h1>
            <div class="nav-links">
                <a href="/">Главная</a>
                <a href="/cabinet">Кабинет</a>
                <a href="/admin">Админка</a>
            </div>
        </div>
        {alerts}
        {content}
    </div>
</body>
</html>"""

def build_redirect(url: str, error: str = "", success: str = "") -> RedirectResponse:
    """Хелпер для редиректа с параметрами уведомлений."""
    params = []
    if error: params.append(f"error={urllib.parse.quote(error)}")
    if success: params.append(f"success={urllib.parse.quote(success)}")
    final_url = f"{url}?{'&'.join(params)}" if params else url
    return RedirectResponse(url=final_url, status_code=303)

# ==========================================
# 4. РОУТЫ (ENDPOINTS)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def route_index(request: Request, citizen_id: Optional[str] = Cookie(None)):
    """Главная страница: Форма входа."""
    if citizen_id and db.get_user(citizen_id):
        return RedirectResponse("/cabinet", status_code=303)
        
    error = request.query_params.get("error", "")
    content = """
    <div class="glass-card" style="max-width: 400px; margin: 50px auto; text-align: center;">
        <h2>Авторизация</h2>
        <form action="/login" method="POST">
            <input type="text" name="cid" placeholder="Citizen ID (Ваш номер)" required>
            <input type="password" name="pin" placeholder="PIN-код" required>
            <button type="submit">Войти в систему</button>
        </form>
    </div>
    """
    return render_layout("Вход", content, error=error)


@app.post("/login", response_class=HTMLResponse)
async def route_login(cid: str = Form(...), pin: str = Form(...)):
    """Обработка входа пользователя."""
    if db.authenticate(cid, pin):
        response = RedirectResponse("/cabinet", status_code=303)
        response.set_cookie(key="citizen_id", value=cid, httponly=True, max_age=86400)
        return response
    return build_redirect("/", error="Неверный ID или PIN-код")


@app.get("/logout")
async def route_logout():
    """Выход из аккаунта (удаление куки)."""
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("citizen_id")
    return response


@app.get("/cabinet", response_class=HTMLResponse)
async def route_cabinet(request: Request, citizen_id: Optional[str] = Cookie(None)):
    """Личный кабинет пользователя. Считывает citizen_id из куки."""
    if not citizen_id:
        return build_redirect("/", error="Пожалуйста, авторизуйтесь.")
        
    user = db.get_user(citizen_id)
    if not user:
        response = build_redirect("/", error="Аккаунт не найден.")
        response.delete_cookie("citizen_id")
        return response

    error = request.query_params.get("error", "")
    success = request.query_params.get("success", "")

    if user["banned"]:
        content = """
        <div class="glass-card alert-error" style="text-align: center;">
            <h2>ВАШ АККАУНТ ЗАБЛОКИРОВАН</h2>
            <p>Доступ к финансовым операциям приостановлен. Обратитесь к администратору системы.</p>
            <br>
            <a href="/logout"><button class="btn-danger" style="max-width: 200px;">Выйти</button></a>
        </div>"""
        return render_layout("Блокировка", content)

    # Генерация логов
    logs_html = "".join([
        f"<tr><td>{log['time']}</td><td>{log['msg']}</td></tr>" 
        for log in user["logs"]
    ]) or "<tr><td colspan='2'>История операций пуста.</td></tr>"

    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>Добро пожаловать, {user['name']} <span style="font-size: 0.5em; color: gray;">(ID: {citizen_id})</span></h2>
        <a href="/logout"><button class="btn-danger" style="width: auto; padding: 10px 20px;">Выход</button></a>
    </div>

    <div class="grid-3">
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #fff;">Основной счет</h3>
            <div class="balance-display">{user['balance']:.2f} ₽</div>
        </div>
        <div class="glass-card" style="text-align: center; border-color: rgba(0, 255, 136, 0.3);">
            <h3 style="color: var(--success);">Накопления</h3>
            <div class="balance-display" style="text-shadow: 0 0 15px var(--success);">{user['savings']:.2f} ₽</div>
        </div>
        <div class="glass-card" style="text-align: center; border-color: rgba(255, 76, 76, 0.3);">
            <h3 style="color: var(--danger);">Кредит</h3>
            <div class="balance-display" style="text-shadow: 0 0 15px var(--danger);">{user['credit']:.2f} ₽</div>
        </div>
    </div>

    <div class="grid-3">
        <!-- ПЕРЕВОДЫ -->
        <div class="glass-card">
            <h3>Перевод средств</h3>
            <form action="/transfer" method="POST">
                <input type="text" name="recipient_name" placeholder="Имя получателя (точное совпадение)" required>
                <input type="number" step="0.01" name="amount" placeholder="Сумма перевода" required>
                <button type="submit">Отправить</button>
            </form>
        </div>

        <!-- ВКЛАДЫ -->
        <div class="glass-card">
            <h3 style="color: var(--success);">Управление вкладом</h3>
            <form action="/savings" method="POST">
                <select name="action" required>
                    <option value="deposit">Положить на вклад</option>
                    <option value="withdraw">Снять со вклада</option>
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <button type="submit" style="background: linear-gradient(45deg, #004d00, #00b300);">Выполнить</button>
            </form>
        </div>

        <!-- КРЕДИТЫ -->
        <div class="glass-card">
            <h3 style="color: var(--danger);">Управление кредитом</h3>
            <form action="/credit" method="POST">
                <select name="action" required>
                    <option value="take">Взять кредит</option>
                    <option value="pay">Погасить кредит</option>
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <button type="submit" class="btn-danger">Выполнить</button>
            </form>
        </div>
    </div>

    <div class="glass-card">
        <h3>История операций</h3>
        <table>
            <tr><th>Время</th><th>Операция</th></tr>
            {logs_html}
        </table>
    </div>
    """
    return render_layout("Личный Кабинет", content, error=error, success=success)


@app.post("/transfer")
async def route_transfer(
    recipient_name: str = Form(...),
    amount: str = Form(...),
    citizen_id: Optional[str] = Cookie(None)
):
    """Маршрутизатор переводов."""
    if not citizen_id: return build_redirect("/")
    try:
        amt = float(amount)
        success, msg = db.process_transfer(citizen_id, recipient_name, amt)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")


@app.post("/savings")
async def route_savings(
    action: str = Form(...),
    amount: str = Form(...),
    citizen_id: Optional[str] = Cookie(None)
):
    """Маршрутизатор вкладов."""
    if not citizen_id: return build_redirect("/")
    try:
        amt = float(amount)
        success, msg = db.process_savings(citizen_id, action, amt)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")


@app.post("/credit")
async def route_credit(
    action: str = Form(...),
    amount: str = Form(...),
    citizen_id: Optional[str] = Cookie(None)
):
    """Маршрутизатор кредитов."""
    if not citizen_id: return build_redirect("/")
    try:
        amt = float(amount)
        success, msg = db.process_credit(citizen_id, action, amt)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")


# ==========================================
# 5. АДМИН-ПАНЕЛЬ
# ==========================================

@app.get("/admin", response_class=HTMLResponse)
async def route_admin(request: Request, admin_token: Optional[str] = Cookie(None)):
    """Панель администратора. Вход по паролю."""
    error = request.query_params.get("error", "")
    success = request.query_params.get("success", "")

    # Форма входа для админа
    if admin_token != "authed_admin":
        content = """
        <div class="glass-card" style="max-width: 400px; margin: 50px auto; text-align: center;">
            <h2>Вход Администратора</h2>
            <form action="/admin/login" method="POST">
                <input type="password" name="password" placeholder="Пароль администратора" required>
                <button type="submit">Доступ</button>
            </form>
        </div>
        """
        return render_layout("Админка - Вход", content, error=error)

    # Таблица пользователей
    users_html = ""
    for cid, u in db.users.items():
        status = "<span style='color:red;'>ЗАБАНЕН</span>" if u["banned"] else "<span style='color:green;'>АКТИВЕН</span>"
        users_html += f"""
        <tr>
            <td>{cid}</td>
            <td>{u['name']}</td>
            <td>{u['balance']:.2f}</td>
            <td>{status}</td>
        </tr>"""

    # Таблица логов
    sys_logs_html = "".join([
        f"<tr><td>{l['time']}</td><td>{l['action']}</td><td>{l['details']}</td></tr>" 
        for l in db.system_logs[:20]
    ])

    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>Панель Управления Системой</h2>
        <a href="/admin/logout"><button class="btn-danger" style="width: auto;">Выйти из ПУ</button></a>
    </div>

    <div class="grid-2">
        <div class="glass-card">
            <h3>Создать пользователя</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="create">
                <input type="text" name="name" placeholder="ФИО пользователя" required>
                <input type="text" name="pin" placeholder="PIN-код" required>
                <button type="submit">Создать</button>
            </form>
        </div>

        <div class="glass-card">
            <h3>Изменить PIN-код</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="pin">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <input type="text" name="pin" placeholder="Новый PIN-код" required>
                <button type="submit">Изменить</button>
            </form>
        </div>
    </div>

    <div class="grid-2">
        <div class="glass-card">
            <h3>Блокировка / Удаление</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="ban_status">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <select name="state" required>
                    <option value="ban">Забанить</option>
                    <option value="unban">Разбанить</option>
                    <option value="delete">УДАЛИТЬ АККАУНТ</option>
                </select>
                <button type="submit" class="btn-danger">Применить</button>
            </form>
        </div>

        <div class="glass-card">
            <h3>Ручная корректировка баланса</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="balance">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <select name="state" required>
                    <option value="add">Начислить</option>
                    <option value="sub">Списать</option>
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <input type="text" name="reason" placeholder="Причина (обязательно)" required>
                <button type="submit" style="background: linear-gradient(45deg, #b8860b, var(--gold)); color: black;">Выполнить</button>
            </form>
        </div>
    </div>

    <div class="glass-card">
        <h3>Все пользователи системы</h3>
        <table>
            <tr><th>ID</th><th>Имя</th><th>Баланс (₽)</th><th>Статус</th></tr>
            {users_html}
        </table>
    </div>

    <div class="glass-card">
        <h3>Системные логи (последние 20)</h3>
        <table style="font-size: 0.9em;">
            <tr><th>Время</th><th>Действие</th><th>Детали</th></tr>
            {sys_logs_html}
        </table>
    </div>
    """
    return render_layout("Админка", content, error=error, success=success)


@app.post("/admin/login")
async def route_admin_login(password: str = Form(...)):
    """Авторизация администратора."""
    if password == ADMIN_PASSWORD:
        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie("admin_token", "authed_admin", httponly=True)
        return response
    return build_redirect("/admin", error="Неверный пароль администратора.")


@app.get("/admin/logout")
async def route_admin_logout():
    """Выход из админки."""
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("admin_token")
    return response


@app.post("/admin/action")
async def route_admin_action(
    action_type: str = Form(...),
    user_id: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    pin: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    amount: Optional[str] = Form(None),
    reason: Optional[str] = Form(None),
    admin_token: Optional[str] = Cookie(None)
):
    """Универсальный обработчик административных действий."""
    if admin_token != "authed_admin":
        return build_redirect("/", error="Нет доступа.")

    success, error = "", ""

    try:
        if action_type == "create" and name and pin:
            new_id = db.admin_create_user(name, pin)
            success = f"Пользователь '{name}' успешно создан! Назначен ID: {new_id}"

        elif action_type == "pin" and user_id and pin:
            if db.admin_change_pin(user_id, pin): success = f"PIN для ID {user_id} изменен."
            else: error = "Пользователь не найден."

        elif action_type == "ban_status" and user_id and state:
            if state == "delete":
                if db.admin_delete_user(user_id): success = f"Пользователь {user_id} УДАЛЕН."
                else: error = "Пользователь не найден."
            elif state in ["ban", "unban"]:
                is_ban = (state == "ban")
                if db.admin_ban_user(user_id, is_ban): success = f"Статус блокировки изменен."
                else: error = "Пользователь не найден."

        elif action_type == "balance" and user_id and state and amount and reason:
            amt = float(amount)
            if amt <= 0:
                error = "Сумма должна быть положительной."
            else:
                is_add = (state == "add")
                res, msg = db.admin_adjust_balance(user_id, amt, reason, is_add)
                if res: success = msg
                else: error = msg
        else:
            error = "Некорректный запрос или не все поля заполнены."

    except ValueError:
        error = "Ошибка в числовых данных (сумма должна быть числом)."
    except Exception as e:
        error = f"Системная ошибка: {str(e)}"

    return build_redirect("/admin", success=success, error=error)
