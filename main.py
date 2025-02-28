from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, User
from pydantic import BaseModel

app = FastAPI()

# Modelo Pydantic para entrada de datos
class UserInput(BaseModel):
    name: str
    age: int

# Dependencia para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/add-user")
def add_user(user_input: UserInput, db: Session = Depends(get_db)):
    new_user = User(name=user_input.name, age=user_input.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {new_user.name} added to the database!"}