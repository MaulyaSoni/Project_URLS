from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database.db import get_db
from database.schema import Users
from operations.user import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def admin_context(
    db : Session = Depends(get_db),
    current_user : Users = Depends(get_current_user)):

    if current_user.user_role != "Admin":
        raise HTTPException(status_code = 403 , detail="Admin access rejected")

    return {'db' : db , 'current_user' : current_user}

def current_user_context(
    db : Session = Depends(get_db),
    current_user : Users = Depends(get_current_user)  
    ):

    return {'db' : db , 'current_user' : current_user}

def owner_context (
    db : Session = Depends(get_db),
    current_user : Users = Depends(get_current_user)
    ):
    if url_res.owner_id != current_user.userid and current_user.user_role != 'Admin':
        raise HTTPException(status_code = 403 , detail = "!! Access restricted !!")

    return {'db' : db , 'current_user' : current_user} 
    
def new_user_context(
    db : Session = Depends(get_db)    
    ):
    return {'db' : db}
