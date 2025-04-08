from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1/python"

engine = create_engine(DATABASE_URL)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(120))

Base.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

