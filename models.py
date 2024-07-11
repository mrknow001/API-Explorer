# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/3 17:08
@Auth ： YD
@File ：models.py
@IDE ：PyCharm
@Description ：sqlite数据库模型
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base

Base = declarative_base()


# 定义应用模型类
class APP(Base):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    # 应用名称,不允许为空
    application = Column(String, nullable=False)
    groups = relationship('Group', back_populates='app')
    # 应用id标签，不允许为空
    id_tab = Column(String, nullable=False)
    # 应用key标签，不允许为空
    key_tab = Column(String, nullable=False)
    # 基础路径
    baseurl = Column(String, nullable=False)


# 定义功能分组模型类
class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('application.id'))
    # 分组名称,不允许为空，不允许重复
    group = Column(String, nullable=False, unique=True)
    functions = relationship('Function', back_populates='group')
    app = relationship('APP', back_populates='groups')


# 定义功能模型类
class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    # 功能名称,不允许为空
    function = Column(String, nullable=False)
    # 请求类型,不允许为空
    type = Column(String, nullable=False)
    # 请求地址,不允许为空
    url = Column(String, nullable=False)
    # 请求头
    headers = Column(String)
    # get参数
    get_params = Column(String)
    # 参数类型
    content_type = Column(String)
    # post参数
    post_params = Column(String)
    # 是否为token接口,内容为1或0,不允许为空
    is_token = Column(Integer, nullable=False)
    # token正则表达式
    token_re = Column(String)
    # 接口文档
    api_doc = Column(String)
    group = relationship('Group', back_populates='functions')
