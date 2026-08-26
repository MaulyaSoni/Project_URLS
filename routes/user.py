import os
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException , Depends ,  Request , BackgroundTasks
from security.user import authenticate_user , get_current_user
from security.password import generate_hash_password
from schema import Users
from models.user import UsersRequest , UsersResponse

load_dotenv()
ADMIN_KEY = os.getenv("ADMIN_KEY")

logging.basicConfig(
    filename="Log_employee_project.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

#----------------------------------------------------------

def create_user(
    db: Session,
    user_data: UsersRequest):

    existing_user = (db.query(Users).filter(Users.email == user_data.email).first())

    if existing_user:
        logging.warning("Duplicate User details input ")
        raise HTTPException(status_code=409,detail="User already exists")
 
    new_user = Users(
        username=user_data.username,
        hashed_password=generate_hash_password(user_data.password),
        email = user_data.email,
        user_role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logging.info(f"{user_data.username} New User created")
    return new_user

def create_admin(
    db:Session,
    user_data : UsersRequest,
    admin_key : str
    ):

    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code = 403 , detail="You don't have valid ADMIN KEY to create admin")
    
    existing_user = (db.query(Users).filter(Users.email == user_data.email).first())
    if existing_user and existing_user.user_role == 'Admin':
        raise HTTPException(status_code = 409 , detail = "Admin already exists")

    new_user = Users(
        username=user_data.username,
        hashed_password=generate_hash_password(user_data.password),
        email=user_data.email,
        user_role="Admin"
    )
    db.add(new_user)
    db.commit()
    logging.info(f"New admin : {user_data.username} created")
    return new_user

def fetch_all_user(
    db:Session,
    user_log : Users):

    # logging.info(f"Fetch all users call by '{user_log.username}'")
    return db.query(Users).all()

#----------------------------------------------------------

def delete_user(
    db: Session,
    userid : str,
    current_user : Users):
    
    user = db.get(Users , userid)
    if user is None:
        raise HTTPException(status_code = 404 , detail="user not found")
    
    db.delete(user)
    db.commit()
    logging.info(f"{userid} , user deleted by {current_user.username}")
    return {"message" : f"{userid} , deleted successfully"}