import os 
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime , timedelta , timezone
from db import get_db
from schema import Users
from security.password import verify_hash_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

def get_username_from_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY , algorithms= [ALGORITHM])
        username = payload.get("sub")
        #here not giving the userid or the name  , that's why "sub" is given as unique identifie
        if username is None:
            raise HTTPException(status_code = 401 , detail = "Invalid Token")
        return username
    
    except jwt.PyJWTError :
        raise HTTPException(status_code = 401 , detail = "Invalid Token or you have not register with token")

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    username = get_username_from_token(token)
    user = (db.query(Users).filter(Users.username == username).first())
    if user is None:
        raise HTTPException(status_code=401,detail="User not found")
    return user

def authenticate_user(db: Session, username: str, password: str):

    user = (db.query(Users).filter(Users.username == username).first())

    if user is None:
        return None
  
    if not verify_hash_password(password,user.hashed_password):
        return None
    return user

def create_access_token(username: str) -> str:

    expire = (datetime.now(timezone.utc)+ timedelta(minutes=300))
    payload = {"sub": username,"exp": expire}

    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)