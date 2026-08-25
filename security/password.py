from argon2 import PasswordHasher

from argon2.exceptions import InvalidHashError, VerifyMismatchError
password_hash = PasswordHasher()

def generate_hash_password(password:str):   

    return password_hash.hash(password)

def verify_hash_password(plain_password : str , hashed_password : str):
    try:
        return password_hash.verify(plain_password , hashed_password)
    
    except VerifyMismatchError as e:
        return e
    
    except InvalidHashError as e:
        return e