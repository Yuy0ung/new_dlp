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


class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    tempFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)
    enableShowFullPathChanged=pyqtSignal(bool)
    enableAddProtectionChanged=pyqtSignal(bool)
    enablebackScanChanged=pyqtSignal(bool)
    def __init__(self,text,parent=None):
        super().__init__(parent=parent)
        self.parent=parent
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)
        self.setObjectName(text.replace(' ', '-'))
        # music folders
        self.foldersGroup = SettingCardGroup(
            self.tr("文件夹"), self.scrollWidget)
        # self.musicFolderCard = FolderListSettingCard(
        #     cfg.musicFolders,
        #     self.tr("Local music library"),
        #     directory=QStandardPaths.writableLocation(QStandardPaths.MusicLocation),
        #     parent=self.musicInThisPCGroup
        # )
        self.tempFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.SAVE,
            self.tr("temp directory"),
            cfg.get(cfg.tempDir),
            self.foldersGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard=CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # scan
        self.scanGroup = SettingCardGroup(self.tr('扫描'), self.scrollWidget)
        self.maxThreadCard = RangeSettingCard(
            cfg.maxThread,
            FIF.SEARCH,
            self.tr("扫描线程限制"),
            parent=self.scanGroup
        )
        self.scanModelCard = OptionsSettingCard(
            cfg.scanModel,
            FIF.MESSAGE,
            self.tr('模型选择'),
            texts=[
                self.tr('Standard quality'), self.tr('High quality'),
                self.tr('Super quality'), self.tr('Lossless quality')
            ],
            parent=self.scanGroup
        )
        self.enableShowFullPathCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("展示文件完整路径"),
            self.tr("包含盘符的完整文件路径"),
            configItem=cfg.enableShowFullPath,
            parent=self.scanGroup
        )
        self.enableAddProtectionCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("自动将敏感文件加入保护范围"),
            self.tr("当扫描中出现敏感文件,将会自动将其加入敏感数据库并对其执行保护(需开启保护功能)"),
            configItem=cfg.enableAddProtection,
            parent=self.scanGroup
        )
        self.enablebackScanCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("自动扫描当前进行操作的文件"),
            self.tr("当用户读取文件时,会自动扫描其是否为敏感文件"),
            configItem=cfg.enablebackScan,
            parent=self.scanGroup
        )
        # desktop lyric
        self.deskLyricGroup = SettingCardGroup(self.tr('Desktop Lyric'), self.scrollWidget)
        self.deskLyricFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font'),
            parent=self.deskLyricGroup
        )
        self.deskLyricHighlightColorCard = ColorSettingCard(
            cfg.deskLyricHighlightColor,
            FIF.PALETTE,
            self.tr('Foreground color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeColorCard = ColorSettingCard(
            cfg.deskLyricStrokeColor,
            FIF.PENCIL_INK,
            self.tr('Stroke color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeSizeCard = RangeSettingCard(
            cfg.deskLyricStrokeSize,
            FIF.HIGHTLIGHT,
            self.tr('Stroke size'),
            parent=self.deskLyricGroup
        )
        self.deskLyricAlignmentCard = OptionsSettingCard(
            cfg.deskLyricAlignment,
            FIF.ALIGNMENT,
            self.tr('Alignment'),
            texts=[
                self.tr('Center aligned'), self.tr('Left aligned'),
                self.tr('Right aligned')
            ],
            parent=self.deskLyricGroup
        )

        # main panel
        self.mainPanelGroup = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('关闭后最小化到托盘'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )
        self.enableProctectionCard = SwitchSettingCard(
            FIF.PROJECTOR,
            self.tr('保护模式'),
            self.tr('会阻拦所有选择的文件的读取写入操作'),
            configItem=cfg.enableProctection,
            parent=self.mainPanelGroup
        )
        # update software
        self.updateSoftwareGroup = SettingCardGroup(self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)

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
        # self.musicInThisPCGroup.addSettingCard(self.musicFolderCard)
        self.foldersGroup.addSettingCard(self.tempFolderCard)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.scanGroup.addSettingCard(self.maxThreadCard)
        self.scanGroup.addSettingCard(self.scanModelCard)
        self.scanGroup.addSettingCard(self.enableShowFullPathCard)
        self.scanGroup.addSettingCard(self.enableAddProtectionCard)
        self.scanGroup.addSettingCard(self.enablebackScanCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricFontCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricHighlightColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeSizeCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricAlignmentCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)
        self.mainPanelGroup.addSettingCard(self.enableProctectionCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.foldersGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.scanGroup)
        self.expandLayout.addWidget(self.deskLyricGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.desktopLyricFont = font

    def __onTempFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.tempDir) == folder:
            return

        cfg.set(cfg.tempDir, folder)
        self.tempFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # music in the pc
        # self.musicFolderCard.folderChanged.connect(
        #     self.musicFoldersChanged)
        self.tempFolderCard.clicked.connect(
            self.__onTempFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # playing interface
        self.deskLyricFontCard.clicked.connect(self.__onDeskLyricFontCardClicked)

        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)
        self.enableShowFullPathCard.checkedChanged.connect(
            self.parent.homeInterface.DisplyFullPath
        )
        self.enableAddProtectionCard.checkedChanged.connect(
            self.enableAddProtectionChanged
        )
        self.enablebackScanCard.checkedChanged.connect(
            self.enablebackScanChanged
        )
        self.enableProctectionCard.checkedChanged.connect(
            self.parent.homeInterface.DisplyProtection
        )
        self.enableProctectionCard.checkedChanged.connect(
            self.parent.ProtectionThreadEnd
        )
        
