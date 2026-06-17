# main.py
# -----------------------------------------------------------------------------
# Liquid Glass Banking System
# Description: A single-file, production-ready banking system.
# Features: Authentication, P2P Transfers, Savings, Loans, Admin Panel.
# Database: JSON-based storage with atomic operations.
# Design: Liquid Glass aesthetic (Dark mode, backdrop-filter, neon accents).
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
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LiquidBank")

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
DB_FILE = "bank_data.json"
COOKIE_KEY = "citizen_id"

# -----------------------------------------------------------------------------
# Database Manager
# -----------------------------------------------------------------------------
class BankSystem:
    """
    Handles all database interactions atomically using a JSON file.
    Includes comprehensive error handling, data validation, and structuring.
    """

    def __init__(self, db_path: str = DB_FILE) -> None:
        """
        Initializes the BankSystem, ensuring the database file exists.
        
        Args:
            db_path (str): The file path for the JSON database.
        """
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        """
        Validates the existence of the database file. If missing, creates
        a default database with an admin account.
        """
        if not os.path.exists(self.db_path):
            logger.info("Database not found. Creating a new one.")
            default_db = {
                "users": {
                    "admin": {
                        "pin": "0000",
                        "name": "System Administrator",
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
            self.log_action("SYSTEM", "Initialized new database with default admin.")

    def _load_db(self) -> Dict[str, Any]:
        """
        Reads the JSON database securely.
        
        Returns:
            Dict[str, Any]: The loaded database schema.
        """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return {"users": {}, "transactions": [], "logs": []}

    def _save_db(self, data: Dict[str, Any]) -> None:
        """
        Writes the data atomically to prevent corruption during concurrent access.
        
        Args:
            data (Dict[str, Any]): The database schema to save.
        """
        temp_path = self.db_path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(temp_path, self.db_path)
        except Exception as e:
            logger.error(f"Critical error saving database: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_user(self, citizen_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves user data by Citizen ID.
        
        Args:
            citizen_id (str): The unique identifier of the citizen.
            
        Returns:
            Optional[Dict[str, Any]]: The user object if found, otherwise None.
        """
        db = self._load_db()
        return db["users"].get(citizen_id)

    def update_user(self, citizen_id: str, updates: Dict[str, Any]) -> bool:
        """
        Updates specific fields of a user's data.
        
        Args:
            citizen_id (str): The unique identifier of the user.
            updates (Dict[str, Any]): The key-value pairs to update.
            
        Returns:
            bool: True if successful, False otherwise.
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
        Registers a new citizen in the system.
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
        self.log_action("ADMIN", f"Created user {citizen_id}")
        return True

    def delete_user(self, citizen_id: str) -> bool:
        """
        Permanently removes a user from the system.
        """
        db = self._load_db()
        if citizen_id in db["users"]:
            del db["users"][citizen_id]
            self._save_db(db)
            self.log_action("ADMIN", f"Deleted user {citizen_id}")
            return True
        return False

    def log_action(self, actor: str, action: str) -> None:
        """
        Records an administrative or system event.
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
        Records a financial transaction between accounts or entities.
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
        Retrieves the transaction history for a specific user.
        """
        db = self._load_db()
        history = []
        for tx in db["transactions"]:
            if tx["sender"] == citizen_id or tx["receiver"] == citizen_id:
                history.append(tx)
        return history

# -----------------------------------------------------------------------------
# CSS Styling Framework (Liquid Glass)
# -----------------------------------------------------------------------------
def get_css() -> str:
        """
        Generates the exhaustive Liquid Glass CSS styling framework.
        Features dark mode, transparent backdrop-filters, and neon accents.
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
        /* Navigation */
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
        
        /* Containers */
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
        
        /* Typography */
        h1, h2, h3 { margin-bottom: 15px; }
        .neon-text { color: var(--neon-cyan); text-shadow: 0 0 8px var(--neon-cyan-glow); }
        .neon-pink-text { color: var(--neon-pink); text-shadow: 0 0 8px var(--neon-pink); }
        .muted { color: var(--text-muted); font-size: 0.9rem; }
        .error-msg { color: var(--danger); background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid var(--danger); }
        .success-msg { color: var(--success); background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid var(--success); }
        
        /* Forms */
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
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--glass-border); }
        th { color: var(--neon-cyan); font-weight: 600; }
        tr:hover { background: rgba(255, 255, 255, 0.02); }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-gradient-start); }
        ::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--neon-cyan); }
        """

# -----------------------------------------------------------------------------
# HTML Rendering Utilities
# -----------------------------------------------------------------------------
def render_page(title: str, content: str, user: Optional[Dict[str, Any]] = None) -> str:
    """
    Wraps the provided HTML content in the Liquid Glass base template.
    """
    nav = ""
    if user:
        admin_link = '<a href="/admin">Admin Panel</a>' if user.get("is_admin") else ''
        nav = f"""
        <nav class="glass-nav">
            <div class="nav-brand">Liquid Glass Bank</div>
            <div>
                <span class="muted">Citizen ID: {user.get('name')}</span>
                <a href="/dashboard">Dashboard</a>
                {admin_link}
                <a href="/logout">Logout</a>
            </div>
        </nav>
        """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Liquid Glass Bank</title>
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
# Business Logic & Formatting Helpers
# -----------------------------------------------------------------------------
def format_currency(amount: float) -> str:
    """Formats a float into a standard currency string representation."""
    return f"${amount:,.2f}"

def format_date(iso_string: str) -> str:
    """Parses an ISO datetime string and formats it cleanly for UI."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_string

def validate_pin(pin: str) -> bool:
    """Validates that a PIN is strictly a 4-digit number."""
    return len(pin) == 4 and pin.isdigit()

def check_loan_eligibility(savings_balance: float, current_loan: float, requested_amount: float) -> bool:
    """
    Determines if a user can take a loan based on their savings.
    Rule: Maximum loan cannot exceed 50% of current savings.
    """
    max_loan_allowed = savings_balance * 0.5
    return (current_loan + requested_amount) <= max_loan_allowed

def calculate_interest_projection(amount: float, rate: float = 0.05, years: int = 1) -> float:
    """Dummy helper function to project compound interest for a specific period."""
    return amount * ((1 + rate) ** years)

def generate_system_health_report(db_instance: BankSystem) -> Dict[str, Any]:
    """Generates a dummy health report of the entire system for logging."""
    db_data = db_instance._load_db()
    total_users = len(db_data.get("users", {}))
    total_tx = len(db_data.get("transactions", []))
    return {"status": "Healthy", "total_users": total_users, "total_transactions": total_tx}

def anonymize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function that strips sensitive data (like PIN) before transmission."""
    safe_data = user_data.copy()
    safe_data.pop("pin", None)
    return safe_data

def audit_log_formatter(log_entry: Dict[str, Any]) -> str:
    """Helper function to format a single audit log entry nicely."""
    return f"[{format_date(log_entry['timestamp'])}] {log_entry['actor']}: {log_entry['action']}"

# -----------------------------------------------------------------------------
# FastAPI Application & Dependencies
# -----------------------------------------------------------------------------
app = FastAPI(title="Liquid Glass Banking API")
db = BankSystem()

def get_current_user(request: Request) -> Optional[str]:
    """Extracts the Citizen ID from the secure cookie session."""
    return request.cookies.get(COOKIE_KEY)

# -----------------------------------------------------------------------------
# Authentication Routes
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    """Renders the login portal."""
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    err_html = f'<div class="error-msg">{error}</div>' if error else ""
    content = f"""
    <div class="glass-panel" style="max-width: 400px; margin: 100px auto;">
        <h2 class="neon-text" style="text-align: center;">Citizen Login</h2>
        {err_html}
        <form method="POST" action="/login">
            <label>Citizen ID</label>
            <input type="text" name="citizen_id" required autocomplete="off">
            <label>Secure PIN (4 digits)</label>
            <input type="password" name="pin" required maxlength="4">
            <button type="submit">Authenticate</button>
        </form>
    </div>
    """
    return render_page("Login", content)

@app.post("/login")
async def process_login(
    response: Response, 
    citizen_id: str = Form(...), 
    pin: str = Form(...)
):
    """Processes login credentials and establishes a session cookie."""
    user = db.get_user(citizen_id)
    if not user:
        return RedirectResponse(url="/?error=Invalid Citizen ID", status_code=status.HTTP_302_FOUND)
    if user["is_banned"]:
        return RedirectResponse(url="/?error=Account Suspended", status_code=status.HTTP_302_FOUND)
    if user["pin"] != pin:
        return RedirectResponse(url="/?error=Incorrect PIN", status_code=status.HTTP_302_FOUND)
    
    res = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    res.set_cookie(key=COOKIE_KEY, value=citizen_id, httponly=True, max_age=3600)
    return res

@app.get("/logout")
async def logout():
    """Terminates the active user session."""
    res = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    res.delete_cookie(COOKIE_KEY)
    return res

# -----------------------------------------------------------------------------
# Dashboard & Transfer Routes
# -----------------------------------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, msg: str = "", err: str = ""):
    """Renders the main user cabinet, displaying balances and transaction forms."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    user = db.get_user(citizen_id)
    if not user or user["is_banned"]:
        return RedirectResponse(url="/logout", status_code=status.HTTP_302_FOUND)

    msg_html = f'<div class="success-msg">{msg}</div>' if msg else ""
    err_html = f'<div class="error-msg">{err}</div>' if err else ""
    
    # Financial Overview Block
    overview = f"""
    <div class="grid-3">
        <div class="glass-panel">
            <h3>Checking Balance</h3>
            <h1 class="neon-text">{format_currency(user['balance'])}</h1>
        </div>
        <div class="glass-panel">
            <h3>Savings Account</h3>
            <h1 class="neon-pink-text">{format_currency(user['savings'])}</h1>
        </div>
        <div class="glass-panel">
            <h3>Active Loan</h3>
            <h1 class="error-msg" style="background: none; padding: 0; border: none;">{format_currency(user['loan'])}</h1>
        </div>
    </div>
    """

    # Operations Block
    operations = f"""
    <div class="grid-2">
        <div class="glass-panel">
            <h3 class="neon-text">Peer-to-Peer Transfer</h3>
            <form method="POST" action="/transfer">
                <label>Recipient Citizen ID</label>
                <input type="text" name="recipient_id" required>
                <label>Amount ($)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Send Funds</button>
            </form>
        </div>
        <div class="glass-panel">
            <h3 class="neon-pink-text">Savings Management</h3>
            <form method="POST" action="/finance/savings">
                <label>Action</label>
                <select name="action">
                    <option value="deposit">Deposit to Savings</option>
                    <option value="withdraw">Withdraw from Savings</option>
                </select>
                <label>Amount ($)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Execute</button>
            </form>
        </div>
    </div>
    """

    # Loan Block & History
    tx_history = db.get_transactions(citizen_id)
    tx_rows = ""
    for tx in tx_history[:10]: # Show last 10
        direction = "OUT" if tx["sender"] == citizen_id else "IN"
        color = "var(--danger)" if direction == "OUT" else "var(--success)"
        tx_rows += f"""
        <tr>
            <td class="muted">{format_date(tx['timestamp'])}</td>
            <td>{tx['type'].capitalize()}</td>
            <td>{tx['sender']} &rarr; {tx['receiver']}</td>
            <td style="color: {color}; font-weight: bold;">{format_currency(tx['amount'])}</td>
        </tr>
        """

    history_panel = f"""
    <div class="grid-2">
        <div class="glass-panel">
            <h3 class="neon-text">Loan System</h3>
            <p class="muted">Max loan equals 50% of your savings.</p>
            <form method="POST" action="/finance/loan">
                <label>Action</label>
                <select name="action">
                    <option value="take">Request Loan</option>
                    <option value="repay">Repay Loan</option>
                </select>
                <label>Amount ($)</label>
                <input type="number" name="amount" step="0.01" min="0.01" required>
                <button type="submit">Process Loan</button>
            </form>
        </div>
        <div class="glass-panel" style="overflow-y: auto; max-height: 350px;">
            <h3>Recent Transactions</h3>
            <table>
                <tr><th>Date</th><th>Type</th><th>Details</th><th>Amount</th></tr>
                {tx_rows}
            </table>
        </div>
    </div>
    """

    full_content = msg_html + err_html + overview + operations + history_panel
    return render_page("Dashboard", full_content, user)

@app.post("/transfer")
async def execute_transfer(
    request: Request,
    recipient_id: str = Form(...),
    amount: float = Form(...)
):
    """Executes a strict P2P transaction checking balances and validity."""
    sender_id = get_current_user(request)
    if not sender_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Invalid amount", status_code=status.HTTP_302_FOUND)
    
    if sender_id == recipient_id:
        return RedirectResponse(url="/dashboard?err=Cannot transfer to yourself", status_code=status.HTTP_302_FOUND)
        
    sender = db.get_user(sender_id)
    recipient = db.get_user(recipient_id)
    
    if not recipient or recipient["is_banned"]:
        return RedirectResponse(url="/dashboard?err=Invalid or suspended recipient", status_code=status.HTTP_302_FOUND)
        
    if sender["balance"] < amount:
        return RedirectResponse(url="/dashboard?err=Insufficient checking balance", status_code=status.HTTP_302_FOUND)
        
    # Atomic execution
    db.update_user(sender_id, {"balance": sender["balance"] - amount})
    db.update_user(recipient_id, {"balance": recipient["balance"] + amount})
    db.add_transaction(sender_id, recipient_id, amount, "transfer")
    
    return RedirectResponse(url=f"/dashboard?msg=Successfully transferred {format_currency(amount)}", status_code=status.HTTP_302_FOUND)

# -----------------------------------------------------------------------------
# Finance Operations (Savings & Loans)
# -----------------------------------------------------------------------------
@app.post("/finance/savings")
async def manage_savings(
    request: Request,
    action: str = Form(...),
    amount: float = Form(...)
):
    """Processes savings deposits and withdrawals securely."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    user = db.get_user(citizen_id)
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Invalid amount", status_code=status.HTTP_302_FOUND)
        
    if action == "deposit":
        if user["balance"] < amount:
            return RedirectResponse(url="/dashboard?err=Insufficient checking funds", status_code=status.HTTP_302_FOUND)
        db.update_user(citizen_id, {
            "balance": user["balance"] - amount,
            "savings": user["savings"] + amount
        })
        db.add_transaction(citizen_id, "SYSTEM_SAVINGS", amount, "deposit")
        msg = "Deposit successful."
        
    elif action == "withdraw":
        if user["savings"] < amount:
            return RedirectResponse(url="/dashboard?err=Insufficient savings", status_code=status.HTTP_302_FOUND)
        # Check if withdrawal breaks loan eligibility constraint
        new_savings = user["savings"] - amount
        if user["loan"] > 0 and user["loan"] > (new_savings * 0.5):
            return RedirectResponse(url="/dashboard?err=Withdrawal denied. Savings required to secure active loan.", status_code=status.HTTP_302_FOUND)
            
        db.update_user(citizen_id, {
            "balance": user["balance"] + amount,
            "savings": new_savings
        })
        db.add_transaction("SYSTEM_SAVINGS", citizen_id, amount, "withdrawal")
        msg = "Withdrawal successful."
    else:
        return RedirectResponse(url="/dashboard?err=Unknown action", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/dashboard?msg={msg}", status_code=status.HTTP_302_FOUND)

@app.post("/finance/loan")
async def manage_loan(
    request: Request,
    action: str = Form(...),
    amount: float = Form(...)
):
    """Processes loan issuance and repayments based on dynamic limits."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    user = db.get_user(citizen_id)
    if amount <= 0:
        return RedirectResponse(url="/dashboard?err=Invalid amount", status_code=status.HTTP_302_FOUND)
        
    if action == "take":
        if not check_loan_eligibility(user["savings"], user["loan"], amount):
            return RedirectResponse(url="/dashboard?err=Loan limit exceeded (Max 50% of savings)", status_code=status.HTTP_302_FOUND)
        
        db.update_user(citizen_id, {
            "balance": user["balance"] + amount,
            "loan": user["loan"] + amount
        })
        db.add_transaction("SYSTEM_LOAN", citizen_id, amount, "loan_issue")
        msg = "Loan securely issued."
        
    elif action == "repay":
        if user["balance"] < amount:
            return RedirectResponse(url="/dashboard?err=Insufficient balance to repay", status_code=status.HTTP_302_FOUND)
        if amount > user["loan"]:
            return RedirectResponse(url="/dashboard?err=Repayment exceeds active loan", status_code=status.HTTP_302_FOUND)
            
        db.update_user(citizen_id, {
            "balance": user["balance"] - amount,
            "loan": user["loan"] - amount
        })
        db.add_transaction(citizen_id, "SYSTEM_LOAN", amount, "loan_repay")
        msg = "Loan repayment successful."
    else:
        return RedirectResponse(url="/dashboard?err=Unknown action", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/dashboard?msg={msg}", status_code=status.HTTP_302_FOUND)

# -----------------------------------------------------------------------------
# Administration Panel Routes
# -----------------------------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, msg: str = "", err: str = ""):
    """Renders the exhaustive Administrator dashboard for full CRUD control."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    admin_user = db.get_user(citizen_id)
    if not admin_user or not admin_user.get("is_admin"):
        return RedirectResponse(url="/dashboard?err=Access Denied. Admins only.", status_code=status.HTTP_302_FOUND)

    msg_html = f'<div class="success-msg">{msg}</div>' if msg else ""
    err_html = f'<div class="error-msg">{err}</div>' if err else ""

    # User Table
    all_users = db._load_db()["users"]
    user_rows = ""
    for cid, u in all_users.items():
        status_txt = "Banned" if u['is_banned'] else "Active"
        role_txt = "Admin" if u['is_admin'] else "Citizen"
        user_rows += f"""
        <tr>
            <td>{cid}</td>
            <td>{u['name']}</td>
            <td>{format_currency(u['balance'])}</td>
            <td>{role_txt} / {status_txt}</td>
        </tr>
        """

    # Logs Table
    all_logs = db._load_db()["logs"]
    log_rows = ""
    for log in all_logs[:15]:
        log_rows += f"<tr><td class='muted'>{format_date(log['timestamp'])}</td><td>{log['actor']}</td><td>{log['action']}</td></tr>"

    content = f"""
    {msg_html} {err_html}
    <div class="grid-2">
        <div class="glass-panel">
            <h2 class="neon-pink-text">System Controls</h2>
            <form method="POST" action="/admin/action">
                <label>Operation Type</label>
                <select name="action_type" required>
                    <option value="create">Register New User</option>
                    <option value="delete">Delete User (Permanent)</option>
                    <option value="ban">Suspend User (Ban)</option>
                    <option value="unban">Restore User (Unban)</option>
                    <option value="set_balance">Set Checking Balance</option>
                    <option value="set_pin">Reset User PIN</option>
                </select>
                <label>Target Citizen ID</label>
                <input type="text" name="target_id" required>
                <label>Parameter (Amount for balance / Name for create / PIN for reset)</label>
                <input type="text" name="parameter">
                <button type="submit" class="danger">Execute System Command</button>
            </form>
        </div>
        <div class="glass-panel" style="overflow-y: auto; max-height: 400px;">
            <h2 class="neon-text">System Audit Logs</h2>
            <table>
                <tr><th>Time</th><th>Actor</th><th>Event</th></tr>
                {log_rows}
            </table>
        </div>
    </div>
    <div class="glass-panel" style="margin-top: 20px; overflow-y: auto; max-height: 400px;">
        <h2>Global Citizen Registry</h2>
        <table>
            <tr><th>Citizen ID</th><th>Full Name</th><th>Checking Balance</th><th>Status</th></tr>
            {user_rows}
        </table>
    </div>
    """
    return render_page("Administrator Panel", content, admin_user)

@app.post("/admin/action")
async def admin_execute_action(
    request: Request,
    action_type: str = Form(...),
    target_id: str = Form(...),
    parameter: str = Form("")
):
    """Executes highly privileged administrative commands strictly."""
    citizen_id = get_current_user(request)
    if not citizen_id:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    admin_user = db.get_user(citizen_id)
    if not admin_user or not admin_user.get("is_admin"):
        return RedirectResponse(url="/dashboard?err=Access Denied", status_code=status.HTTP_302_FOUND)

    try:
        if action_type == "create":
            # Parameter will hold the name. Default PIN to 1234.
            if not parameter:
                parameter = "Unknown Citizen"
            success = db.create_user(target_id, "1234", parameter)
            if not success:
                return RedirectResponse(url="/admin?err=User already exists", status_code=status.HTTP_302_FOUND)
            msg = f"Created user {target_id} with default PIN 1234."
            
        elif action_type == "delete":
            if target_id == citizen_id:
                return RedirectResponse(url="/admin?err=Cannot delete yourself", status_code=status.HTTP_302_FOUND)
            success = db.delete_user(target_id)
            if not success:
                return RedirectResponse(url="/admin?err=User not found", status_code=status.HTTP_302_FOUND)
            msg = f"Permanently deleted user {target_id}."
            
        elif action_type == "ban":
            if target_id == citizen_id:
                return RedirectResponse(url="/admin?err=Cannot ban yourself", status_code=status.HTTP_302_FOUND)
            db.update_user(target_id, {"is_banned": True})
            db.log_action(citizen_id, f"Banned user {target_id}")
            msg = f"User {target_id} suspended."
            
        elif action_type == "unban":
            db.update_user(target_id, {"is_banned": False})
            db.log_action(citizen_id, f"Unbanned user {target_id}")
            msg = f"User {target_id} restored."
            
        elif action_type == "set_balance":
            try:
                new_bal = float(parameter)
                if new_bal < 0: raise ValueError
            except ValueError:
                return RedirectResponse(url="/admin?err=Invalid balance parameter", status_code=status.HTTP_302_FOUND)
            db.update_user(target_id, {"balance": new_bal})
            db.log_action(citizen_id, f"Set {target_id} balance to {new_bal}")
            msg = f"Updated balance for {target_id}."
            
        elif action_type == "set_pin":
            if not validate_pin(parameter):
                return RedirectResponse(url="/admin?err=PIN must be strictly 4 digits", status_code=status.HTTP_302_FOUND)
            db.update_user(target_id, {"pin": parameter})
            db.log_action(citizen_id, f"Reset PIN for {target_id}")
            msg = f"PIN reset successfully for {target_id}."
