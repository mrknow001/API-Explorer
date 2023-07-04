# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/3 17:09
@Auth ： YD
@File ：database.py
@IDE ：PyCharm
@Description ：数据库连接
"""


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./ApiInfo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()