# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/3 17:22
@Auth ： YD
@File ：core.py
@IDE ：PyCharm
@Description ：核心功能
"""
import codecs
import html
import json
import threading

from PyQt5 import QtCore, QtWidgets

import DocUI
from database import SessionLocal
from models import APP, Group, Function
import ConfigUI
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from ParamsAnalysis import get_api


confWindow = None
docWindow = None


# 打开配置窗口
def openConfigWindow(ui):
    global confWindow
    confWindow = None
    if confWindow is None:
        # 获取lineEdit，lineEdit_2，lineEdit_3，query_function(ui).id
        id = ui.lineEdit.text()
        key = ui.lineEdit_2.text()
        token = ui.lineEdit_3.text()
        function_id = query_function(ui).id
        try:
            confWindow = ConfigUI.Ui_Form(id, key, token, function_id)
            confWindow.setupUi(confWindow)
            confWindow.show()

            # 在子窗口的 closeEvent 中执行操作
            def onChildWindowClose(event):
                # 弹出提示框，提示信息已保存
                try:
                    confWindow.close()
                    QtWidgets.QMessageBox.information(ui.pushButton_4, "提示", "信息已保存")
                except Exception as e:
                    print(e)

            confWindow.pushButton_2.clicked.connect(onChildWindowClose)
        except Exception as e:
            print(e)

# 接口文档处理
def doc_mofify(doc):
    return doc

# 获取接口对应说明文档，弹出新窗口显示
def get_doc(ui):
    function_id = query_function(ui).id
    db = SessionLocal()
    # 根据function_id获取对应的文档api_doc
    api_doc = db.query(Function).filter(Function.id == function_id).first().api_doc
    # 文档处理
    api_doc = doc_mofify(api_doc)
    # 根据function_id获取对应的文档function
    api_name = db.query(Function).filter(Function.id == function_id).first().function
    return api_doc, api_name

# 打开文档窗口
def open_doc_windows(ui):
    global docWindow
    docWindow = None
    try:
        if docWindow is None:
            doc_info = get_doc(ui)
            docWindow = DocUI.Ui_Form(doc_info[0], doc_info[1])
            docWindow.setupUi(docWindow)
            docWindow.show()
    except Exception as e:
        print(e)


# 请求api获取信息
def get_data(ui, get_token=0):
    # 检查是否输入id，key，token三个参数，id加上key与token二者不能同时为空
    if ui.lineEdit.text() == '' and ui.lineEdit_2.text() == '':
        if ui.lineEdit_3.text() == '':
            # ui.textBrowser.append("请输入id，key，token")
            ui.textBrowser.append('<font color="red"><strong>{}</strong></font>'.format("请输入id，key，token"))
            return
    # 获取lineEdit，lineEdit_2，lineEdit_3，query_function(ui).id
    id = ui.lineEdit.text()
    key = ui.lineEdit_2.text()
    token = ui.lineEdit_3.text()
    # 获取api信息
    params_info = query_function(ui)
    ui_params = {"id": id, "key": key, "token": token}
    # 调用get_api函数获取api信息
    result = get_api(params_info, ui_params, get_token)
    data = json.dumps(result["result"], indent=4, ensure_ascii=False).replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;').replace('\n', '<br/>')
    # 如果是获取token，将token写入lineEdit_3
    try:
        if get_token == 1:
            # 判断token是否为空
            if result["token"] is None:
                ui.textBrowser.append("token获取失败")
                ui.textBrowser.append(data)
                ui.textBrowser.append('<font color="red"><strong>{}</strong></font>'.format("token获取失败"))
                ui.textBrowser.append('<font color="green">{}</font>'.format(data))
            else:
                # ui.textBrowser.append(params_info.function)
                # ui.textBrowser.append(data)
                ui.lineEdit_3.setText(result["token"])
                ui.textBrowser.append('<font color="blue"><strong>{}</strong></font>'.format(params_info.function))
                ui.textBrowser.append('<font color="green">{}</font>'.format(data))
        else:
            # ui.textBrowser.append(params_info.function)
            # ui.textBrowser.append(data)
            ui.textBrowser.append('<font color="blue"><strong>{}</strong></font>'.format(params_info.function))
            ui.textBrowser.append('<font color="green">{}</font>'.format(data))
    except Exception as e:
        # ui.textBrowser.append(str(e))
        ui.textBrowser.append('<font color="red"><strong>{}</strong></font>'.format(str(e)))

# 按键功能
def key_function(ui):
    # pushButton点击按键获取token
    ui.pushButton.clicked.connect(lambda: get_token(ui))
    # pushButton_2点击按键获取接口信息
    ui.pushButton_2.clicked.connect(lambda: get_data(ui))
    # pushButton_3清空日志
    ui.pushButton_3.clicked.connect(lambda: ui.textBrowser.clear())
    # pushButton_4获取comBox对应功能id
    # ui.pushButton_4.clicked.connect(lambda: print(query_function(ui).id))
    ui.pushButton_4.clicked.connect(lambda : openConfigWindow(ui))
    # pushButton_5获取说明文档
    ui.pushButton_5.clicked.connect(lambda: open_doc_windows(ui))


# 获取lineEdit与lineEdit_2的值，并检查是否为空，同时对输入数据进行检查，删除前后空格以及特殊符号
def get_token(ui):
    id = ui.lineEdit.text()
    key = ui.lineEdit_2.text()
    id = id.strip()
    key = key.strip()
    if id == '' or key == '':
        ui.textBrowser.append('id或key不能为空')
        return
    if id.isalnum() == False or key.isalnum() == False:
        ui.textBrowser.append('id或key不能包含特殊字符')
        return
    # 根据comBox获取应用名称，在其所有分组中查找is_token为1的数据
    db = SessionLocal()
    app_id = db.query(APP.id).filter(APP.application == ui.comboBox.currentText()).first()
    token_api = ''
    try:
        groups = db.query(Group).filter(Group.app_id == app_id[0]).all()
        for group in groups:
            try:
                function = db.query(Function).filter(Function.group_id == group.id).filter(Function.is_token == 1).first()
                token_api = function.url
            except Exception as e:
                # print(e)
                pass
    except Exception as e:
        # print(e)
        pass
    if token_api == '':
        ui.textBrowser.append('未找到token接口')
        return
    # 请求api接口获取token
    get_data(ui,get_token=1)



# comboBox选择功能，数据从数据库中application表读取
def comboBox_function(ui):
    db = SessionLocal()
    # comboBox添加应用数据
    apps = db.query(APP).all()
    for app in apps:
        ui.comboBox.addItem(app.application)

# comboBox_2添加分组数据,分组数据根据comboBox数据变化，根据应用名称修改label跟label_2的值
def comboBox_2_function(ui):
    # 如果comboBox为空,则不执行
    if ui.comboBox.currentText() == '':
        return
    db = SessionLocal()
    # 查询comboBox中的应用名称对应的id,并赋值给app_id
    app_id = db.query(APP.id).filter(APP.application == ui.comboBox.currentText()).first()
    # 查询分组表中的分组名称,并赋值给groups
    groups = db.query(Group.group).filter(Group.app_id == app_id[0]).all()
    # 清空comboBox_2中的数据
    ui.comboBox_2.clear()
    # 将groups中的数据添加到comboBox_2中
    for group in groups:
        ui.comboBox_2.addItem(group.group)
    # 根据应用id查询应用id标签,并设置label跟label_2的值
    id_tab = db.query(APP).filter(APP.id == app_id[0]).first()
    ui.label.setText(id_tab.id_tab)
    ui.label_2.setText(id_tab.key_tab)

# comboBox_3添加功能数据,功能数据根据comboBox_2数据变化
def comboBox_3_function(ui):
    # 如果comboBox_2为空,则不执行
    if ui.comboBox_2.currentText() == '':
        return
    db = SessionLocal()
    # 查询comboBox_2中的应用名称对应的分组id,并赋值给group_id
    group_id = db.query(Group.id).filter(Group.group == ui.comboBox_2.currentText()).first()
    # 查询功能表中的功能名称,并赋值给functions
    functions = db.query(Function.function).filter(Function.group_id == group_id[0]).all()
    # 清空comboBox_3中的数据
    ui.comboBox_3.clear()
    # 将functions中的数据添加到comboBox_3中
    for function in functions:
        ui.comboBox_3.addItem(function.function)

# 根据分组以及功能名称查询功能信息
def query_function(ui):
    # 先判断comboBox_2和comboBox_3是否为空
    if ui.comboBox_2.currentText() == '' or ui.comboBox_3.currentText() == '':
        return
    db = SessionLocal()
    # 查询comboBox_2中的应用名称对应的分组id,并赋值给group_id
    group_id = db.query(Group.id).filter(Group.group == ui.comboBox_2.currentText()).first()
    # 查询comboBox_3中的应用名称对应的功能id,并赋值给function_id
    function_id = db.query(Function.id).filter(Function.function == ui.comboBox_3.currentText()).first()
    # 查询功能表中的功能信息,并赋值给function
    function = db.query(Function).filter(Function.group_id == group_id[0], Function.id == function_id[0]).first()
    # 将function中的数据显示到textBrowser中
    return function