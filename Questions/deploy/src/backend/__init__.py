from fastapi import FastAPI
from routes import auth, users, questions
from database.db import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])