# -*- coding:utf-8 -*-

import os
import sys
import webbrowser
from PyQt5.QtCore import pyqtSlot, QProcess
from PyQt5.QtWidgets import QWidget, QApplication, QInputDialog, QMessageBox
from PyQt5.uic import loadUi
from github_config import config
from fileutil import check_and_create, check_and_create_dir


class kdgithubsync(QWidget):
    def __init__(self):
        super(kdgithubsync, self).__init__()
        loadUi("kdgithubsync.ui", self)
        self.config = config()
        self.config.show_result = self.show_result
        if self.config.conf:
            self.path = self.config.conf["path"]
            self.le_path.setText(self.path)
        # ~ 用于执行linux的git指令
        self.process = QProcess()
        #~ self.process.readyReadStandardError.connect(self.onReadyReadStandardOutput)
        #~ self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.onReadyReadStandardOutput)
        #~ self.process.finished.connect(self.onReadyReadStandardOutput)
        #~ self.process.stateChanged.connect(self.onReadyReadStandardOutput)


    # ~ 配置帐号
    @pyqtSlot()
    def on_pb_config_account_clicked(self):
        self.config.show()
        self.config.path = self.le_path.text()

    # ~ 生成令牌
    @pyqtSlot()
    def on_pb_generate_key_clicked(self):
        if not self.config.conf["email"]:
            self.on_pb_config_account_clicked()
        self.show_result("$ 正在生成令牌，请回到终端回车确认")
        self.exec_cmd("ssh-keygen -t rsa -C {}".format(self.config.conf["email"]))
        # ~ self.show_result("$ 生成令牌结束")

    # ~ 查看令牌
    @pyqtSlot()
    def on_pb_view_key_clicked(self):
        with open(os.environ["HOME"] + "/.ssh/id_rsa.pub", "r") as f:
            QMessageBox.information(self, "令牌", f.read(), QMessageBox.Yes)

    # ~ 打开github.com
    @pyqtSlot()
    def on_pb_open_github_clicked(self):
        self.init_project_name()
        webbrowser.open_new_tab("https://www.github.com/" + self.config.conf["username"] + "/" + self.project_name)

    # ~ 初始化项目
    @pyqtSlot()
    def on_pb_init_project_clicked(self):
        self.path = self.le_path.text()
        if self.path and self.config.conf:
            check_and_create_dir(self.path)
            self.init_project_name()
            # ~ self.show_result("$正在初始化项目" + self.project_name)
            os.chdir(self.path)
            cmd_init_project = "cd {};git init;git remote add origin git@github.com:{}/{}.git".format(
                self.path, self.config.conf["username"], self.project_name
            )
            self.exec_cmd(cmd_init_project)
            self.show_result("$ 初始化项目成功")

    # ~ 根据项目地址截取项目名称,如/home/bkd/pyqt/kdPythonAPIViewer,则项目名为kdPythonAPIViewer
    def init_project_name(self):
        project_path = self.le_path.text()
        if "/" == project_path[-1]:
            project_path = project_path[:-1]
        last_index_slash = project_path.rfind("/")
        self.project_name = project_path[last_index_slash + 1 :]

    # ~ 更新代码
    @pyqtSlot()
    def on_pb_update_repository_clicked(self):
        self.show_result("$ 正在更新代码")
        self.init_project_name()
        self.path = self.le_path.text()
        os.chdir(self.path)
        self.exec_cmd(
            "cd {};pwd;git pull https://www.github.com/{}/{}.git".format(
                self.path, self.config.conf["username"], self.project_name
            )
        )
        self.show_result("$ 更新代码成功")

    # ~ 提交更新到本地仓库,不会推送到服务器
    @pyqtSlot()
    def on_pb_commit_update_clicked(self):
        comment, ok = QInputDialog.getMultiLineText(self, "备注更新", "请输入备注本次更新（可为空）:", "")
        if ok:
            # ~ self.show_result("正在提交更新")
            self.path = self.le_path.text()
            os.chdir(self.path)
            self.exec_cmd(
                "cd {};git add -A;git commit -m '{}'".format(self.path, comment)
            )
            self.show_result("$ 提交更新成功")

    # ~ 推送修改过的代码到github服务器
    @pyqtSlot()
    def on_pb_push_update_clicked(self):
        # ~ self.show_result("正在推送代码到服务器")
        os.chdir(self.path)
        self.exec_cmd("cd {};git push -u origin master".format(self.path))
        self.show_result("$ 推送代码到服务器成功")

    # ~ 在终端输出信息
    def show_result(self, result):
        print(result)
        self.te_result.append(result)

    def onReadyReadStandardOutput(self):
        result = self.process.readAllStandardOutput().data().decode()
        self.show_result(result.strip())

    def exec_cmd(self, cmd):
        if cmd.find("ssh-keygen") >= 0:
            self.process.startDetached(cmd)
        else:
            cmds = cmd.split(";")
            for single_cmd in cmds:
                #~ 尚未启动
                print("cmd:" + single_cmd +",process state:" + str(self.process.state()))
                self.show_result("$ " + single_cmd)
                if self.process.state() == 0:
                    self.process.start(single_cmd)
                #~ 正在运行中
                elif  self.process.state() == 1:
                    self.process.waitForFinished(-1)
                    self.process.start(single_cmd)
        self.process.waitForFinished(-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = kdgithubsync()
    win.show()
    sys.exit(app.exec_())
