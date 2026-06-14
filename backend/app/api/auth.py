from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt
import os

from app.core.database import get_db
from app.models.user import User

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- Schemas ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Helpers ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token буруу эсвэл хугацаа дууссан")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Хэрэглэгч олдсонгүй")
    return user


# --- Endpoints ---
@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="И-мэйл бүртгэгдсэн байна")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Бүртгэл амжилттай", "user_id": user.id}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="И-мэйл эсвэл нууц үг буруу"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Хаагдсан хэрэглэгч")

    token = create_token(user.id, user.email)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
