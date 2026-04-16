from db.models import create_user, fetch_user, update_user_password
from utils.security import (
    hash_password,
    verify_password,
    validate_email,
    validate_password,
    sanitize_input,
    generate_otp
)

# =========================
# REGISTER USER
# =========================
def register_user(name: str, email: str, password: str) -> dict:
    name = sanitize_input(name)
    email = sanitize_input(email)
    password = sanitize_input(password)

    # Validation
    if not validate_email(email):
        return {"success": False, "msg": "Invalid email format"}

    if not validate_password(password):
        return {"success": False, "msg": "Password must be at least 6 characters"}

    # Create user
    success = create_user(name, email, hash_password(password))

    if success:
        return {"success": True, "msg": "User registered successfully"}
    else:
        return {"success": False, "msg": "User already exists"}


# =========================
# LOGIN USER
# =========================
def login_user(email: str, password: str) -> dict:
    email = sanitize_input(email)
    password = sanitize_input(password)

    user = fetch_user(email)

    if not user:
        return {"success": False, "msg": "User not found"}

    # user[3] → password column
    if verify_password(password, user[3]):
        return {
            "success": True,
            "msg": "Login successful",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        }

    return {"success": False, "msg": "Incorrect password"}


# =========================
# FORGOT PASSWORD (RESET)
# =========================
def reset_password(email: str, new_password: str) -> dict:
    email = sanitize_input(email)
    new_password = sanitize_input(new_password)

    if not validate_password(new_password):
        return {"success": False, "msg": "Password too weak"}

    user = fetch_user(email)

    if not user:
        return {"success": False, "msg": "User not found"}

    update_user_password(email, hash_password(new_password))

    return {"success": True, "msg": "Password updated successfully"}


# =========================
# OTP SYSTEM
# =========================
def generate_login_otp() -> str:
    return generate_otp()


def verify_otp(input_otp: str, actual_otp: str) -> bool:
    return input_otp == actual_otp
