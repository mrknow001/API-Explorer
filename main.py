from PyQt5 import QtWidgets, QtCore, QtGui
from UI import Ui_MainWindow
import sys
import images
import core
from database import SessionLocal, engine
from models import APP, Group, Function

# 创建数据库表
APP.metadata.create_all(bind=engine)
Group.metadata.create_all(bind=engine)
Function.metadata.create_all(bind=engine)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 连接ComboBox的currentIndexChanged信号到change_combox2方法
        self.ui.comboBox.currentIndexChanged.connect(self.change_combox2)
        # 连接ComboBox_2的currentIndexChanged信号到change_combox3方法
        self.ui.comboBox_2.currentIndexChanged.connect(self.change_combox3)

    def change_combox2(self):
        # 先清空comboBox_2以及comboBox_3中的数据
        self.ui.comboBox_2.clear()
        self.ui.comboBox_3.clear()
        core.comboBox_2_function(self.ui)

    def change_combox3(self):
        # 先清空comboBox_3中的数据
        self.ui.comboBox_3.clear()
        core.comboBox_3_function(self.ui)

    def closeEvent(self, event):
        try:
            reply = QtWidgets.QMessageBox.question(self, '提醒', "是否要退出程序？",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
                print("主窗口已关闭")
            else:
                event.ignore()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 解决高分辨率问题（网上搜的，暂未发现，如果发现有问题可以试试这条）
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    ui = widget.ui
    widget.setWindowTitle("API-Explorer v2.1.0")
    widget.setWindowIcon(QtGui.QIcon(":/icon.ico"))
    widget.show()
    core.key_function(ui)
    core.comboBox_function(ui)
    sys.exit(app.exec_())
