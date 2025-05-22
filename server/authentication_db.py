#import mysql.connector
#from mysql.connector.errors import Error
import os
import logging as logger
import uuid

# mysql DB support
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Index
)
################################

"""
host=os.getenv("DB_HOST")
user=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")
database=os.getenv("DB_NAME")
port=os.getenv("DB_PORT")
"""
################################

"""
def log_db_user(user_id, user_email, user_name, first_logged_in, last_accessed):
    try:
        connection = mysql.connector.connect(host=host, database=database, user=user, password=password)

        if connection.is_connected():
            cursor = connection.cursor()
            sql_query = "SELECT COUNT(*) from users WHERE email_id = %s"
            cursor.execute(sql_query, (user_email,))
            row_count = cursor.fetchone()[0]

            if row_count == 0:
                sql_query = "INSERT INTO users (user_id, email_id, user_name, first_logged_in, last_accessed) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_query, (user_id, user_email, user_name, first_logged_in, last_accessed))

            # Commit changes
            connection.commit()
            logger.info("Record inserted successfully")

    except Error as e:
        logger.info("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection is closed")


def log_db_token(access_token, user_email):
    session_id = str(uuid.uuid4())
    try:
        connection = mysql.connector.connect(host=host, database=database, user=user, password=password)

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to insert data
            sql_query = "INSERT INTO issued_tokens (token, email_id, session_id) VALUES (%s,%s,%s)"
            # Execute the SQL query
            cursor.execute(sql_query, (access_token, user_email, session_id))

            # Commit changes
            connection.commit()
            logger.info("Record inserted successfully")

    except Error as e:
        logger.info("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection is closed")
"""


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False)
    user_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    first_logged_in = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    tokens = relationship("AccessToken", back_populates="user", cascade="all, delete")

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
    )


class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, ForeignKey('users.email'), nullable=False)
    token = Column(Text, nullable=False)

    user = relationship("User", back_populates="tokens")

    __table_args__ = (
        Index("ix_access_tokens_email", "email"),
    )


def init_db(db_path):
    if not os.path.exists(db_path):
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("DB has been created")
    else:
        logger.info(f"DB exists: {db_path}")


def log_db_user_access(user_id, user_email, user_name, first_logged_in, last_accessed, token, db_path):

    init_db(db_path)

    DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    user = session.query(User).filter_by(email=user_email).first()

    if not user:
        user = User(
            user_id=user_id,
            email=user_email,
            user_name=user_name,
            first_logged_in=first_logged_in,
            last_accessed=last_accessed
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Token has been added: {user_id}, {user_email}, {user_name}")
    else:
        logger.info(f"User: {user.email}, id:{user.user_id}")
        if (user_id != user.user_id): return None

    session_id = str(uuid.uuid4())  # TODO:

    if token is not None:
        email_token = AccessToken(email=user_email, token=token)
        session.add(email_token)
        session.commit()
        logger.info(f"Token has been added: {user_email}, {token}")

    session.close()
    return user_id
