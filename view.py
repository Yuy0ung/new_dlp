# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QUrl,QThreadPool
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, SplitFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont)

from qfluentwidgets import FluentIcon as FIF ,Icon
from widgets.filter import FilterInterface
from widgets.home import HomeWidget
from widgets.mutifile import MutiFileWidget
from widgets.setting import SettingInterface
from widgets.history import HistroyWidget
from plugin.protection.protection import Protection
from plugin.config.config import cfg
class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)
        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

        # !IMPORTANT: leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)


class Window(SplitFluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
       
        self.homeInterface = HomeWidget('扫描', self)#包含扫描一系
        self.folderInterface = MutiFileWidget('多文件夹扫描', self)#当前包含的文件夹
        self.historyInterface=HistroyWidget('历史记录',self)#敏感程序列表和拦截列表
        self.filterInterface = FilterInterface('过滤器',self)
        self.settingInterface = SettingInterface('设置', self)#设置
        #TODO 历史防护记录
        self.threadpool=QThreadPool()
        self.threadpool.setMaxThreadCount(cfg.maxThread.value)
        self.initNavigation()
        self.initWindow()
        if cfg.enableProctection.value:
            try:
                self.Protection=Protection()
                self.threadpool.start(self.Protection)
            except Exception as e:
                print(e)
        else:
            self.Protection=Protection()
        
        self.Protection.signals.UnknownEnd.connect(self.ProtectionThreadEnd)    
        self.Protection.signals.reject.connect(self.historyInterface.addHistory)
    def ProtectionThreadEnd(self,isUnkownEnd):
        if isUnkownEnd:
            self.threadpool.start(self.Protection)
        else:
            if self.Protection.stoped:
                del self.Protection
            else:
                self.Protection.stop()
            self.Protection=Protection()
        
        
    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', NavigationItemPosition.TOP)

        self.navigationInterface.addSeparator()
        self.addSubInterface(self.folderInterface, FIF.FOLDER, '多文件扫描', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.historyInterface,FIF.HISTORY,'历史记录',NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.filterInterface, FIF.FILTER, '过滤器', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        # NOTE: enable acrylic 
        
        # self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('Python')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
    if w.Protection:
        w.Protection.stop()
    w.threadpool.waitForDone()
    QThreadPool.globalInstance().waitForDone()
