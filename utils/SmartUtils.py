"""
SmartUtils
==========
A complete utility module made specifically for SmartLinker global needs.

:Copyright: © 2025-2026 by #theF∆STER™ UN!TY.
"""
__version__ = "v3.0.0" # Alpha #3
__author__ = "#theF∆STER™ CODE&BU!LD"

# NOTE: CODE&BU!LD is actually the software development section of the UN!TY group.
# (In case you would be wondering...)
# =========================================================

import argparse, ctypes, darkdetect, datetime, hashlib, json, magic, markdown, os, pathlib, pickle, platform, psutil, pygame, random, re
import requests, shutil, socket, stat, subprocess, sys, time, traceback, typing, threading, webbrowser, win32api, winreg
from bs4 import BeautifulSoup
from collections import Counter
from colorama import init, Fore, Back, Style
from enum import Enum
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from packaging.version import Version
from pathlib import Path
from PyQt6.Qsci import QsciScintilla, QsciLexerMarkdown
from PyQt6.QtCore import (
    pyqtSignal, QCoreApplication, QEvent, QEventLoop, QFileInfo, QLocale, QModelIndex, QObject, QRegularExpression, QSize, Qt, QThread, QTimer,
    QUrl
)
from PyQt6.QtGui import (
    QColor, QContextMenuEvent, QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QFont, QFontDatabase, QFontMetrics, QGuiApplication,
    QIcon, QKeyEvent, QPainter, QPixmap, QResizeEvent, QStandardItem, QStandardItemModel, QSyntaxHighlighter, QTextCharFormat, QTextCursor
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWebEngineCore import QWebEngineHistoryItem, QWebEngineNavigationRequest, QWebEngineSettings
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QBoxLayout, QCompleter, QFileDialog, QFileIconProvider, QGraphicsOpacityEffect, QGridLayout, QHBoxLayout,
    QHeaderView, QLayout, QScrollBar, QSizePolicy, QStatusBar, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
)
from qfluentwidgets import (
    getIconColor, qconfig, setFont, setTheme, setThemeColor, theme, themeColor, Action, BodyLabel, BoolValidator, CaptionLabel, CardWidget,
    ColorConfigItem, ColorDialog, ComboBox, CommandBar, ConfigItem, Dialog, ElevatedCardWidget, ExpandGroupSettingCard, FlowLayout,
    FluentFontIconBase, FluentIcon as FICO, FluentIconBase, FluentWidget, FluentWidgetTitleBar, FluentWindow, HyperlinkButton, HyperlinkCard,
    IconInfoBadge, IconWidget, ImageLabel, IndeterminateProgressRing, IndicatorPosition, InfoBadgePosition, InfoBar, InfoBarPosition,
    LargeTitleLabel, LineEdit, ListWidget, MessageBox, MessageBoxBase, MSFluentWindow, NavigationItemPosition, OptionsConfigItem, OptionsSettingCard,
    OptionsValidator, PrimaryDropDownPushButton, PrimaryPushButton, PrimaryPushSettingCard, ProgressBar, ProgressRing, PushButton, PushSettingCard,
    QConfig, RangeConfigItem, RangeValidator, RoundMenu, ScrollBar, SearchLineEdit, SimpleCardWidget, SimpleExpandGroupSettingCard,
    SingleDirectionScrollArea, SpinBox, SplashScreen, StateToolTip, StrongBodyLabel, SubtitleLabel, SwitchButton, SwitchSettingCard,
    TabCloseButtonDisplayMode, TableWidget, TabWidget, TextEdit, Theme, TitleLabel, ToolButton, ToolTipFilter, ToolTipPosition,
    TransparentDropDownPushButton, TransparentToggleToolButton, TransparentToolButton
)
from qframelesswindow import FramelessWindow, StandardTitleBar, TitleBar
from qframelesswindow.utils import getSystemAccentColor
from qframelesswindow.webengine import FramelessWebEngineView
from rich.console import Console
from rich.progress import Progress
from rich.theme import Theme as RTheme
from rich.traceback import install
from shiboken6 import isValid
from urllib.parse import quote, unquote, urlparse


# =========================================================

ROOT_PATH = Path(__file__).resolve().parent.parent #.parent

SmartLinkerID: str = "theFASTER.SmartLinker"
SmartLinkerName: str = "SmartLinker"
SmartLinkerVersion: str = __version__
SmartLinkerAuthor: str = __author__
SmartLinkerOwner: str = "#theF∆STER™ UN!TY"
SmartLinkerGitRepoURL: str = "https://github.com/theFASTER-UNiTY/SmartLinker"
SmartLinkerGitRepoAPI: str = "https://api.github.com/repos/theFASTER-UNiTY/SmartLinker"
SmartRichTheme = RTheme(
    {"smpurple": "#793bcc", "smblue": "#2196f3"}
)
RichCLI = Console(theme=SmartRichTheme)
install()
PURPLE = "\x1b[35m" # soon deprecated
init() # soon deprecated
pygame.init()
pygame.mixer.init()
soundStreamer = None
smLocale = QLocale.system()

class Config(QConfig):
    """
    SmartUtils
    ==========
    Global SmartLinker configuration handling class
    """
    mainBrowser = ConfigItem("General", "MainBrowser", "")
    mainBrowserPath = ConfigItem("General", "MainBrowserPath", "")
    mainBrowserIsManual = ConfigItem("General", "MainBrowserIsManual", False, BoolValidator())
    
    appTheme = OptionsConfigItem("Personalization", "AppTheme", "Auto", OptionsValidator(["Light", "Dark", "Auto"]))
    accentMode = OptionsConfigItem("Personalization", "AccentMode", "Custom", OptionsValidator(["System", "Custom"]))
    accentColor = ColorConfigItem("Personalization", "CustomAccentColorHex", "")
    micaEffect = ConfigItem("Personalization", "EnableMicaEffect", True, BoolValidator())
    showCommandBar = ConfigItem("Personalization", "ShowCommandBar", False, BoolValidator())
    showSplash = ConfigItem("Personalization", "ShowSplash", True, BoolValidator())
    splashDuration = RangeConfigItem("Personalization", "SplashDuration", 3000, RangeValidator(0, 10000))
    showUpdateBanners = ConfigItem("Personalization", "ShowUpdateBanners", True, BoolValidator(), restart=True)
    
    enableSoundEffects = ConfigItem("Sound", "EnableSoundEffects", False, BoolValidator())
    startupSFXPath = ConfigItem("Sound", "StartupSFXPath", "")
    successSFXPath = ConfigItem("Sound", "SuccessSFXPath", "")
    infoSFXPath = ConfigItem("Sound", "InfoSFXPath", "")
    warningSFXPath = ConfigItem("Sound", "WarningSFXPath", "")
    errorSFXPath = ConfigItem("Sound", "ErrorSFXPath", "")
    questionSFXPath = ConfigItem("Sound", "QuestionSFXPath", "")
    selectorSFXPath = ConfigItem("Sound", "SelectorSFXPath", "")
    
    closeOnBrowserSelect = ConfigItem("Selector", "CloseOnBrowserSelect", False, BoolValidator())
    showAddBrowserCard = ConfigItem("Selector", "ShowAddBrowserCard", False, BoolValidator())
    showLinkPreview = ConfigItem("Selector", "ShowLinkPreview", False, BoolValidator())

    checkUpdatesOnStart = ConfigItem("About", "CheckUpdatesOnStart", True, BoolValidator())
    lastCheckedDate = ConfigItem("About", "LastCheckedDate", "")
    updateAvailable = ConfigItem("About", "UpdateAvailable", False)
    updateVersion = ConfigItem("About", "UpdateVersion", "")
    
    mdStartInEditMode = ConfigItem("Markdown-General", "StartInEditMode", False, BoolValidator())
    
    mdFontFamily = ConfigItem("Markdown-Editor", "FontFamily", "")
    mdFontSize = ConfigItem("Markdown-Editor", "FontSize", 12)
    mdFontWeight = RangeConfigItem("Markdown-Editor", "FontWeight", 400, RangeValidator(100, 800))
    mdDisplayLineNumbers = ConfigItem("Markdown-Editor", "DisplayLineNumbers", True, BoolValidator())
    mdDisplaySymbolsBar = ConfigItem("Markdown-Editor", "DisplaySymbolsBar", True, BoolValidator())
    mdDisplayStatusBar = ConfigItem("Markdown-Editor", "DisplayStatusBar", True, BoolValidator())
    mdEnableWordWrap = ConfigItem("Markdown-Editor", "EnableWordWrap", False, BoolValidator())
    mdIndentWidth = RangeConfigItem("Markdown-Editor", "IndentationWidth", 4, RangeValidator(2, 8))
    mdDisplayIndentGuides = ConfigItem("Markdown-Editor", "DisplayIndentationGuides", True, BoolValidator())
    mdEnableAutoIndent = ConfigItem("Markdown-Editor", "EnableAutoIndent", True, BoolValidator())
    mdHighlightCurrentLine = ConfigItem("Markdown-Editor", "HighlightCurrentLine", True, BoolValidator())
    mdSelectionColorMode = OptionsConfigItem("Markdown-Editor", "SelectionColorMode", "Accent", OptionsValidator(["Accent", "Custom"]))
    mdSelectionCustomColor = ColorConfigItem("Markdown-Editor", "SelectionCustomColor", "#7f793bcc") #ff793bcc
    mdEnableSyntaxHighlighting = ConfigItem("Markdown-Editor", "EnableSyntaxHighlighting", True, BoolValidator())
    # to-do: syntax colors
    
    mdOpenExternalLinks = ConfigItem("Markdown-Viewer", "OpenExternalLinks", False, BoolValidator())
    mdCssSource = OptionsConfigItem("Markdown-Viewer", "CSSSource", "Default", OptionsValidator(["Default", "Local", "Custom"]))
    mdCssSourcePath = ConfigItem("Markdown-Viewer", "CSSSourcePath", "Default")
    mdCssProperties = ConfigItem("Markdown-Viewer", "CSSProperties", "")
    mdHomepageSource = OptionsConfigItem("Markdown-Viewer", "HomepageSource", "Default", OptionsValidator(["Default", "Local", "Custom"]))
    mdHomepageSourcePath = ConfigItem("Markdown-Viewer", "HomepageSourcePath", "Default")
    mdHomepageProperties = ConfigItem("Markdown-Viewer", "HomepageProperties", "")
    mdDragEnterJSFunction = ConfigItem("Markdown-Viewer", "DragEnterJSFunction", "")
    mdDragLeaveJSFunction = ConfigItem("Markdown-Viewer", "DragLeaveJSFunction", "")
    mdDropJSFunction = ConfigItem("Markdown-Viewer", "DropJSFunction", "")


class SegoeFontIcon(FluentFontIconBase):
    """
    SmartUtils
    ==========
    Class for SmartLinker's custom font-based icons
    """

    def path(self, theme=Theme.AUTO):
        return smart.resourcePath("resources/fonts/Icons.ttf")

    def iconNameMapPath(self):
        """ Override this method if you want to use `fromName` to create icons """
        return smart.resourcePath("resources/fonts/SegoeIconsMap.json")


class SegoeSVGIcon(FluentIconBase, Enum):
    """
    SmartUtils
    ==========
    Class for custom SVG-based Segoe Fluent icons
    """

    CHECK_CIRCLE = "CheckCircle"
    COLOR_LINE = "ColorLine"
    ERROR_CIRCLE = "ErrorCircle"
    LINK = "Link"
    MARKDOWN = "Markdown"
    NUMBER_SYMBOL = "NumberSymbol"
    REFRESH = "Refresh"
    SMARTLINKER_FILL = "SmartLinkerFill"
    SMARTLINKER_OUTLINE = "SmartLinkerOutline"
    STYLE_GUIDE = "StyleGuide"
    TEXT_WRAP = "TextWrap"

    def path(self, theme=Theme.AUTO) -> str:
        return smart.resourcePath(f"resources/icons/svg/{getIconColor(theme)}/{self.value}.svg")


class SmartLogic(QObject):
    """
    SmartUtils
    ==========
    General class for SmartLinker functions
    """
    historyChanged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def resourcePath(self, relativePath: str) -> str:
        """
        SmartUtils
        ==========
        Dynamic provider of internal resources and files
        
        Parameters
        ----------
        relativePath: string
            The path to the internal resource you want to access
        
        Returns
        -------
        :string: The dynamically-provided path to resource
        """
        if hasattr(sys, "_MEIPASS"):
            basePath = getattr(sys, "_MEIPASS", os.path.abspath("."))
        else:
            basePath = os.path.abspath(".")
        return os.path.join(basePath, relativePath)
        
    def loadBrowsers(self) -> dict[str, list]:
        """
        SmartUtils
        ==========
        Load all the saved browsers

        Returns
        -------
        _dict[str, list]_: THe complete, decrypted browsers registry
        """
        try:
            with open(browsersCfgFilePath, "rb") as browserReader:
                return pickle.load(browserReader)
        except Exception:
            return {
                "MyBrowsers": []
            }

    def writeBrowsers(self, browsers: dict[str, list]):
        """
        SmartUtils
        ==========
        Save all the changes made to the browsers list
        
        Parameters
        ----------
        browsers: dictionary[string, list]
            The browsers list you want to save to the browsers config file
        """
        try:
            with open(browsersCfgFilePath, "wb") as browserWriter:
                pickle.dump(browsers, browserWriter)
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to save browser-related changes: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to save browser-related changes: {e}")

    def loadHistory(self) -> dict[str, dict[str, list]]:
        """
        SmartUtils
        ==========
        Load the opened links history

        Returns
        -------
        *dict[str, list]*: The complete, unencrypted history
        """
        try:
            with open(historyFilePath, "rb") as historyReader:
                return pickle.load(historyReader)
        except Exception:
            return {
                "MyHistory": {}
            }

    def saveHistory(self, history: dict[str, dict[str, list]]):
        """
        SmartUtils
        ==========
        Save all the changes made to the opened links history
        
        Parameters
        ----------
        history: dict[str, list]
            The history you want to save to the encrypted history file
        """
        try:
            with open(historyFilePath, "wb") as historyWriter:
                pickle.dump(history, historyWriter)
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to save history-related changes: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to save history-related changes: {e}")

    def registerEntryToHistory(self, history: dict[str, dict[str, list]], browser: str, address: str):
        """
        SmartUtils
        ==========
        Register a new entry to the history

        Parameters
        ----------
        browser: str
            The name of the selected browser *(based on the SmartList)*
        address: str
            The URL loaded into the browser
        """
        now = datetime.datetime.now(datetime.timezone.utc)

        dateKey = now.strftime("%Y-%m-%d")

        # Calculate time integer (seconds since midnight)
        lastVisited = (now.hour * 3600) + (now.minute * 60) + now.second

        newEntry = {
            "lastVisited": lastVisited,
            "browser": browser,
            "address": address
        }

        historyReg = history["MyHistory"]
        if dateKey not in historyReg:
            historyReg[dateKey] = []
        historyReg[dateKey].insert(0, newEntry)

        self.saveHistory(history)
        self.historyChanged.emit(history)

    def renderTimeFromSecInt(self, secInt: int, showSec: bool = True, use24h: bool = True) -> str:
        """
        SmartUtils
        ==========
        Convert a total of seconds into time format

        Parameters
        ----------
        secInt: int
            The total of seconds to convert into time format
            *(it only converts seconds within a **24-hour span**)*
        use24h: bool
            Whether to render time into 24-hour format
            *(if `False`, render into AM/PM format)*
        """
        hours = secInt // 3600
        minutes = (secInt % 3600) // 60
        seconds = secInt % 60

        if not use24h:
            # Convert to 12-hour AM/PM format
            suffix = "PM" if hours >= 12 else "AM"
            hours12 = hours % 12
            if hours12 == 0:
                hours12 = 12
            return f"{hours12:02d}:{minutes:02d}{f":{seconds:02d}" if showSec else ""} {suffix}"
        else:
            # Standard 2h-hour format
            return f"{hours:02d}:{minutes:02d}{f":{seconds:02d}" if showSec else ""}"

    def restartApp(self, isScript: bool = False):
        """
        SmartUtils
        ==========
        Global method to restart the app

        Parameters
        ----------
        isScript: bool
            Whether the restart is called from a script
        """
        if isScript:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            execPath = sys.executable
            execArgs = sys.argv
            
            try:
                subprocess.Popen([execPath] + execArgs[1:])
                sys.exit()
            except Exception as e:
                print(f"{Fore.RED}Something went wrong while attempting to restart {SmartLinkerName} with 'subprocess': {e}{Style.RESET_ALL}\nRetrying with 'os.execv'...")
                self.managerLog(f"ERROR: Failed to restart {SmartLinkerName} with 'subprocess': {e}")
                self.managerLog("Retrying with 'os.execv'...")
                try:
                    os.execv(execPath, tuple([execPath] + execArgs[1:]))
                except Exception as ee:
                    print(f"{Fore.RED}Something went wrong while attempting to restart {SmartLinkerName} with 'os.execv': {ee}\nFailed to restart {SmartLinkerName}, please try again...{Style.RESET_ALL}")
                    self.managerLog(f"ERROR: Failed to restart {SmartLinkerName} with 'os.execv': {ee}")

    def stopApp(self):
        """
        SmartUtils
        ==========
        Global method to stop the app process
        """
        sys.exit()

    def centerWindow(self, window: QWidget):
        """
        SmartUtils
        ==========
        Center the target window

        Parameters
        ----------
        window: QWidget
            The window you want to center
        """
        screen = QApplication.primaryScreen()
        
        if screen:
            screenGeometry = screen.availableGeometry()
            windowGeometry = window.frameGeometry()
            screenCenter = screenGeometry.center()
            
            windowGeometry.moveCenter(screenCenter)
            
            window.move(windowGeometry.topLeft())

    def isDarkModeEnabled(self) -> bool:
        """
        SmartUtils
        ==========
        Windows registry-based checker for system dark mode

        Returns
        -------
        isDarkMode: boolean
            whether the system is in dark mode
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                isDarkMode = bool(value == 0)  # 0 = dark, 1 = light
        except Exception:
            isDarkMode = False  # default = light
        finally: return isDarkMode

    def playSound(self, sound, path: str, label: str):
        """
        SmartUtils
        ==========
        Sound effects player

        Parameters
        ----------
        sound: Unknown
            The component responsible for playing sound effect
        path: string
            The path to the sound effect file
        label: string
            The name you want to give the sound effect (for notification purposes)
        """
        sound = None
        try:
            sound = pygame.mixer.Sound(path)
            if sound: sound.play()
            else:
                print(f"{Fore.YELLOW}Unable to play the {label} sound, because it has not been loaded...{Style.RESET_ALL}")
                self.managerLog(f"WARNING: Unable to play the {label} sound, because it has not been loaded...")
        except Exception as e:
            sound = None
            print(f"{Fore.RED}Something went wrong while attempting to play the {label} sound: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to play the {label} sound: {e}")

    def checkConnectivity(self, hostname: str = "8.8.8.8", port: int = 53, timeout: float = 5.0) -> bool:
        """
        SmartUtils
        ==========
        Internet connectivity checker

        Parameters
        ----------
        hostname: string
            The IP address or the host name of the target server (8.8.8.8 = Google DNS)
        port: integer
            The port to be tested (53 = DNS, 443 = HTTP)
        timeout: float
            The maximum connection delay
        
        Returns
        -------
        isConnected: boolean
            Whether an internet connection has been established
        """
        isConnected = False
        try:
            socket.create_connection((hostname, port), timeout)
            isConnected = True
        except socket.gaierror:
            print(f"{Fore.RED}Failed to establish connection: the DNS address cannot be resolved...{Style.RESET_ALL}")
            self.managerLog("ERROR: Failed to establish connection: could not resolve DNS address...")
        except TimeoutError:
            print(f"{Fore.RED}Failed to establish connection: the timeout has been exceeded...{Style.RESET_ALL}")
            self.managerLog("ERROR: Failed to establish connection: timeout exceeded...")
        except OSError as ose:
            print(f"{Fore.RED}Failed to establish connection: an OS-related error occured: {ose}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to establish connection because of an OS-related error: {ose}")
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to establish connection: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to establish connection: {e}")
        finally: return isConnected

    def isWebLink(self, url: str) -> bool:
        """
        SmartUtils
        ==========
        Check if the provided URL is a web link

        Parameters
        ----------
        url: string
            The URL you want to check

        Returns
        -------
        isWebLink: boolean
            Whether the provided URL is a web link
        """
        isWebLink = False
        try:
            parsedUrl = urlparse(url)
            isWebLink = parsedUrl.scheme in ["http", "https"]
        except Exception as e:
            RichCLI.log(f"[red][b u]ERROR[/b u]: Failed to check if the provided URL is a web link: {e}[/]")
            self.managerLog(f"ERROR: Failed to check if the provided URL is a web link: {e}")
        finally: return isWebLink

    def isDarkMode(self) -> bool:
        """
        SmartUtils
        ==========
        DarkDetect library-based checker for system dark mode

        Returns
        -------
        :boolean: whether the system is in dark mode
        """
        return bool(darkdetect.isDark())

    def successNotify(self, title: str, content: str = "", parent = None):
        """
        SmartUtils
        ==========
        Success notification bar
        
        Parameters
        ----------
        title: string
            The title of the success notification bar
        content: string
            The message you want the success notification bar to display (optional)
        """
        InfoBar.success(
            title = title,
            content = content,
            orient = Qt.Orientation.Horizontal,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = 5000,
            parent = parent
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.successSFXPath), "success notification")

    def warningNotify(self, title: str, content: str = "", parent = None):
        """
        SmartUtils
        ==========
        Warning notification bar
        
        Parameters
        ----------
        title: string
            The title of the warning notification bar
        content: string
            The message you want the warning notification bar to display (optional)
        """
        InfoBar.warning(
            title = title,
            content = content,
            orient = Qt.Orientation.Vertical,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = 5000,
            parent = parent
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.warningSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.warningSFXPath), "warning notification")

    def errorNotify(self, traceback: typing.Any, title: str, content: str = "", parent = None):
        """
        SmartUtils
        ==========
        Error notification bar
        
        Parameters
        ----------
        traceback: Any
            The complete traceback of the error
        title: string
            The title of the error notification bar
        content: string
            The message you want the error notification bar to display (optional)
        parent
            The parent widget
        canCopy: boolean
            Whether the error can be copied to the clipboard
        """
        def showErrorDialog(infoBar: InfoBar):
            infoBar.closedSignal.emit()
            errorDlg = None
            errorDlg = ErrorDialog(traceback, parent)
            errorDlg.exec()

        bar = InfoBar.error(
            title = title,
            content = f"{content}\n\nClick on this notification to see more details.",
            orient = Qt.Orientation.Vertical,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = -1,
            parent = parent
        )
        bar.mousePressEvent = lambda a0, infoBar=bar: showErrorDialog(infoBar)

        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.errorSFXPath), "error notification")

    def infoNotify(self, title: str, content: str = "", parent = None): 
        """
        SmartUtils
        ==========
        Informative notification bar
        
        Parameters
        ----------
        title: string
            The title of the informative notification bar
        content: string
            The message you want the informative notification bar to display (optional)
        """
        InfoBar.info(
            title = title,
            content = content,
            orient = Qt.Orientation.Horizontal,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = 5000,
            parent = parent
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.infoSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.infoSFXPath), "information notification")

    def getFileIcon(self, filePath: str) -> QIcon:
        """
        SmartUtils
        ==========
        Specified executable icon provider

        Parameters
        ----------
        filePath: string
            The path to the executable you want the icon to be provided

        Returns
        -------
        :QIcon: The icon of the provided executable (whose path must be valid)
        """
        if filePath: return QFileIconProvider().icon(QFileInfo(filePath))
        return QIcon()

    def browseFileDialog(self, parent: typing.Optional[QWidget], dialogTitle: str = "", mainDir: str = "", typeFilter: str = "") -> str:
        """
        SmartUtils
        ==========
        Load a specified type file through file picker dialog

        Parameters
        ----------
        parent: QWidget
            The parent of the file picker dialog (optional)
        dialogTitle: string
            The file picker dialog title (optional but preferred)
        mainDir: string
            The main directory you want the dialog to open into (optional)
        typeFilter: string
            All the different file types you want to filter in the dialog (optional)
        
        Returns
        -------
        filePath: string
            The selected file path returned by the dialog
        """
        filePath, _ = QFileDialog.getOpenFileName(
            parent,
            dialogTitle,
            mainDir,
            typeFilter
        )
        if filePath: return filePath
        return ""

    def saveFileDialog(self, parent: typing.Optional[QWidget], dialogTitle: str = "", mainDir: str = "", typeFilter: str = "") -> str:
        """
        SmartUtils
        ==========
        Save a specified type file through file picker dialog

        Parameters
        ----------
        parent: QWidget
            The parent of the file picker dialog (optional)
        dialogTitle: string
            The file picker dialog title (optional but preferred)
        mainDir: string
            The main directory you want the dialog to open into (optional)
        typeFilter: string
            All the different file types you want to filter in the dialog (optional)
        
        Returns
        -------
        filePath: string
            The selected file path returned by the dialog
        """
        filePath, _ = QFileDialog.getSaveFileName(
            parent,
            dialogTitle,
            mainDir,
            typeFilter
        )
        if filePath: return filePath
        return ""

    def copyToClipboard(self, text: str):
        """
        SmartUtils
        ==========
        Copy the forwarded content to the system's clipboard

        Parameters
        ----------
        text: string
            The content you want to copy
        """
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        if isinstance(app, QApplication):
            clipboard = app.clipboard()

        if clipboard:
            clipboard.setText(text)
            print(f"Copied to clipboard: {Fore.BLUE}'{clipboard.text()}'{Style.RESET_ALL}")
        else:
            self.copyToClipboard(text)

    def isSystemDefault(self, appID: str) -> bool:
        """
        SmartUtils
        ==========
        Check if SmartLinker is set as the system's default browser
        
        Parameters
        ----------
        appID: string
            System-level SmartLinker's application identifier
        
        Returns
        -------
        isSystemDefault: boolean
            Whether SmartLinker is system's default browser
        """
        isSystemDefault = False
        httpKeyPath = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
        httpsKeyPath = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
        try:
            # Opens the registry key in read mode
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, httpKeyPath, 0, winreg.KEY_READ) as httpKey:
                # Gets the 'Progid' value
                httpProgID, _ = winreg.QueryValueEx(httpKey, 'Progid')
                # Compare the value with SmartLinker's ID
                isHttpDefault = bool(httpProgID == appID)
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, httpsKeyPath, 0, winreg.KEY_READ) as httpsKey:
                    httpsProgID, _ = winreg.QueryValueEx(httpsKey, 'Progid')
                    isHttpsDefault = bool(httpsProgID == appID)
                    isSystemDefault = isHttpDefault and isHttpsDefault
        except FileNotFoundError as fe:
            # The key doesn't exist, so no default browser has been set
            print(f"Registry information: {fe}")
        except Exception as e:
            print(f"An error occured while checking registry : {e}")
            self.errorNotify("Something went wrong...", f"An error occured while checking registry : {e}")
        finally: return isSystemDefault

    def isBrowserOpen(self, exePath: str) -> bool:
        """
        SmartUtils
        ==========
        Check if the specified SmartList browser process is running
        
        Parameters
        ----------
        exePath: string
            The complete path to the browser
        
        Returns
        -------
        isProcessOpen: boolean
            Whether the specified browser is running
        """
        browsName = os.path.basename(exePath).lower()
        for process in psutil.process_iter(['exe']):
            if process.info['exe']:
                isProcessOpen = os.path.basename(process.info['exe']).lower() == browsName
                if isProcessOpen:
                    RichCLI.print(f"[white on green]{browsName} == {os.path.basename(process.info['exe']).lower()}[/]")
                    break
                else: RichCLI.print(f"[white on red]{browsName} != {os.path.basename(process.info['exe']).lower()}[/]")
        RichCLI.print(f"\n'{browsName}' is running: [bold italic {"green]" if isProcessOpen else " red]"}{isProcessOpen}[/]\n")
        return isProcessOpen
    
    def isSoftwareRunning(self, exePath: str) -> bool:
        """
        SmartUtils
        ==========
        Check if the specified software process is running
        
        Parameters
        ----------
        exePath: string
            The complete path to the software executable
        
        Returns
        -------
        isProcessOpen: boolean
            Whether the specified software is running
        """
        softName = os.path.basename(exePath).lower()
        for process in psutil.process_iter(['exe']):
            if process.info['exe']:
                isProcessOpen = os.path.basename(process.info['exe']).lower() == softName
                if isProcessOpen: break
        return isProcessOpen

    def clearCLI(self):
        """
        SmartUtils
        ==========
        Command-line interface cleaner
        """
        os.system("cls")

    def consoleScript(self) -> str:
        """
        SmartUtils
        ==========
        SmartLinker name in-console renderer

        Returns
        -------
        :string: The rendered SmartLinker name
        """
        from utils.SmartCLIScripts import AsciiNames

        scripts = [
            AsciiNames._1911, AsciiNames.ANSI_SHADOW, AsciiNames.BALISTIC, AsciiNames.BANSHEE, AsciiNames.BIG_LIMPY,
            AsciiNames.BROADWAY, AsciiNames.COLOSSAL, AsciiNames.DOH, AsciiNames.REBEL, AsciiNames.SHADED_BLOCKY
        ]

        return random.choice(scripts)

    def managerLog(self, message: typing.Any):
        """
        SmartUtils
        ==========
        SmartLinker activity log writer

        Parameters
        ----------
        message: Any
            The message you want to write in the log
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("SmartLinkerReport.log", 'a', encoding="utf-8") as logger:
                logger.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to log the last event in the log file: {e}{Style.RESET_ALL}")
            return

    def selectorLog(self, message: typing.Any):
        """
        SmartUtils
        ==========
        Smart Selector activity log writer

        Parameters
        ----------
        message: Any
            The message you want to write in the log
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ROOT_PATH / "SmartSelectorReport.log", 'a', encoding="utf-8") as logger:
                logger.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to log the last event in the Selector log file: {e}{Style.RESET_ALL}")
            return

    def emptyManagerLog(self):
        """
        SmartUtils
        ==========
        Initialize SmartLinker activity log
        """
        try:
            with open("SmartLinkerReport.log", 'w') as clear:
                clear.write("SmartLinker - Smart Manager Activity Report\n" \
                            "-------------------------------------------\n\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to initialize the log file: {e}{Style.RESET_ALL}")
            return

    def emptySelectorLog(self):
        """
        SmartUtils
        ==========
        Initialize Smart Selector activity log
        """
        try:
            with open(ROOT_PATH / "SmartSelectorReport.log", 'w') as clear:
                clear.write("SmartLinker - Smart Selector Activity Report\n" \
                            "--------------------------------------------\n\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to initialize the Selector log file: {e}{Style.RESET_ALL}")
            return

    def hideLayoutWidgets(self, layout: QLayout):
        """
        SmartUtils
        ==========
        Hide the child widgets of a layout

        Parameters
        ----------
        layout: unknown
            The layout whose child widgets you want to hide
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item:
                widget = item.widget()
                cLayout = item.layout()
                if widget:
                    widget.hide()
                elif cLayout:
                    self.hideLayoutWidgets(cLayout)

    def showLayoutWidgets(self, layout: QLayout):
        """
        SmartUtils
        ==========
        Show the child widgets of a layout

        Parameters
        ----------
        layout: unknown
            The layout whose child widgets you want to show
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item:
                widget = item.widget()
                cLayout = item.layout()
                if widget:
                    widget.show()
                elif cLayout:
                    self.showLayoutWidgets(cLayout)

    def emptyLayout(self, layout: QLayout, childLayout: bool = False):
        """
        SmartUtils
        ==========
        Clear a layout (remove all the layout's child widgets)

        Parameters
        ----------
        layout: QLayout
            The layout you want to clear
        childLayout: boolean
            Whether to clean the child layout(s) of the current one
        """
        while layout.count():
            item = layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                subLayout = item.layout()
                if widget is not None:
                    widget.setParent(None)
                    layout.removeWidget(widget)
                if childLayout and subLayout is not None:
                    self.emptyLayout(subLayout)

    def getLatestVersionTagLocal(self) -> str:
        """
        SmartUtils
        ==========
        SmartLinker's latest version tag checker (local Git repository)

        Returns
        -------
        versionTag: string
            The latest version tag detected
        """
        try:
            print("Checking for latest version...")
            self.managerLog("Checking for latest version...")
            version = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                check=True,
                capture_output=True,
                text=True
            )
            versionTag = version.stdout.strip()
            print(f"{Fore.BLUE}Latest version: {versionTag}{Style.RESET_ALL}")
            self.managerLog(f"Latest version: {versionTag}")
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while checking the latest version: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to check latest version: {e}")
            versionTag = ""
        finally: return versionTag

    def getLatestVersionTag(self) -> str:
        """
        SmartUtils
        ==========
        SmartLinker's latest version tag checker

        Returns
        -------
        versionTag: string
            The latest version tag detected
        """
        tagUrl = f"{SmartLinkerGitRepoAPI}/tags"
        params = {'per_page': 1}
        versionTag: str = ""
        try:
            print("Checking for latest version...")
            self.managerLog("Checking for latest version...")
            response = requests.get(tagUrl, params, timeout=5)
            response.raise_for_status()
            tagsList = response.json()
            if tagsList:
                versionTag = tagsList[0].get("name")
                print(f"{Fore.BLUE}Latest version: {versionTag}{Style.RESET_ALL}")
                self.managerLog(f"Latest version: {versionTag}")
            else:
                print(f"{Fore.RED}Failed to get latest version tag from GitHub repository: there are no tags to be found...{Style.RESET_ALL}")
                self.managerLog("ERROR: Failed to get latest version tag from GitHub repository: could not find any tags...")
        except requests.exceptions.RequestException as re:
            print(f"{Fore.RED}Failed to communicate with GitHub repository: {re}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to communicate with GitHub repository: {re}")
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to get the latest version tag from GitHub: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to get latest version tag from GitHub repository: {e}")
        finally: return versionTag

    def getLatestReleaseTag(self) -> str:
        """
        SmartUtils
        ==========
        SmartLinker's latest release tag checker

        Returns
        -------
        releaseTag: string
            The latest release tag detected
        """
        releaseUrl = f"{SmartLinkerGitRepoAPI}/releases/latest"
        releaseTag: str = ""
        try:
            print("Checking for latest release version...")
            self.managerLog("Checking for latest release version...")
            response = requests.get(releaseUrl, timeout=5)
            response.raise_for_status()
            data = response.json()
            print(f"Latest release version: {releaseTag}")
            self.managerLog(f"Latest release version: {releaseTag}")
            releaseTag = data.get("tag_name")
        except requests.exceptions.RequestException as re:
            print(f"{Fore.RED}Failed to communicate with GitHub repository: {re}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to communicate with GitHub repository: {re}")
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to get the latest release tag from GitHub: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to get latest release tag from GitHub repository: {e}")
        finally: return releaseTag

    def covertToNoAlphaHEX(self, color: typing.Union[str, QColor]) -> str:
        """
        SmartUtils
        ==========
        Convert a color from HEX w/ alpha (#AARRGGBB) to HEX w/o alpha (#RRGGBB) format 

        Parameters
        ----------
        color: string | QColor
            The color whose format must be converted.
        
        Returns
        -------
        newColor: string
            The re-formatted color string.
        """
        try:
            oldColor = QColor(color)
            if not isValid(oldColor): raise ValueError("Incorrect HEX color format")
            
            red = oldColor.red()
            green = oldColor.green()
            blue = oldColor.blue()
            newColor = f"#{red:02x}{green:02x}{blue:02x}"
            return newColor
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to convert color format: {e}")
            newColor = ""
        finally: return newColor

    def convertToRGBA(self, color: typing.Union[str, QColor]) -> str:
        """
        SmartUtils
        ==========
        Convert a color to RGBA format 

        Parameters
        ----------
        color: string | QColor
            The color whose format must be converted.
        
        Returns
        -------
        newColor: string
            The re-formatted color string.
        """
        try:
            oldColor = QColor(color)
            if not isValid(oldColor): raise ValueError("Invalid color format")

            red = oldColor.red()
            green = oldColor.green()
            blue = oldColor.blue()
            alpha = oldColor.alphaF()
            newColor = f"rgba({red}, {green}, {blue}, {alpha})"
            return newColor
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to convert color format: {e}")
            newColor = ""
        finally: return newColor

    def convertToRGB(self, color: typing.Union[str, QColor]) -> str:
        """
        SmartUtils
        ==========
        Convert color to RGB format

        Parameters
        ----------
        color: string | QColor
            The color whose format must be converted.
        
        Returns
        -------
        newColor: string
            The re-formatted color string.
        """
        newColor = ""
        try:
            oldColor = QColor(color)
            if not isValid(oldColor): raise ValueError("Invalid color format")

            red = oldColor.red()
            green = oldColor.green()
            blue = oldColor.blue()
            newColor = f"{red}, {green}, {blue}"
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to convert color format: {e}")
        finally: return newColor

    def applyAlphaToRGB(self, color: typing.Union[str, QColor], alpha: int) -> QColor:
        """
        SmartUtils
        ==========
        Apply custom alpha value to color

        Parameters
        ----------
        color: string | QColor
            The color you want to modify.
        alpha: integer
            The alpha value you want to apply.

        Returns
        -------
        newColor: QColor
            The modified version of the color.
        """
        newColor = QColor()
        try:
            oldColor = QColor(color)
            if not isValid(oldColor): raise ValueError("Invalid color format entered")

            r, g, b, a = oldColor.getRgb()
            if r and g and b: oldColor.setRgb(r, g, b, alpha)
            newColor = oldColor
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to convert color format: {e}")
        finally: return newColor

    def getRed(self, color: typing.Union[str, QColor]) -> typing.Union[int, None]:
        """
        SmartUtils
        ==========
        Fetch a color's red value

        Parameters
        ----------
        color: string | QColor
            The color you want to get the red value from.

        Returns
        -------
        red: int | None
            The red value
        """
        red = 0
        try:
            rColor = QColor(color)
            if rColor.isValid():
                red, g, b, a = rColor.getRgb()
            else: red = 0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during red value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick red value from color: {e}")
            red = 0
        finally:
            return red

    def getGreen(self, color: typing.Union[str, QColor]) -> typing.Union[int, None]:
        """
        SmartUtils
        ==========
        Fetch a color's green value

        Parameters
        ----------
        color: string | QColor
            The color you want to get the green value from.

        Returns
        -------
        green: int | None
            The green value
        """
        green = 0
        try:
            gColor = QColor(color)
            if gColor.isValid():
                r, green, b, a = gColor.getRgb()
            else: green = 0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during green value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick green value from color: {e}")
            green = 0
        finally: return green

    def getBlue(self, color: typing.Union[str, QColor]) -> typing.Union[int, None]:
        """
        SmartUtils
        ==========
        Fetch a color's blue value

        Parameters
        ----------
        color: string | QColor
            The color you want to get the blue value from.

        Returns
        -------
        blue: int | None
            The blue value
        """
        blue = 0
        try:
            bColor = QColor(color)
            if bColor.isValid():
                r, g, blue, a = bColor.getRgb()
            else: blue = 0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during blue value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick blue value from color: {e}")
            blue = 0
        finally: return blue

    def getAlpha(self, color: typing.Union[str, QColor]) -> typing.Union[int, None]:
        """
        SmartUtils
        ==========
        Fetch a color's alpha value as an integer

        Parameters
        ----------
        color: string | QColor
            The color you want to get the alpha value from.

        Returns
        -------
        alpha: int | None
            The alpha value
        """
        alpha = 0
        try:
            aColor = QColor(color)
            if aColor.isValid():
                r, g, b, alpha = aColor.getRgb()
            else: alpha = 0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during alpha value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick alpha value from color: {e}")
            alpha = 0
        finally: return alpha

    def getAlphaFloat(self, color: typing.Union[str, QColor]) -> typing.Union[float, None]:
        """
        SmartUtils
        ==========
        Fetch a color's alpha value as a float

        Parameters
        ----------
        color: string | QColor
            The color you want to get the alpha value from.

        Returns
        -------
        alpha: float | None
            The alpha float value
        """
        alpha = 0.0
        try:
            aColor = QColor(color)
            if aColor.isValid():
                r, g, b, alpha = aColor.getRgbF()
            else: alpha = 0.0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during alpha value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick alpha value from color: {e}")
            alpha = 0.0
        finally: return alpha

    def getSystemVersionBuild(self) -> int:
        """
        SmartUtils
        ==========
        Fetch the installed Windows version build

        Returns
        -------
        :int: Installed Windows version build number
        """
        if platform.system() == "Windows":
            return sys.getwindowsversion().build
        return 0
    
    def getSystemInformation(self) -> dict[str, typing.Any]:
        """
        SmartUtils
        ==========
        Fetch system hardware and software information provider

        Returns
        -------
        systemInfo: dictionary[string, Any]
            The system information dictionary
        """
        systemInfo = {}
        try:
            systemInfo = {
                "osName": platform.system(),
                "osVersion": platform.release(),
                "osBuildNumber": sys.getwindowsversion().build,
                "computerName": platform.node(),
                "osVersionInfo": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "coreCount": os.cpu_count()
            }
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to get system information: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to get system information: {e}")
        finally: return systemInfo
    
    def isSoftwareCompatible(self, minBuild: int) -> bool:
        """
        SmartUtils
        ==========
        Compatibility checker for specified minimum build number 

        Parameters
        ----------
        minBuild: integer
            The minimum build number for compatibility check
        
        Returns
        -------
        isCompatible: boolean
            Whether the system's build number is above/equivalent to the specified one
        """
        isCompatible = False
        try:
            if not platform.system() == "Windows":
                isCompatible = False
            else:
                isCompatible = sys.getwindowsversion().build >= minBuild 
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to check system compatibility: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to check system compatibility: {e}")
        finally: return isCompatible

    def getFileMimeType(self, path: str) -> str:
        """
        SmartUtils
        ==========
        Fetch a file's MIME type
        
        Parameters
        ----------
        path: string
            The file path to check

        Returns
        -------
        mimeType: string
            The MIME type of the file
        """
        magicMime = magic.from_file(path, True)
        if path: return magicMime
        return ""

    def isMarkdownExtension(self, path: str) -> bool:
        """
        SmartUtils
        ==========
        Check if a file's extension is Markdown-related
        
        Parameters
        ----------
        path: string
            The file path to check

        Returns
        -------
        isMarkdown: boolean
            Whether the file has a Markdown extension
        """
        isMarkdown = (
            path.endswith(".md") or path.endswith(".markdown") or
            path.endswith(".mdown") or path.endswith(".mdwn") or
            path.endswith(".mkdn") or path.endswith(".mkd") or
            path.endswith(".mdtxt") or path.endswith(".mdtext")
        )
        return isMarkdown


class SmartIcons:

    """
    SmartUtils
    ==========
    Class for SVG-based icons
    """

    def __init__(self):
        super().__init__()
        self.MARKDOWN = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -44 208 208">
            <rect width="198" height="118" x="5" y="5" ry="10" stroke="#000" stroke-width="10" fill="#FFF"/>
            <path fill="#000" d="M30 98V30h20l20 25 20-25h20v68H90V59L70 84 50 59v39zm125 0l-30-33h20V30h20v35h20z"/>
        </svg>
        """
        self.CSS = """
        <svg width="800px" height="800px" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g id="SVGRepo_bgCarrier" stroke-width="0"/>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"/>
            <g id="SVGRepo_iconCarrier"> <path d="M6 28L4 3H28L26 28L16 31L6 28Z" fill="#1172B8"/> <path d="M26 5H16V29.5L24 27L26 5Z" fill="#33AADD"/> <path d="M19.5 17.5H9.5L9 14L17 11.5H9L8.5 8.5H24L23.5 12L17 14.5H23L22 24L16 26L10 24L9.5 19H12.5L13 21.5L16 22.5L19 21.5L19.5 17.5Z" fill="white"/> </g>
        </svg>
        """
        self.HTML = """
        <svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" aria-label="HTML5" role="img" viewBox="0 0 512 512" fill="#000000">
            <g id="SVGRepo_bgCarrier" stroke-width="0"/>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"/>
            <g id="SVGRepo_iconCarrier">
                <path fill="#e34f26" d="M71 460L30 0h451l-41 460-185 52"/>
                <path fill="#ef652a" d="M256 472l149-41 35-394H256"/>
                <path fill="#ebebeb" d="M256 208h-75l-5-58h80V94H114l15 171h127zm-1 147l-63-17-4-45h-56l7 89 116 32z"/>
                <path fill="#ffffff" d="M255 208v57h70l-7 73-63 17v59l116-32 16-174zm0-114v56h137l5-56z"/>
            </g>
        </svg>
        """

    def renderIcon(self, svgData: str, size: int = 32) -> QIcon:
        """
        SmartUtils
        ==========
        SVG data to QIcon converter

        Parameters
        ----------
        svgData: string
            The SVG data you want to convert to a QIcon
        
        Returns
        -------
        :QIcon: The rendered QIcon (empty if the conversion failed)
        """
        # color = QColor("#FFFFFF") if not smart.isDarkModeEnabled() else QColor("#000000")
        try:
            renderer = QSvgRenderer(svgData.encode('utf-8'))
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            # painter.setPen(color)
            # painter.setBrush(color)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except: return QIcon()


class SmartColors(Enum):
    """
    SmartUtils
    ==========
    Class for SmartLinker's color palette
    """

    SMART_BLUE = QColor("#2196F3")
    SMART_PURPLE = QColor("#793BCC")
    SMART_RED = QColor("#F44336")
    SMART_YELLOW = QColor("#FCAF00")
    SMART_GREEN = QColor("#4CAF50")
    SMART_GRAY = QColor("#777777")
    CAPTION_LIGHT = QColor("#646464")
    CAPTION_DARK = QColor("#727272")


class ThemeController(QObject):
    themeChanged = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self._connect()
    
    def _connect(self):
        hints = QGuiApplication.styleHints()
        if hints: hints.colorSchemeChanged.connect(self._onSystemThemeChanged)
    
    def _onSystemThemeChanged(self):
        self.themeChanged.emit("Auto")


class BrowserScanWorker(QObject):
    """
    SmartUtils
    ==========
    SmartLinker's browser scanning processor
    """
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, requestURL: str):
        super().__init__()
        self.requestURL = requestURL
    
    def run(self):
        try:
            results = []
            myBrowsers = smart.loadBrowsers()
            if smart.isMarkdownExtension(self.requestURL) and smart.getFileMimeType(self.requestURL).startswith("text"):
                results.append({"type": "markdown", "name": "Smart DownMarker", "path": "", "status": "Embedded"})
            if myBrowsers["MyBrowsers"]:
                for browser in myBrowsers["MyBrowsers"]:
                    isRunning = smart.isBrowserOpen(browser["path"])
                    results.append({"type": "browser", "name": browser["name"], "path": browser["path"], "status": "Running" if isRunning else ""})
            if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                isRunning = smart.isBrowserOpen(cfg.get(cfg.mainBrowserPath))
                results.append({"type": "browser", "name": os.path.basename(cfg.get(cfg.mainBrowserPath)), "path": cfg.get(cfg.mainBrowserPath), "status": "Manual - Running" if isRunning else "Manual"})
            if cfg.get(cfg.showAddBrowserCard):
                results.append({"type": "add", "name": "Add a browser", "path": "", "status": ""})
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QObject):
    """
    SmartUtils
    ==========
    SmartLinker's file downloading processor
    """
    progress = pyqtSignal(int, int, str) # (bytes downloaded, total bytes, speed)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename
        self.isCancelled = False
        # Event used to implement pause/resume. When set -> not paused. When clear -> paused.
        self.pauseEvent = threading.Event()
        self.pauseEvent.set()

        # Expose a convenience flag for external checks (not strictly required)
        self.isPaused = False

    def run(self):
        """
        SmartUtils
        ==========
        Method to run the download
        """
        try:
            reponse = requests.get(self.url, stream=True, timeout=10)
            reponse.raise_for_status()

            totalSize = int(reponse.headers.get('content-length', 0))
            chunkSize = 1024  # 1 KB
            downloadedSize = 0
            
            startTime = time.time()

            with open(self.filename, 'wb') as f:
                for chunk in reponse.iter_content(chunk_size=chunkSize):
                    # Respect pause/resume state: if paused, wait for the event to be set
                    try: self.pauseEvent.wait()
                    except Exception: pass

                    # Check at each chunk if the user has cancelled the download
                    if self.isCancelled:
                        self.error.emit("The download process has been cancelled by the user...")
                        return

                    downloadedSize += len(chunk)
                    f.write(chunk)
                    
                    # Speed calculation
                    elapsedTime = time.time() - startTime
                    speed = downloadedSize / elapsedTime if elapsedTime > 0 else 0
                    speedStr = f"{speed / 1024 / 1024:.2f} MB/s" if speed > 1024*1024 else f"{speed / 1024:.2f} KB/s"
                    
                    # Send progress signal to the interface
                    if totalSize > 0: self.progress.emit(downloadedSize, totalSize, speedStr)
            
            # If we exit the loop without cancelling, it's a success
            self.finished.emit(f"The file '{os.path.basename(urlparse(self.url).path)}' has been successfully downloaded!")

        except requests.exceptions.RequestException as e:
            self.error.emit(f"Network error: {e}")
        except Exception as e:
            self.error.emit(f"An unexpected error has occured: {e}")

    def cancel(self):
        """
        SmartUtils
        ==========
        Method to request the cancellation of the download
        """
        # Mark cancelled and ensure we unblock any wait caused by pause
        self.isCancelled = True
        try: self.pauseEvent.set()
        except Exception: pass

    def pause(self):
        """
        SmartUtils
        ==========
        Method to request the pause of the download.

        :Note: the download must already be started for the pause to take effect
        (the thread is iterating over `response.iter_content`).
        """
        self.isPaused = True
        try: self.pauseEvent.clear()
        except Exception: pass

    def resume(self):
        """
        SmartUtils
        ==========
        Method to resume a previously paused download
        """
        self.isPaused = False
        try: self.pauseEvent.set()
        except Exception: pass


class DownloadDialog(MessageBoxBase):
    """
    SmartUtils
    ==========
    Dialog box for download purposes
    """

    def __init__(self, title: str, icon: QIcon | FICO | FluentFontIconBase, url: str, filename: str, parent = None):
        super().__init__(parent)
        self.titleBox = QHBoxLayout()
        self.titleLabel = SubtitleLabel(title, self)
        self.dialogIcon = IconWidget(icon)
        self.statusLabel = BodyLabel("Please wait while we are initializing the download...", self)
        self.progress = ProgressRing(self, True)
        self.detailsBox = QHBoxLayout()
        self.downloadSize = BodyLabel(self)
        self.downloadSpeed = BodyLabel(self)
        self.pauseButton = PushButton(self)
        self.url = url
        self.filename = filename

        self.dialogIcon.setFixedSize(24, 24)
        self.dialogIcon.setIcon(FICO.DOWNLOAD)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setContentsMargins(20, 0, 20, 0)
        self.progress.setValue(0)
        self.progress.setFixedSize(160, 160)
        self.progress.setStrokeWidth(12)
        self.pauseButton.setEnabled(False)
        self.pauseButton.setVisible(False)
        self.yesButton.setEnabled(False)
        self.yesButton.setVisible(False)

        self.pauseButton.clicked.connect(self.togglePause)
        self.cancelButton.clicked.connect(self.cancelDownload)

        self.viewLayout.addLayout(self.titleBox)
        self.titleBox.addWidget(self.dialogIcon)
        self.titleBox.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.statusLabel)
        self.viewLayout.addWidget(self.progress, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addLayout(self.detailsBox)
        self.detailsBox.addWidget(self.downloadSize)
        self.detailsBox.addStretch(1)
        self.detailsBox.addWidget(self.downloadSpeed)
        self.viewLayout.addWidget(self.pauseButton)

        tempPath = Path(smart.resourcePath(".temp"))
        if tempPath.exists() and tempPath.is_dir(): shutil.rmtree(tempPath)
        tempPath.mkdir(parents = True, exist_ok = True)
        self.startDownload(url, filename)

    def startDownload(self, url: str, filename: str):
        """
    SmartUtils
        ==========
        Method to start the download through the worker
        """
        self.downloadThread = QThread()
        self.worker = DownloadWorker(url, filename)

        self.worker.moveToThread(self.downloadThread)
        self.worker.progress.connect(self.updateProgress)
        self.worker.finished.connect(self.onFinished)
        self.worker.error.connect(self.onError)
        self.downloadThread.started.connect(self.worker.run)

        self.downloadThread.start()
        self.titleLabel.setText("Download in progress...")
        self.statusLabel.setText(f"The following file is currently being downloaded:\n{os.path.basename(urlparse(url).path)}")
        print(f'Starting download of "{os.path.basename(urlparse(url).path)}"...')
        smart.managerLog(f'Pending operation: Starting download of "{os.path.basename(urlparse(url).path)}"...')
        try:
            self.pauseButton.setEnabled(True)
            self.pauseButton.setVisible(True)
            self.pauseButton.setIcon(FICO.PAUSE)
            self.pauseButton.setText("Pause download")
        except Exception: pass
    
    def updateProgress(self, downloaded, total, speed):
        """
    SmartUtils
        ==========
        Method to update the download progress bar
        """
        with open(smart.resourcePath(".temp\\.metadata"), "wb") as metaWriter:
            pickle.dump(total, metaWriter)
        if total > 0:
            percentage = int((downloaded / total) * 100)
            self.progress.setValue(percentage)
            self.progress.setTextVisible(True)

            downloadedMB = downloaded / 1024 / 1024
            totalMB = total / 1024 / 1024
            self.downloadSize.setText(f"{downloadedMB:.2f} MB / {totalMB:.2f} MB")
        else:
            self.progress = IndeterminateProgressRing(self)
            self.downloadSize.setText(f"{downloaded / 1024 / 1024:.2f} MB")
        
        self.downloadSpeed.setText(speed)
    
    def onFinished(self, message):
        """
    SmartUtils
        ==========
        Operations to apply once the download is complete
        """
        self.titleLabel.setText("Download complete!")
        self.dialogIcon.setIcon(FICO.ACCEPT)
        self.statusLabel.setText(message)
        self.statusLabel.setTextColor(QColor("green"), QColor("#4CAF50"))
        self.progress.setVisible(False)
        if cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath): smart.playSound(soundStreamer, cfg.get(cfg.successSFXPath), "successful download")
        self.pauseButton.setEnabled(False)
        self.pauseButton.setVisible(False)
        self.yesButton.setEnabled(True)
        self.yesButton.setVisible(True)
        self.cancelButton.setEnabled(True)
        self.cancelButton.setVisible(True)
        self.yesButton.setText("Install")
        self.cancelButton.setText("OK")
        self.cancelButton.clicked.connect(lambda: self.closeAndCleanup())
        print(f'{Fore.GREEN}The file "{self.filename}" has been downloaded successfully!{Style.RESET_ALL}')

    def onError(self, message):
        """
    SmartUtils
        ==========
        Operations to apply when an error occurs during download
        """
        self.titleLabel.setText("Oops! Something went wrong...")
        self.dialogIcon.setIcon(FICO.CLOSE)
        self.statusLabel.setText("It looks like we are unable to connect to the Internet... Please check your network connection, then try again.")
        self.statusLabel.setTextColor(QColor("red"), QColor("#F44336"))
        self.progress.setVisible(False)
        if cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath): smart.playSound(soundStreamer, cfg.get(cfg.errorSFXPath), "download error")
        self.pauseButton.setEnabled(False)
        self.pauseButton.setVisible(False)
        self.yesButton.setEnabled(True)
        self.yesButton.setVisible(True)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setVisible(False)
        self.yesButton.clicked.connect(lambda: self.closeAndCleanup())
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")

    def cancelDownload(self):
        """
    SmartUtils
        ==========
        Method to cancel the download
        """
        self.titleLabel.setText("Cancelling download...")
        self.dialogIcon.setIcon(FICO.REMOVE_FROM)
        self.statusLabel.setText("Please wait for the download process to stop...")
        self.statusLabel.setTextColor(QColor("#FCAF00"), QColor("yellow"))
        self.cancelButton.setEnabled(False)
        try: self.pauseButton.setEnabled(False)
        except Exception: pass
        if self.worker: self.worker.cancel()

    def togglePause(self):
        """
    SmartUtils
        ==========
        Toggle between pause and resume (only works if the download has been started)
        """
        if not hasattr(self, 'worker') or self.worker is None: return

        if getattr(self.worker, 'isPaused', False):
            try:
                self.worker.resume()
                self.progress.resume() # type: ignore
                self.pauseButton.setIcon(FICO.PAUSE)
                self.pauseButton.setText("Pause download")
                self.titleLabel.setText("Download in progress...")
                self.dialogIcon.setIcon(FICO.DOWNLOAD)
            except Exception as e: print(f"Failed to resume download: {e}")
        else:
            try:
                self.worker.pause()
                self.progress.pause() # type: ignore
                self.pauseButton.setIcon(FICO.PLAY)
                self.pauseButton.setText("Resume download")
                self.titleLabel.setText("Download paused")
                self.dialogIcon.setIcon(FICO.PAUSE)
            except Exception as e: print(f"Failed to pause download: {e}")
    
    def closeEvent(self, event):
        """
    SmartUtils
        ==========
        Closing event listener
        """
        self.cancelDownload()
        event.accept()

    def closeAndCleanup(self):
        """
    SmartUtils
        ==========
        Operations to apply when the download dialog is closed
        """
        if self.downloadThread.isRunning():
            self.downloadThread.quit()
            self.downloadThread.wait()
        self.accept()


class UpdateSnack(QWidget):
    """
    SmartUtils
    ==========
    Class for the update snack
    """

    def __init__(self, objName: str, parent = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName(objName)
        self.setVisible(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners)))
        self.setEnabled(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners)))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.snackLayout = QHBoxLayout(self)
        self.snackLayout.setContentsMargins(20, 10, 20, 10)
        self.snackLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.snackIcon = IconWidget(segFont.fromName("GiftboxOpen"))
        self.snackIcon.setFixedSize(32, 32)
        self.snackLayout.setSpacing(20)
        self.snackLayout.addWidget(self.snackIcon)
        self.snackLabel = StrongBodyLabel("A new update is available for download!")
        self.snackLayout.addWidget(self.snackLabel)
        self.snackLayout.addStretch(1)
        self.snackButton = PrimaryPushButton(FICO.DOWNLOAD, "Download now")
        self.snackLayout.addWidget(self.snackButton)
        self.snackInstall = PrimaryPushButton(segFont.fromName("OpenIn"), "Install now")
        self.snackInstall.setToolTip("The latest update has been found in your system.\nYou can install it right away.")
        self.snackInstall.installEventFilter(ToolTipFilter(self.snackInstall))
        self.snackLayout.addWidget(self.snackInstall)


class LinkScraperThread(QThread):
    """
    SmartUtils
    ==========
    Link scraping thread
    """
    dataFetched = pyqtSignal(dict)
    errorOccurred = pyqtSignal(str)

    def __init__(self, url) -> None:
        super().__init__()
        self.url = url
    
    def run(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
        }

        try:
            # Fetching the webpage
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            def extractMeta(propertyName, nameFallback=None):
                tag = soup.find("meta", property=propertyName)
                if not tag and nameFallback:
                    tag = soup.find("meta", attrs={"name": nameFallback})
                return tag["content"] if tag and tag.get("content") else ""
            
            title = extractMeta("og:title") or (soup.title.string if soup.title else "Title not found")
            description = extractMeta("og:description", "description") or "No description"
            imageUrl = extractMeta("og:image")

            # Downloading the image (in bare bytes)
            imgBytes = None
            if imageUrl:
                try:
                    imgResponse = requests.get(imageUrl, timeout=10) # type: ignore
                    imgResponse.raise_for_status()
                    imgBytes = imgResponse.content
                except Exception: pass

            # Sending data through the signal
            self.dataFetched.emit({
                "title": title.strip(), # type: ignore
                "description": description.strip(), # type: ignore
                "url": self.url,
                "imgBytes": imgBytes
            })

        except Exception as e:
            self.errorOccurred.emit(f"Failed loading: {str(e)}")


class MigrationDialog(MessageBoxBase):
    """
    SmartUtils
    ==========
    Migration dialog
    """

    def __init__(self, parent = None):
        super().__init__(parent)
        baseLayout = QHBoxLayout()
        iconLayout = QVBoxLayout()
        textLayout = QVBoxLayout()
        self.iconLabel = IconWidget(self)
        self.progress = IndeterminateProgressRing(self)
        self.titleLabel = TitleLabel(self)
        self.descriptionLabel = BodyLabel(self)
        self.proceedButton = PrimaryPushButton("Proceed", self)
        self.isSuccess: bool = False

        baseLayout.setContentsMargins(30, 30, 30, 30)
        baseLayout.setSpacing(30)
        baseLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        iconLayout.setContentsMargins(0, 0, 0, 0)
        iconLayout.setSpacing(0)
        iconLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(10)
        textLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.iconLabel.setFixedSize(96, 96)
        self.iconLabel.setIcon(segFont.fromName("Warning").colored(QColor("#FCAF00"), QColor("yellow")))
        self.progress.setFixedSize(96, 96)
        self.progress.setVisible(False)
        self.titleLabel.setText("Migration Notice")
        self.descriptionLabel.setText(
            'Since the 3.0.0 "Great Leap" update, some major changes have been made to the structure '
           f'and configuration of {SmartLinkerName}. This is a one-time migration process to ensure that '
            'your current configuration is compatible with the new version.\n'
            'Do not worry, your previous settings will be preserved and there is no risk of data loss.\n\n'
            'Click the "Proceed" button below to start the migration process.'
        )
        self.descriptionLabel.setWordWrap(True)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(baseLayout)
        baseLayout.addLayout(iconLayout)
        iconLayout.addWidget(self.iconLabel)
        iconLayout.addWidget(self.progress)
        baseLayout.addLayout(textLayout)
        textLayout.addWidget(self.titleLabel)
        textLayout.addWidget(self.descriptionLabel)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.proceedButton, 1)

        self.yesButton.setText("Migrating...")
        self.yesButton.setEnabled(False)
        self.yesButton.setVisible(False)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setVisible(False)

        self.proceedButton.clicked.connect(self.migrate)
        self.proceedButton.contextMenuEvent = lambda a0: smart.stopApp()
    
    def migrate(self):
        """
        SmartUtils
        ==========
        Migrate the old configuration to the new one
        """
        data = {}
        newDict: dict[str, dict[str, typing.Any]] = {}

        self.proceedButton.setEnabled(False)
        self.proceedButton.setVisible(False)
        self.yesButton.setVisible(True)
        self.buttonLayout.removeWidget(self.yesButton)
        # self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.yesButton, 1)

        if not os.path.exists(ROOT_PATH / "_internal" / "bin"):
            return
        
        try:
            RichCLI.log("[blue][b u]OPERATION[/b u]: Migrating the old configuration to the new one...")
            self.titleLabel.setText("Please wait...")
            self.descriptionLabel.setText(
               f"Your current {SmartLinkerName} configuration is being converted to the latest model..."
            )
            self.iconLabel.setVisible(False)
            self.progress.setVisible(True)
            
            if not os.path.exists(ROOT_PATH / "bin"):
                shutil.move(ROOT_PATH / "_internal" / "bin", ROOT_PATH)
            else:
                binItems = Path(ROOT_PATH / "_internal" / "bin").iterdir()
                for item in binItems:
                    shutil.move(item, ROOT_PATH / "bin" / item.name)
            shutil.rmtree(ROOT_PATH / "_internal")

            with open(ROOT_PATH / "bin" / "config.json", 'r') as readConfig:
                data = json.load(readConfig)
            
            if (
                not "Markdown-General" in data
                or ("Markdown-General" in data and not isinstance(data.get("Markdown-General"), dict))
            ):
                newDict = { "Markdown-General": { "StartInEditMode": False } }
                data.update(newDict)
            
            if (
                not "Markdown-Editor" in data
                or ("Markdown-Editor" in data and not isinstance(data.get("Markdown-Editor"), dict))
            ):
                newDict = {
                    "Markdown-Editor": {
                        "FontFamily": "",
                        "FontSize": 12,
                        "FontWeight": 400,
                        "DisplayLineNumbers": True,
                        "DisplaySymbolsBar": True,
                        "DisplayStatusBar": True,
                        "EnableWordWrap": False,
                        "IndentationWidth": 4,
                        "DisplayIndentationGuides": True,
                        "EnableAutoIndent": True,
                        "HighlightCurrentLine": True,
                        "SelectionColorModeMode": "Accent",
                        "SelectionCustomColor": "#7f793bcc",
                        "EnableSyntaxHighlighting": True
                    }
                }
                data.update(newDict)
            
            if (
                not "Markdown-Viewer" in data
                or ("Markdown-Viewer" in data and not isinstance(data.get("Markdown-Viewer"), dict))
            ):
                newDict = {
                    "Markdown-Viewer": {
                        "OpenExternalLinks": False,
                        "CSSSource": "Default",
                        "CSSSourcePath": "Default",
                        "CSSProperties": "",
                        "HomepageSource": "Default",
                        "HomepageSourcePath": "Default",
                        "HomepageProperties": "",
                        "DragEnterJSFunction": "",
                        "DragLeaveJSFunction": "",
                        "DropJSFunction": ""
                    }
                }
                data.update(newDict)
            
            with open(ROOT_PATH / "bin" / "config.json", 'w') as writeConfig:
                json.dump(data, writeConfig, indent=4, ensure_ascii=False, sort_keys=True)

            RichCLI.log("[green][b u]SUCCESS[/b u]: The migration has been completed successfully!")
            self.isSuccess = True

        except Exception as e:
            RichCLI.log(f"[red][b u]ERROR[/b u]: Failed to migrate configuration: [i]{e}[/]")
            self.isSuccess = False

        finally:
            self.iconLabel.setIcon(
                segSVG.CHECK_CIRCLE.colored(QColor("green"), QColor("#4CAF50")) if self.isSuccess
                else segSVG.ERROR_CIRCLE.colored(QColor("red"), QColor("#F44336"))
            )
            self.iconLabel.setVisible(True)
            self.progress.setVisible(False)
            title = "Migration complete!" if self.isSuccess else "Migration failed..."
            description = (
                f"{SmartLinkerName} is now fully migrated to the latest, compatible version. "
                f"You can now close this window and continue using {SmartLinkerName}."
            ) if self.isSuccess else "An error occured while attempting to migrate your current configuration to the new one..."
            self.titleLabel.setText(title)
            self.descriptionLabel.setText(description)
            self.yesButton.setText(f"Continue with {SmartLinkerName}" if self.isSuccess else "Close")
            self.yesButton.setEnabled(True)
    
    def validate(self) -> bool:
        return (
            os.path.exists(ROOT_PATH / "bin") and not os.path.exists(ROOT_PATH / "_internal")
        ) if self.isSuccess else True


class ErrorDialog(MessageBoxBase):
    """
    SmartUtils
    ==========
    Error dialog
    """

    def __init__(self, traceback: typing.Any, parent=None):
        super().__init__(parent)
        self.icon = IconWidget(segSVG.ERROR_CIRCLE.colored(QColor("#F44336"), QColor("red")), self)
        self.title = TitleLabel("Oops! Something went wrong...", self)
        self.description = BodyLabel(
            f"It seems like an unexpected error occured while using {SmartLinkerName}, and " 
            "we sincerely apologize for the inconvenience. Just in case, we provide you with "
            "the complete error message, so you can send us its content via GitHub Issues or email, "
            "and we will work thoroughly in order to definitely solve the issue.",
            self
        )
        self.errorTextBox = TextEdit(self)
        self.sendDropdown = PrimaryDropDownPushButton("Send error", self)
        self.copyButton = PushButton("Copy error", self)
        self.sendMenu = RoundMenu("Send error", self)
        self.confirmOption: int = 0 # 0 - GitHub Issues; 1 - Email

        self.icon.setFixedSize(96, 96)
        self.title.setTextColor(QColor("#F44336"), QColor("red"))
        self.description.setWordWrap(True)

        self.errorTextBox.setReadOnly(True)
        self.errorTextBox.setFontFamily("Cascadia Code" or "Consolas")
        self.errorTextBox.setAcceptRichText(False)
        self.errorTextBox.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
        self.errorTextBox.setText(traceback)

        self.sendMenu.addActions([
            Action(FICO.GITHUB, "Submit to GitHub Issues"),
            Action(FICO.MAIL, "Send as an email")
        ])
        self.sendDropdown.setMenu(self.sendMenu)

        self.widget.setMinimumWidth(550)

        self.viewLayout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.title, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.description)
        self.viewLayout.addWidget(self.errorTextBox)

        self.yesButton.setParent(None)
        self.buttonLayout.removeWidget(self.yesButton)
        self.buttonLayout.removeWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.sendDropdown, 1, Qt.AlignmentFlag.AlignVCenter)
        self.buttonLayout.addWidget(self.copyButton, 1, Qt.AlignmentFlag.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignmentFlag.AlignVCenter)

        self.copyButton.clicked.connect(lambda checked: (
            smart.copyToClipboard(self.errorTextBox.toPlainText()),
            smart.infoNotify("", "The stack trace has been copied to your clipboard.", InfoBar.desktopView())
        ))

# ======================================================

cfg = Config()
smart = SmartLogic()
smIco = SmartIcons()
segFont = SegoeFontIcon
segSVG = SegoeSVGIcon
smartCol = SmartColors
cfgFilePath = Path(ROOT_PATH / "bin" / "config.json")
browsersCfgFilePath = Path(ROOT_PATH / "bin" / "browsers_config.dat")
historyFilePath = Path(ROOT_PATH / "bin" / "history.dat")
qconfig.load(cfgFilePath, cfg)

""" if __name__ == "__main__":
    smart.clearCLI()
    RichCLI.print(smart.consoleScript())
    # 3 "parent" for .exe, 2 "parent" for .py 
     
    # À quoi sert __init__.py ? """
