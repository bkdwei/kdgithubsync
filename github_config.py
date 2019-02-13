# coding: utf-8

import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.uic import loadUi
from fileutil import check_and_create, check_and_create_dir


class config(QDialog):

    def __init__(self):
        super(config, self).__init__()
        loadUi("github_config.ui", self)
        self.config_path = os.environ["HOME"] + \
            "/.config/kdgithubsync/config.json"
        print(self.config_path)
        self.init_conf()

    def init_conf(self):
        check_and_create(self.config_path)
        with open(self.config_path, "r") as f:
            content = f.read().strip()
            print("content:"+content)
            if content != "":
                conf = json.loads(content)
                self.le_username.setText(conf["username"])
                self.le_email.setText(conf["email"])
                self.le_project.setText(conf["project"])
                self.conf = conf
                self.path = conf["path"]
            else :
                self.conf = None

    @pyqtSlot()
    def on_buttonBox_accepted(self):
        print("accepted")
        conf = {}
        conf["username"] = self.le_username.text()
        conf["email"] = self.le_email.text()
        conf["project"] = self.le_project.text()
        conf["path"] = self.path
        check_and_create(self.config_path)
        check_and_create_dir(self.path)
        with open(self.config_path, "w+") as f:
            f.write(json.dumps(conf))
            os.system("cd {};git config --global user.name {};git config --global user.email {};".format(
                self.path, conf["username"], conf["email"]))
            os.system("echo 设置帐号信息成功")
        self.conf = conf

    @pyqtSlot()
    def on_buttonBox_rejected(self):
        print("rejected(")
