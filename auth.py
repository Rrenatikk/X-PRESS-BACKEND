import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Токен будет жить 1 час

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

# НОВАЯ ФУНКЦИЯ ДЛЯ ПРОВЕРКИ ТОКЕНА
def verify_access_token(token: str, credentials_exception):
    try:
        # Пытаемся расшифровать токен
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        # Достаем наш id (мы клали его в ключ "sub")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except jwt.InvalidTokenError:
        # Если токен подделан, просрочен или сломан
        raise credentials_exception