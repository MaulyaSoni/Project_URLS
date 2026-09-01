import os
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database.schema import Users
from models.user import UsersRequest 
from security.user import authenticate_user , create_access_token
from security.password import generate_hash_password
from email_validator import validate_email , EmailNotValidError

load_dotenv()
ADMIN_KEY = os.getenv("ADMIN_KEY")

logging.basicConfig(
    filename="Log_employee_project.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
#----------------------------------------------------

def login_with_token(
    db : Session,
    form_data : OAuth2PasswordRequestForm):

    user = authenticate_user(db , form_data.username , form_data.password)
    if not user :
        raise HTTPException(status_code=401,detail="Incorrect username or password")
 
    token = create_access_token(data = {"sub": user.username})
    logging.info(f"Access token created for user : '{form_data.username}'")
    
    return {"access_token": token,"token_type": "bearer"}

#----------------------------------------------------------

def create_user(
    db: Session,
    user_data: UsersRequest):

    try:
        valid_email = validate_email(user_data.email, check_deliverability=True)
  
    except (EmailNotValidError,Exception) as e:
        raise HTTPException(status_code = 400 , detail=f"!! Invalid email !!, {e}")

    existing_user = (db.query(Users).filter(Users.email == user_data.email).first())

    if existing_user:
        logging.warning("Duplicate User details input ")
        raise HTTPException(status_code=409,detail="User already exists")

    new_user = Users(
        username=user_data.username,
        hashed_password=generate_hash_password(user_data.password),
        email = valid_email.email,
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

#-------------------------------------------------------------------

def fetch_all_user(
    db:Session,
    user_log : Users):
    logging.info(f"Fetch all users call : '{user_log.userid}'")
    return db.query(Users).all()


#----------------------------------------------------------

def delete_user(
    db: Session,
    userid : str,
    current_user : Users):
    
    user = db.get(Users , userid)
   
    try :

        if userid is None :
            raise HTTPException(status_code = 404 , detail = "Invalid UserID")

        if user is None:
            raise HTTPException(status_code = 404 , detail = "UserID not found ")
     
    except (AttributeError , Exception , ValueError) as e:
        raise e
    
    db.delete(user)
    db.commit()
    logging.info(f"{userid} , user deleted by : '{current_user.username}'")
    return {"message" : f"{userid} , deleted successfully"}