#TODO 成task批量管理,需要成task结构
import shutil
from PyQt5.QtCore import QRunnable, pyqtSlot,QThreadPool,pyqtSignal,QObject
from PyQt5.Qt import (QApplication, QWidget, QPushButton)
import sys
from plugin.scan.preprocess.preprocess import start_preprocess
from plugin.scan.model.model import predict_all
from plugin.config.config import cfg
import os
class TaskSignals(QObject):
    # 这些信号只能写在继承自QObject的类型里。注意不能写在__init__里。
        finished = pyqtSignal(str)#Task结束,输出扫描文件夹位置
        getFile=pyqtSignal((str,str,str))#扫描到文件 参数分别为 文件路径，文件名，文件类型
        getFileType=pyqtSignal(bool,str)#得到文件类型(敏感) 参数为 文件敏感度，文件路径
       
class ScanTask(QRunnable):
    class ModelTask(QRunnable):
        def __init__(self, inputText,fullpath):
            super().__init__()
            self.inputText=inputText
            self.fullpath=fullpath
            self.signals=TaskSignals()
        def run(self):
            self.signals.getFileType.emit(predict_all(self.inputText),self.fullpath) # 发送函数执行完成的信号
    def __init__(self, path:str):
        super().__init__()
        self.path=path
        self.signals=TaskSignals()
        self.ThreadPool=QThreadPool()
        self.ThreadPool.setMaxThreadCount(cfg.maxThread.value)
    def run(self):
        for text,fullpath in start_preprocess(self.path,False,self.signals):
            m=ScanTask.ModelTask(text,fullpath)
            m.signals.getFileType.connect(self.signals.getFileType)
            self.ThreadPool.start(m)
        self.ThreadPool.waitForDone()
        self.signals.finished.emit(self.path) # 发送函数执行完成的信号
     