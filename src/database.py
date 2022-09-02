from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# SQLALCHEMY_POSTGRES_DATABASE_URL
SQLALCHEMY_DATABASE_URL = config("DB_URL")

print("********************")
print(SQLALCHEMY_DATABASE_URL)
print("********************")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
