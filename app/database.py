from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Строка подключения: postgresql://пользователь:пароль@хост:порт/имя_базы
SQLALCHEMY_DATABASE_URL = "postgresql://xpress_admin:supersecretpassword@localhost:5432/xpress_db"

# Создаем движок (engine) - основную точку входа в БД
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс, от которого будут наследоваться все наши модели таблиц
Base = declarative_base()

# Зависимость для FastAPI, чтобы открывать и закрывать сессию БД для каждого запроса
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()