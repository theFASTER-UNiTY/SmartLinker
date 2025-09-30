"""
SmartUtils
==========
A complete utility module made specifically for SmartLinker basic and technical needs.

:Copyright: © 2025 by #theF∆STER™ UN!TY.
"""
__version__ = "v1.0.0"
__author__ = "#theF∆STER™ CODE&BU!LD"

# NOTE: CODE&BU!LD is actually the software development section of the UN!TY group.
# (In case you would be wondering...)
# =========================================================

from tkinter import E
import darkdetect, datetime, json, os, pickle, platform, psutil, pygame, requests, socket, subprocess, sys, typing, webbrowser
import win32api, winreg
from PyQt6.QtCore import QEventLoop, QFileInfo, Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QFileDialog, QFileIconProvider, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QWidget
)
from qfluentwidgets import (
    Action, BodyLabel, BoolValidator, CaptionLabel, CardWidget, ColorConfigItem, ColorDialog, ComboBox, CommandBar, ConfigItem,
    ElevatedCardWidget, ExpandGroupSettingCard, FluentIcon as FICO, FluentWindow, HyperlinkCard, IconInfoBadge, IconWidget,
    IndicatorPosition, InfoBadgePosition, InfoBar, InfoBarPosition, LineEdit, MessageBox, MessageBoxBase, NavigationItemPosition,
    OptionsConfigItem, OptionsSettingCard, OptionsValidator, PrimaryPushButton, PrimaryPushSettingCard, PushButton, PushSettingCard,
    QConfig, qconfig, RangeConfigItem, RangeValidator, setTheme, setThemeColor, SimpleExpandGroupSettingCard,
    SingleDirectionScrollArea, SpinBox, SplashScreen, StrongBodyLabel, SubtitleLabel, SwitchButton, SwitchSettingCard, TableWidget,
    Theme, theme, themeColor, TitleLabel, ToolButton, ToolTipFilter, ToolTipPosition
)
from qframelesswindow import FramelessWindow, TitleBar
from qframelesswindow.utils import getSystemAccentColor
from colorama import init, Fore, Back, Style
from shiboken6 import isValid
from packaging.version import Version

# =========================================================

SmartLinkerID: str = "theFASTER.SmartLinker"
SmartLinkerName: str = "SmartLinker"
SmartLinkerVersion: str = __version__
SmartLinkerAuthor: str = __author__
SmartLinkerOwner: str = "#theF∆STER™ UN!TY"
SmartLinkerGitRepoURL: str = "https://github.com/theFASTER-UNiTY/SmartLinker"
SmartLinkerGitRepoAPI: str = "https://api.github.com/repos/theFASTER-UNiTY/SmartLinker"
PURPLE = "\x1b[35m"
init()
pygame.init()
pygame.mixer.init()
configTemplate = {
	"General": {
		"MainBrowser": "",
		"MainBrowserPath": "",
		"MainBrowserIsManual": False
	},
	"Personalization": {
		"AppTheme": "Auto",
		"AccentMode": "System",
		"CustomAccentColorHex": "#ff793bcc",
		"EnableMicaEffect": True,
		"ShowCommandBar": False,
		"ShowSplash": True,
		"SplashDuration": 3000,
		"EnableAcrylicOnSidebar": True,
		"ShowUpdateBanners": True
	},
	"Sound": {
		"EnableSoundEffects": False,
		"StartupSFXPath": "",
		"SuccessSFXPath": "",
		"InfoSFXPath": "",
		"WarningSFXPath": "",
		"ErrorSFXPath": "",
		"QuestionSFXPath": ""
	},
	"Selector": {
		"CloseOnBrowserSelect": False
	},
	"About": {
		"CheckUpdatesOnStart": True,
		"LastCheckedDate": "",
		"UpdateAvailable": False,
		"UpdateVersion": ""
	},
	"QFluentWidgets": {
		"ThemeMode": "",
		"ThemeColor": ""
	}
}
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
    accentMode = OptionsConfigItem("Personalization", "AccentMode", "System", OptionsValidator(["System", "Custom"]))
    accentColor = ColorConfigItem("Personalization", "CustomAccentColorHex", "#ff793bcc")
    micaEffect = ConfigItem("Personalization", "EnableMicaEffect", True, BoolValidator())
    showCommandBar = ConfigItem("Personalization", "ShowCommandBar", False, BoolValidator())
    showSplash = ConfigItem("Personalization", "ShowSplash", True, BoolValidator())
    splashDuration = RangeConfigItem("Personalization", "SplashDuration", 3000, RangeValidator(0, 10000))
    enableAcrylicOnSidebar = ConfigItem("Personalization", "EnableAcrylicOnSidebar", True, BoolValidator())
    showUpdateBanners = ConfigItem("Personalization", "ShowUpdateBanners", True, BoolValidator())
    enableSoundEffects = ConfigItem("Sound", "EnableSoundEffects", False, BoolValidator())
    startupSFXPath = ConfigItem("Sound", "StartupSFXPath", "")
    successSFXPath = ConfigItem("Sound", "SuccessSFXPath", "")
    infoSFXPath = ConfigItem("Sound", "InfoSFXPath", "")
    warningSFXPath = ConfigItem("Sound", "WarningSFXPath", "")
    errorSFXPath = ConfigItem("Sound", "ErrorSFXPath", "")
    questionSFXPath = ConfigItem("Sound", "QuestionSFXPath", "")
    closeOnBrowserSelect = ConfigItem("Selector", "CloseOnBrowserSelect", False, BoolValidator())
    checkUpdatesOnStart = ConfigItem("About", "CheckUpdatesOnStart", True, BoolValidator())
    lastCheckedDate = ConfigItem("About", "LastCheckedDate", "")
    updateAvailable = ConfigItem("About", "UpdateAvailable", False)
    updateVersion = ConfigItem("About", "UpdateVersion", "")
    qAccentColor = ColorConfigItem("QFluentWidgets", "ThemeColor", "#ff25d9e6")

class SmartLogic():
    """ SmartUtils
    ==========
    General SmartLinker functions class
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

    def isDarkMode(self) -> bool:
        """ SmartUtils
        ==========
        DarkDetect library-based checker for system dark mode

        Returns
        -------
        :boolean: whether the system is in dark mode
        """
        return bool(darkdetect.isDark())

    def openURL(self, requestURL: str):
        """ SmartUtils
        ==========
        Specified URL loader
        
        Parameters
        ----------
        requestURL: string
            The URL you want a browser to load
        """
        webbrowser.open(requestURL)

    def successNotify(self, title: str, content: typing.Optional[str], parent = None):
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
            position = InfoBarPosition.TOP,
            duration = 5000,
            parent = self
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.successSFXPath), "success notification")

    def warningNotify(self, title: str, content: typing.Optional[str], parent = None):
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
            orient = Qt.Orientation.Horizontal,
            isClosable = True,
            position = InfoBarPosition.BOTTOM,
            duration = 5000,
            parent = parent
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.warningSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.warningSFXPath), "warning notification")

    def errorNotify(self, title: str, content: typing.Optional[str], parent = None):  
        """ SmartUtils
        ==========
        Error notification bar
        
        Parameters
        ----------
        title: string
            The title of the error notification bar
        content: string
            The message you want the error notification bar to display (optional)
        """
        InfoBar.error(
            title = title,
            content = content,
            orient = Qt.Orientation.Horizontal,
            isClosable = True,
            position = InfoBarPosition.BOTTOM_RIGHT,
            duration = -1,
            parent = parent
        ).show()
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)):
            self.playSound(soundStreamer, cfg.get(cfg.errorSFXPath), "error notification")

    def infoNotify(self, title: str, content: typing.Optional[str], parent = None): 
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

    def browseFileDialog(self, parent: typing.Optional[QWidget], dialogTitle: typing.Optional[str], mainDir: typing.Optional[str], typeFilter: typing.Optional[str]) -> str:
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
        typeFilter: string | list[string]
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
                    print(f"{Back.GREEN}{browsName} == {os.path.basename(process.info['exe']).lower()}{Style.RESET_ALL}")
                    break
                else: print(f"{Back.RED}{browsName} != {os.path.basename(process.info['exe']).lower()}{Style.RESET_ALL}")
        print(f"\n'{browsName}' is running: {Fore.GREEN if isProcessOpen else Fore.RED}{isProcessOpen}{Style.RESET_ALL}\n")
        return isProcessOpen

    def consoleScript(self) -> str:
        """ SmartUtils
        ==========
        SmartLinker name in-console renderer

        Returns
        -------
        :string: The rendered SmartLinker name
        """
        return f"{PURPLE}============================{Style.RESET_ALL} {SmartLinkerAuthor} presents {Fore.BLUE}============================{Style.RESET_ALL}\n\n" \
            f"{PURPLE}███████╗███╗   ███╗ █████╗ ██████╗ ████████╗{Fore.BLUE}██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗ {Style.RESET_ALL}\n" \
            f"{PURPLE}██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝{Fore.BLUE}██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗{Style.RESET_ALL}\n" \
            f"{PURPLE}███████╗██╔████╔██║███████║██████╔╝   ██║   {Fore.BLUE}██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██████╔╝{Style.RESET_ALL}\n" \
            f"{PURPLE}╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   {Fore.BLUE}██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██╔══██╗{Style.RESET_ALL}\n" \
            f"{PURPLE}███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   {Fore.BLUE}███████╗██║██║ ╚████║██║  ██╗███████╗██║  ██║{Style.RESET_ALL}\n" \
            f"{PURPLE}╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   {Fore.BLUE}╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{Style.RESET_ALL}\n\n" \
            f"{PURPLE}================================={Style.RESET_ALL} Mastering URL Handling {Fore.BLUE}================================{Style.RESET_ALL}\n"

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
            with open("SmartSelectorReport.log", 'a', encoding="utf-8") as logger:
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
            with open("SmartSelectorReport.log", 'w') as clear:
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
            if not platform.system() is "Windows": isCompatible = False
            else: isCompatible = sys.getwindowsversion().build >= minBuild 
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to check system compatibility: {e}{Style.RESET_ALL}")
            self.managerLog(f"ERROR: Failed to check system compatibility: {e}")
        finally: return isCompatible

cfg = Config()
smart = SmartLogic()
cfgFilePath = smart.resourcePath("bin/config.json")
browsersCfgFilePath = smart.resourcePath("bin/browsers_config.dat")
qconfig.load(cfgFilePath, cfg)
