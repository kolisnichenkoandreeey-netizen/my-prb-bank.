"""
ZET BANK - Высоконагруженная банковская система (Flask & Google Sheets API)
Архитектура: Monolithic Single-File App
Стиль: Liquid Glass (Dark Theme, Neon Gold & Purple)
Особенности: 
- База данных полностью на Google Sheets.
- Интеграция Бизнес-Счетов и системы ролей сотрудников.
- Автоматическое начисление процентов по кредиту (Автоматизация дат).
"""

import os
import json
import gspread
import urllib.parse  # <--- Добавь это
from datetime import datetime, timedelta  # <--- Теперь тут два импорта
from google.oauth2 import service_account
from flask import Flask, request, jsonify, redirect, url_for, render_template_string, make_response
app = Flask(__name__)
# Получаем ключ из переменной окружения
creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if not creds_json:
    raise ValueError("Ошибка: Переменная GOOGLE_APPLICATION_CREDENTIALS_JSON не найдена!")

# Преобразуем JSON-строку в словарь
creds_dict = json.loads(creds_json)

# Используем правильный метод авторизации
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# Подключение к таблице
sheet = client.open("ZET_BANK_DB").sheet1
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
            --info: #00d2ff;
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

        .btn-danger { background: linear-gradient(45deg, #8b0000, #ff0000); }
        .btn-danger:hover { background: #ff4c4c; box-shadow: 0 0 15px #ff4c4c; }

        .btn-info { background: linear-gradient(45deg, #004d80, #0088cc); }
        .btn-info:hover { background: #00d2ff; color: black; box-shadow: 0 0 15px #00d2ff; }

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

        th { color: var(--gold); font-family: 'Orbitron', sans-serif; }
        tr:hover { background: rgba(138, 43, 226, 0.1); }

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

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }

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
    def __init__(self):
        creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        creds_dict = json.loads(creds_json)
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        self.doc = client.open("ZET_BANK_DB")
        self.sheet = self.doc.sheet1
        self.sheet_users = self.get_or_create_sheet("Users", 1000, 10)
        self.sheet_businesses = self.get_or_create_sheet("Businesses", 100, 4)
        self.sheet_employees = self.get_or_create_sheet("Employees", 500, 3)
        self.users = {}
        self.businesses = {}
        self.employees = []
        self.system_logs = []
        self.load()
        self.init_db()

    def get_or_create_sheet(self, title, rows, cols):
        try:
            return self.doc.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            return self.doc.add_worksheet(title, rows, cols)

    def init_db(self):
        if not self.users:
            self.users["1000"] = {
                "name": "Системный Администратор",
                "pin": "7777",
                "balance": 1000000.0,
                "savings": 0.0,
                "credit": 0.0,
                "credit_date": "",
                "banned": False,
                "role": "admin",
                "logs": []
            }
            self.save_users()
    # <--- Здесь функция init_db заканчивается, отступ возвращается к уровню класса (4 пробела)

    def find_user_by_name(self, name_query):
        results = []
        for user_id, data in self.users.items():
            if name_query.lower() in data.get("name", "").lower():
                user_info = data.copy()
                user_info["id"] = user_id
                results.append(user_info)
        return results

    def load(self):
        # ... твой код ...
        """Считывает данные из Google Sheets (Кеширование)"""
        # Считываем пользователей
        users_records = self.sheet_users.get_all_records()
        self.users = {}
        for r in users_records:
            try:
                logs = json.loads(r.get('logs', '[]'))
            except:
                logs = []
            
            self.users[str(r.get('id', ''))] = {
                "name": str(r.get('name', 'Неизвестно')),
                "pin": str(r.get('pin', '0000')),
                "balance": float(r.get('balance', 0)),
                "savings": float(r.get('savings', 0)),
                "credit": float(r.get('credit', 0)),
                "credit_date": str(r.get('credit_date', '')),
                "banned": str(r.get('banned', 'False')).lower() == 'true',
                "role": str(r.get('role', 'user')),
                "logs": logs
            }

        # Считываем бизнесы
        biz_records = self.sheet_businesses.get_all_records()
        self.businesses = {str(r.get('id', '')): {
            "name": str(r.get('name', '')),
            "balance": float(r.get('balance', 0)),
            "owner_id": str(r.get('owner_id', ''))
        } for r in biz_records if r.get('id')}

        # Считываем сотрудников
        emp_records = self.sheet_employees.get_all_records()
        self.employees = [{
            "business_id": str(r.get('business_id', '')),
            "user_id": str(r.get('user_id', '')),
            "role": str(r.get('role', 'worker'))
        } for r in emp_records if r.get('business_id')]

    # --- СОХРАНЕНИЕ ---

    def save_users(self):
        data = [["id", "name", "pin", "balance", "savings", "credit", "credit_date", "banned", "role", "logs"]]
        for cid, u in self.users.items():
            data.append([
                cid, u["name"], u["pin"], u["balance"], u["savings"], u["credit"],
                u.get("credit_date", ""), str(u["banned"]), u["role"], json.dumps(u["logs"])
            ])
        self.sheet_users.clear()
        if len(data) > 1:
            self.sheet_users.update(values=data)

    def save_businesses(self):
        data = [["id", "name", "balance", "owner_id"]]
        for bid, b in self.businesses.items():
            data.append([bid, b["name"], b["balance"], b["owner_id"]])
        self.sheet_businesses.clear()
        if len(data) > 1:
            self.sheet_businesses.update(values=data)

    def save_employees(self):
        data = [["business_id", "user_id", "role"]]
        for e in self.employees:
            data.append([e["business_id"], e["user_id"], e["role"]])
        self.sheet_employees.clear()
        if len(data) > 1:
            self.sheet_employees.update(values=data)

    # --- ЛОГИРОВАНИЕ ---

    def log_system_action(self, action: str, details: str):
        ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.system_logs.insert(0, {"time": ts, "action": action, "details": details})
        self.system_logs = self.system_logs[:100]

    def log_user_action(self, cid: str, message: str, auto_save: bool = True):
        if cid in self.users:
            ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.users[cid]["logs"].insert(0, {"time": ts, "msg": message})
            self.users[cid]["logs"] = self.users[cid]["logs"][:50]
            if auto_save:
                self.save_users()

    # --- БАЗОВЫЕ МЕТОДЫ ---

    def get_user(self, cid: str) -> Optional[Dict[str, Any]]:
        return self.users.get(cid)

    def find_users_by_name(self, name: str) -> List[str]:
        target = name.strip().lower()
        return [cid for cid, u in self.users.items() if u["name"].strip().lower() == target]

    def authenticate(self, cid: str, pin: str) -> bool:
        user = self.get_user(cid)
        return bool(user and user["pin"] == pin)

    # --- АВТОМАТИЗАЦИЯ КРЕДИТОВ ---
    def process_automatic_payments(self):
        changed = False
        now = datetime.now()
        for cid, u in self.users.items():
            if u.get("credit", 0) > 0:
                c_date_str = u.get("credit_date", "")
                if c_date_str:
                    try:
                        c_date = datetime.strptime(c_date_str, "%Y-%m-%d")
                        if now >= c_date:
                            interest = u["credit"] * 0.05  # 5% ставка за период (30 дней)
                            u["balance"] -= interest
                            u["credit_date"] = (c_date + timedelta(days=30)).strftime("%Y-%m-%d")
                            u["logs"].insert(0, {
                                "time": now.strftime("%d.%m.%Y %H:%M:%S"), 
                                "msg": f"Авто-списание % по кредиту: {interest:.2f} ₽"
                            })
                            changed = True
                    except ValueError:
                        pass
        if changed:
            self.save_users()

    # --- ФИНАНСОВЫЕ ОПЕРАЦИИ (ПОЛЬЗОВАТЕЛИ) ---

    def process_transfer(self, sender_id: str, recipient_name: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        
        sender = self.get_user(sender_id)
        if not sender: return False, "Отправитель не найден."
        if sender["banned"]: return False, "Ваш счет заблокирован. Операция отклонена."
        if sender["balance"] < amount: return False, "Недостаточно средств на основном счете."

        matches = self.find_users_by_name(recipient_name)
        if not matches: return False, f"Получатель с именем '{recipient_name}' не найден."
        if len(matches) > 1: return False, f"Найдено несколько пользователей '{recipient_name}'."
        
        recipient_id = matches[0]
        if sender_id == recipient_id: return False, "Нельзя перевести средства самому себе."

        recipient = self.get_user(recipient_id)
        if recipient["banned"]: return False, "Счет получателя заблокирован."

        sender["balance"] -= amount
        recipient["balance"] += amount

        self.log_user_action(sender_id, f"Перевод {amount:.2f} ₽ -> {recipient['name']}.", auto_save=False)
        self.log_user_action(recipient_id, f"Получено {amount:.2f} ₽ <- {sender['name']}.", auto_save=False)
        self.log_system_action("Перевод", f"{sender_id} -> {recipient_id}: {amount:.2f} ₽")
        self.save_users()
        return True, "Перевод успешно завершен."

    def process_savings(self, cid: str, action: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        user = self.get_user(cid)
        if not user or user["banned"]: return False, "Операция недоступна."

        if action == "deposit":
            if user["balance"] < amount: return False, "Недостаточно средств."
            user["balance"] -= amount
            user["savings"] += amount
            self.log_user_action(cid, f"Пополнение вклада: {amount:.2f} ₽")
            return True, "Вклад пополнен."
        elif action == "withdraw":
            if user["savings"] < amount: return False, "Недостаточно средств на вкладе."
            user["savings"] -= amount
            user["balance"] += amount
            self.log_user_action(cid, f"Снятие со вклада: {amount:.2f} ₽")
            return True, "Средства сняты."
        return False, "Неизвестная операция."

    def process_credit(self, cid: str, action: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        user = self.get_user(cid)
        if not user or user["banned"]: return False, "Операция недоступна."

        if action == "take":
            if user["credit"] + amount > 5000000: return False, "Превышен лимит."
            user["credit"] += amount
            user["balance"] += amount
            
            # Установка даты первой выплаты процента (через 30 дней)
            if not user.get("credit_date"):
                user["credit_date"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                
            self.log_user_action(cid, f"Взят кредит: {amount:.2f} ₽")
            return True, "Кредит оформлен."
        elif action == "pay":
            if user["balance"] < amount: return False, "Недостаточно средств."
            actual = min(amount, user["credit"])
            if actual <= 0: return False, "У вас нет задолженностей."
            
            user["balance"] -= actual
            user["credit"] -= actual
            
            # Очистка даты, если кредит закрыт
            if user["credit"] <= 0:
                user["credit_date"] = ""
                
            self.log_user_action(cid, f"Погашение кредита: {actual:.2f} ₽")
            return True, f"Погашено {actual:.2f} ₽."
        return False, "Неизвестная операция."

    # --- ФИНАНСОВЫЕ ОПЕРАЦИИ (БИЗНЕС) ---

    def process_business_payment(self, cid: str, biz_id: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        user = self.get_user(cid)
        biz = self.businesses.get(biz_id)
        if not user or not biz: return False, "Системная ошибка. Данные не найдены."
        if user["banned"]: return False, "Ваш счет заблокирован."
        if user["balance"] < amount: return False, "Недостаточно средств."

        user["balance"] -= amount
        biz["balance"] += amount

        self.log_user_action(cid, f"Оплата услуг бизнеса '{biz['name']}': {amount:.2f} ₽", auto_save=False)
        self.save_users()
        self.save_businesses()
        return True, "Оплата успешно выполнена."

    def process_business_transfer(self, cid: str, biz_id: str, recipient_name: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0: return False, "Сумма должна быть больше нуля."
        biz = self.businesses.get(biz_id)
        if not biz: return False, "Бизнес не найден."
        
        # Проверка прав доступа
        role = "owner" if biz["owner_id"] == cid else None
        if not role:
            emp = next((e for e in self.employees if e["business_id"] == biz_id and e["user_id"] == cid), None)
            if emp: role = emp["role"]

        if role not in ["owner", "manager"]:
            return False, "У вас нет прав (требуется Owner или Manager)."
            
        if biz["balance"] < amount: return False, "Недостаточно средств на счете бизнеса."

        matches = self.find_users_by_name(recipient_name)
        if not matches: return False, "Получатель не найден."
        if len(matches) > 1: return False, "Найдено несколько получателей. Уточните имя."

        recipient = self.get_user(matches[0])
        biz["balance"] -= amount
        recipient["balance"] += amount

        self.log_user_action(matches[0], f"Поступление от бизнеса '{biz['name']}': {amount:.2f} ₽", auto_save=False)
        self.save_businesses()
        self.save_users()
        return True, "Средства успешно переведены со счета бизнеса."

    def assign_employee(self, cid: str, biz_id: str, emp_user_id: str, role: str) -> Tuple[bool, str]:
        biz = self.businesses.get(biz_id)
        if not biz: return False, "Бизнес не найден."
        if biz["owner_id"] != cid: return False, "Только владелец может назначать сотрудников."
        if not self.get_user(emp_user_id): return False, "Пользователь-сотрудник не найден."
        
        # Удаляем старую запись, если есть
        self.employees = [e for e in self.employees if not (e["business_id"] == biz_id and e["user_id"] == emp_user_id)]
        self.employees.append({"business_id": biz_id, "user_id": emp_user_id, "role": role})
        self.save_employees()
        return True, f"Сотрудник {emp_user_id} назначен ({role})."

    # --- АДМИН ПАНЕЛЬ ---

    def admin_create_user(self, name: str, pin: str) -> str:
        existing_ids = [int(k) for k in self.users.keys() if k.isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1000"
        self.users[new_id] = {
            "name": name, "pin": pin, "balance": 0.0, "savings": 0.0,
            "credit": 0.0, "credit_date": "", "banned": False, "role": "user", "logs": []
        }
        self.log_system_action("Создан пользователь", f"ID: {new_id}, Имя: {name}")
        self.save_users()
        return new_id

    def admin_create_business(self, name: str, owner_id: str) -> Tuple[bool, str]:
        if not self.get_user(owner_id): return False, "Владелец не найден."
        existing_ids = [int(k[1:]) for k in self.businesses.keys() if k.startswith('b') and k[1:].isdigit()]
        new_id = f"b{max(existing_ids) + 1}" if existing_ids else "b100"
        
        self.businesses[new_id] = {"name": name, "balance": 0.0, "owner_id": owner_id}
        self.log_system_action("Создан бизнес", f"ID: {new_id}, Владелец: {owner_id}")
        self.save_businesses()
        return True, f"Бизнес создан (ID: {new_id})."

    def admin_adjust_balance(self, cid: str, amount: float, reason: str, is_add: bool, account_type="balance") -> Tuple[bool, str]:
        user = self.get_user(cid)
        if not user: return False, "Пользователь не найден."
        
        if is_add:
            user[account_type] += amount
            action_log = f"Начислено ({account_type}): {amount:.2f} ₽. Причина: {reason}"
        else:
            if user[account_type] < amount: return False, "Недостаточно средств."
            user[account_type] -= amount
            action_log = f"Списано ({account_type}): {amount:.2f} ₽. Причина: {reason}"

        self.log_user_action(cid, f"Админ: {action_log}", auto_save=False)
        self.log_system_action(f"Корректировка {account_type}", f"ID: {cid} | {action_log}")
        self.save_users()
        return True, "Успешно скорректировано."


# Инициализация БД и Приложения
db = BankDatabase()
app = Flask(__name__)
ADMIN_PASSWORD = "admin"

# ==========================================
# 3. HTML ШАБЛОНЫ (JINJA2 + FLASK)
# ==========================================

def render_layout(title: str, content: str) -> str:
    template = f"""
    <!DOCTYPE html>
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
                    {{% if user and user.role == 'admin' %}}
                        <a href="/admin">Админка</a>
                    {{% endif %}}
                </div>
            </div>
            {{% if error %}}<div class='alert-error'><strong>Ошибка:</strong> {{{{ error }}}}</div>{{% endif %}}
            {{% if success %}}<div class='alert-success'><strong>Успешно:</strong> {{{{ success }}}}</div>{{% endif %}}
            {content}
        </div>
    </body>
    </html>
    """
    return template

def build_redirect(url: str, error: str = "", success: str = ""):
    params = []
    if error: params.append(f"error={urllib.parse.quote(error)}")
    if success: params.append(f"success={urllib.parse.quote(success)}")
    final_url = f"{url}?{'&'.join(params)}" if params else url
    return redirect(final_url)

@app.before_request
def auto_payments_hook():
    # Проверяем автоматические платежи перед каждым запросом (выполняется сохранение только если дата пришла)
    db.process_automatic_payments()

# ==========================================
# 4. РОУТЫ (ENDPOINTS)
# ==========================================

@app.route("/")
def index():
    cid = request.cookies.get("citizen_id")
    user = db.get_user(cid) if cid else None
    if user:
        return redirect("/cabinet")
        
    error = request.args.get("error", "")
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
    return render_template_string(render_layout("Вход", content), error=error, user=user)

@app.route("/login", methods=["POST"])
def login():
    cid = request.form.get("cid", "")
    pin = request.form.get("pin", "")
    if db.authenticate(cid, pin):
        resp = make_response(redirect("/cabinet"))
        resp.set_cookie("citizen_id", cid, max_age=86400, httponly=True)
        return resp
    return build_redirect("/", error="Неверный ID или PIN-код")

@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie("citizen_id", "", expires=0)
    return resp

@app.route("/cabinet")
def cabinet():
    cid = request.cookies.get("citizen_id")
    user = db.get_user(cid) if cid else None
    if not user:
        return build_redirect("/", error="Пожалуйста, авторизуйтесь.")

    error = request.args.get("error", "")
    success = request.args.get("success", "")

    if user["banned"]:
        content = """
        <div class="glass-card alert-error" style="text-align: center;">
            <h2>ВАШ АККАУНТ ЗАБЛОКИРОВАН</h2>
            <p>Доступ к финансовым операциям приостановлен. Обратитесь к администратору.</p>
            <br>
            <a href="/logout"><button class="btn-danger" style="max-width: 200px;">Выйти</button></a>
        </div>"""
        return render_template_string(render_layout("Блокировка", content), user=user)

    # Определяем доступы бизнеса для пользователя
    my_businesses = []
    for bid, b in db.businesses.items():
        role = "owner" if b["owner_id"] == cid else None
        if not role:
            emp = next((e for e in db.employees if e["business_id"] == bid and e["user_id"] == cid), None)
            if emp: role = emp["role"]
        
        if role:
            my_businesses.append({"id": bid, "name": b["name"], "balance": b["balance"], "role": role})

    content = """
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>Добро пожаловать, {{ user.name }} <span style="font-size: 0.5em; color: gray;">(ID: {{ cid }})</span></h2>
        <a href="/logout"><button class="btn-danger" style="width: auto; padding: 10px 20px;">Выход</button></a>
    </div>

    <div class="grid-3">
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #fff;">Основной счет</h3>
            <div class="balance-display">{{ "%.2f"|format(user.balance) }} ₽</div>
        </div>
        <div class="glass-card" style="text-align: center; border-color: rgba(0, 255, 136, 0.3);">
            <h3 style="color: var(--success);">Накопления</h3>
            <div class="balance-display" style="text-shadow: 0 0 15px var(--success);">{{ "%.2f"|format(user.savings) }} ₽</div>
        </div>
        <div class="glass-card" style="text-align: center; border-color: rgba(255, 76, 76, 0.3);">
            <h3 style="color: var(--danger);">Кредит</h3>
            <div class="balance-display" style="text-shadow: 0 0 15px var(--danger);">{{ "%.2f"|format(user.credit) }} ₽</div>
            {% if user.credit_date %}
                <small style="color: #ccc;">След. процент: {{ user.credit_date }}</small>
            {% endif %}
        </div>
    </div>

    <div class="grid-3">
        <!-- ПЕРЕВОДЫ -->
        <div class="glass-card">
            <h3>Перевод средств</h3>
            <form action="/transfer" method="POST">
                <input type="text" name="recipient_name" placeholder="Имя получателя (точно)" required>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <button type="submit">Отправить</button>
            </form>
        </div>

        <!-- ОПЛАТА БИЗНЕСУ -->
        <div class="glass-card">
            <h3 style="color: var(--info);">Оплата услуг</h3>
            <form action="/biz/pay" method="POST">
                <select name="biz_id" required>
                    {% for bid, b in db.businesses.items() %}
                        <option value="{{ bid }}">{{ b.name }}</option>
                    {% endfor %}
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <button type="submit" class="btn-info">Оплатить</button>
            </form>
        </div>

        <!-- УПРАВЛЕНИЕ -->
        <div class="glass-card">
            <h3 style="color: var(--success);">Вклад / Кредит</h3>
            <form action="/savings_credit" method="POST">
                <select name="action_type" required>
                    <option value="savings_deposit">Положить на вклад</option>
                    <option value="savings_withdraw">Снять со вклада</option>
                    <option value="credit_take">Взять кредит</option>
                    <option value="credit_pay">Погасить кредит</option>
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <button type="submit" style="background: linear-gradient(45deg, #004d00, #00b300);">Выполнить</button>
            </form>
        </div>
    </div>

    {% if my_businesses %}
    <h2>Бизнес-Кабинет</h2>
    <div class="grid-2">
        {% for b in my_businesses %}
        <div class="glass-card" style="border-color: var(--info);">
            <h3 style="color: var(--info);">{{ b.name }} <span style="font-size:0.6em; color:gray;">({{ b.role }})</span></h3>
            <div class="balance-display" style="font-size: 2rem;">{{ "%.2f"|format(b.balance) }} ₽</div>
            
            {% if b.role in ['owner', 'manager'] %}
            <form action="/biz/transfer" method="POST" style="margin-top: 15px;">
                <input type="hidden" name="biz_id" value="{{ b.id }}">
                <input type="text" name="recipient_name" placeholder="Имя получателя (человека)" required>
                <input type="number" step="0.01" name="amount" placeholder="Сумма списания" required>
                <button type="submit" class="btn-danger">Перевод со счета бизнеса</button>
            </form>
            {% endif %}
            
            {% if b.role == 'owner' %}
            <form action="/biz/employee" method="POST" style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <h4>Назначить сотрудника</h4>
                <input type="hidden" name="biz_id" value="{{ b.id }}">
                <input type="text" name="emp_user_id" placeholder="Citizen ID пользователя" required>
                <select name="emp_role" required>
                    <option value="manager">Менеджер (Управление счетом)</option>
                    <option value="worker">Работник (Только просмотр)</option>
                </select>
                <button type="submit" style="background: linear-gradient(45deg, #4b0082, #8A2BE2);">Назначить</button>
            </form>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="glass-card">
        <h3>История операций</h3>
        <table>
            <tr><th>Время</th><th>Операция</th></tr>
            {% for log in user.logs %}
                <tr><td>{{ log.time }}</td><td>{{ log.msg }}</td></tr>
            {% else %}
                <tr><td colspan='2'>История операций пуста.</td></tr>
            {% endfor %}
        </table>
    </div>
    """
    return render_template_string(render_layout("Личный Кабинет", content), 
                                  user=user, cid=cid, db=db, my_businesses=my_businesses, 
                                  error=error, success=success)


@app.route("/transfer", methods=["POST"])
def transfer():
    cid = request.cookies.get("citizen_id")
    if not cid: return redirect("/")
    try:
        amount = float(request.form.get("amount", 0))
        recipient = request.form.get("recipient_name", "")
        success, msg = db.process_transfer(cid, recipient, amount)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")

@app.route("/savings_credit", methods=["POST"])
def savings_credit():
    cid = request.cookies.get("citizen_id")
    if not cid: return redirect("/")
    try:
        action_type = request.form.get("action_type", "")
        amount = float(request.form.get("amount", 0))
        
        if "savings_" in action_type:
            success, msg = db.process_savings(cid, action_type.replace("savings_", ""), amount)
        elif "credit_" in action_type:
            success, msg = db.process_credit(cid, action_type.replace("credit_", ""), amount)
        else:
            success, msg = False, "Неизвестная операция."
            
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")

@app.route("/biz/pay", methods=["POST"])
def biz_pay():
    cid = request.cookies.get("citizen_id")
    if not cid: return redirect("/")
    try:
        amount = float(request.form.get("amount", 0))
        biz_id = request.form.get("biz_id", "")
        success, msg = db.process_business_payment(cid, biz_id, amount)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")

@app.route("/biz/transfer", methods=["POST"])
def biz_transfer():
    cid = request.cookies.get("citizen_id")
    if not cid: return redirect("/")
    try:
        amount = float(request.form.get("amount", 0))
        biz_id = request.form.get("biz_id", "")
        recipient = request.form.get("recipient_name", "")
        success, msg = db.process_business_transfer(cid, biz_id, recipient, amount)
        return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")
    except ValueError:
        return build_redirect("/cabinet", error="Некорректная сумма.")

@app.route("/biz/employee", methods=["POST"])
def biz_employee():
    cid = request.cookies.get("citizen_id")
    if not cid: return redirect("/")
    biz_id = request.form.get("biz_id", "")
    emp_user_id = request.form.get("emp_user_id", "")
    emp_role = request.form.get("emp_role", "")
    
    success, msg = db.assign_employee(cid, biz_id, emp_user_id, emp_role)
    return build_redirect("/cabinet", success=msg if success else "", error=msg if not success else "")


# ==========================================
# 5. АДМИН-ПАНЕЛЬ
# ==========================================

@app.route("/admin")
def admin():
    cid = request.cookies.get("citizen_id")
    user = db.get_user(cid) if cid else None
    if not user or user.get("role") != "admin":
        return build_redirect("/", error="Нет доступа.")

    admin_token = request.cookies.get("admin_token")
    error = request.args.get("error", "")
    success = request.args.get("success", "")

    if admin_token != "authed_admin":
        content = """
        <div class="glass-card" style="max-width: 400px; margin: 50px auto; text-align: center;">
            <h2>Доступ Администратора</h2>
            <form action="/admin/login" method="POST">
                <input type="password" name="password" placeholder="Root Password" required>
                <button type="submit" class="btn-danger">Подтвердить</button>
            </form>
        </div>
        """
        return render_template_string(render_layout("Админка - Вход", content), user=user, error=error)

    content = """
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>Панель Управления Системой</h2>
        <a href="/admin/logout"><button class="btn-danger" style="width: auto;">Закрыть ПУ</button></a>
    </div>

    <div class="grid-3">
        <div class="glass-card">
            <h3>Создать пользователя</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="create">
                <input type="text" name="name" placeholder="ФИО" required>
                <input type="text" name="pin" placeholder="PIN-код" required>
                <button type="submit">Создать</button>
            </form>
        </div>

        <div class="glass-card" style="border-color: var(--info);">
            <h3 style="color: var(--info);">Создать бизнес</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="create_biz">
                <input type="text" name="name" placeholder="Название бизнеса" required>
                <input type="text" name="user_id" placeholder="ID владельца" required>
                <button type="submit" class="btn-info">Создать бизнес</button>
            </form>
        </div>

        <div class="glass-card">
            <h3>Статус / PIN</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="status_pin">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <select name="state">
                    <option value="none">--- Выберите действие ---</option>
                    <option value="ban">Забанить</option>
                    <option value="unban">Разбанить</option>
                    <option value="change_pin">Сменить PIN (указать ниже)</option>
                </select>
                <input type="text" name="pin" placeholder="Новый PIN-код">
                <button type="submit" class="btn-danger">Применить</button>
            </form>
        </div>
    </div>

    <div class="grid-2">
        <div class="glass-card">
            <h3>Корректировка Баланса</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="balance">
                <input type="hidden" name="account_type" value="balance">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <select name="state" required><option value="add">Начислить</option><option value="sub">Списать</option></select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <input type="text" name="reason" placeholder="Причина (обязательно)" required>
                <button type="submit" style="background: linear-gradient(45deg, #b8860b, var(--gold)); color: black;">Выполнить</button>
            </form>
        </div>

        <div class="glass-card" style="border-color: var(--success);">
            <h3 style="color: var(--success);">Управление Вкладами</h3>
            <form action="/admin/action" method="POST">
                <input type="hidden" name="action_type" value="balance">
                <input type="hidden" name="account_type" value="savings">
                <input type="text" name="user_id" placeholder="ID пользователя" required>
                <select name="state" required><option value="add">Пополнить вклад</option><option value="sub">Снять со вклада</option></select>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <input type="text" name="reason" placeholder="Причина (обязательно)" required>
                <button type="submit" style="background: linear-gradient(45deg, #004d00, #00b300);">Выполнить</button>
            </form>
        </div>
    </div>

    <div class="glass-card">
        <h3>Все пользователи</h3>
        <table>
            <tr><th>ID</th><th>Имя</th><th>Баланс</th><th>Вклад</th><th>Роль</th><th>Статус</th></tr>
            {% for uid, u in db.users.items() %}
            <tr>
                <td>{{ uid }}</td>
                <td>{{ u.name }}</td>
                <td>{{ "%.2f"|format(u.balance) }}</td>
                <td>{{ "%.2f"|format(u.savings) }}</td>
                <td>{{ u.role }}</td>
                <td>{% if u.banned %}<span style='color:red;'>ЗАБАНЕН</span>{% else %}<span style='color:green;'>АКТИВЕН</span>{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    """
    return render_template_string(render_layout("Админка", content), user=user, db=db, error=error, success=success)

@app.route("/admin/login", methods=["POST"])
def admin_login():
    if request.form.get("password") == ADMIN_PASSWORD:
        resp = make_response(redirect("/admin"))
        resp.set_cookie("admin_token", "authed_admin", httponly=True)
        return resp
    return build_redirect("/admin", error="Неверный пароль администратора.")

@app.route("/admin/logout")
def admin_logout():
    resp = make_response(redirect("/cabinet"))
    resp.set_cookie("admin_token", "", expires=0)
    return resp

@app.route("/admin/action", methods=["POST"])
def admin_action():
    if request.cookies.get("admin_token") != "authed_admin":
        return redirect("/")

    action_type = request.form.get("action_type")
    user_id = request.form.get("user_id")
    
    success_msg, error_msg = "", ""

    try:
        if action_type == "create":
            name, pin = request.form.get("name"), request.form.get("pin")
            if name and pin:
                new_id = db.admin_create_user(name, pin)
                success_msg = f"Пользователь '{name}' создан. ID: {new_id}"
                
        elif action_type == "create_biz":
            name, owner_id = request.form.get("name"), request.form.get("user_id")
            if name and owner_id:
                res, msg = db.admin_create_business(name, owner_id)
                if res: success_msg = msg
                else: error_msg = msg

        elif action_type == "status_pin":
            state = request.form.get("state")
            user = db.get_user(user_id)
            if not user: error_msg = "Пользователь не найден."
            elif state == "ban":
                user["banned"] = True
                db.log_system_action("Бан", f"ID: {user_id}")
                db.save_users()
                success_msg = "Пользователь забанен."
            elif state == "unban":
                user["banned"] = False
                db.log_system_action("Разбан", f"ID: {user_id}")
                db.save_users()
                success_msg = "Пользователь разбанен."
            elif state == "change_pin":
                pin = request.form.get("pin")
                if pin:
                    user["pin"] = pin
                    db.save_users()
                    success_msg = "PIN изменен."

        elif action_type == "balance":
            account_type = request.form.get("account_type", "balance")
            state = request.form.get("state")
            amount = float(request.form.get("amount", 0))
            reason = request.form.get("reason", "")
            
            if amount <= 0: error_msg = "Сумма должна быть положительной."
            else:
                res, msg = db.admin_adjust_balance(user_id, amount, reason, state == "add", account_type)
                if res: success_msg = msg
                else: error_msg = msg
                
    except Exception as e:
        error_msg = f"Ошибка выполнения: {str(e)}"

    return build_redirect("/admin", success=success_msg, error=error_msg)

# --- Поиск получателя для переводов ---
@app.route('/find_recipient', methods=['GET', 'POST'])
def find_recipient():
    results = []
    if request.method == 'POST':
        query = request.form.get('name')
        results = db.find_user_by_name(query)
    
    return render_template_string('''
        <h2>Поиск получателя</h2>
        <form method="POST">
            <input type="text" name="name" placeholder="Введите имя" required>
            <button type="submit">Найти</button>
        </form>
        <hr>
        {% for user in results %}
            <div style="margin: 10px 0;">
                {{ user.name }} (ID: {{ user.id }})
                <a href="/transfer?target_id={{ user.id }}">Выбрать</a>
            </div>
        {% endfor %}
        <br><a href="/transfer">Назад к переводу</a>
    ''', results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
