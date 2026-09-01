from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
def generate_hash_password(password:str):   

    return password_hash.hash(password)

def verify_hash_password(plain_password , hashed_password ):
    return password_hash.verify(plain_password , hashed_password)
    
