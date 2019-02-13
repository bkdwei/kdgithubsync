# coding: utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt, QFile, QTextCodec
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QWidget
import os
import sys
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from github_config import config
from fileutil import check_and_create, check_and_create_dir


class kdgithubsync(QWidget):
    def __init__(self):
        super(kdgithubsync, self).__init__()
        loadUi("kdgithubsync.ui", self)
        self.config = config()
        self.exec_cmd = self.config.exec_cmd
        self.config.show_result = self.show_result
        if self.config.conf:
            self.path = self.config.conf["path"]
            self.le_path.setText(self.path)

    @pyqtSlot()
    def on_pb_config_account_clicked(self):
        self.config.show()
        self.config.path = self.le_path.text()

    @pyqtSlot()
    def on_pb_generate_key_clicked(self):
        if not self.config.conf["email"]:
            self.on_pb_config_account_clicked()
        self.show_result("正在生成令牌，请回车确认")
        self.exec_cmd("ssh-keygen -t rsa -C {}".format(self.config.conf["email"]))
        self.show_result("生成令牌结束")

    @pyqtSlot()
    def on_pb_view_key_clicked(self):
        with open(os.environ["HOME"] + "/.ssh/id_rsa.pub", "r") as f:
            QMessageBox.information(self, "令牌", f.read(), QMessageBox.Yes)

    @pyqtSlot()
    def on_pb_open_github_clicked(self):
        webbrowser.open_new_tab("https://www.github.com")

    @pyqtSlot()
    def on_pb_init_project_clicked(self):
        self.path = self.le_path.text()
        if self.path and self.config.conf:
            check_and_create_dir(self.path)
            self.show_result("正在初始化项目")
            cmd_init_project = "cd {};git init;git remote add origin git@github.com:{}/{}.git".format(
                self.path, self.config.conf["username"], self.config.conf["project"]
            )
            self.exec_cmd(cmd_init_project)
            self.show_result("初始化项目成功")

    @pyqtSlot()
    def on_pb_update_repository_clicked(self):
        self.show_result("正在更新代码")
        self.path = self.le_path.text()
        self.exec_cmd(
            "cd {};git pull https://www.github.com/{}/{}.git".format(
                self.path, self.config.conf["username"], self.config.conf["project"]
            )
        )
        self.show_result("更新代码成功")

    @pyqtSlot()
    def on_pb_commit_update_clicked(self):
        comment, ok = QInputDialog.getMultiLineText(self, "备注更新", "请输入备注本次更新（可为空）:", "")
        if ok:
            self.show_result("正在提交更新")
            self.path = self.le_path.text()
            self.exec_cmd(
                "cd {};git add -A;git commit -m '{}'".format(self.path, comment)
            )
            self.show_result("提交更新成功")

    @pyqtSlot()
    def on_pb_push_update_clicked(self):
        self.show_result("正在推送代码到服务器")
        self.exec_cmd("cd {};git push -u origin master".format(self.path))
        self.show_result("推送代码到服务器成功")

    def show_result(self, result):
        self.te_result.setText(self.te_result.toPlainText() + "\n" + result)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = kdgithubsync()
    win.show()
    sys.exit(app.exec_())
