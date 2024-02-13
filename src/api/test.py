from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed_password = pwd_context.hash("datascientest")
print('hey')
print(hashed_password)

