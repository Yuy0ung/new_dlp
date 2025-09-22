#设置，包含保护模式，模型切换等\
# coding:utf-8
from plugin.config.config import cfg
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog


class FilterInterface(ScrollArea):
    """ Setting interface """

    whiteBoardCardChanged = pyqtSignal(list)
    blackBoardCardChanged=pyqtSignal(list)
    def __init__(self,text,parent=None):
        super().__init__(parent=parent)
        self.parent=parent
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        
        self.settingLabel = QLabel(self.tr("过滤器"), self)
        self.FiltersGroup = SettingCardGroup(
            self.tr("黑/白名单"), self.scrollWidget)
        self.setObjectName(text.replace(' ', '-'))
        self.whiteBoardCard = FolderListSettingCard(#白名单
            cfg.whiteFolders,
            self.tr("不会被保护的文件夹"),
            directory=QStandardPaths.writableLocation(QStandardPaths.MusicLocation),
            parent=self.FiltersGroup
        )
        self.blackBoardCard = FolderListSettingCard(#黑名单
            cfg.blackFolders,
            self.tr("保护的文件夹"),
            directory=QStandardPaths.writableLocation(QStandardPaths.MusicLocation),
            parent=self.FiltersGroup
        )
        # music folders
        # application
        cfg.themeChanged.connect(self.__setQss)
        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # add cards to group
        self.FiltersGroup.addSettingCard(self.whiteBoardCard)
        self.FiltersGroup.addSettingCard(self.blackBoardCard)
        # add setting card group to layout
        self.expandLayout.addWidget(self.FiltersGroup)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
    def __connectSignalToSlot(self):
        """ connect signal to slot """

        # music in the pc
        self.whiteBoardCard.folderChanged.connect(
            self.whiteBoardCardChanged)
        self.blackBoardCard.folderChanged.connect(
            self.whiteBoardCardChanged)
