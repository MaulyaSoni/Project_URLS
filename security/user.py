import os 
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime , timedelta , timezone
from sqlalchemy.orm import Session
from database.db import get_db
from database.schema import Users
from security.password import verify_hash_password
from pwdlib import PasswordHash


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

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

def authenticate_user(db: Session, email: str, password: str):

    # user = db.get(Users , email)
    user = (db.query(Users).filter(Users.email == email).first())

    # print(user.email)
    if not user :
        verify_hash_password(password , DUMMY_HASH )
        return False
  
    if not verify_hash_password(password,user.hashed_password):
        return False
    
    print("pass",verify_hash_password(password, user.hashed_password ))

    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# def create_access_token(username: str) -> str:

#     expire = (datetime.now(timezone.utc)+ timedelta(minutes=300))
#     payload = {"sub": username,"exp": expire}

#     return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)