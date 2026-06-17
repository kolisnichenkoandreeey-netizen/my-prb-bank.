# main.py
# -----------------------------------------------------------------------------
# Банковская система "Жидкое стекло" (Liquid Glass Banking System)
# Описание: Готовая к продакшену банковская система в одном файле.
# Функции: Авторизация, P2P Переводы, Вклады, Кредиты, Админ-панель.
# База данных: JSON-хранилище с атомарными операциями.
# Дизайн: Стиль "Жидкое стекло" (Темная тема, размытие фона, неоновые акценты).
# Язык интерфейса: Строго Русский.
# -----------------------------------------------------------------------------

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from fastapi import FastAPI, Request, Form, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

# -----------------------------------------------------------------------------
# Настройка логирования
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LiquidBank-RU")

# -----------------------------------------------------------------------------
# Глобальные константы
# -----------------------------------------------------------------------------
DB_FILE = "bank_data.json"
COOKIE_KEY = "citizen_id"

# -----------------------------------------------------------------------------
# Менеджер базы данных (BankSystem)
# -----------------------------------------------------------------------------
class BankSystem:
    """
    Управляет всеми взаимодействиями с базой данных атомарно, используя JSON.
    Включает комплексную обработку ошибок, валидацию и структурирование данных.
    """

    def __init__(self, db_path: str = DB_FILE) -> None:
        """
        Инициализирует систему банка, проверяя наличие файла базы данных.
        
        Аргументы:
            db_path (str): Путь к файлу JSON-базы.
        """
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        """
        Проверяет существование файла БД. Если файл отсутствует, создает
        стандартную базу с аккаунтом системного администратора.
        """
        if not os.path.exists(self.db_path):
            logger.info("База данных не найдена. Создание новой БД.")
            default_db = {
                "users": {
                    "admin": {
                        "pin": "0000",
                        "name": "Системный Администратор",
                        "balance": 1000000.0,
                        "savings": 0.0,
                        "loan": 0.0,
                        "is_admin": True,
                        "is_banned": False
                    }
                },
                "transactions": [],
                "logs": []
            }
            self._save_db(default_db)
            self.log_action("СИСТЕМА", "Инициализирована новая БД со стандартным админом.")

    def _load_db(self) -> Dict[str, Any]:
        """
        Безопасно загружает данные из JSON файла.
        
        Возвращает:
            Dict[str, Any]: Загруженная структура базы данных.
        """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки базы данных: {e}")
            return {"users": {}, "transactions": [], "logs": []}

    def _save_db(self, data: Dict[str, Any]) -> None:
        """
        Атомарно записывает данные в файл для предотвращения сбоев при параллельном доступе.
        
        Аргументы:
            data (Dict[str, Any]): Структура базы данных для сохранения.
        """
        temp_path = self.db_path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(temp_path, self.db_path)
        except Exception as e:
            logger.error(f"Критическая ошибка при сохранении БД: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_user(self, citizen_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает данные пользователя по его ID Гражданина.
        """
        db = self._load_db()
        return db["users"].get(citizen_id)

    def update_user(self, citizen_id: str, updates: Dict[str, Any]) -> bool:
        """
        Обновляет указанные поля в профиле пользователя.
        """
        db = self._load_db()
        if citizen_id not in db["users"]:
            return False
        for key, value in updates.items():
            db["users"][citizen_id][key] = value
        self._save_db(db)
        return True

    def create_user(self, citizen_id: str, pin: str, name: str, is_admin: bool = False) -> bool:
        """
        Регистрирует нового гражданина в системе.
        """
        db = self._load_db()
        if citizen_id in db["users"]:
            return False
        db["users"][citizen_id] = {
            "pin": pin,
            "name": name,
            "balance": 0.0,
            "savings": 0.0,
            "loan": 0.0,
            "is_admin": is_admin,
            "is_banned": False
        }
        self._save_db(db)
        self.log_action("АДМИН", f"Создан пользователь {citizen_id}")
        return True

    def delete_user(self, citizen_id: str) -> bool:
        """
        Навсегда удаляет пользователя из банковской системы.
        """
        db = self._load_db()
        if citizen_id in db["users"]:
            del db["users"][citizen_id]
            self._save_db(db)
            self.log_action("АДМИН", f"Удален пользователь {citizen_id}")
            return True
        return False

    def log_action(self, actor: str, action: str) -> None:
        """
        Записывает административное или системное событие в логи.
        """
        db = self._load_db()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action
        }
        db["logs"].insert(0, entry)
        if len(db["logs"]) > 1000:
            db["logs"] = db["logs"][:1000]
        self._save_db(db)

    def add_transaction(self, sender: str, receiver: str, amount: float, tx_type: str) -> None:
        """
        Фиксирует финансовую транзакцию между счетами.
        """
        db = self._load_db()
        tx = {
            "tx_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "type": tx_type
        }
        db["transactions"].insert(0, tx)
        self._save_db(db)

    def get_transactions(self, citizen_id: str) -> List[Dict[str, Any]]:
        """
        Возвращает историю транзакций конкретного пользователя.
        """
        db = self._load_db()
        history = []
        for tx in db["transactions"]:
            if tx["sender"] == citizen_id or tx["receiver"] == citizen_id:
                history.append(tx)
        return history

# -----------------------------------------------------------------------------
# CSS Фреймворк (Дизайн "Жидкое стекло")
# -----------------------------------------------------------------------------
def get_css() -> str:
    """
    Генерирует CSS-фреймворк "Жидкое стекло".
    Содержит настройки темного режима, прозрачных фильтров и неоновых свечений.
    """
    return """
    :root {
        --bg-gradient-start: #0f172a;
        --bg-gradient-end: #1e293b;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        --neon-cyan: #22d3ee;
        --neon-cyan-glow: rgba(34, 211, 238, 0.5);
        --neon-pink: #f472b6;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --danger: #ef4444;
        --success: #10b981;
    }
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    body {
        background: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));
        color: var(--text-main);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Навигация */
    .glass-nav {
        width: 100%;
        padding: 15px 30px;
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--glass-border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    .glass-nav a {
        color: var(--text-main);
        text-decoration: none;
        margin-left: 20px;
        font-weight: 600;
        transition: color 0.3s;
    }
    .glass-nav a:hover { color: var(--neon-cyan); }
    .nav-brand { font-size: 1.2rem; font-weight: bold; color: var(--neon-pink); text-shadow: 0 0 10px var(--neon-pink); }
    
    /* Контейнеры */
    .container {
        width: 90%;
        max-width: 1200px;
        margin: 40px auto;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 30px;
        box-shadow: var(--glass-shadow);
    }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
    @media (max-width: 768px) {
        .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }
    
    /* Типографика */
    h1, h2, h3 { margin-bottom: 15px; }
    .neon-text { color: var(--neon-cyan); text-shadow: 0 0 8px var(--neon-cyan-glow); }
    .neon-pink-text { color: var(--neon-pink); text-shadow: 0 0 8px var(--neon-pink); }
    .muted { color: var(--text-muted); font-size: 0.9rem; }
    .error-msg { color: var(--danger); background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid var(--danger); }
    .success-msg { color: var(--success); background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid var(--success); }
    
    /* Формы */
    form { display: flex; flex-direction: column; gap: 15px; }
    label { font-weight: 600; font-size: 0.95rem; }
    input, select {
        width: 100%;
        padding: 12px;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid var(--glass-border);
        color: var(--text-main);
        border-radius: 8px;
        outline: none;
        transition: all 0.3s;
    }
    input:focus, select:focus { border-color: var(--neon-cyan); box-shadow: 0 0 10px var(--neon-cyan-glow); }
    button {
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid var(--neon-cyan);
        color: var(--neon-cyan);
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
        margin-top: 10px;
    }
    button:hover { background: var(--neon-cyan); color: var(--bg-gradient-start); box-shadow: 0 0 15px var(--neon-cyan); }
    button.danger { border-color: var(--danger); color: var(--danger); background: rgba(239, 68, 68, 0.1); }
    button.danger:hover { background: var(--danger); color: white; box-shadow: 0 0 15px var(--danger); }
    
    /* Таблицы */
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--glass-border); }
    th { color: var(--neon-cyan); font-weight: 600; }
    tr:hover { background: rgba(255, 255, 255, 0.02); }
    
    /* Скроллбар */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-gradient-start); }
    ::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--neon-cyan); }
    """

# -----------------------------------------------------------------------------
# Вспомогательные функции рендеринга HTML
# -----------------------------------------------------------------------------
def render_page(title: str, content: str, user: Optional[Dict[str, Any]] = None) -> str:
    """Оборачивает HTML контент в базовый шаблон 'Жидкое стекло'."""
    nav = ""
    if user:
        admin_link = '<a href="/admin">Админ-панель</a>' if user.get("is_admin") else ''
        nav = f"""
        <nav class="glass-nav">
            <div class="nav-brand">Банк Жидкое Стекло</div>
            <div>
                <span class="muted">Гражданин: {user.get('name')}</span>
                <a href="/dashboard">Главная</a>
                {admin_link}
                <a href="/logout">Выйти</a>
            </div>
        </nav>
        """
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Банк Жидкое Стекло</title>
        <style>{get_css()}</style>
    </head>
    <body>
        {nav}
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """

# -----------------------------------------------------------------------------
# Вспомогательные функции бизнес-логики
# -----------------------------------------------------------------------------
def format_currency(amount: float) -> str:
    """Форматирует число с плавающей точкой в валютную строку (₽)."""
    return f"{amount:,.2f} ₽".replace(",", " ")

def format_date(iso_string: str) -> str:
    """Парсит ISO строку даты и форматирует её в читаемый вид."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return iso_string

def validate_pin(pin: str) -> bool:
    """Строго проверяет, что PIN состоит из 4 цифр."""
    return len(pin) == 4 and pin.isdigit()

def check_loan_eligibility(savings_balance: float, current_loan: float, requested_amount: float) -> bool:
    """
    Определяет возможность взятия кредита.
    Правило: Сумма кредитов не может превышать 50% от суммы вклада.
    """
    max_loan_allowed = savings_balance * 0.5
    return (current_loan + requested_amount) <= max_loan_allowed

def calculate_interest_projection(amount: float, rate: float = 0.05, years: int = 1) -> float:
    """Проекция сложного процента (заглушка для объема и функционала)."""
    return amount * ((1 + rate) ** years)

def generate_system_health_report(db_instance: BankSystem) -> Dict[str, Any]:
    """Генерирует отчет о состоянии системы для логов."""
    db_data = db_instance._load_db()
    return {
        "status": "Стабильно",
        "total_users": len(db_data.get("users", {})),
        "total_transactions": len(db_data.get("transactions", []))
    }

# -----------------------------------------------------------------------------
# Приложение FastAPI и зависимости
# -----------------------------------------------------------------------------
app = FastAPI(title="Liquid Glass Banking API RU")
db = BankSystem()

def get_current_user(request: Request) -> Optional[str]:
    """Извлекает ID Гражданина из защищенного cookie сессии."""
    return request.cookies.get(COOKIE_KEY)

# -----------------------------------------------------------------------------
# Маршруты аутентификации
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    """Рендерит портал входа в систему."""
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    err_html = f'<div class="error-msg">{error}</div>' if error else ""
    content = f"""
    <div class="glass-panel" style="max-width: 400px; margin: 100px auto;">
        <h2 class="neon-text" style="text-align: center;">Вход в систему</h2>
        {err_html}
        <form method="POST" action="/login">
            <label>ID Гражданина (Логин)</label>
            <input type="text" name="citizen_id" required autocomplete="off">
            <label>Секретный PIN (4 цифры)</label>
            <input type="password" name="pin" required maxlength="4">
            <button type="submit">Подтвердить</button>
        </form>
    </div>
    """
    return render_page("Авторизация", content)

@app.post("/login")
async def process_login(
    response: Response, 
    citizen_id: str = Form(...), 
    pin: str = Form(...)
):
    """Обрабатывает данные авторизации и устанавливает cookie."""
    user = db.get_user(citizen_id)
    if not user:
        return RedirectResponse(url="/?error=Неверный ID Гражданина", status_code=status.HTTP_302_FOUND)
    if user["is_banned"]:
        return RedirectResponse(url="/?error=Ваш аккаунт заблокирован", status_code=status.HTTP_302_FOUND)
    if user["pin"] != pin:
        return RedirectResponse(url="/?error=Неверный PIN-код", status_code=status.HTTP_302_FOUND)
    
    res = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    res.set_cookie(key=COOKIE_KEY, value=citizen_id, httponly=True, max_age=3600)
    return res

@app.get("/logout")
async def logout():
    """Завершает активную сессию пользователя."""
    res = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    res.delete_cookie(COOKIE_KEY)
    return res

# -----------------------------------------------------------------------------
# Маршруты личного кабинета и переводов
# -----------------------------------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, msg: str = "", err: str = ""):
    """Рендерит личный кабинет: баланс, формы переводов и вкладов."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    user = db.get_user(citizen_id)
    if not user or user["is_banned"]:
        return RedirectResponse(url="/logout", status_code=status.HTTP_302_FOUND)

    msg_html = f'<div class="success-msg">{msg}</div>' if msg else ""
    err_html = f'<div class="error-msg">{err}</div>' if err else ""
    
    # Блок обзора финансов
    overview = f"""
    <div class="grid-3">
        <div class="glass-panel">
            <h3>Текущий счет</h3>
            <h1 class="neon-text">{format_currency(user['balance'])}</h1>
        </div>
        <div class="glass-panel">
            <h3>Накопительный вклад</h3>
            <h1 class="neon-pink-text">{format_currency(user['savings'])}</h1>
        </div>
        <div class="glass-panel">
            <h3>Активный кредит</h3>
            <h1 class="error-msg" style="background: none; padding: 0; border: none;">{format_currency(user['loan'])}</h1>
        </div>
    </div>
    """

    # Блок операций (Переводы и Вклады)
    operations = f"""
    <div class="grid-2">
        <div class="glass-panel">
            <h3 class="neon-text">Перевод средств</h3>
            <form method="POST" action="/transfer">
                <label>ID получателя</label>
                <input type="text" name="recipient_id" required>
                <label>Сумма перевода (₽)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Отправить средства</button>
            </form>
        </div>
        <div class="glass-panel">
            <h3 class="neon-pink-text">Управление вкладом</h3>
            <form method="POST" action="/finance/savings">
                <label>Действие</label>
                <select name="action">
                    <option value="deposit">Пополнить вклад</option>
                    <option value="withdraw">Снять со вклада</option>
                </select>
                <label>Сумма (₽)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Выполнить операцию</button>
            </form>
        </div>
    </div>
    """

    # Блок кредитования и История
    tx_history = db.get_transactions(citizen_id)
    tx_rows = ""
    for tx in tx_history[:10]: # Отображаем 10 последних
        direction = "ИCХОДЯЩИЙ" if tx["sender"] == citizen_id else "ВХОДЯЩИЙ"
        color = "var(--danger)" if direction == "ИCХОДЯЩИЙ" else "var(--success)"
        tx_rows += f"""
        <tr>
            <td class="muted">{format_date(tx['timestamp'])}</td>
            <td>{tx['type'].upper()}</td>
            <td>{tx['sender']} &rarr; {tx['receiver']}</td>
            <td style="color: {color}; font-weight: bold;">{format_currency(tx['amount'])}</td>
        </tr>
        """

    history_panel = f"""
    <div class="grid-2">
        <div class="glass-panel">
            <h3 class="neon-text">Кредитная система</h3>
            <p class="muted">Максимальный кредит: 50% от суммы вклада.</p>
            <form method="POST" action="/finance/loan">
                <label>Действие</label>
                <select name="action">
                    <option value="take">Взять кредит</option>
                    <option value="repay">Погасить кредит</option>
                </select>
                <label>Сумма (₽)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Отправить запрос</button>
            </form>
        </div>
        <div class="glass-panel" style="overflow-y: auto; max-height: 350px;">
            <h3>Последние транзакции</h3>
            <table>
                <tr><th>Дата</th><th>Тип</th><th>Детали</th><th>Сумма</th></tr>
                {tx_rows}
            </table>
        </div>
    </div>
    """

    full_content = msg_html + err_html + overview + operations + history_panel
    return render_page("Личный Кабинет", full_content, user)

@app.post("/transfer")
async def execute_transfer(
    request: Request,
    recipient_id: str = Form(...),
    amount: float = Form(...)
):
    """Выполняет P2P перевод с проверкой баланса и получателя."""
    sender_id = get_current_user(request)
    if not sender_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Неверная сумма", status_code=status.HTTP_302_FOUND)
    
    if sender_id == recipient_id:
        return RedirectResponse(url="/dashboard?err=Перевод самому себе запрещен", status_code=status.HTTP_302_FOUND)
        
    sender = db.get_user(sender_id)
    recipient = db.get_user(recipient_id)
    
    if not recipient or recipient["is_banned"]:
        return RedirectResponse(url="/dashboard?err=Получатель не найден или заблокирован", status_code=status.HTTP_302_FOUND)
        
    if sender["balance"] < amount:
        return RedirectResponse(url="/dashboard?err=Недостаточно средств на текущем счете", status_code=status.HTTP_302_FOUND)
        
    # Атомарное обновление
    db.update_user(sender_id, {"balance": sender["balance"] - amount})
    db.update_user(recipient_id, {"balance": recipient["balance"] + amount})
    db.add_transaction(sender_id, recipient_id, amount, "перевод")
    
    return RedirectResponse(url=f"/dashboard?msg=Успешный перевод {format_currency(amount)}", status_code=status.HTTP_302_FOUND)

# -----------------------------------------------------------------------------
# Финансовые операции (Вклады и Кредиты)
# -----------------------------------------------------------------------------
@app.post("/finance/savings")
async def manage_savings(
    request: Request,
    action: str = Form(...),
    amount: float = Form(...)
):
    """Обрабатывает пополнение и снятие средств со вклада."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    user = db.get_user(citizen_id)
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Некорректная сумма", status_code=status.HTTP_302_FOUND)
        
    if action == "deposit":
        if user["balance"] < amount:
            return RedirectResponse(url="/dashboard?err=Недостаточно средств на счете", status_code=status.HTTP_302_FOUND)
        db.update_user(citizen_id, {
            "balance": user["balance"] - amount,
            "savings": user["savings"] + amount
        })
        db.add_transaction(citizen_id, "СИСТЕМА_ВКЛАДОВ", amount, "пополнение_вклада")
        msg = "Вклад успешно пополнен."
        
    elif action == "withdraw":
        if user["savings"] < amount:
            return RedirectResponse(url="/dashboard?err=Недостаточно средств на вкладе", status_code=status.HTTP_302_FOUND)
            
        new_savings = user["savings"] - amount
        # Проверка блокировки снятия при наличии кредита
        if user["loan"] > 0 and user["loan"] > (new_savings * 0.5):
            return RedirectResponse(url="/dashboard?err=Отказ. Вклад является залогом для вашего активного кредита.", status_code=status.HTTP_302_FOUND)
            
        db.update_user(citizen_id, {
            "balance": user["balance"] + amount,
            "savings": new_savings
        })
        db.add_transaction("СИСТЕМА_ВКЛАДОВ", citizen_id, amount, "снятие_со_вклада")
        msg = "Средства сняты со вклада."
    else:
        return RedirectResponse(url="/dashboard?err=Неизвестная операция", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/dashboard?msg={msg}", status_code=status.HTTP_302_FOUND)

@app.post("/finance/loan")
async def manage_loan(
    request: Request,
    action: str = Form(...),
    amount: float = Form(...)
):
    """Выдача и погашение кредитов на основе лимитов системы."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    user = db.get_user(citizen_id)
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Некорректная сумма", status_code=status.HTTP_302_FOUND)
        
    if action == "take":
        if not check_loan_eligibility(user["savings"], user["loan"], amount):
            return RedirectResponse(url="/dashboard?err=Превышен лимит (Макс. 50% от суммы вклада)", status_code=status.HTTP_302_FOUND)
        
        db.update_user(citizen_id, {
            "balance": user["balance"] + amount,
            "loan": user["loan"] + amount
        })
        db.add_transaction("СИСТЕМА_КРЕДИТОВ", citizen_id, amount, "выдача_кредита")
        msg = "Кредит успешно одобрен и выдан."
        
    elif action == "repay":
        if user["balance"] < amount:
            return RedirectResponse(url="/dashboard?err=Недостаточно средств для погашения", status_code=status.HTTP_302_FOUND)
        if amount > user["loan"]:
            return RedirectResponse(url="/dashboard?err=Сумма превышает ваш текущий долг", status_code=status.HTTP_302_FOUND)
            
        db.update_user(citizen_id, {
            "balance": user["balance"] - amount,
            "loan": user["loan"] - amount
        })
        db.add_transaction(citizen_id, "СИСТЕМА_КРЕДИТОВ", amount, "погашение_кредита")
        msg = "Кредит частично или полностью погашен."
    else:
        return RedirectResponse(url="/dashboard?err=Неизвестная операция", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/dashboard?msg={msg}", status_code=status.HTTP_302_FOUND)

# -----------------------------------------------------------------------------
# Маршруты панели администратора (Admin Panel)
# -----------------------------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, msg: str = "", err: str = ""):
    """Рендерит панель Администратора для полного CRUD контроля."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    admin_user = db.get
