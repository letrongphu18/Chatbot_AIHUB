from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL
#SQLALCHEMY_DATABASE_URL = "sqlite:///./chatbot_fanpage.db"
# # Tạo engine
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},  
#     echo=False
# )
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/chatbot_fanpage?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)


# Tạo session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo base class
Base = declarative_base()
