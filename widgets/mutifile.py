#TODO 主页，主要有扫描的文件夹(多个),当前已经扫描的文件

from tkinter.filedialog import FileDialog
from PyQt5.QtCore import QModelIndex, Qt,QThreadPool
from PyQt5.QtGui import QIcon, QDesktopServices,QPalette
from PyQt5.QtWidgets import QApplication, QFrame, QLayout, QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout,QSizePolicy,QFileDialog,QWIDGETSIZE_MAX
import pandas as pd
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, SplitFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, CheckBox)
from qfluentwidgets import FluentIcon as FIF

from PyQt5.QtCore import Qt, QTimer,pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QHBoxLayout, QHeaderView, QCheckBox
from qfluentwidgets import IndeterminateProgressBar, ProgressBar, FluentThemeColor, ToggleToolButton, FluentIcon,TextEdit,VBoxLayout,TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet
from plugin.scan.scan import ScanTask,TaskSignals
from plugin.config.config import cfg
from plugin.tips.tips import TipsDesktop
class MutiFileWidget(QFrame):
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
    class TextEdit1(TextEdit):
        doubleclicked = pyqtSignal()  # 自定义 clicked 信号

        def mouseDoubleClickEvent(self, event):
            """重写鼠标点击事件"""
            super().mouseDoubleClickEvent(event)
            self.doubleclicked.emit()  # 发送 clicked 信号

        def dragEnterEvent(self, e):
            if e.mimeData().hasUrls():  # 如果拖入的是文件
                e.accept()  # 接受拖入事件
            else:
                e.ignore()

        def dropEvent(self, e):
            urls = e.mimeData().urls()
            if urls and urls[0].scheme() == 'file':
                paths = [url.toLocalFile() for url in urls]
                current_text = self.toPlainText().strip()
                if current_text:
                    paths = current_text.split(';') + paths
                self.setText('; '.join(paths))
                e.accept()
            else:
                e.ignore()
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        #个人变量
        self.ButtonLocked=False
        self.map=dict()
        self.TaskCount=0
        # 设置路径变量
        self.ScanPath = ''
        self.setObjectName(text.replace(' ', '-'))
        # 主垂直布局（上中下结构）
        self.vBoxLayout = VBoxLayout(self)

        # 上方水平布局（输入框+按钮）
        self.topLayout = QHBoxLayout()
        self.scandirEdit = MutiFileWidget.TextEdit1()
        self.scandirEdit.setMaximumHeight(40)  # 限制输入框高度



        self.button = ToggleToolButton(FluentIcon.PAUSE_BOLD, self)
        self.sharedButton = ToggleToolButton(FluentIcon.SHARE, self)
        # 中间进度条
        self.inProgressBar = IndeterminateProgressBar()
         # 默认隐藏
        self.inProgressBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # 下方表格（核心区域）
        self.tableView = TableWidget()
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)

        self.tableView.setWordWrap(False)
        # self.tableView.setRowCount(60)
        self.tableView.setColumnCount(5)
        self.tableView.setAutoScroll(True)
        
        self.tableView.setMinimumHeight(380)
        # self.tableView.setMaximumSize(65536, 65536)
        self.tableView.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableView.setItemDelegate(MutiFileWidget.CustomTableItemDelegate(self.tableView))
        # 设置表格列宽度自适应
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        # pathsTableView 用于显示拖入的文件路径
        self.pathsTableView = TableWidget()
        self.pathsTableView.setBorderVisible(True)
        self.pathsTableView.setBorderRadius(8)
        self.pathsTableView.setWordWrap(False)
        self.pathsTableView.setColumnCount(2)
        self.pathsTableView.setHorizontalHeaderLabels(['Path', 'Delete'])
        self.pathsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pathsTableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pathsTableView.setMinimumHeight(160)
        # 布局配置
        self.topLayout.addWidget(self.scandirEdit, 1)  # 输入框横向拉伸
        self.topLayout.addWidget(self.button, 0, Qt.AlignRight)  # 按钮右对齐
        self.topLayout.addWidget(self.sharedButton, 0, Qt.AlignRight)  # 按钮右对齐
        self.vBoxLayout.addLayout(self.topLayout,0)     # 上方布局（不拉伸）
        self.vBoxLayout.insertWidget(1, self.pathsTableView)  # 在进度条上方插入新的 TableWidget
        self.vBoxLayout.addWidget(self.inProgressBar,0,Qt.AlignVCenter) # 进度条（自动高度） 
        self.vBoxLayout.addWidget(self.tableView,20)  # 表格区域（垂直拉伸）
        self.vBoxLayout.setContentsMargins(30, 50, 20,20)
        self.vBoxLayout.setSpacing(12)  # 控件间距
        #初始值设置
        self.inProgressBar.setHidden(True)
        self.inProgressBar.pause()
        self.button.setIcon(FluentIcon.PLAY_SOLID)
        #事件连接
        self.button.clicked.connect(self.onButtonClicked)
        self.scandirEdit.doubleclicked.connect(self.onScandirEditDoubleClicked)
        self.scandirEdit.textChanged.connect(self.onScandirEditTextChanged)

        # 支持拖曳
        self.scandirEdit.setAcceptDrops(True)
        self.sharedButton.clicked.connect(self.output_csv)
        self.tableView.setHorizontalHeaderLabels(['FullPath', 'FileName', 'Type', 'FileType', 'IsProtection'])
        self.tableView.setSelectionBehavior(QTableWidget.SelectItems)
        self.tableView.setSelectionMode(QTableWidget.ContiguousSelection)
    def onButtonClicked(self):
        if self.ButtonLocked:
            return
        if self.inProgressBar.isStarted():
            self.inProgressBar.setHidden(True)
            self.inProgressBar.pause()
            self.button.setIcon(FluentIcon.PLAY_SOLID)
        elif(self.ScanPath==''): # 路径为空
            return
        else:
            self.inProgressBar.setHidden(False)
            self.inProgressBar.resume()
            self.button.setIcon(FluentIcon.PAUSE_BOLD)
            self.StartScanTask()
    def onScandirEditDoubleClicked(self):
        """设置扫描路径"""
        path = QFileDialog.getExistingDirectory(self, "扫描路径", "C:\\")
        self.ScanPath=(self.ScanPath+";"+path).strip(";").strip()
        self.scandirEdit.setText(self.ScanPath)
        print(f"扫描路径为 {path}")
    def onScandirEditTextChanged(self):
        self.ScanPath = self.scandirEdit.toPlainText().strip()
        self.updatePathsTableView()

    def updatePathsTableView(self):
        paths = self.ScanPath.split(';')
        self.pathsTableView.setRowCount(len(paths))
        for i, path in enumerate(paths):
            pathItem = QTableWidgetItem(path)
            self.pathsTableView.setItem(i, 0, pathItem)

            deleteCheckBox = CheckBox()  # 替换为 Fluent 的 CheckBox
            deleteCheckBox.setChecked(False)
            self.pathsTableView.setCellWidget(i, 1, deleteCheckBox)  # 使用 setCellWidget 替代 setItem
            # 连接 stateChanged 信号到槽函数
            deleteCheckBox.stateChanged.connect(lambda state, row=i: self.deletePathRow(row) if state == Qt.Checked else None)

    def deletePathRow(self, row):
        paths = self.ScanPath.split(';')
        del paths[row]
        self.ScanPath = '; '.join(paths)
        self.scandirEdit.setText(self.ScanPath)
        # self.pathsTableView.removeRow(row)  # 删除指定行

    def StartScanTask(self):
        self.ButtonLocked = True
        self.TaskCount=0
        # 扫描进程
        threadPool=QThreadPool.globalInstance()

        scan_paths = self.ScanPath.split(';')
        def UnlockButton():
            self.TaskCount+=1
            if self.TaskCount==len(scan_paths):
                self.ButtonLocked = False
                TipsDesktop.createSuccessInfoBar("扫描","扫描结束！")
            self.onButtonClicked()
        for path in scan_paths:
            task = ScanTask(path.strip())
            task.signals.finished.connect(UnlockButton)
            task.signals.getFile.connect(self.taskOnGetFile)
            task.signals.getFileType.connect(self.taskOnGetType)
            threadPool.start(task)
    def taskOnGetType(self,type,path):
        path=path.replace('\\','/')
        # print(self.map[path],2,type)
        filetypeItem = QTableWidgetItem( "敏感" if type else "普通")
        self.tableView.setItem(self.map[path.replace('\\','/')],2, filetypeItem)
        self.map.pop(path)
    def taskOnGetFile(self,fullpath,filename,type):
        rowCount=self.tableView.rowCount()
        self.tableView.insertRow(rowCount)
        fullpath=fullpath.replace('\\','/')
        fullpathItem=QTableWidgetItem(fullpath)
        self.tableView.setItem(rowCount,0, fullpathItem)
        filenameItem = QTableWidgetItem(filename)
        self.tableView.setItem(rowCount,1, filenameItem)
        filetypeItem = QTableWidgetItem(type)
        self.tableView.setItem(rowCount,3, filetypeItem)
        protectionChioce = QTableWidgetItem()
        protectionChioce.setCheckState(Qt.Unchecked)
        self.tableView.setItem(rowCount, 4, protectionChioce)
        item1 =QTableWidgetItem()
        self.tableView.setItem(rowCount,2,item1)
        self.map[fullpath]=rowCount


    def output_csv(self):
        """将表格数据导出为CSV文件"""
        path, _ = QFileDialog.getSaveFileName(self, "保存CSV文件", "", "CSV Files (*.csv)")
        ranges=self.tableView.selectedRanges()
        if path:
            if len(ranges)==0:
            # 获取表格中的所有数据
                rows = self.tableView.rowCount()
                cols = self.tableView.columnCount()
                data = []
                for row in range(rows):
                    row_data = []
                    for col in range(cols):
                        item = self.tableView.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    data.append(row_data)

                # 使用 pandas 将数据写入CSV文件
                df = pd.DataFrame(data, columns=[self.tableView.horizontalHeaderItem(i).text() for i in range(cols)])
                df.to_csv(path, index=False)
                print(f"数据已成功保存到 {path}")
            else:
                trange=ranges[0]
                data = []
                for row in range(trange.topRow(),trange.bottomRow()+1):
                    row_data = []
                    for col in range(trange.leftColumn(),trange.rightColumn()+1):
                        item = self.tableView.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    data.append(row_data)

                # 使用 pandas 将数据写入CSV文件
                df = pd.DataFrame(data, columns=[self.tableView.horizontalHeaderItem(i).text() for i in range(trange.leftColumn(),trange.rightColumn()+1)])
                df.to_csv(path, index=False)
                print(f"数据已成功保存到 {path}")
        pass
