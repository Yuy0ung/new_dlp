# coding:utf-8
from enum import Enum

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QGuiApplication, QFont
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)


class SongQuality(Enum):
    """ Online song quality enumeration class """

    STANDARD = "Standard quality"
    HIGH = "High quality"
    SUPER = "Super quality"
    LOSSLESS = "Lossless quality"


class MvQuality(Enum):
    """ MV quality enumeration class """

    FULL_HD = "Full HD"
    HD = "HD"
    SD = "SD"
    LD = "LD"


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # folders
    # musicFolders = ConfigItem(
    #     "Folders", "LocalMusic", [], FolderListValidator())
    tempDir = ConfigItem(
        "缓存目录", "Temp", "temp", FolderValidator())
    blackFolders=ConfigItem(
        "Folders", "blackFolders", [], FolderListValidator())
    whiteFolders=ConfigItem(
        "Folders", "whiteFolders", [], FolderListValidator())
    # scan
    scanModel = OptionsConfigItem(
        "Scan", "scanModel", SongQuality.STANDARD, OptionsValidator(SongQuality), EnumSerializer(SongQuality))
    maxThread = RangeConfigItem(
        "Scan", "maxThread", 30, RangeValidator(0, 50))
    enableShowFullPath =  ConfigItem(
        "Scan", "EnableShowFullPath", False, BoolValidator())
    enableAddProtection = ConfigItem(
        "Scan", "EnableAddProtection", False, BoolValidator())
    enablebackScan=ConfigItem(
        "Scan", "enablebackScan", False, BoolValidator())
    # main window
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    enableProctection=ConfigItem(
        "MainWindow", "Protection", False, BoolValidator())
    playBarColor = ColorConfigItem("MainWindow", "PlayBarColor", "#225C7F")
    recentPlaysNumber = RangeConfigItem(
        "MainWindow", "RecentPlayNumbers", 300, RangeValidator(10, 300))
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # desktop lyric
    deskLyricHighlightColor = ColorConfigItem(
        "DesktopLyric", "HighlightColor", "#0099BC")
    deskLyricFontSize = RangeConfigItem(
        "DesktopLyric", "FontSize", 50, RangeValidator(15, 50))
    deskLyricStrokeSize = RangeConfigItem(
        "DesktopLyric", "StrokeSize", 5, RangeValidator(0, 20))
    deskLyricStrokeColor = ColorConfigItem(
        "DesktopLyric", "StrokeColor", Qt.black)
    deskLyricFontFamily = ConfigItem(
        "DesktopLyric", "FontFamily", "Microsoft YaHei")
    deskLyricAlignment = OptionsConfigItem(
        "DesktopLyric", "Alignment", "Center", OptionsValidator(["Center", "Left", "Right"]))

    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())

    @property
    def desktopLyricFont(self):
        """ get the desktop lyric font """
        font = QFont(self.deskLyricFontFamily.value)
        font.setPixelSize(self.deskLyricFontSize.value)
        return font

    @desktopLyricFont.setter
    def desktopLyricFont(self, font: QFont):
        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
        self.deskLyricFontFamily.value = font.family()
        self.deskLyricFontSize.value = max(15, int(font.pointSize()*dpi/72))
        self.save()


# YEAR = 2023
# AUTHOR = "zhiyiYo"
# VERSION = __version__
# HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"
# FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
# RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"


cfg = Config()
qconfig.load('~/config.json', cfg)