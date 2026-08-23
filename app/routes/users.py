import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models import User
from app.schemas import UserProfileSchema, UserProfileSchemaCreate, UserProfileSchemaUpdate, UserLoginSchema, \
    EmailCheckSchema
from auth import create_access_token, oauth2_scheme, verify_access_token

# ВМЕСТО schemes=["bcrypt"] ИСПОЛЬЗУЕМ pbkdf2_sha256:
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Функция для сравнения обычного пароля с хешем из БД
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

router = APIRouter(prefix="/users", tags=["Users"])

# НОВЫЙ ЭНДПОИНТ ДЛЯ ПРОВЕРКИ EMAIL
@router.post("/check-email")
def check_email(data: EmailCheckSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    return {"exists": user is not None}

@router.post("/login")
def login_user(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    # Генерируем токен. В payload (мы назвали его data) кладем id пользователя
    # По стандарту JWT, subject (субъект) обозначается ключом "sub" и должен быть строкой
    access_token = create_access_token(data={"sub": str(user.id)})

    # По стандарту OAuth2 (который использует FastAPI) ответ должен выглядеть именно так:
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ (Регистрация)
@router.post("/register", response_model=UserProfileSchema, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserProfileSchemaCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже такого email в базе
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Создаем нового пользователя с захешированным паролем
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        birth_date=user_data.birth_date,
        height_cm=user_data.height_cm,
        top_size=user_data.top_size,
        bottom_size=user_data.bottom_size,
        shoe_size=user_data.shoe_size,
        preferred_fit=user_data.preferred_fit,
        favorite_colors=user_data.favorite_colors,
        style_aesthetics=user_data.style_aesthetics
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# НОВАЯ ЗАВИСИМОСТЬ: Получение текущего юзера
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Заготавливаем стандартную ошибку "401 Unauthorized"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Расшифровываем токен и получаем ID
    user_id = verify_access_token(token, credentials_exception)

    # 2. Ищем пользователя в базе
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None:
        raise credentials_exception

    # 3. Возвращаем найденного пользователя
    return user


# ЗАЩИЩЕННЫЙ РОУТ ПРОФИЛЯ (Ставим его ДО /{user_id})
@router.get("/me", response_model=UserProfileSchema)
def get_my_profile(current_user: User = Depends(get_current_user)):
    # Сюда запрос дойдет только если токен валидный!
    # Тебе даже не нужно лезть в базу, current_user уже содержит все данные.
    return current_user

# 2. ОБНОВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (Только свой профиль)
@router.put("/me", response_model=UserProfileSchema)
def update_user(
        user_data: UserProfileSchemaUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Запрашиваем токен
):
    # Нам больше не нужно искать юзера по id или проверять его существование,
    # зависимость get_current_user уже сделала это и вернула нам объект current_user.

    # Обновляем только те поля, которые были переданы (exclude_unset=True)
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


# 3. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (Только свой профиль)
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Запрашиваем токен
):
    # Зависимость гарантирует, что пользователь удалит только самого себя
    db.delete(current_user)
    db.commit()
    return None