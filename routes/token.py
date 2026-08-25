import logging
from fastapi import Depends , HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from security.user import authenticate_user , create_access_token

logging.basicConfig(
    filename="Log_employee_project.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

#----------------------------------------------------------

def create_token(
    db : Session,
    form_data : OAuth2PasswordRequestForm):

    user = authenticate_user(db , form_data.username , form_data.password)
    if user is None:
        raise HTTPException(status_code=401,detail="Incorrect username or password")
    
    token = create_access_token(user.username)
    logging.info(f"Access token created for user : {form_data.username}")
    
    return {"access_token": token,"token_type": "bearer"}
