#TODO 扫描的记录以及保护的记录
# coding:utf-8

import os
from tkinter.filedialog import FileDialog
from PyQt5.QtCore import QModelIndex, Qt,QThreadPool
from PyQt5.QtGui import QIcon, QDesktopServices,QPalette
from PyQt5.QtWidgets import QApplication, QFrame, QLayout, QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout,QSizePolicy,QFileDialog,QWIDGETSIZE_MAX
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, SplitFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

from PyQt5.QtCore import Qt, QTimer,pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QVBoxLayout, QHeaderView
from qfluentwidgets import IndeterminateProgressBar, ProgressBar, FluentThemeColor, ToggleToolButton, FluentIcon,TextEdit,VBoxLayout,TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet
from plugin.scan.scan import ScanTask,TaskSignals
from plugin.config.config import cfg
from plugin.tips.tips import TipsDesktop
from plugin.protection.protection import DosDict,NtDict
import time

class HistroyWidget(QFrame):
    class CustomTableItemDelegate(TableItemDelegate):
        """ Custom table item delegate """
        def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
            super().initStyleOption(option, index)
            if index.column() != 1:
                return

            if isDarkTheme():
                option.palette.setColor(QPalette.Text, Qt.white)
                option.palette.setColor(QPalette.HighlightedText, Qt.white)
            else:
                option.palette.setColor(QPalette.Text, Qt.red)
                option.palette.setColor(QPalette.HighlightedText, Qt.red)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        # setTheme(Theme.DARK)

        self.vBoxLayout = QVBoxLayout(self)
        self.tableView = TableWidget(self)
        
        # NOTE: use custom item delegate
        self.tableView.setItemDelegate(HistroyWidget.CustomTableItemDelegate(self.tableView))

        # select row on right-click
        self.tableView.setSelectRightClickedRow(True)

        # enable border
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)

        self.tableView.setWordWrap(False)
        self.tableView.setRowCount(0)
        self.tableView.setColumnCount(2)


        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['Date', 'fullpath'])
        self.tableView.resizeColumnsToContents()
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setSortingEnabled(True)
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setStyleSheet("Demo{background: rgb(255, 255, 255)} ")
        self.vBoxLayout.setContentsMargins(50, 30, 50, 30)

        spacer = QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.vBoxLayout.addItem(spacer)
        self.vBoxLayout.addWidget(self.tableView)
        self.resize(735, 760)
    def addHistory(self,inputpath):
        inputpath=(NtDict[inputpath[:23]]+inputpath[23:]).replace('\\',"/")#将nt路径转换成dos路径
        rowCount=self.tableView.rowCount()
        self.tableView.insertRow(rowCount)
        Date=QTableWidgetItem(time.ctime())
        fullpathItem=QTableWidgetItem(inputpath)
        self.tableView.setItem(rowCount,1, fullpathItem)
        dateItem=QTableWidgetItem(Date)
        self.tableView.setItem(rowCount,0, dateItem)
        

