from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL 정의
DATABASE_URL = "mysql+pymysql://root:root@localhost/spring_of_dish"

# 엔진 생성
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()
