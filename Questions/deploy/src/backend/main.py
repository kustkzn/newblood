# deploy/src/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Создаём приложение
app = FastAPI()

# ⬇️ CORS middleware ДОЛЖЕН быть первым!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # порт фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем роуты ПОСЛЕ middleware
from routes import auth, users, questions

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])

# Если есть startup-событие — оно должно быть после роутов
from database.db import init_db

@app.on_event("startup")
def startup():
    init_db()