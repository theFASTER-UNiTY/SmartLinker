"""
SmartUtils
==========
A complete utility module made specifically for SmartLinker global needs.

:Copyright: © 2025-2026 by #theF∆STER™ UN!TY.
"""
__version__ = "v3.0.0 Alpha #2"
__author__ = "#theF∆STER™ CODE&BU!LD"

# NOTE: CODE&BU!LD is actually the software development section of the UN!TY group.
# (In case you would be wondering...)
# =========================================================

from bs4 import BeautifulSoup
import argparse, ctypes, darkdetect, datetime, json, magic, markdown, os, pathlib, pickle, platform, psutil, pygame, re, requests, shutil
import socket, subprocess, sys, time, typing, threading, webbrowser, win32api, winreg
from colorama import init, Fore, Back, Style
from enum import Enum
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from packaging.version import Version
from pathlib import Path
from PyQt6.Qsci import QsciScintilla, QsciLexerMarkdown
from PyQt6.QtCore import (
    QCoreApplication, QEvent, QEventLoop, QFileInfo, QModelIndex, QObject, QRegularExpression, QSize, Qt, QThread, QTimer, QUrl, pyqtSignal
)
from PyQt6.QtGui import (
    QColor, QContextMenuEvent, QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QFont, QFontDatabase, QFontMetrics, QGuiApplication,
    QIcon, QKeyEvent, QPainter, QPixmap, QResizeEvent, QStandardItem, QStandardItemModel, QSyntaxHighlighter, QTextCharFormat, QTextCursor
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWebEngineCore import QWebEngineHistoryItem, QWebEngineNavigationRequest, QWebEngineSettings
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QCompleter, QFileDialog, QFileIconProvider, QHBoxLayout, QLayout, QScrollBar, QSizePolicy, QStatusBar,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
)
from qfluentwidgets import (
    getIconColor, qconfig, setFont, setTheme, setThemeColor, theme, themeColor, Action, BodyLabel, BoolValidator, CaptionLabel, CardWidget,
    ColorConfigItem, ColorDialog, ComboBox, CommandBar, ConfigItem,DropDownPushButton, ElevatedCardWidget, ExpandGroupSettingCard,
    FluentFontIconBase, FluentIcon as FICO, FluentIconBase, FluentWindow, HyperlinkButton, HyperlinkCard, IconInfoBadge, IconWidget, ImageLabel,
    IndeterminateProgressRing, IndicatorPosition, InfoBadgePosition, InfoBar, InfoBarPosition, LargeTitleLabel, LineEdit, ListWidget, MessageBox,
    MessageBoxBase, NavigationItemPosition, OptionsConfigItem, OptionsSettingCard, OptionsValidator, PrimaryPushButton, PrimaryPushSettingCard,
    ProgressBar, ProgressRing, PushButton, PushSettingCard, QConfig, RangeConfigItem, RangeValidator, RoundMenu, ScrollBar, SearchLineEdit,
    SimpleCardWidget, SimpleExpandGroupSettingCard, SingleDirectionScrollArea, SpinBox, SplashScreen, StateToolTip, StrongBodyLabel, SubtitleLabel,
    SwitchButton, SwitchSettingCard, TableWidget, TextEdit, Theme, TitleLabel, ToolButton, ToolTipFilter, ToolTipPosition, TransparentDropDownPushButton,
    TransparentToggleToolButton, TransparentToolButton
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

SmartLinkerID: str = "theFASTER.SmartLinker"
SmartLinkerName: str = "SmartLinker"
SmartLinkerVersion: str = __version__
SmartLinkerAuthor: str = __author__
SmartLinkerOwner: str = "#theF∆STER™ UN!TY"
SmartLinkerGitRepoURL: str = "https://github.com/theFASTER-UNiTY/SmartLinker"
SmartLinkerGitRepoAPI: str = "https://api.github.com/repos/theFASTER-UNiTY/SmartLinker"
SmartRichTheme = RTheme({"smartpurple": "#793bcc", "smartblue": "#2196f3"})
RichCLI = Console(theme=SmartRichTheme)
install()
PURPLE = "\x1b[35m" # soon deprecated
init() # soon deprecated
pygame.init()
pygame.mixer.init()
soundStreamer = None

class Config(QConfig):
    """ SmartUtils
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
    
    qAccentColor = ColorConfigItem("QFluentWidgets", "ThemeColor", "#ff25d9e6") #ff25d9e6

class MarkdownConfig(QConfig):
    """ SmartUtils
    ==========
    Markdown viewer configuration handling class
    """
    startInEditMode = ConfigItem("General", "StartInEditMode", False, BoolValidator())
    
    fontFamily = ConfigItem("Editor", "FontFamily", "")
    fontSize = ConfigItem("Editor", "FontSize", 12)
    fontWeight = RangeConfigItem("Editor", "FontWeight", 400, RangeValidator(100, 800))
    displayLineNumbers = ConfigItem("Editor", "DisplayLineNumbers", True, BoolValidator())
    displaySymbolsBar = ConfigItem("Editor", "DisplaySymbolsBar", True, BoolValidator())
    displayStatusBar = ConfigItem("Editor", "DisplayStatusBar", True, BoolValidator())
    enableWordWrap = ConfigItem("Editor", "EnableWordWrap", False, BoolValidator())
    indentWidth = RangeConfigItem("Editor", "IndentationWidth", 4, RangeValidator(2, 8))
    displayIndentGuides = ConfigItem("Editor", "DisplayIndentationGuides", True, BoolValidator())
    enableAutoIndent = ConfigItem("Editor", "EnableAutoIndent", True, BoolValidator())
    highlightCurrentLine = ConfigItem("Editor", "HighlightCurrentLine", True, BoolValidator())
    selectionColorMode = OptionsConfigItem("Editor", "SelectionColorMode", "Accent", OptionsValidator(["Accent", "Custom"]))
    selectionCustomColor = ColorConfigItem("Editor", "SelectionCustomColor", "#7f793bcc") #ff793bcc
    enableSyntaxHighlighting = ConfigItem("Editor", "EnableSyntaxHighlighting", True, BoolValidator())
    # to-do: syntax colors
    
    openExternalLinks = ConfigItem("Viewer", "OpenExternalLinks", False, BoolValidator())
    cssSource = OptionsConfigItem("Viewer", "CSSSource", "Default", OptionsValidator(["Default", "Local", "Custom"]))
    cssSourcePath = ConfigItem("Viewer", "CSSSourcePath", "Default")
    cssProperties = ConfigItem("Viewer", "CSSProperties", "")
    homepageSource = OptionsConfigItem("Viewer", "HomepageSource", "Default", OptionsValidator(["Default", "Local", "Custom"]))
    homepageSourcePath = ConfigItem("Viewer", "HomepageSourcePath", "Default")
    homepageProperties = ConfigItem("Viewer", "HomepageProperties", "")
    
    qThemeColor = ColorConfigItem("QFluentWidgets", "ThemeColor", "")

class SegoeFontIcon(FluentFontIconBase):
    """ SmartUtils
    ==========
    Class for SmartLinker's custom font-based icons
    """

    def path(self, theme=Theme.AUTO):
        return smart.resourcePath("resources/fonts/SegoeIcons.ttf")

    def iconNameMapPath(self):
        """ Override this method if you want to use `fromName` to create icons """
        return smart.resourcePath("resources/fonts/SegoeIconsMap.json")

class SegoeSVGIcon(FluentIconBase, Enum):
    """ SmartUtils
    ==========
    Class for custom SVG-based Segoe Fluent icons
    """

    COLOR_LINE = "ColorLine"
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

class SmartLogic:
    """ SmartUtils
    ==========
    General class for SmartLinker functions
    """
    def __init__(self):
        super().__init__()

    def resourcePath(self, relativePath: str) -> str:
        """ SmartUtils
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

    def loadBrowsersJSON(self):
        """ SmartUtils
        ==========
        Loader of all the saved browsers
        """
        try:
            with open(browsersCfgFilePath, "r") as browserReader:
                return json.load(browserReader)
        except: return {
                "MyBrowsers": []
            }
        
    def loadBrowsers(self):
        """ SmartUtils
        ==========
        Loader of all the saved browsers
        """
        try:
            with open(browsersCfgFilePath, "rb") as browserReader:
                return pickle.load(browserReader)
        except:
            return {
                "MyBrowsers": []
            }

    def writeBrowsersJSON(self, browsers: dict[str, list[str]]):
        """ SmartUtils
        ==========
        Saver of all the changes made to browsers list
        
        Parameters
        ----------
        browsers: dictionary[string | list of strings]
            The browsers list you want to save to the browsers config file
        """
        with open(browsersCfgFilePath, "w") as browserWriter:
            json.dump(browsers, browserWriter, indent=4)

    def writeBrowsers(self, browsers: dict[str, list[str]]):
        """ SmartUtils
        ==========
        Saver of all the changes made to browsers list
        
        Parameters
        ----------
        browsers: dictionary[string | list of strings]
            The browsers list you want to save to the browsers config file
        """
        try:
            with open(browsersCfgFilePath, "wb") as browserWriter:
                pickle.dump(browsers, browserWriter)
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to save browser-related changes: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to save browser-related changes: {e}")

    def restartApp(self):
        """ SmartUtils
        ==========
        Global function to restart the app (script purpose)
        """
        os.execl(sys.executable, sys.executable, *sys.argv)

    def stopApp(self):
        """ SmartUtils
        ==========
        Global function to stop the app process
        """
        sys.exit()

    def restartAppPlus(self):
        """ SmartUtils
        ==========
        Global function to restart the app (executable purpose)
        """
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

    def centerWindow(self, window):
        """ SmartUtils
        ==========
        Center the window

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
        """ SmartUtils
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
        """ SmartUtils
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

    def checkConnectivity(self, hostname = "8.8.8.8", port = 53, timeout = 5.0):
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
        ==========
        DarkDetect library-based checker for system dark mode

        Returns
        -------
        :boolean: whether the system is in dark mode
        """
        return bool(darkdetect.isDark())

    def successNotify(self, title: str, content: str = "", parent = None):
        """ SmartUtils
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
        """ SmartUtils
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

    def errorNotify(self, title: str, content: str = "", parent = None, canCopy: bool = True):
        """ SmartUtils
        ==========
        Error notification bar
        
        Parameters
        ----------
        title: string
            The title of the error notification bar
        content: string
            The message you want the error notification bar to display (optional)
        parent
            The parent widget
        canCopy: boolean
            Whether the error can be copied to the clipboard
        """
        copyBtn = PushButton(FICO.COPY, "Copy error")
        copyBtn.clicked.connect(lambda: self.copyToClipboard(content))

        bar = InfoBar.error(
            title = title,
            content = content,
            orient = Qt.Orientation.Vertical,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = -1,
            parent = parent
        )
        if canCopy: bar.addWidget(copyBtn)
        bar.show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.errorSFXPath), "error notification")

    def infoNotify(self, title: str, content: str = "", parent = None): 
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
        ==========
        Specified type file provider through file picker dialog

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
        """ SmartUtils
        ==========
        Specified type file saver through file picker dialog

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
        """ SmartUtils
        ==========
        Copy the forwarded link to the system's clipboard

        Parameters
        ----------
        text: string
            The link you want to copy
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
        """ SmartUtils
        ==========
        SmartLinker-as-default-browser checker
        
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
        """ SmartUtils
        ==========
        Specified SmartList browser process checker
        
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
        """ SmartUtils
        ==========
        Specified software running process checker
        
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

    def consoleScript(self) -> str:
        """ SmartUtils
        ==========
        SmartLinker name in-console renderer

        Returns
        -------
        :string: The rendered SmartLinker name
        """
        return f"[smartpurple]============================[/] {SmartLinkerAuthor} presents [smartblue]============================\n\n" \
            "[smartpurple]███████╗███╗   ███╗ █████╗ ██████╗ ████████╗[smartblue]██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗ \n" \
            "[smartpurple]██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝[smartblue]██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗\n" \
            "[smartpurple]███████╗██╔████╔██║███████║██████╔╝   ██║   [smartblue]██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██████╔╝\n" \
            "[smartpurple]╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   [smartblue]██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██╔══██╗\n" \
            "[smartpurple]███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   [smartblue]███████╗██║██║ ╚████║██║  ██╗███████╗██║  ██║\n" \
            "[smartpurple]╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   [smartblue]╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝\n\n" \
           f"[smartpurple]=================================[/] {"Mastering URL Handling"} [smartblue]================================[/]\n"

    def managerLog(self, message):
        """ SmartUtils
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

    def selectorLog(self, message):
        """ SmartUtils
        ==========
        Smart Selector activity log writer

        Parameters
        ----------
        message: Any
            The message you want to write in the log
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f"{Path(__file__).parent.parent}\\SmartSelectorReport.log", 'a', encoding="utf-8") as logger:
                logger.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to log the last event in the Selector log file: {e}{Style.RESET_ALL}")
            return

    def emptyManagerLog(self):
        """ SmartUtils
        ==========
        SmartLinker activity log initializing tool
        """
        try:
            with open("SmartLinkerReport.log", 'w') as clear:
                clear.write("SmartLinker - Smart Manager Activity Report\n" \
                            "-------------------------------------------\n\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to initialize the log file: {e}{Style.RESET_ALL}")
            return

    def emptySelectorLog(self):
        """ SmartUtils
        ==========
        Smart Selector activity log initializing tool
        """
        try:
            with open(f"{Path(__file__).parent.parent}\\SmartSelectorReport.log", 'w') as clear:
                clear.write("SmartLinker - Smart Selector Activity Report\n" \
                            "--------------------------------------------\n\n")
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to initialize the Selector log file: {e}{Style.RESET_ALL}")
            return

    def hideLayoutWidgets(self, layout):
        """ SmartUtils
        ==========
        Layout child widgets hiding tool

        Parameters
        ----------
        layout: unknown
            The layout whose child widgets you want to hide
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().hide()
            elif item.layout():
                self.hideLayoutWidgets(item.layout())

    def showLayoutWidgets(self, layout):
        """ SmartUtils
        ==========
        Layout child widgets showing tool

        Parameters
        ----------
        layout: unknown
            The layout whose child widgets you want to show
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().show()
            elif item.layout():
                self.showLayoutWidgets(item.layout())

    def emptyLayout(self, layout: QLayout, childLayout: bool = False):
        """
        SmartUtils
        ==========
        Layout clearing (child widget removing) tool

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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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

    def covertToNoAlphaHEX(self, color: str | QColor) -> str:
        """ SmartUtils
        ==========
        HEX w/ alpha (#AARRGGBB) to HEX w/o alpha (#RRGGBB) color format converter

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

    def convertToRGBA(self, color: str | QColor) -> str:
        """ SmartUtils
        ==========
        RGBA color format converter

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

    def convertToRGB(self, color: str | QColor) -> str:
        """ SmartUtils
        ==========
        RGB color format converter

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

    def customAlphaToRGB(self, color: str | QColor, alpha) -> QColor:
        """ SmartUtils
        ==========
        Custom alpha value to color applying tool

        Parameters
        ----------
        color: Unknown
            The color you want to modify.
        alpha: number
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

    def getRed(self, color):
        """ SmartUtils
        ==========
        A color's red value picker

        Parameters
        ----------
        color: Unknown
            The color you want to get the red value from.

        Returns
        -------
        red: int | None
            The red value
        """
        try:
            rColor = QColor(color)
            if rColor.isValid():
                red, g, b, a = rColor.getRgb()
            else: red = 0
        except Exception as e:
            print(f"{Fore.RED}Something went wrong during red value pick: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to pick red value from color: {e}")
            red = 0
        finally: return red

    def getGreen(self, color):
        """ SmartUtils
        ==========
        A color's green value picker

        Parameters
        ----------
        color: Unknown
            The color you want to get the green value from.

        Returns
        -------
        green: int | None
            The green value
        """
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

    def getBlue(self, color):
        """ SmartUtils
        ==========
        A color's blue value picker

        Parameters
        ----------
        color: Unknown
            The color you want to get the blue value from.

        Returns
        -------
        blue: int | None
            The blue value
        """
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

    def getAlpha(self, color):
        """ SmartUtils
        ==========
        A color's alpha value picker

        Parameters
        ----------
        color: Unknown
            The color you want to get the alpha value from.

        Returns
        -------
        alpha: int | None
            The alpha value
        """
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

    def getAlphaFloat(self, color):
        """ SmartUtils
        ==========
        A color's alpha value picker

        Parameters
        ----------
        color: Unknown
            The color you want to get the alpha value from.

        Returns
        -------
        alpha: float | None
            The alpha float value
        """
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
        """ SmartUtils
        ==========
        Installed Windows version build indicator

        Returns
        -------
        :int: Installed Windows version build number
        """
        if platform.system() == "Windows": return sys.getwindowsversion().build
        return 0
    
    def getSystemInformation(self):
        """ SmartUtils
        ==========
        System hardware and software information provider

        Returns
        -------
        systemInfo: dictionary[string, Unknown]
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
        """ SmartUtils
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
            if not platform.system() == "Windows": isCompatible = False
            else: isCompatible = sys.getwindowsversion().build >= minBuild 
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to check system compatibility: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to check system compatibility: {e}")
        finally: return isCompatible

    def getFileMimeType(self, path: str) -> str:
        """ SmartUtils
        ==========
        File MIME type provider
        
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
        """ SmartUtils
        ==========
        Markdown file extension checker
        
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
    """ SmartUtils
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
        """ SmartUtils
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
    """ SmartUtils
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
    """ SmartUtils
    ==========
    SmartLinker's file downloading processor
    """
    # Definition of signals that the worker can send to the interface
    progress = pyqtSignal(int, int, str) # (bytes downloaded, total bytes, speed)
    finished = pyqtSignal(str)           # (success message)
    error = pyqtSignal(str)              # (error message)

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
        """ SmartUtils
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
        """ SmartUtils
        ==========
        Method to request the cancellation of the download
        """
        # Mark cancelled and ensure we unblock any wait caused by pause
        self.isCancelled = True
        try: self.pauseEvent.set()
        except Exception: pass

    def pause(self):
        """ SmartUtils
        ==========
        Method to request the pause of the download.

        :Note: the download must already be started for the pause to take effect
        (the thread is iterating over `response.iter_content`).
        """
        self.isPaused = True
        try: self.pauseEvent.clear()
        except Exception: pass

    def resume(self):
        """ SmartUtils
        ==========
        Method to resume a previously paused download
        """
        self.isPaused = False
        try: self.pauseEvent.set()
        except Exception: pass

class DownloadDialog(MessageBoxBase):
    """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
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
        """ SmartUtils
        ==========
        Closing event listener
        """
        self.cancelDownload()
        event.accept()

    def closeAndCleanup(self):
        """ SmartUtils
        ==========
        Operations to apply when the download dialog is closed
        """
        if self.downloadThread.isRunning():
            self.downloadThread.quit()
            self.downloadThread.wait()
        self.accept()

class UpdateSnack(QWidget):
    """ SmartUtils
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

# Elidable labels ======================================

class ElidableTitleLabel(TitleLabel):
    def __init__(self, text: str, parent = None):
        super().__init__(text, parent)
        self.initText = text
        super().setToolTip(text)
    
    def resizeEvent(self, event):
        metrics = QFontMetrics(self.font())
        self.setText(
            metrics.elidedText(
                self.text(),
                Qt.TextElideMode.ElideRight,
                self.width()
            )
        )
        super().resizeEvent(event)
    
    def setToolTip(self, text: str | None) -> None:
        if text is None: text = self.initText
        super().setToolTip(text)

    def installEventFilter(self, obj: QObject | None) -> None:
        super().installEventFilter(ToolTipFilter(self))

class ElidableSubtitleLabel(SubtitleLabel):
    def __init__(self, text: str, parent = None):
        super().__init__(text)
        self.initText = text
        super().setToolTip(text)
    
    def setToolTip(self, text: str | None) -> None:
        if text is None: text = self.initText
        super().setToolTip(text)

    def installEventFilter(self, obj: QObject | None) -> None:
        super().installEventFilter(ToolTipFilter(self))

    def setText(self, text: str) -> None:
        super().setText(text)
        self.initText = text
        self.setToolTip(text)
        self.installEventFilter(ToolTipFilter(self))
        print(self.initText)
    
    def resizeEvent(self, event):
        metrics = QFontMetrics(self.font())
        self.setText(
            metrics.elidedText(
                self.text(),
                Qt.TextElideMode.ElideMiddle,
                self.width()
            )
        )
        super().resizeEvent(event)

class ElidableBodyLabel(BodyLabel):
    def resizeEvent(self, event):
        metrics = QFontMetrics(self.font())
        self.setText(
            metrics.elidedText(
                self.text(),
                Qt.TextElideMode.ElideRight,
                self.width()
            )
        )
        super().resizeEvent(event)

class ElidableCaptionLabel(CaptionLabel):
    def resizeEvent(self, event):
        metrics = QFontMetrics(self.font())
        self.setText(
            metrics.elidedText(
                self.text(),
                Qt.TextElideMode.ElideRight,
                self.width()
            )
        )
        super().resizeEvent(event)

# ======================================================

cfg = Config()
markCfg = MarkdownConfig()
smart = SmartLogic()
smIco = SmartIcons()
segFont = SegoeFontIcon
segSVG = SegoeSVGIcon
cfgFilePath = smart.resourcePath("bin\\config.json")
markCfgFilePath = smart.resourcePath("bin\\markdown_config.json")
browsersCfgFilePath = smart.resourcePath("bin\\browsers_config.dat")
qconfig.load(cfgFilePath, cfg)
qconfig.load(markCfgFilePath, markCfg)
