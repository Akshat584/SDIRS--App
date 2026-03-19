import random
import string
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..models import Token

# In a real application, these would be in a config file
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP."""
    characters = string.digits
    return "".join(random.choice(characters) for _ in range(length))

def send_otp(phone_number: str, otp: str):
    """
    Sends the OTP to the user's phone number.
    In a real application, this would integrate with an SMS gateway like Twilio.
    For now, we'll just print it to the console.
    """
    print(f"Sending OTP {otp} to {phone_number}")

def verify_otp(user_otp: str, stored_otp: str) -> bool:
    """
    Verifies the OTP provided by the user.
    """
    return user_otp == stored_otp
