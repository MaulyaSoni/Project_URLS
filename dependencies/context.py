from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from security.user import get_current_user
from schema import Users
def admin_context(
    db : Session = Depends(get_db),
    current_user : Users = Depends(get_current_user)):

    if current_user.user_role != "Admin":
        raise HTTPException(status_code = 403 , detail="Admin access rejected")

    return {'db' : db , 'current_user' : current_user}

def user_context(
    db : Session = Depends(get_db),
    current_user : Users = Depends(get_current_user)  
    ):

    return {'db' : db , 'current_user' : current_user}

def new_user_context(
    db : Session = Depends(get_db)    
    ):
    return {'db' : db}