from db.database import get_connection

# =========================
# USER MODELS
# =========================

def create_user(name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def fetch_user(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    conn.close()
    return user


def update_user_password(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET password=? WHERE email=?",
        (password, email)
    )

    conn.commit()
    conn.close()


# =========================
# PORTFOLIO MODELS
# =========================

def add_holding(email, crypto, amount, date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO holdings (email, crypto, amount, date) VALUES (?, ?, ?, ?)",
        (email, crypto, amount, date)
    )

    conn.commit()
    conn.close()


def get_holdings(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT crypto, amount, date FROM holdings WHERE email=?",
        (email,)
    )

    data = cur.fetchall()
    conn.close()

    return data


def delete_holding(email, crypto):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM holdings WHERE email=? AND crypto=?",
        (email, crypto)
    )

    conn.commit()
    conn.close()

def create_alert(email, coin, condition, target_price):
    """condition: 'above' or 'below'"""
    conn = get_conn()
    conn.execute("""
        INSERT INTO alerts (email, coin, condition, target_price, active)
        VALUES (?, ?, ?, ?, 1)
    """, (email, coin, condition, target_price))
    conn.commit()
    conn.close()

def get_alerts(email):
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, coin, condition, target_price, active
        FROM alerts WHERE email = ?
    """, (email,)).fetchall()
    conn.close()
    return rows

def deactivate_alert(alert_id):
    conn = get_conn()
    conn.execute("UPDATE alerts SET active = 0 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
# =========================
# OPTIONAL ANALYTICS HELPERS
# =========================

def get_total_investment(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT SUM(amount) FROM holdings WHERE email=?",
        (email,)
    )

    total = cur.fetchone()[0]
    conn.close()

    return total if total else 0

def get_all_active_alerts():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, email, coin, condition, target_price
        FROM alerts WHERE active = 1
    """).fetchall()
    conn.close()
    return rows
def get_crypto_distribution(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT crypto, SUM(amount) FROM holdings WHERE email=? GROUP BY crypto",
        (email,)
    )

    data = cur.fetchall()
    conn.close()

    return data
