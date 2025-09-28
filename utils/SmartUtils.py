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

import darkdetect, datetime, json, os, pickle, psutil, pygame, requests, socket, subprocess, sys, typing, webbrowser, win32api, winreg
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

def smartResourcePath(relativePath: str):
    """ SmartUtils
    ==========
    Dynamic provider of internal resources and files
    
    Parameters
    ----------
    relativePath: string
        The path to the internal resource you want to access
    """
    if hasattr(sys, "_MEIPASS"):
        basePath = getattr(sys, "_MEIPASS", os.path.abspath("."))
    else:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relativePath)

cfg = Config()
cfgFilePath = smartResourcePath("bin/config.json")
browsersCfgFilePath = smartResourcePath("bin/browsers_config.dat")
qconfig.load(cfgFilePath, cfg)
soundStreamer = None

def smartLoadBrowsersJSON():
    """ SmartUtils
    ==========
    Loader of all the saved browsers """
    try:
        with open(browsersCfgFilePath, "r") as browserReader:
            return json.load(browserReader)
    except: return {
            "MyBrowsers": []
        }
    
def smartLoadBrowsers():
    """ SmartUtils
    ==========
    Loader of all the saved browsers """
    try:
        with open(browsersCfgFilePath, "rb") as browserReader:
            return pickle.load(browserReader)
    except:
        return {
            "MyBrowsers": []
        }

def smartWriteBrowsersJSON(browsers: dict[str, list[str]]):
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

def smartWriteBrowsers(browsers: dict[str, list[str]]):
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
        smartLog(f"ERROR: Failed to save browser-related changes: {e}")

def restartApp():
    """ SmartUtils
    ==========
    Global function to restart the app """
    os.execl(sys.executable, sys.executable, *sys.argv)

def stopApp():
    """ SmartUtils
    ==========
    Global function to stop the app process """
    sys.exit()

def smartRestartApp():
    """ SmartUtils
    ==========
    Global function to restart the app """
    execPath = sys.executable
    execArgs = sys.argv
    
    try:
        subprocess.Popen([execPath] + execArgs[1:])
        sys.exit()
    except Exception as e:
        print(f"{Fore.RED}Something went wrong while attempting to restart {SmartLinkerName} with 'subprocess': {e}{Style.RESET_ALL}\nRetrying with 'os.execv'...")
        smartLog(f"ERROR: Failed to restart {SmartLinkerName} with 'subprocess': {e}")
        smartLog("Retrying with 'os.execv'...")
        try:
            os.execv(execPath, tuple([execPath] + execArgs[1:]))
        except Exception as ee:
            print(f"{Fore.RED}Something went wrong while attempting to restart {SmartLinkerName} with 'os.execv': {ee}\nFailed to restart {SmartLinkerName}, please try again...{Style.RESET_ALL}")
            smartLog(f"ERROR: Failed to restart {SmartLinkerName} with 'os.execv': {ee}")

def isDarkModeEnabled() -> bool:
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
            isDarkMode = value == 0  # 0 = dark, 1 = light
            return isDarkMode
    except Exception:
        return False  # défaut = clair

def smartPlaySound(sound, path: str, label: str):
    sound = None
    try:
        sound = pygame.mixer.Sound(path)
        if sound: sound.play()
        else:
            print(f"{Fore.YELLOW}Unable to play the {label} sound, because it has not been loaded...{Style.RESET_ALL}")
            smartLog(f"WARNING: Unable to play the {label} sound, because it has not been loaded...")
    except Exception as e:
        sound = None
        print(f"{Fore.RED}Something went wrong while attempting to play the {label} sound: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to play the {label} sound: {e}")

def smartCheckConnectivity(hostname = "8.8.8.8", port = 53, timeout = 5.0):
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
    try:
        socket.create_connection((hostname, port), timeout)
        isConnected = True
    except socket.gaierror:
        print(f"{Fore.RED}Failed to establish connection: the DNS address cannot be resolved...{Style.RESET_ALL}")
        smartLog("ERROR: Failed to establish connection: could not resolve DNS address...")
        isConnected = False
    except TimeoutError:
        print(f"{Fore.RED}Failed to establish connection: the timeout has been exceeded...{Style.RESET_ALL}")
        smartLog("ERROR: Failed to establish connection: timeout exceeded...")
        isConnected = False
    except OSError as ose:
        print(f"{Fore.RED}Failed to establish connection: an OS-related error occured: {ose}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to establish connection because of an OS-related error: {ose}")
        isConnected = False
    except Exception as e:
        print(f"{Fore.RED}Something went wrong while attempting to establish connection: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to establish connection: {e}")
        isConnected = False
    finally: return isConnected

def smartIsDarkMode() -> bool:
    """ SmartUtils
    ==========
    DarkDetect library-based checker for system dark mode

    Returns
    -------
    isDarkMode: boolean
        whether the system is in dark mode
    """
    isDarkMode = bool(darkdetect.isDark())
    return isDarkMode

def smartOpenURL(requestURL: str):
    """ SmartUtils
    ==========
    Specified URL loader
    
    Parameters
    ----------
    requestURL: string
        The URL you want a browser to load
    """
    webbrowser.open(requestURL)

def smartSuccessNotify(self, title: str, content: typing.Optional[str]):
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
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=5000,
        parent=self
    ).show()
    if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath)):
        smartPlaySound(soundStreamer, cfg.get(cfg.successSFXPath), "success notification")

def smartWarningNotify(self, title: str, content: typing.Optional[str]):
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
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.BOTTOM,
        duration=5000,
        parent=self
    ).show()
    if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.warningSFXPath)):
        smartPlaySound(soundStreamer, cfg.get(cfg.warningSFXPath), "warning notification")

def smartErrorNotify(self, title: str, content: typing.Optional[str]):
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
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.BOTTOM_RIGHT,
        duration=-1,
        parent=self
    ).show()
    if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)):
        smartPlaySound(soundStreamer, cfg.get(cfg.errorSFXPath), "error notification")

def smartInfoNotify(self, title: str, content: typing.Optional[str]):
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
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.BOTTOM_RIGHT,
        duration=5000,
        parent=self
    ).show()
    if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.infoSFXPath)):
        smartPlaySound(soundStreamer, cfg.get(cfg.infoSFXPath), "information notification")

def smartGetFileIcon(filePath: str) -> QIcon:
    """ SmartUtils
    ==========
    Specified executable icon provider

    Parameters
    ----------
    filePath: string
        The path to the executable you want the icon to be provided

    Returns
    -------
    fileIcon: QIcon
        The icon of the provided executable (whose path must be valid)
    """
    if filePath: return QFileIconProvider().icon(QFileInfo(filePath))
    return QIcon(smartResourcePath("resources/images/icons/icon.ico"))

def smartBrowseFileDialog(parent: typing.Optional[QWidget], dialogTitle: typing.Optional[str], mainDir: typing.Optional[str], typeFilter: typing.Optional[str]) -> str:
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
    isFileExists: boolean
        Whether the selected file path returned by the dialog is valid
    """
    filePath, _ = QFileDialog.getOpenFileName(
        parent,
        dialogTitle,
        mainDir,
        typeFilter
    )
    if filePath: return filePath
    return ""
    
def smartIsSystemDefault(self, appID: str) -> bool:
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
                return isSystemDefault
    except FileNotFoundError as fe:
        # The key doesn't exist, so no default browser has been set
        print(f"Registry information: {fe}")
        # smartInfoNotify(self, "Did you know?", "Until now, no browser has been set by default in your system.")
        return False
    except Exception as e:
        print(f"An error occured while checking registry : {e}")
        smartErrorNotify(self, "Something went wrong...", f"An error occured while checking registry : {e}")
        return False

def smartIsBrowserOpen(exePath: str) -> bool:
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

"""
SmartLinker
"""

def smartConsoleScript() -> str:
    """ SmartUtils
    ==========
    SmartLinker name in-console renderer

    Returns
    -------
    consName: string
        The rendered SmartLinker name
    """
    return f"{PURPLE}============================{Style.RESET_ALL} {SmartLinkerAuthor} presents {Fore.BLUE}============================{Style.RESET_ALL}\n\n" \
           f"{PURPLE}███████╗███╗   ███╗ █████╗ ██████╗ ████████╗{Fore.BLUE}██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗ {Style.RESET_ALL}\n" \
           f"{PURPLE}██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝{Fore.BLUE}██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗{Style.RESET_ALL}\n" \
           f"{PURPLE}███████╗██╔████╔██║███████║██████╔╝   ██║   {Fore.BLUE}██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██████╔╝{Style.RESET_ALL}\n" \
           f"{PURPLE}╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   {Fore.BLUE}██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██╔══██╗{Style.RESET_ALL}\n" \
           f"{PURPLE}███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   {Fore.BLUE}███████╗██║██║ ╚████║██║  ██╗███████╗██║  ██║{Style.RESET_ALL}\n" \
           f"{PURPLE}╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   {Fore.BLUE}╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{Style.RESET_ALL}\n\n" \
           f"{PURPLE}================================={Style.RESET_ALL} Mastering URL Handling {Fore.BLUE}================================{Style.RESET_ALL}\n"

def smartLog(message):
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

def smartSelectorLog(message):
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

def smartEmptyLog():
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

def smartEmptySelectorLog():
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

def smartHideLayoutWidgets(layout):
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
            smartHideLayoutWidgets(item.layout())

def smartShowLayoutWidgets(layout):
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
            smartShowLayoutWidgets(item.layout())

def smartSegoeTitle() -> QFont:
    font = QFont()
    font.setFamily("Segoe UI Variable")
    font.setPixelSize(28)
    font.setWeight(QFont.Weight.DemiBold)
    return font

def smartSegoeSubtitle() -> QFont:
    font = QFont()
    font.setFamily("Segoe UI Variable")
    font.setPixelSize(20)
    font.setWeight(QFont.Weight.DemiBold)
    return font

def smartSegoeBody() -> QFont:
    font = QFont()
    font.setFamily("Segoe UI Variable")
    font.setPixelSize(14)
    return font

def smartSegoeCaption() -> QFont:
    font = QFont()
    font.setFamily("Segoe UI Variable")
    font.setPixelSize(12)
    return font

def smartGetLatestVersionTagLocal():
    """ SmartUtils
    ==========
    SmartLinker's latest version tag checker

    Returns
    -------
    versionTag: str
        The latest version tag detected
    """
    try:
        print("Checking for latest version...")
        smartLog("Checking for latest version...")
        version = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            check=True,
            capture_output=True,
            text=True
        )
        versionTag = version.stdout.strip()
        print(f"{Fore.BLUE}Latest version: {versionTag}{Style.RESET_ALL}")
        smartLog(f"Latest version: {versionTag}")
        return versionTag
    except Exception as e:
        print(f"{Fore.RED}Something went wrong while checking the latest version: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to check latest version: {e}")
        return ""

def smartGetLatestVersionTag():
    tagUrl = f"{SmartLinkerGitRepoAPI}/tags"
    params = {'per_page': 1}
    latestTag: str = ""

    try:
        print("Checking for latest version...")
        smartLog("Checking for latest version...")
        response = requests.get(tagUrl, params, timeout=5)
        response.raise_for_status()

        tagsList = response.json()
        if tagsList:
            latestTag = tagsList[0].get("name")
            print(f"{Fore.BLUE}Latest version: {latestTag}{Style.RESET_ALL}")
            smartLog(f"Latest version: {latestTag}")
        else:
            latestTag = ""
            print(f"{Fore.RED}Failed to get latest version tag from GitHub repository: there are no tags to be found...{Style.RESET_ALL}")
            smartLog("ERROR: Failed to get latest version tag from GitHub repository: could not find any tags...")
    except requests.exceptions.RequestException as re:
        latestTag = ""
        print(f"{Fore.RED}Failed to communicate with GitHub repository: {re}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to communicate with GitHub repository: {re}")
    except Exception as e:
        latestTag = ""
        print(f"{Fore.RED}Something went wrong while attempting to get the latest version tag from GitHub: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to get latest version tag from GitHub repository: {e}")
    finally: return latestTag

def smartGetLatestReleaseTag():
    releaseUrl = f"{SmartLinkerGitRepoAPI}/releases/latest"
    latestTag: str = ""
    try:
        print("Checking for latest release version...")
        smartLog("Checking for latest release version...")
        response = requests.get(releaseUrl, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Latest release version: {latestTag}")
        smartLog(f"Latest release version: {latestTag}")
        latestTag = data.get("tag_name")
    except requests.exceptions.RequestException as re:
        print(f"{Fore.RED}Failed to communicate with GitHub repository: {re}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to communicate with GitHub repository: {re}")
        latestTag = ""
    except Exception as e:
        print(f"{Fore.RED}Something went wrong while attempting to get the latest release tag from GitHub: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to get latest release tag from GitHub repository: {e}")
        latestTag = ""
    finally: return latestTag

def smartConvertToHEX(color: str | QColor):
    """ SmartUtils
    ==========
    HEX w/ alpha (#AARRGGBB) to HEX w/o alpha (#RRGGBB) color format converter

    Parameters
    ----------
    color: str | QColor
        The color whose format must be converted.
    
    Returns
    -------
    newColor: str
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
        smartLog(f"ERROR: Failed to convert color format: {e}")

def smartConvertToRGBA(color: str | QColor):
    """ SmartUtils
    ==========
    RGBA color format converter

    Parameters
    ----------
    color: str | QColor
        The color whose format must be converted.
    
    Returns
    -------
    newColor: str
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
        smartLog(f"ERROR: Failed to convert color format: {e}")

def smartConvertToRGB(color: str | QColor):
    """ SmartUtils
    ==========
    RGB color format converter

    Parameters
    ----------
    color: str | QColor
        The color whose format must be converted.
    
    Returns
    -------
    newColor: str
        The re-formatted color string.
    """
    try:
        oldColor = QColor(color)
        if not isValid(oldColor): raise ValueError("Invalid color format")

        red = oldColor.red()
        green = oldColor.green()
        blue = oldColor.blue()
        newColor = f"{red}, {green}, {blue}"
        return newColor
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to convert color format: {e}")

def smartCustomAlphaToRGB(color, alpha):
    """ SmartUtils
    ==========
    Custom alpha value to color applying tool

    Parameters
    ----------
    color: Unknown
        The color you want to modify.
    alpha: num
        The alpha value you want to apply.

    Returns
    -------
    newColor: Unknown
        The modified version of the color.
    """
    try:
        oldColor = QColor(color)
        if not isValid(oldColor): raise ValueError("Invalid color format entered")

        r, g, b, a = oldColor.getRgb()
        if r and g and b: newColor = oldColor.setRgb(r, g, b, alpha)
        return newColor
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during color conversion: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to convert color format: {e}")

def smartGetRed(color):
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
            return red
        else: return 0
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during red value pick: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to pick red value from color: {e}")

def smartGetGreen(color):
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
            return green
        else: return 0
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during green value pick: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to pick green value from color: {e}")

def smartGetBlue(color):
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
            return blue
        else: return 0
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during blue value pick: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to pick blue value from color: {e}")

def smartGetAlpha(color):
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
            return alpha
        else: return 0
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during alpha value pick: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to pick alpha value from color: {e}")

def smartGetAlphaFloat(color):
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
            return alpha
        else: return 0.0
    except Exception as e:
        print(f"{Fore.RED}Something went wrong during alpha value pick: {e}{Style.RESET_ALL}")
        smartLog(f"ERROR: Failed to pick alpha value from color: {e}")
