import os
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# APP CONFIG
# =========================
APP_NAME = "Crypto SaaS Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# =========================
# DATABASE CONFIG
# =========================
DB_NAME = os.getenv("DB_NAME", "crypto.db")

# =========================
# EMAIL CONFIG
# =========================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# =========================
# API CONFIG
# =========================
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# =========================
# SECURITY CONFIG
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

# =========================
# REFRESH SETTINGS
# =========================
AUTO_REFRESH_INTERVAL = int(os.getenv("AUTO_REFRESH_INTERVAL", 30))  # seconds

# =========================
# SUPPORTED CRYPTO (TOP 10)
# =========================
TOP_10_COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "TRX": "tron",
    "MATIC": "polygon"
}
