import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_PASS


# =========================
# CORE EMAIL SENDER
# =========================
def send_email(to_email: str, subject: str, html_content: str):

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)

        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False
# =========================
# PRICE ALERT EMAIL
# =========================
def send_alert_email(to_email: str, coin: str, condition: str, target_price: float, current_price: float):

    subject = f"🚨 Price Alert: {coin} is {condition} ${target_price}"

    arrow = "📈" if condition == "above" else "📉"
    color = "#00ffcc" if condition == "above" else "#ff4b4b"

    html = f"""
    <html>
    <body style="font-family:Arial;background:#0f0c29;color:white;padding:20px;">
        <h2 style="color:#4cc9f0;">🚨 Price Alert Triggered</h2>

        <div style="background:#302b63;padding:15px;border-radius:10px;margin:20px 0;">
            <p style="font-size:18px;">{arrow} <b>{coin}</b> has gone <b>{condition}</b> your target</p>

            <table style="width:100%;margin-top:10px;">
                <tr>
                    <td style="color:gray;">Current Price</td>
                    <td style="color:{color};font-size:22px;font-weight:bold;">${current_price:.2f}</td>
                </tr>
                <tr>
                    <td style="color:gray;">Your Target</td>
                    <td style="color:white;">${target_price:.2f}</td>
                </tr>
                <tr>
                    <td style="color:gray;">Condition</td>
                    <td style="color:white;">Price goes {condition} target</td>
                </tr>
            </table>
        </div>

        <p style="color:gray;font-size:12px;">
            This alert has been deactivated. Set a new one from your dashboard.
        </p>

        <p style="margin-top:20px;">Happy Investing 💰</p>
    </body>
    </html>
    """

    return send_email(to_email, subject, html)

# =========================
# WELCOME EMAIL
# =========================
def send_welcome_email(to_email: str):

    subject = "🎉 Welcome to Crypto SaaS Platform"

    html = f"""
    <html>
    <body style="font-family:Arial;background:#0f0c29;color:white;padding:20px;">
        <h2 style="color:#4cc9f0;">🚀 Welcome to Crypto SaaS</h2>
        <p>Your account has been successfully created.</p>
        
        <div style="background:#302b63;padding:15px;border-radius:10px;">
            <p>✔ Track your portfolio</p>
            <p>✔ AI-based insights</p>
            <p>✔ Real-time crypto prices</p>
        </div>

        <p style="margin-top:20px;">Happy Investing 💰</p>
    </body>
    </html>
    """

    return send_email(to_email, subject, html)


# =========================
# OTP EMAIL
# =========================
def send_otp_email(to_email: str, otp: str):

    subject = "🔐 Your OTP Code - Crypto SaaS"

    html = f"""
    <html>
    <body style="font-family:Arial;background:#0f0c29;color:white;padding:20px;">
        <h2 style="color:#4cc9f0;">🔐 OTP Verification</h2>

        <p>Your One-Time Password is:</p>

        <h1 style="
            background:#4cc9f0;
            color:black;
            padding:10px;
            border-radius:8px;
            text-align:center;
            letter-spacing:5px;">
            {otp}
        </h1>

        <p>This OTP is valid for a short time.</p>
    </body>
    </html>
    """

    return send_email(to_email, subject, html)


# =========================
# RISK ALERT EMAIL
# =========================
def send_risk_alert_email(to_email: str, risk_data):

    subject = "⚠ Crypto Risk Alert"

    rows = ""

    for _, row in risk_data.iterrows():
        color = "red" if row["Risk"] == "High" else "orange" if row["Risk"] == "Medium" else "green"

        rows += f"""
        <tr>
            <td>{row['Crypto']}</td>
            <td>${round(row['Volatility'],2)}</td>
            <td style="color:{color};">{row['Risk']}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family:Arial;background:#0f0c29;color:white;padding:20px;">
        <h2 style="color:#ff4d4d;">⚠ Risk Alert</h2>

        <p>Your portfolio risk analysis:</p>

        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#302b63;">
                <th style="padding:10px;">Crypto</th>
                <th>Volatility</th>
                <th>Risk</th>
            </tr>
            {rows}
        </table>

        <p style="margin-top:20px;">
        Stay cautious and diversify your investments.
        </p>
    </body>
    </html>
    """

    return send_email(to_email, subject, html)
def send_portfolio_summary_email(to_email: str, portfolio_df):

    subject = "📊 Your Crypto Portfolio Summary"

    if portfolio_df.empty:
        html = """
        <html><body style="background:#0f0c29;color:white;padding:20px;">
        <h2>No portfolio data available</h2>
        </body></html>
        """
        return send_email(to_email, subject, html)

    total_invested = portfolio_df["Amount"].sum()
    total_value = portfolio_df["Current Value"].sum()
    total_profit = total_value - total_invested
    profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0

    rows = ""

    for _, row in portfolio_df.iterrows():
        color = "green" if row["Profit ($)"] >= 0 else "red"

        rows += f"""
        <tr>
            <td>{row['Crypto']}</td>
            <td>${row['Amount']}</td>
            <td>${row['Current Value']:.2f}</td>
            <td style="color:{color};">${row['Profit ($)']:.2f}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family:Arial;background:#0f0c29;color:white;padding:20px;">

        <h2 style="color:#00ffcc;">📊 Portfolio Summary</h2>

        <div style="background:#302b63;padding:15px;border-radius:10px;">
            <p><b>Total Invested:</b> ${total_invested:.2f}</p>
            <p><b>Current Value:</b> ${total_value:.2f}</p>
            <p><b>Profit:</b> ${total_profit:.2f} ({profit_pct:.2f}%)</p>
        </div>

        <h3 style="margin-top:20px;">💼 Holdings</h3>

        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#302b63;">
                <th style="padding:10px;">Crypto</th>
                <th>Invested</th>
                <th>Current Value</th>
                <th>Profit</th>
            </tr>
            {rows}
        </table>

        <p style="margin-top:20px;">
        🚀 Keep tracking your investments and stay ahead!
        </p>

    </body>
    </html>
    """

    return send_email(to_email, subject, html)
