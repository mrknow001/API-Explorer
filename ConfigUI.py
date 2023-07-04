# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/3 22:33
@Auth ： YD
@File ：Config_UI.py
@IDE ：PyCharm
@Description ：参数配置界面
"""

from PyQt5 import QtCore, QtWidgets
from database import SessionLocal
from models import Function
import ParamsAnalysis


class Ui_Form(QtWidgets.QWidget):
    def __init__(self, id, key, token, db_id):
        super().__init__()
        self.id = id
        self.key = key
        self.token = token
        self.db_id = db_id
        self.title = "Undefined"

    # 获取参数并以[["a","1"],["b","2"]]的形式返回
    def get_params(self):
        db = SessionLocal()
        # 获取功能名称以及对应的参数
        params = db.query(Function).filter(Function.id == self.db_id).first()
        # 设置groupbox的标题
        self.title = params.function
        # 将参数转换为列表
        params_list = ParamsAnalysis.get_list_params(params.get_params, params.headers, params.post_params)
        if params_list is None:
            return [["Unknow",""]]
        else:
            return params_list

    # 参数替换,将特殊标识内容替换
    def params_replace(self, params_list):
        for i in range(len(params_list)):
            if params_list[i][1] == "{id}":
                params_list[i][1] = self.id
            elif params_list[i][1] == "{secert}":
                params_list[i][1] = self.key
            elif params_list[i][1] == "{token}":
                params_list[i][1] = self.token
        return params_list

    # 清空groupBox内所有lineEdit
    def clear_lineEdit(self):
        for i in range(self.gridLayout.count()):
            if isinstance(self.gridLayout.itemAt(i).widget(), QtWidgets.QLineEdit):
                self.gridLayout.itemAt(i).widget().setText("")

    # 保存lineEdit内容到数据库，替换数据库params字段
    def save_params(self):
        # 读取groupBox内所有lineEdit，存为字典,字典键为label，值为lineEdit内容
        new_params = {}
        for i in range(self.gridLayout.count()):
            if isinstance(self.gridLayout.itemAt(i).widget(), QtWidgets.QLabel):
                key = self.gridLayout.itemAt(i).widget().text()
            if isinstance(self.gridLayout.itemAt(i).widget(), QtWidgets.QLineEdit):
                new_params[key] = self.gridLayout.itemAt(i).widget().text()
        db = SessionLocal()
        # 获取原始params
        old_params = db.query(Function).filter(Function.id == self.db_id).first()
        result = ParamsAnalysis.change_params(old_params, new_params)
        # 将替换后的params存入数据库
        old_params.get_params = result[0]
        old_params.headers = result[1]
        old_params.post_params = result[2]
        db.commit()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(458, 180)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")

        params = self.get_params()
        params = self.params_replace(params)
        if len(params) == 0:
            label = QtWidgets.QLabel(self.groupBox)
            label.setObjectName(f"label")
            label.setText("Unknow")
            self.gridLayout.addWidget(label, i, 0, 1, 1)

            lineEdit = QtWidgets.QLineEdit(self.groupBox)
            lineEdit.setObjectName(f"lineEdit")
            lineEdit.setText("Error")
            self.gridLayout.addWidget(lineEdit, i, 1, 1, 1)
        for i, param in enumerate(params):
            label = QtWidgets.QLabel(self.groupBox)
            label.setObjectName(f"label_{i}")
            label.setText(param[0])
            self.gridLayout.addWidget(label, i, 0, 1, 1)

            lineEdit = QtWidgets.QLineEdit(self.groupBox)
            lineEdit.setObjectName(f"lineEdit_{i}")
            lineEdit.setText(str(param[1]))
            self.gridLayout.addWidget(lineEdit, i, 1, 1, 1)

        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, len(params), 0, 1, 1)

        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, len(params), 1, 1, 1)

        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # 设置清空按键的点击事件，点击后所有的lineEdit清空
        self.pushButton.clicked.connect(self.clear_lineEdit)
        # 设置保存按键的点击事件，点击后将所有lineEdit的内容保存到数据库
        self.pushButton_2.clicked.connect(self.save_params)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "参数配置"))
        self.groupBox.setTitle(_translate("Form", self.title))
        self.pushButton.setText(_translate("Form", "清空"))
        self.pushButton_2.setText(_translate("Form", "保存"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form(1,2,3)
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

