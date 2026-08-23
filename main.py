from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.products import router as products_router
from app.routes.users import router as users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене здесь будет URL твоего React-сайта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(users_router)

@app.get("/")
def health_check():
    # Я немного поправил корневой роут, так как тестовый список products нам здесь больше не нужен
    return {"status": "ok", "app": "X-PRESS API"}