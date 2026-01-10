"""
SmartCLIHandler
===============
An advanced argument parser and handler for SmartLinker's command-line interface.

:Copyright: © 2025 by #theF∆STER™ UN!TY.
"""

# =========================================================

from utils.SmartUtils import *
import contextlib, mimetypes, wave

# ==========================================================================

class ArgumentsHandler:
    """ SmartCLIHandler
    ===============
    Class for handling command-line arguments for SmartLinker.
    """

    def __init__(self):
        super().__init__()
    
    def validateExe(self, path: str):
        """ SmartCLIHandler
        ===============
        Checks if an executable exists at the specified path

        Parameters
        ----------
        path: string
            The path to be specified
        """
        if not os.path.exists(path): raise argparse.ArgumentTypeError(f"The file at the specified path cannot be found ({path}) ...")
        if not path.endswith((".exe", ".bat", ".cmd")): raise argparse.ArgumentTypeError(f'The specified file "{path}" does not appear to be a valid executable...')
        return path
        
    def validateSmartListBrowser(self, browser: str):
        """ SmartCLIHandler
        ===============
        Checks if the specified browser exists in the SmartList

        Parameters
        ----------
        browser: string
            The browser to be specified
        """
        browsersNames = [browser["name"] for browser in smart.loadBrowsers()["MyBrowsers"]]
        if browser not in browsersNames: raise argparse.ArgumentTypeError(f'The specified browser "{browser}" does not exist in your current SmartList...')
        return browser
    
    def validateSFX(self, sfx: str):
        """ SmartCLIHandler
        ===============
        Validates the sound effects

        Parameters
        ----------
        sfx: string
            The sound effect to be specified
        """
        sfxGroup = ["startup", "success", "info", "warning", "error", "question", "selector"]
        if sfx not in sfxGroup: raise argparse.ArgumentTypeError(f'The specified sound effect "{sfx}" is invalid. Allowed values are: {sfxGroup}')
        return sfx
    
    def validateAudio(self, path: str):
        """ SmartCLIHandler
        ===============
        Validates that the provided path points to an audio file.

        Parameters
        ----------
        path: string
            The path to the audio file to validate
        """
        if not os.path.exists(path): raise argparse.ArgumentTypeError(f"The file at the specified path cannot be found ({path}) ...")

        mime_type, _ = mimetypes.guess_type(path)
        if mime_type and mime_type.startswith("audio"): return path

        # Fallback: try opening as WAV (standard library)
        try: 
            with contextlib.closing(wave.open(path, "rb")): return path
        except Exception: pass

        raise argparse.ArgumentTypeError(f'The specified file "{path}" does not appear to be a supported audio file.')
    
    def subCommands(self):
        """ SmartCLIHandler
        ===============
        Main command-line handlers for specific commands
        """
        parser = argparse.ArgumentParser(description=f"{SmartLinkerName} Command-Line Interface")
        subparser = parser.add_subparsers(dest="cmd", help="Sub-commands")
        
        # +-------------------+
        # | SUB-COMMAND: load |
        # +-------------------+
        argLoad = subparser.add_parser("load", help="Load a specified URL. Can be used with specific options.")

        # Mandatory positional
        argLoad.add_argument(
            "requestURL",
            help="The URL you would want to load into a browser."
        )
        argLoadGroup = argLoad.add_mutually_exclusive_group()

        # Optional - if not specified, the Smart Selector will show up
        argLoadGroup.add_argument(
            "-sl", "--smart-list",
            type=self.validateSmartListBrowser,
            help="The browser from your SmartList you want to load your URL into."
        )

        # Optional - if not specified, the Smart Selector will show up
        argLoadGroup.add_argument(
            "-eb", "--external-browser",
            type=self.validateExe,
            help="An external browser you would want to specify manually from your storage."
        )

        # +-------------------+
        # | SUB-COMMAND: core |
        # +-------------------+
        argCore = subparser.add_parser("core", help=f"Manage your {SmartLinkerName} configuration. Can be used with specific options.")
        argCoreSub = argCore.add_subparsers(dest="action", help=f"{SmartLinkerName} configuration sub-commands")

        # ---------- core add-browser ----------
        argCoreAddBrowser = argCoreSub.add_parser("add-browser", help=f"Add a new browser to your SmartList.")
        argCoreAddBrowser.add_argument("-n", "--name", required=True, help="The name of the browser to add.")
        argCoreAddBrowser.add_argument("-p", "--path", required=True, type=self.validateExe, help="The executable path of the browser to add.")

        # ---------- core clear-browsers ----------
        argCoreClearBrowsers = argCoreSub.add_parser("clear-browsers", help=f"Clear all browsers from your SmartList.")
        argCoreClearBrowsers.add_argument("-ncf", "--noconfirm", action="store_true", help="Confirm clearing all browsers without prompt.")

        # ---------- core edit-browser ----------
        argCoreEditBrowser = argCoreSub.add_parser("edit-browser", help=f"Edit an existing browser from your SmartList.")
        argCoreEditBrowser.add_argument("-n", "--name", required=True, type=self.validateSmartListBrowser, help="The name of the browser to edit.")
        argCoreEditBrowser.add_argument("-new", "--new-name", help="The new name of the browser.")
        argCoreEditBrowser.add_argument("-p", "--path", type=self.validateExe, help="The new executable path of the browser.")

        # ---------- core list-browsers ----------
        argCoreListBrowsers = argCoreSub.add_parser("list-browsers", help="List all browsers currently saved in your SmartList.")
        argCoreListBrowsers.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to show more details about each browser.")
        argCoreListBrowsers.add_argument("-j", "--json", action="store_true", help="Output the list in JSON format.")
        argCoreListBrowsers.add_argument("-o", "--output", help="File path to save the browser list output.")
        argCoreListBrowsers.add_argument("--name-only", action="store_true", help="Output only the names of the browsers in the list.")

        # ---------- core main-browser ----------
        argCoreMainBrowser = argCoreSub.add_parser("main-browser", help=f"Display the current main browser for {SmartLinkerName} (if already set).")
        mainBrowserGroup = argCoreMainBrowser.add_mutually_exclusive_group()
        mainBrowserGroup.add_argument("-sl", "--smart-list", type=self.validateSmartListBrowser, help="Set a browser from your SmartList as the main browser.")
        mainBrowserGroup.add_argument("-eb", "--external-browser", type=self.validateExe, help="Set an external browser as the main browser.")

        # ---------- core remove-browser ----------
        argCoreRemoveBrowser = argCoreSub.add_parser("remove-browser", help="Remove a browser from your SmartList.")
        argCoreRemoveBrowser.add_argument("-n", "--name", required=True, type=self.validateSmartListBrowser, help="The name of the browser to remove.")
        
        # ---------- core sfx ----------
        argCoreSfx = argCoreSub.add_parser("sfx", help=f"Enable or disable sound effects in {SmartLinkerName}.")
        sfxGroup = argCoreSfx.add_mutually_exclusive_group()
        sfxGroup.add_argument("--enable", action="store_true", help="Enable sound effects.")
        sfxGroup.add_argument("--disable", action="store_true", help="Disable sound effects.")
        argCoreSfx.add_argument("-t", "--type", type=self.validateSFX, help="The sound effect you would want to configure.") # required=True
        argCoreSfx.add_argument("-f", "--file", type=self.validateAudio, help="The sound effect file path to set.") # required=True
        
        # ---------- core splash ----------
        argCoreSplash = argCoreSub.add_parser("splash", help=f"Enable or disable the splash screen on {SmartLinkerName} startup.")
        splashGroup = argCoreSplash.add_mutually_exclusive_group(required=True)
        splashGroup.add_argument("--enable", action="store_true", help="Enable the splash screen.")
        splashGroup.add_argument("--disable", action="store_true", help="Disable the splash screen.")
        splashGroup.add_argument("--state", action="store_true", help="Show the current state of the splash screen.")
        argCoreSplash.add_argument("--duration", type=int, help="Set the duration (in milliseconds) for the splash screen display.")

        # ---------- core temp-clean ----------
        argCoreTempClean = argCoreSub.add_parser("temp-clean", help=f"Clean temporary files created by {SmartLinkerName}.")
        argCoreTempClean.add_argument("-ncf", "--noconfirm", action="store_true", help="Confirm cleaning temporary files without prompt.")

        # ---------- core update ----------
        argCoreUpdate = argCoreSub.add_parser("update", help=f"Check for {SmartLinkerName} updates or install a previously downloaded update.")
        argCoreUpdateGroup = argCoreUpdate.add_mutually_exclusive_group(required=True)
        argCoreUpdateGroup.add_argument("-ace", "--auto-check-enable", action="store_true", help="Enable the automatic check for updates.")
        argCoreUpdateGroup.add_argument("-acd", "--auto-check-disable", action="store_true", help="Disable the automatic check for updates.")
        argCoreUpdateGroup.add_argument("-c", "--check", action="store_true", help="Check for the latest available update.")
        argCoreUpdateGroup.add_argument("-i", "--install", action="store_true", help="Install the latest update previously downloaded.")
        
        # ---------- core update-banners ----------
        argCoreUpdateBanners = argCoreSub.add_parser("update-banners", help=f"Enable or disable update banners in {SmartLinkerName}.")
        updateBannersGroup = argCoreUpdateBanners.add_mutually_exclusive_group(required=True)
        updateBannersGroup.add_argument("--enable", action="store_true", help="Enable update banners.")
        updateBannersGroup.add_argument("--disable", action="store_true", help="Disable update banners.")
        updateBannersGroup.add_argument("--state", action="store_true", help="Show the current state of the update banners.")

        # ---------- core version ----------
        argCoreSub.add_parser("version", help=f"Display the current version of {SmartLinkerName}.")

        return parser.parse_args()
    
class ArgumentsProcessor:
    """ SmartCLIHandler
    ===============
    Class for processing and executing actions based on parsed command-line arguments.
    """

    def __init__(self):
        super().__init__()
        self.argHandler = ArgumentsHandler()
        self.args = self.argHandler.subCommands()
    
        if not self.args: return

        if self.args.cmd == "load": self.loadURL()
        if self.args.cmd == "core":
            if self.args.action == "sfx": self.manageSoundEffects()
            if self.args.action == "splash": self.manageSplashScreen()
            if self.args.action == "temp-clean": self.cleanTempFiles()
            if self.args.action == "update": self.manageUpdates()
            if self.args.action == "update-banners": self.manageUpdateBanners()
            if self.args.action == "version": self.displayVersion()
    
    def loadURL(self):
        """ SmartCLIHandler
        ===============
        Loads a URL into the specified browser or shows the Smart Selector if none is specified.
        """
        url = self.args.requestURL
        smartBrowser = self.args.smart_list
        externalBrowser = self.args.external_browser

        if smartBrowser:
            browserPath = None
            try: browsers = smart.loadBrowsers()["MyBrowsers"]
            except Exception as e:
                print(f"Unable to load SmartList: {e}")
                browsers = None
            
            if browsers:
                for browser in browsers:
                    if browser["name"] == smartBrowser:
                        idx = browsers.index(browser)
                        browserPath = browsers[idx]["path"]
                        if browserPath: subprocess.Popen([browserPath, url])
                        else: print(f"The browser '{smartBrowser}' has no valid path specified.")
                        break
                    else: print(f"The browser '{smartBrowser}' cannot be found in your SmartList...")
            else: print(f"Sorry, your SmartList appears to be empty...")
            
        elif externalBrowser:
            if not self.argHandler.validateExe(externalBrowser):
                raise ValueError(f"The specified external browser path is invalid: {externalBrowser}")
            
            try: subprocess.Popen([externalBrowser, url])
            except Exception:
                try: os.startfile(url)
                except Exception as e: print(f"Failed to launch external browser '{externalBrowser}': {e}")
    
    def manageSoundEffects(self):
        """ SmartCLIHandler
        ===============
        Manages the sound effects state in the SmartLinker main interface.
        """
        if self.args.enable:
            if self.args.type or self.args.file:
                print(f"{Fore.BLUE}[SmartCommands] If you want to enable a specific sound effect, you need to follow this pattern:\n{Style.RESET_ALL}"
                      "\tcore sfx -t|--type <TYPE> -f|--file <PATH_TO_FILE>")
            
            else:
                cfg.set(cfg.enableSoundEffects, True)
                print(f"{Fore.BLUE}[SmartCommands] The sound effects state is now set as {Fore.GREEN}enabled{Fore.BLUE}.{Style.RESET_ALL}")
        
        elif self.args.disable:
            if self.args.type or self.args.file:
                print(f"{Fore.BLUE}[SmartCommands] If you want to disable a specific sound effect, you need to follow this pattern:\n{Style.RESET_ALL}"
                      '\tcore sfx -t|--type <TYPE> -f|--file ""')

            else:
                cfg.set(cfg.enableSoundEffects, False)
                print(f"{Fore.BLUE}[SmartCommands] The sound effects state is now set as {Fore.RED}disabled{Fore.BLUE}.{Style.RESET_ALL}")
        
        elif self.args.type:
            if not self.args.file:
                print(f"{Fore.BLUE}[SmartCommands] If you want to set a specific sound effect file, you need to follow this pattern:\n{Style.RESET_ALL}"
                      "\tcore sfx -t|--type <TYPE> -f|--file <PATH_TO_FILE>")
            
            else:
                try:
                    SFXLib = {
                        "startup": cfg.startupSFXPath,
                        "success": cfg.successSFXPath,
                        "info": cfg.infoSFXPath,
                        "warning": cfg.warningSFXPath,
                        "error": cfg.errorSFXPath,
                        "question": cfg.questionSFXPath,
                        "selector": cfg.selectorSFXPath
                    }
                    sfxType = self.argHandler.validateSFX(self.args.type)
                    sfxFile = self.argHandler.validateAudio(self.args.file)
                    for key, value in SFXLib.items():
                        if key == sfxType:
                            cfg.set(value, sfxFile)
                            print(f"{Fore.BLUE}[SmartCommands] The sound effect '{sfxType}' has been successfully set to the file: {PURPLE}{sfxFile}{Style.RESET_ALL}")
                            break
                except Exception as e: print(f"{Fore.RED}{e}{Style.RESET_ALL}")

        elif self.args.file and not self.args.type:
                print(f"{Fore.BLUE}[SmartCommands] If you want to set a specific sound effect file, you need to follow this pattern:\n{Style.RESET_ALL}"
                  "\tcore sfx -t|--type <TYPE> -f|--file <PATH_TO_FILE>")
        
        else: print(f"{Fore.BLUE}[SmartCommands] The sound effects are currently {Fore.GREEN if cfg.get(cfg.enableSoundEffects) else Fore.RED}{'enabled' if cfg.get(cfg.enableSoundEffects) else 'disabled'}{Fore.BLUE}.{Style.RESET_ALL}")

    def manageSplashScreen(self):
        """ SmartCLIHandler
        ===============
        Manages the splash screen state in the SmartLinker main interface.
        """

        if self.args.enable:
            if not self.args.duration:
                print(f"{Fore.YELLOW}[SmartCommands - Warning] To enable the splash screen, you need to specify the display duration in milliseconds (eg. core splash --enable --duration 5000).")
                duration = int(input(f"{Fore.BLUE}\tPlease enter the display duration in milliseconds: {Style.RESET_ALL}"))
                if duration and duration >= 1:
                    cfg.set(cfg.showSplash, True)
                    cfg.set(cfg.splashDuration, duration)
                    print(f"{Fore.BLUE}[SmartCommands] The splash screen state is now set as {Fore.GREEN}enabled{Fore.BLUE} and will be displayed for {PURPLE}{duration} milliseconds{Fore.BLUE}.{Style.RESET_ALL}")
                    if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
                
                else: print(f"{Fore.BLUE}[SmartCommands] The splash screen duration must be at least {PURPLE}1 millisecond{Fore.BLUE}.{Style.RESET_ALL}")
            
            elif self.args.duration >= 1:
                cfg.set(cfg.showSplash, True)
                cfg.set(cfg.splashDuration, self.args.duration)
                print(f"{Fore.BLUE}[SmartCommands] The splash screen state is now set as {Fore.GREEN}enabled{Fore.BLUE} and will be display for {PURPLE}{self.args.duration} milliseconds{Fore.BLUE}.{Style.RESET_ALL}")
                if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
            
            else: print(f"{Fore.BLUE}[SmartCommands] The splash screen duration must be at least {PURPLE}1 millisecond{Fore.BLUE}.{Style.RESET_ALL}")
        
        elif self.args.disable:
            if self.args.duration: print(f"{Fore.BLUE}[SmartCommands] You cannot set a duration when disabling the splash screen. The duration parameter will be ignored.{Style.RESET_ALL}")
            cfg.set(cfg.showSplash, False)
            print(f"{Fore.BLUE}[SmartCommands] The splash screen state is now set as {Fore.RED}disabled{Fore.BLUE}.{Style.RESET_ALL}")
            if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
        
        elif self.args.state:
            if self.args.duration: print(f"{Fore.BLUE}[SmartCommands] You cannot set a duration when checking the splash screen state. The duration parameter will be ignored.{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[SmartCommands] Splash screen current configuration:\n"
                  f"\tState: {Fore.GREEN if cfg.get(cfg.showSplash) else Fore.RED}{"Enabled" if cfg.get(cfg.showSplash) else "Disabled"}{Fore.BLUE}\n"
                  f"\tDuration: {PURPLE}{cfg.get(cfg.splashDuration)} milliseconds{Style.RESET_ALL}")

    def cleanTempFiles(self):
        """ SmartCLIHandler
        ===============
        Clears the temporary files (if they exist) generated by SmartLinker
        """
        tempPath = smart.resourcePath(".temp")
        tempFiles: str = ""

        if os.path.exists(tempPath):
            if not self.args.noconfirm:
                if os.listdir(tempPath):
                    for tempFile in os.listdir(tempPath): tempFiles = f"{tempFiles}\t→ {tempFile}\n"
                    print(f"{Fore.YELLOW}[SmartCommands - Warning] The temporary folder contains some files:\n{tempFiles}")
                    response = str(input(f"Do you still want to proceed with cleaning the temporary files? (y/n): {Style.RESET_ALL}")).lower()

                    if response in ["y", "yes"]:
                        try:
                            shutil.rmtree(tempPath)
                            print(f"{Fore.GREEN}[SmartCommands - Success] Temporary files have been successfully cleaned.{Style.RESET_ALL}")
                        except Exception as e: print(f"{Fore.RED}[SmartCommands - Error] An error occurred while cleaning temporary files: {e}{Style.RESET_ALL}")
                    
                    elif response in ["n", "no"]: print(f"{Fore.BLUE}[SmartCommands] Temporary files cleaning operation has been cancelled by the user.{Style.RESET_ALL}")
                    
                    else: print(f"{Fore.YELLOW}[SmartCommands - Warning] Invalid response. Temporary files cleaning operation has been cancelled.{Style.RESET_ALL}")
                
                else:
                    os.rmdir(tempPath)
                    print(f"{Fore.GREEN}[SmartCommands - Success] The temporary folder has been successfully cleaned.{Style.RESET_ALL}")
            
            else:
                try:
                    shutil.rmtree(tempPath)
                    print(f"{Fore.GREEN}[SmartCommands - Success] Temporary files have been successfully cleaned.{Style.RESET_ALL}")
                except Exception as e: print(f"{Fore.RED}[SmartCommands - Error] An error occurred while cleaning temporary files: {e}{Style.RESET_ALL}")
        
        else: print(f"{Fore.BLUE}[SmartCommands] No temporary files found to clean.{Style.RESET_ALL}")

    def manageUpdates(self):
        """ SmartCLIHandler
        ===============
        Manages the update-related settings in the SmartLinker main interface.
        """
        if self.args.auto_check_enable:
            cfg.set(cfg.checkUpdatesOnStart, True)
            print(f"{Fore.BLUE}[SmartCommands] The automatic update check is now set as {Fore.GREEN}enabled{Fore.BLUE}.{Style.RESET_ALL}")
            if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
        
        elif self.args.auto_check_disable:
            cfg.set(cfg.checkUpdatesOnStart, False)
            print(f"{Fore.BLUE}[SmartCommands] The automatic update check is now set as {Fore.RED}disabled{Fore.BLUE}.{Style.RESET_ALL}")
            if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
        
        elif self.args.check:
            isConnected = smart.checkConnectivity()
            if isConnected:
                self.latestVersion = smart.getLatestVersionTag()
                checkTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                
                if not self.latestVersion:
                    self.lastChecked = f"Last checked: {checkTime} (Failed to check for updates)"
                    print(f"{Fore.YELLOW}[SmartCommands - Warning] No version tags have been found...{Style.RESET_ALL}")
                
                elif Version(self.latestVersion) > Version(SmartLinkerVersion):
                    self.lastChecked = f"Last checked: {checkTime} (Latest version: {self.latestVersion})"
                    cfg.set(cfg.updateAvailable, True)
                    cfg.set(cfg.updateVersion, self.latestVersion)
                    print(f"{Fore.BLUE}[SmartCommands] The latest version of {SmartLinkerName} is now available:\n"
                          f"\tCurrent version: {PURPLE}{SmartLinkerVersion}{Fore.BLUE}\n"
                          f"\tLatest version: {Fore.GREEN}{self.latestVersion}{Fore.BLUE}\n\n")
                    response = str(input(f"Do you want to download the latest update now? (y/n): {Style.RESET_ALL}")).lower()
                    if response in ["y", "yes"]: self.downloadUpdate()
                    elif response in ["n", "no"]: print(f"{Fore.BLUE}[SmartCommands] Update download operation has been cancelled by the user.\n"
                                                        f"\tPlease note that you can download the update later using the following command:\n\t"
                                                        f"{PURPLE}core update -i|--install{Style.RESET_ALL}")
                    else: print(f"{Fore.YELLOW}[SmartCommands - Warning] Invalid response. Update download operation has been cancelled.{Style.RESET_ALL}")
                
                else:
                    self.lastChecked = f"Last checked: {checkTime}"
                    cfg.set(cfg.updateAvailable, False)
                    cfg.set(cfg.updateVersion, "")
                    print(f"{Fore.BLUE}[SmartCommands] {SmartLinkerName} is currently up-to-date.{Style.RESET_ALL}")

                cfg.set(cfg.lastCheckedDate, checkTime)
            
            else: print(f"{Fore.YELLOW}[SmartCommands - Warning] Please check your internet connection, then try again...{Style.RESET_ALL}")
        
        elif self.args.install:
            if cfg.get(cfg.updateAvailable):
                updatePath = smart.resourcePath(".temp\\SmartLinkerUpdate.exe")
                if os.path.exists(updatePath):
                    try:
                        subprocess.Popen([updatePath])
                    except Exception as e: print(f"{Fore.RED}[SmartCommands - Error] An error occured while executing the update installer: {e}{Style.RESET_ALL}")
                else: self.downloadUpdate()
            
            else: print(f"{Fore.BLUE}[SmartCommands] {SmartLinkerName} is currently up-to-date.{Style.RESET_ALL}")

    def manageUpdateBanners(self):
        """ SmartCLIHandler
        ===============
        Manages the update banners state in the SmartLinker main interface.
        """
        if self.args.enable:
            cfg.set(cfg.showUpdateBanners, True)
            print(f"{Fore.BLUE}[SmartCommands] The update banners state is now set as {Fore.GREEN}enabled{Fore.BLUE}.{Style.RESET_ALL}")
            if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
        
        elif self.args.disable:
            cfg.set(cfg.showUpdateBanners, False)
            print(f"{Fore.BLUE}[SmartCommands] The update banners state is now set as {Fore.RED}disabled{Fore.BLUE}.{Style.RESET_ALL}")
            if smart.isSoftwareRunning(sys.executable): print(f"{Fore.YELLOW}[SmartCommands - Warning] {SmartLinkerName} is currently running, so you will need to restart the software for the changes to take effect.{Style.RESET_ALL}")
        
        elif self.args.state: print(f"{Fore.BLUE}[SmartCommands] The update banners are currently {Fore.GREEN if cfg.get(cfg.showUpdateBanners) else Fore.RED}{"enabled" if cfg.get(cfg.showUpdateBanners) else "disabled"}{Fore.BLUE}.{Style.RESET_ALL}")

    def displayVersion(self):
        """ SmartCLIHandler
        ===============
        Displays the current version of SmartLinker.
        """
        print(f"{Fore.BLUE}[SmartCommands] Current version of {SmartLinkerName}: {PURPLE}{SmartLinkerVersion}{Style.RESET_ALL}")

    def downloadUpdate(self):
        """ SmartCLIHandler
        ===============
        Downloads the latest available update for SmartLinker.
        """
        url = f"{SmartLinkerGitRepoURL}/releases/download/{cfg.get(cfg.updateVersion)}/SmartLinker-setup-win-{cfg.get(cfg.updateVersion)[1:]}.exe"
        destination = smart.resourcePath(".temp\\SmartLinkerUpdate.exe")

        tempPath = Path(smart.resourcePath(".temp"))
        if os.path.exists(tempPath) and tempPath.is_dir(): shutil.rmtree(tempPath)
        os.makedirs(tempPath, exist_ok=True)
        
        print(f"{Fore.BLUE}[SmartCommands] Downloading the latest update from: {PURPLE}{url}{Fore.BLUE}\n"
              f"\tTarget directory: {PURPLE}{destination}{Style.RESET_ALL}")
        response = requests.get(url, stream=True)
        total = int(response.headers.get("content-length", 0))
        with open(smart.resourcePath(".temp\\.metadata"), "wb") as metaWriter: pickle.dump(total, metaWriter)
        print(f"{Fore.BLUE}[SmartCommands] Update setup properties:\n"
              f"\tFilename: {PURPLE}SmartLinker-setup-win-{cfg.get(cfg.updateVersion)[1:]}.exe{Fore.BLUE}\n"
              f"\tFile size: {PURPLE}{total / 1024 / 1024:.2f} MB ({total} Bytes){Style.RESET_ALL}\n")

        with Progress() as progress:
            task = progress.add_task("Downloading the latest update...", total=total)
            
            with open(destination, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                    progress.update(task, advance=len(chunk))
        
        if os.path.exists(destination):
            if os.path.exists(smart.resourcePath(".temp\\.metadata")):
                with open(smart.resourcePath(".temp\\.metadata"), "rb") as metaReader: downloadSize = pickle.load(metaReader)
                if os.path.getsize(destination) == downloadSize:
                    print(f"{Fore.GREEN}[SmartCommands - Success] Update downloaded successfully to: {PURPLE}{destination}{Fore.BLUE}")
                    installPrompt = input(f"\tDo you want to install the update now? [y/n]: {Style.RESET_ALL}").lower()

                    if installPrompt in ["y", "yes"]:
                        try:
                            print(f"{Fore.BLUE}[SmartCommands] Running the downloaded update installer, please wait...{Style.RESET_ALL}")
                            subprocess.Popen([destination])
                        except Exception as e: print(f"{Fore.RED}[SmartCommands - Error] An error occurred while installing the update: {e}{Style.RESET_ALL}")
                    
                    elif installPrompt in ["n", "no"]: print(f"{Fore.BLUE}[SmartCommands] Update installation operation has been cancelled by the user. You can still install it later by executing the update installer manually.{Style.RESET_ALL}")

                    else: print(f"{Fore.YELLOW}[SmartCommands - Warning] Invalid response. Update installation operation has been cancelled.{Style.RESET_ALL}")
                
                else: print(f"{Fore.YELLOW}[SmartCommands - Warning] The update installer has not been correctly downloaded... Please try again...{Style.RESET_ALL}")

        else: print(f"{Fore.YELLOW}[SmartCommands - Warning] The update installer does not exist... Please try again...{Style.RESET_ALL}")
