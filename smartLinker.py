from utils.SmartCLIHandler import *
from utils.settingsInterface import SettingsInterface as Settings
from utils.mybrowsersInterface import MyBrowsersInterface as MyBrowsers
from utils.aboutInterface import AboutInterface as About, BrowserSelectDialog
from utils.markdownViewer import MarkdownViewer as MDView
from utils.smartSelector import SmartSelectorGUI

# =============================================================================

class UpdateCheckWorker(QObject):
    finished = pyqtSignal(str, str, str)
    error = pyqtSignal(str)

    def run(self):
        try:
            checkTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if not smart.checkConnectivity():
                self.finished.emit("offline", "", checkTime)
                return

            latestVersion = smart.getLatestVersionTag()
            self.finished.emit("done", latestVersion or "", checkTime)
        except Exception as exc:
            self.error.emit(str(exc))

class SmartLinkerGUI(FluentWindow):
    """ Class for the SmartLinker Manager (main) window """

    def __init__(self, args = None, parent = None):
        super().__init__(parent)
        RichCLI.print(smart.consoleScript())
        self.setWindowTitle("SmartLinker - Mastering URL Handling")
        self.setWindowIcon(QIcon(smart.resourcePath("resources/icons/ico/icon.ico")))
        self.setMinimumWidth(1040)
        self.resize(1100, 700)
        smart.centerWindow(self)
        self.setStyleSheet('font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;')
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        smart.emptyManagerLog()
        fontDB = QFontDatabase.addApplicationFont(smart.resourcePath("resources/fonts/SegoeFont.ttf"))
        fontUI = QFontDatabase.applicationFontFamilies(fontDB)[0]

        self.themeCtrl = ThemeController(self)
        self.latestVersion = smart.getLatestVersionTag() if bool(cfg.get(cfg.checkUpdatesOnStart) and smart.checkConnectivity()) else ""
        self.myBrowsers = smart.loadBrowsers()
        self.removeKeysDlg = None
        self.listSelectDlg = None
        self.aboutIconBadge = None
        self.updateDownloadDlg = None
        self.updateCheckToolTip = None
        self.updateCheckThread = None
        self.updateCheckWorker = None
        self.browserDlg = None

        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.startupSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.startupSFXPath), "startup")
        if bool(cfg.get(cfg.showSplash)):
            self.splash = SplashScreen(smart.resourcePath("resources/icons/ico/icon_splash.ico"), self)
            self.splash.setIconSize(QSize(125, 125))
            self.show()
            self.createSubInterfaces()
            self.splash.finish()
        else:
            self.mybrowsInterface = MyBrowsers(self)
            self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
            self.markdownViewer = MDView(self)
            self.addSubInterface(self.markdownViewer, smIco.renderIcon(smIco.MARKDOWN), "Markdown Viewer")
            self.settingInterface = Settings(self)
            self.addSubInterface(self.settingInterface, FICO.SETTING, "Settings", NavigationItemPosition.BOTTOM)
            self.aboutInterface = About(self)
            self.addSubInterface(self.aboutInterface, FICO.INFO, "About", NavigationItemPosition.BOTTOM)
            self.show()
        self.setMicaEffectEnabled(smart.isSoftwareCompatible(22000) and self.settingInterface.widgetDef.optionMicaEffect.switchButton.isChecked())
        if bool(cfg.get(cfg.checkUpdatesOnStart)):
            autoCheckTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if not self.latestVersion:
                cfg.set(cfg.updateAvailable, False)
                cfg.set(cfg.updateVersion, "")
                self.aboutInterface.aboutVersion.setContent(f"Last checked: {autoCheckTime} (Failed to check for updates)")
            elif Version(self.latestVersion) > Version(SmartLinkerVersion):
                cfg.set(cfg.updateAvailable, True)
                cfg.set(cfg.updateVersion, self.latestVersion)
                self.aboutInterface.aboutVersion.setContent(f"Last checked: {autoCheckTime} (Latest version: {self.latestVersion})")
                aboutItem = self.navigationInterface.widget(self.aboutInterface.objectName())
                IconInfoBadge.attension(
                    FICO.SYNC,
                    aboutItem.parent(),
                    aboutItem,
                    InfoBadgePosition.NAVIGATION_ITEM
                )
            else:
                cfg.set(cfg.updateAvailable, False)
                cfg.set(cfg.updateVersion, "")
                self.aboutInterface.aboutVersion.setContent(f"Last checked: {autoCheckTime}")
            cfg.set(cfg.lastCheckedDate, autoCheckTime)
        elif bool(cfg.get(cfg.updateAvailable)):
            aboutItem = self.navigationInterface.widget(self.aboutInterface.objectName())
            IconInfoBadge.attension(
                FICO.SYNC,
                aboutItem.parent(),
                aboutItem,
                InfoBadgePosition.NAVIGATION_ITEM
            )
        if args:
            argWarningDlg = MessageBox(
                "Command-line arguments detected",
                "Something went wrong while attempting to handle the arguments you provided "
                "through the command-line interface... The argument handler might have not been initialized properly, "
                "causing the application to open normally instead of processing your request.\n\n"
                f"Here are listed the arguments you provided:\n{args}",
                self)
            argWarningDlg.yesButton.setText("Understood")
            argWarningDlg.cancelButton.setEnabled(False)
            argWarningDlg.cancelButton.setVisible(False)
            argWarningDlg.show()

        self.snackButtons = {
            "Download": [
                self.mybrowsInterface.updateSnack.snackButton,
                self.markdownViewer.updateSnack.snackButton,
                self.settingInterface.updateSnack.snackButton,
                self.aboutInterface.updateSnackButton
            ],
            "Install": [
                self.mybrowsInterface.updateSnack.snackInstall,
                self.markdownViewer.updateSnack.snackInstall,
                self.settingInterface.updateSnack.snackInstall,
                self.aboutInterface.updateSnackInstall
            ]}
        if self.settingInterface.widgetDef.optionMicaEffect:
            self.settingInterface.widgetDef.optionMicaEffect.setEnabled(smart.isSoftwareCompatible(22000))
            self.settingInterface.widgetDef.optionMicaEffect.setVisible(smart.isSoftwareCompatible(22000))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.clicked.connect(lambda: self.settingInterface.cardManualSelect(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.clicked.connect(lambda: self.settingInterface.cardSetFromList(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.removeMainButton.clicked.connect(lambda: self.settingInterface.cardRemove(self))
        self.settingInterface.widgetDef.optionTheme.buttonGroup.buttonClicked.connect(lambda button: self.toggleTheme(button))
        self.settingInterface.optionAccentColor.accentCombo.currentIndexChanged.connect(lambda index: self.settingInterface.optionAccentColor.selectButton.setEnabled(index == 1))
        self.settingInterface.widgetDef.optionMicaEffect.switchButton.checkedChanged.connect(lambda checked: self.setMicaEffectEnabled(checked))
        self.settingInterface.widgetDef.optionShowCommandBar.switchButton.checkedChanged.connect(lambda checked: (
            self.mybrowsInterface.myBrowsCommandBar.setVisible(checked),
            self.mybrowsInterface.actionCaption.setVisible(checked),
            self.mybrowsInterface.actionTable.setVisible(checked),
            self.mybrowsInterface.mybrowsAddCard.setHidden(checked),
            self.mybrowsInterface.mybrowsRefreshCard.setHidden(checked),
            self.mybrowsInterface.mybrowsLoadLinkCard.setHidden(checked),
            self.mybrowsInterface.myBrowsClearCard.setHidden(checked)
        ))
        self.settingInterface.advancedTempClean.button.clicked.connect(lambda: self.cleanTempFiles(self))
        self.settingInterface.advancedRestart.button.clicked.connect(self.confirmRestart)
        self.settingInterface.advancedStop.button.clicked.connect(self.confirmStop)
        self.aboutInterface.aboutVersion.button.clicked.connect(lambda: self.checkForUpdates(self))
        for button in self.snackButtons["Download"]:
            button.clicked.connect(lambda: self.browserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, True, self))
        for button in self.snackButtons["Install"]:
            button.setVisible(self.isUpdateDownloaded())
            button.setEnabled(self.isUpdateDownloaded())
            button.clicked.connect(lambda: self.runUpdate(self))
        self.themeCtrl.themeChanged.connect(lambda text: self.applyTheme(cfg.get(cfg.appTheme)))
        cfg.accentMode.valueChanged.connect(lambda value: (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.convertToRGB(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25)}}"),
            self.markdownViewer.updateSnack.setStyleSheet(f"#MDSnackBase {{background-color: rgba({smart.convertToRGB(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25)}}"),
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.convertToRGB(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25)}}"),
            self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.convertToRGB(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25); margin: 10px; border-radius: 5px}}")
        ))
        cfg.accentColor.valueChanged.connect(lambda value: (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.convertToRGB(value)}, 0.25)}}"),
            self.markdownViewer.updateSnack.setStyleSheet(f"#MDSnackBase {{background-color: rgba({smart.convertToRGB(value)}, 0.25)}}"),
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.convertToRGB(value)}, 0.25)}}"),
            self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.convertToRGB(value)}, 0.25); margin: 10px; border-radius: 5px}}")
        ))

    def createSubInterfaces(self):
        """ Initialize sub-interfaces when splash screen is enabled """
        loop = QEventLoop(self)
        QTimer.singleShot(cfg.get(cfg.splashDuration), loop.quit)
        loop.exec()
        self.mybrowsInterface = MyBrowsers(self)
        self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
        self.markdownViewer = MDView(self)
        self.addSubInterface(self.markdownViewer, segSVG.MARKDOWN, "Markdown Viewer")
        self.settingInterface = Settings(self)
        self.addSubInterface(self.settingInterface, FICO.SETTING, "Settings", NavigationItemPosition.BOTTOM)
        self.aboutInterface = About(self)
        self.addSubInterface(self.aboutInterface, FICO.INFO, "About", NavigationItemPosition.BOTTOM)

    def applyTheme(self, mode):
        """ Apply theme automatically according to system and config """
        if mode == "Auto":
            setTheme(Theme.DARK if smart.isDarkModeEnabled() else Theme.LIGHT)
        elif mode == "Dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        
        self.mybrowsInterface.mybrowsScroll.setStyleSheet(
            self.mybrowsInterface.darkSheetOnLight if theme() == Theme.LIGHT
            else self.mybrowsInterface.lightSheetOnDark
        )
        self.markdownViewer.subtitle.setStyleSheet("color: gray;")
        self.markdownViewer.mdContainer.setStyleSheet(f"""
            QWidget#Container {{
                background: transparent;
                border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                border-left: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                {f'border-bottom: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};'
                 if bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners)) else ""}
            }}
        """)
        self.aboutInterface.aboutCaption.setStyleSheet("color: gray;")
        self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{ background-color: rgba({smart.convertToRGB(themeColor())}, 0.25); }}")
        self.markdownViewer.updateSnack.setStyleSheet(f"#MDSnackBase {{ background-color: rgba({smart.convertToRGB(themeColor())}, 0.25); }}")
        self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{ background-color: rgba({smart.convertToRGB(themeColor())}, 0.25); }}")
        self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{ background-color: rgba({smart.convertToRGB(themeColor())}, 0.25); margin: 10px; border-radius: 5px; }}")

    def toggleTheme(self, button):
        """ Toggle the interface theme """
        if button.text() == "Use system setting":
            self.applyTheme("Auto")
        elif button.text() == "Dark":
            self.applyTheme("Dark")
        else:
            self.applyTheme(Theme.LIGHT)

    def checkForUpdates(self, parent):
        """Connect to the GitHub repository to check for the latest available update."""
        if self.updateCheckThread and self.updateCheckThread.isRunning():
            return

        self.lastChecked = self.aboutInterface.aboutVersion.contentLabel.text()
        self.aboutInterface.aboutVersion.iconLabel.setIcon(FICO.SYNC)
        self.aboutInterface.aboutVersion.setTitle("Checking for updates...")
        self.aboutInterface.aboutVersion.setContent("Please wait a moment...")
        self.aboutInterface.aboutVersion.button.setVisible(False)
        self.aboutInterface.aboutVersion.setEnabled(False)

        self.updateCheckThread = QThread(self)
        self.updateCheckWorker = UpdateCheckWorker()
        self.updateCheckWorker.moveToThread(self.updateCheckThread)

        self.updateCheckThread.started.connect(self.updateCheckWorker.run)
        self.updateCheckWorker.finished.connect(self.onUpdateCheckFinished)
        self.updateCheckWorker.error.connect(self.onUpdateCheckError)

        self.updateCheckWorker.finished.connect(lambda *_: self.updateCheckThread.quit()) # type: ignore
        self.updateCheckWorker.finished.connect(lambda *_: self.updateCheckWorker.deleteLater()) # type: ignore
        self.updateCheckThread.finished.connect(lambda *_: self.updateCheckThread.deleteLater()) # type: ignore

        self.updateCheckThread.start()

    def onUpdateCheckFinished(self, status, latestVersion, checkTime):
        self.aboutInterface.aboutVersion.iconLabel.setIcon(FICO.INFO)
        self.aboutInterface.aboutVersion.setTitle(f"Current version: {SmartLinkerVersion}")
        self.aboutInterface.aboutVersion.button.setVisible(True)
        self.aboutInterface.aboutVersion.setEnabled(True)

        if status == "offline":
            self.lastChecked = f"Last checked: {checkTime} (Failed to check for updates)"
            print(f"{Fore.YELLOW}Please check your internet connection, then try again...{Style.RESET_ALL}")
            smart.managerLog("WARNING: Unable to connect to the Internet...")
            smart.warningNotify("Warning, be careful!", "Please check your internet connection, then try again...", self)
            self.aboutInterface.aboutVersion.setContent(self.lastChecked)
            return

        self.latestVersion = latestVersion
        if not latestVersion:
            self.lastChecked = f"Last checked: {checkTime} (Failed to check for updates)"
            print(f"{Fore.YELLOW}No version tags have been found...{Style.RESET_ALL}")
            smart.managerLog("WARNING: No version tags have been found...")
            smart.warningNotify("Warning, be careful!", "The latest version could not be found...", self)

        elif Version(latestVersion) > Version(SmartLinkerVersion):
            self.lastChecked = f"Last checked: {checkTime} (Latest version: {latestVersion})"
            cfg.set(cfg.updateAvailable, True)
            cfg.set(cfg.updateVersion, latestVersion)
            self.confirmDownloadUpdate()
            self.aboutItem = self.navigationInterface.widget(self.aboutInterface.objectName())
            self.aboutIconBadge = IconInfoBadge.attension(
                FICO.SYNC,
                self.aboutItem.parent(),
                self.aboutItem,
                InfoBadgePosition.NAVIGATION_ITEM
            )
            self.mybrowsInterface.updateSnack.setVisible(True)
            self.mybrowsInterface.updateSnack.setEnabled(True)
            self.markdownViewer.updateSnack.setVisible(True)
            self.markdownViewer.updateSnack.setEnabled(True)
            self.settingInterface.updateSnack.setVisible(True)
            self.settingInterface.updateSnack.setEnabled(True)
            self.aboutInterface.updateSnack.setVisible(True)
            self.aboutInterface.updateSnack.setEnabled(True)
            print(f"{Fore.BLUE}The latest version of {SmartLinkerName} is now available: {latestVersion}{Style.RESET_ALL}")
            smart.managerLog(f"INFO: The latest version of {SmartLinkerName} is now available: {latestVersion}")

        else:
            self.lastChecked = f"Last checked: {checkTime}"
            cfg.set(cfg.updateAvailable, False)
            cfg.set(cfg.updateVersion, "")
            self.mybrowsInterface.updateSnack.setVisible(False)
            self.mybrowsInterface.updateSnack.setEnabled(False)
            self.markdownViewer.updateSnack.setVisible(False)
            self.markdownViewer.updateSnack.setEnabled(False)
            self.settingInterface.updateSnack.setVisible(False)
            self.settingInterface.updateSnack.setEnabled(False)
            self.aboutInterface.updateSnack.setVisible(False)
            self.aboutInterface.updateSnack.setEnabled(False)
            print(f"{Fore.BLUE}{SmartLinkerName} is currently up-to-date.{Style.RESET_ALL}")
            smart.managerLog(f"INFO: {SmartLinkerName} is currently up-to-date.")
            smart.infoNotify(f"{SmartLinkerName} is up-to-date", "This is currently the latest update available.", self)

        cfg.set(cfg.lastCheckedDate, checkTime)
        self.aboutInterface.aboutVersion.setContent(self.lastChecked)

        if self.updateDownloadDlg and self.updateDownloadDlg.exec():
            self.browserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, True, self)

    def onUpdateCheckError(self, message):
        self.aboutInterface.aboutVersion.iconLabel.setIcon(FICO.INFO)
        self.aboutInterface.aboutVersion.setTitle(f"Current version: {SmartLinkerVersion}")
        self.aboutInterface.aboutVersion.setContent(
            f"Last checked: {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')} (Failed to check for updates)"
        )
        self.aboutInterface.aboutVersion.button.setVisible(True)
        self.aboutInterface.aboutVersion.setEnabled(True)
        print(f"{Fore.RED}An error occurred while checking for updates: {message}{Style.RESET_ALL}")
        smart.managerLog(f"ERROR: Failed while checking for updates: {message}")
        smart.errorNotify("Oops! Something went wrong...", f"An error occurred while checking for updates: {message}", self)

    def confirmDeleteDialog(self, name: str, parent):
        """ Open a confirmation dialog to remove a browser from the SmartList """
        self.deleteDlg = MessageBox(
            f"Delete {name}",
            f"Do you really want to remove {name} from your SmartList?\n" \
                "This action is irreversible.",
            parent
        )
        self.deleteDlg.yesButton.setText("Delete")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if self.deleteDlg.exec():
            print(f"Prnding operation: Removing {name} from the SmartList...")
            smart.managerLog(f"Removing {name} from the SmartList...")
            myBrowsList = smart.loadBrowsers()
            baseCount = len(myBrowsList["MyBrowsers"])
            updatedList = {"MyBrowsers": [browser for browser in myBrowsList["MyBrowsers"] if browser["name"] != name]}
            if len(updatedList) == baseCount:
                print(f"{Fore.YELLOW}WARNING!! {name} cannot be found, failed to remove from your SmartList...{Style.RESET_ALL}")
                smart.managerLog(f"WARNING: {name} cannot be found, unable to proceed to its removal from the SmartList...")
                smart.warningNotify("Warning, be careful!", f"{name} cannot be found, failed to remove from your SmartList...", self)
                return
            if cfg.get(cfg.mainBrowser):
                if cfg.get(cfg.mainBrowser) == name:
                    cfg.set(cfg.mainBrowser, "")
                    cfg.set(cfg.mainBrowserPath, "")
                    cfg.set(cfg.mainBrowserIsManual, False)
                    self.settingInterface.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(False)
                    self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(FICO.APPLICATION)
                    self.settingInterface.widgetDef.optionMainBrowserCard.titleLabel.setText("Configure your main browser")
                    self.settingInterface.widgetDef.optionMainBrowserCard.contentLabel.setText("You can either set a browser from your storage or SmartList as your main browser if no one is running.")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromListToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromListToolTip)
            print("Saving the updated browsers database...")
            smart.managerLog(f"{name} has been removed. Updating the browsers database...")
            smart.writeBrowsers(updatedList)
            self.mybrowsInterface.refreshBrowsers(self)
            print(f"{Fore.GREEN}{name} has been successfully removed from your SmartList!{Style.RESET_ALL}")
            smart.managerLog(f"SUCCESS: {name} has been successfully removed from the SmartList.")
            smart.successNotify("Removal complete!", f"{name} has been successfully removed from your SmartList!", self)

    def confirmDownloadUpdate(self):
        """ Open a confirmation dialog to download the latest update from GitHub """
        if not self.updateDownloadDlg:
            self.updateDownloadDlg = MessageBox(
                "Yahoo! We just found an update!",
                f"An updated version of {SmartLinkerName} has been published and is currently available for download.\n" \
                f"If you proceed, you will be redirected to the releases page of {SmartLinkerName}'s official GitHub repository. " \
                 "But you can still do it later if you prefer.\nSo, what do you choose to do?\n\n" \
                f"Current version:\t{SmartLinkerVersion}\nLatest version found:\t{self.latestVersion}",
                self
            )
            self.updateDownloadDlg.yesButton.setText("Download from GitHub releases")
            self.updateDownloadDlg.cancelButton.setText("Update later")
        self.updateDownloadDlg.show()
        if cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.infoSFXPath): smart.playSound(soundStreamer, cfg.get(cfg.infoSFXPath), "update confirmation dialog")

    def browserSelect(self, url: str, title: str, linkType: str, icon: QIcon | FICO | FluentFontIconBase, isDownload: bool, parent):
        """ Open a dialog to select the browser you would want to load a link into """
        if not self.browserDlg:
            self.browserDlg = BrowserSelectDialog(f"Open {title} with...", icon, isDownload, parent)
        else:
            self.browserDlg = None
            self.browserDlg = BrowserSelectDialog(f"Open {title} with...", icon, isDownload, parent)
        self.browserDlg.yesButton.setText(f"Open {title}")
        self.browserDlg.downloadButton.clicked.connect(lambda checked: (
            self.browserDlg.close() if self.browserDlg else None,
            self.downloadDialog(parent) if isDownload else None
        ))
        if isDownload:
            for button in self.snackButtons["Install"]:
                button.setVisible(self.isUpdateDownloaded())
                button.setEnabled(self.isUpdateDownloaded())
        if self.browserDlg.exec():
            failedAttempts = 0
            if not self.browserDlg.browserCombo.currentText() == "Other browser":
                print(f"Opening the {title} {linkType} into {self.browserDlg.browserCombo.currentText()}...")
                smart.managerLog(f"Opening the {title} {linkType} into {self.browserDlg.browserCombo.currentText()}...")
                for browser in self.myBrowsers["MyBrowsers"]:
                    if browser["name"] == self.browserDlg.browserCombo.currentText():
                        if browser["path"]:
                            try:
                                subprocess.Popen([browser["path"], url])
                                print(f"{Fore.GREEN}The {title} {linkType} has been successfully loaded into {browser["name"]}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: The {title} {linkType} has been successfully loaded into {browser["name"]}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the {title} {linkType} into {browser["name"]}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to open the {title} {linkType} into {browser["name"]}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while opening the {title} {linkType} into {browser["name"]}: {e}")
                            break
                        else:
                            smart.warningNotify("Warning, be careful!", f"The path to {browser["name"]} as registered in your SmartList is empty...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The path to {browser["name"]} as registered in your SmartList is empty...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The path to {browser["name"]} as registered in the SmartList is empty...")
                            break
                    elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                        if os.path.basename(cfg.get(cfg.mainBrowserPath)) == self.browserDlg.browserCombo.currentText():
                            try:
                                subprocess.Popen([cfg.get(cfg.mainBrowserPath), url])
                                print(f"{Fore.GREEN}The {title} {linkType} has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: The {title} {linkType} has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the {title} {linkType} into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to open the {title} {linkType} into {cfg.get(cfg.mainBrowserPath)}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while opening the {title} {linkType} into {cfg.get(cfg.mainBrowserPath)}: {e}")
                            break
                    else:
                        failedAttempts += 1
                        if failedAttempts == self.browserDlg.browserCombo.count():
                            smart.warningNotify("Warning, be careful!", f"The name '{self.browserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.browserDlg.browserCombo.currentText()} cannot be found in your SmartList...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The name '{self.browserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.browserDlg.browserCombo.currentText()} cannot be found in your SmartList...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The name '{self.browserDlg.browserCombo.currentText()}' is not registered into the SmartList, or {self.browserDlg.browserCombo.currentText()} cannot be found in the SmartList...")
            else:
                print(f"Opening the {title} {linkType} into {os.path.basename(self.browserDlg.otherBrowsEdit.text())}...")
                smart.managerLog(f"Opening the {title} {linkType} into {os.path.basename(self.browserDlg.otherBrowsEdit.text())}...")
                try:
                    subprocess.Popen([self.browserDlg.otherBrowsEdit.text(), url])
                    print(f"{Fore.GREEN}The {title} {linkType} has been successfully loaded into another browser: '{self.browserDlg.otherBrowsEdit.text()}'{Style.RESET_ALL}")
                    smart.managerLog(f"SUCCESS: The {title} {linkType} has been successfully loaded into other browser '{self.browserDlg.otherBrowsEdit.text()}'")
                except Exception as e:
                    smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the {title} {linkType} into {os.path.basename(self.browserDlg.otherBrowsEdit.text())}: {e}", parent)
                    print(f"{Fore.RED}An error occured while attempting to open the {title} {linkType} into '{os.path.basename(self.browserDlg.otherBrowsEdit.text())}': {e}{Style.RESET_ALL}")
                    smart.managerLog(f"ERROR: Failed to open the {title} {linkType} into browser at path '{self.browserDlg.otherBrowsEdit.text()}': {e}")

    def downloadDialog(self, parent):
        filename = smart.resourcePath(".temp\\SmartLinkerUpdate.exe")
        
        downloadDlg = DownloadDialog(
            "Initializing...",
            FICO.DOWNLOAD,
            f"{SmartLinkerGitRepoURL}/releases/download/{cfg.get(cfg.updateVersion)}/SmartLinker-setup-win-{cfg.get(cfg.updateVersion)[1:]}.exe",
            filename,
            parent
        )
        if downloadDlg.exec():
            downloadSize = 0
            if os.path.exists(filename):
                if os.path.exists(smart.resourcePath(".temp\\.metadata")):
                    with open(smart.resourcePath(".temp\\.metadata"), "rb") as metaReader:
                        downloadSize = pickle.load(metaReader)
                    if os.path.getsize(filename) == downloadSize:
                        print(f"{Fore.BLUE}Opening the downloaded installer at path: '{filename}'...{Style.RESET_ALL}")
                        smart.managerLog(f"INFO: Opening the downloaded installer at path: {filename}...")
                        try:
                            subprocess.Popen([filename])
                            smart.stopApp()
                        except Exception as e:
                            print(f"{Fore.RED}An error occured while attempting to launch the installer at path '{filename}': {e}{Style.RESET_ALL}")
                            smart.managerLog(f"ERROR: Failed to launch the installer at path '{filename}': {e}")
                            smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to launch the installer: {e}", parent)
                    else:
                        print(f"{Fore.YELLOW}The update installer has not been correctly downloaded... Please try again...{Style.RESET_ALL}")
                        smart.managerLog("WARNING: The update installer has not been correctly downloaded...")
                        smart.warningNotify("Warning, be careful!", "The update installer has not been correctly downloaded... Please try again...", parent)
            else:
                print(f"{Fore.YELLOW}The update installer does not exist... Please try again...{Style.RESET_ALL}")
                smart.managerLog("WARNING: The update installer does not exist...")
                smart.warningNotify("Warning, be careful!", "The update installer does not exist... Please try again...", parent)

    def cleanTempFiles(self, parent):
        """ Clean temporary files left over by SmartLinker in the Settings """
        if os.path.exists(smart.resourcePath(".temp")):
            try:
                shutil.rmtree(smart.resourcePath(".temp"))
                for button in self.snackButtons["Install"]:
                    if button.isVisible():
                        button.setVisible(False)
                        button.setEnabled(False)
                print(f"{Fore.GREEN}Temporary files have been successfully cleaned!{Style.RESET_ALL}")
                smart.managerLog("SUCCESS: Temporary files successfully cleaned!")
                smart.successNotify("Clean complete!", "All temporary files have been successfully removed.", parent)
            except Exception as e:
                print(f"{Fore.RED}Error cleaning temporary files: {e}{Style.RESET_ALL}")
                smart.managerLog(f"ERROR: Failed to clean temporary files: {e}")
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to clean temporary files: {e}", parent)
        else:
            print(f"{Fore.BLUE}There are no temporary files to be removed...{Style.RESET_ALL}")
            smart.managerLog("INFO: No temporary files to be removed")
            smart.infoNotify("No temporary files", "There are no temporary files to be removed...", parent)

    def isUpdateDownloaded(self) -> bool:
        if not (os.path.exists(smart.resourcePath(".temp\\SmartLinkerUpdate.exe")) and os.path.exists(smart.resourcePath(".temp\\.metadata"))):
            return False
        
        with open(smart.resourcePath(".temp\\.metadata"), "rb") as metaReader: metaSize = pickle.load(metaReader)
        if not metaSize == os.path.getsize(smart.resourcePath(".temp\\SmartLinkerUpdate.exe")):
            return False
        
        return True

    def runUpdate(self, parent):
        print(f"Opening the latest update installer...\nUpdate installer path: {Fore.BLUE}[{smart.resourcePath(".temp\\SmartLinkerUpdate.exe")}]{Style.RESET_ALL}")
        smart.managerLog(f"Opening the latest update installer at path: [{smart.resourcePath(".temp\\SmartLinkerUpdate.exe")}]...")
        try:
            subprocess.Popen(smart.resourcePath(".temp\\SmartLinkerUpdate.exe"))
            smart.stopApp()
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to run the update installer: {e}{Style.RESET_ALL}")
            smart.managerLog(f"ERROR: Failed while attempting to run the update installer: {e}")
            smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to run the update installer: {e}", parent)

    def confirmRestart(self):
        """ Open a confirmation dialog to restart SmartLinker """
        restartDlg = MessageBox(
            "Restart confirmation",
            "Are you sure you really want to restart SmartLinker?",
            self
        )
        restartDlg.yesButton.setText(f"Restart {SmartLinkerName}")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if restartDlg.exec():
            try: smart.restartAppPlus()
            except Exception as e:
                print(f"{Fore.RED}An error occured while trying to restart the app: {e}{Style.RESET_ALL}")
                smart.managerLog(f"ERROR: Failed to restart the app: {e}")
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to restart SmartLinker: {e}", self)
    
    def confirmStop(self):
        """ Open a confirmation dialog to stop SmartLinker process """
        stopDlg = MessageBox(
            "Quit confirmation",
            f"Are you sure you really want to quit {SmartLinkerName}?",
            self
        )
        stopDlg.yesButton.setText(f"Quit {SmartLinkerName}")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if stopDlg.exec():
            try: smart.stopApp()
            except Exception as e:
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to close SmartLinker: {e}", self)
                print(f"{Fore.RED}An error occured while attempting to stop process: {e}{Style.RESET_ALL}")
                smart.managerLog(f"ERROR: Failed to stop process: {e}")

    def closeEvent(self, e):
        super().closeEvent(e)
        if isinstance(self.settingInterface.selectorWindow, SmartSelectorGUI):
            self.settingInterface.selectorWindow.close()
            self.settingInterface.selectorWindow = None

def isSystemCompatible(minBuild: int) -> bool:
    isCompatible = False
    try:
        if not platform.system() == "Windows": isCompatible = False
        else: isCompatible = sys.getwindowsversion().build >= minBuild 
    except Exception as e:
        print(f"{Fore.RED}An error occured while attempting to check system compatibility: {e}{Style.RESET_ALL}")
        smart.managerLog(f"ERROR: Failed to check system compatibility: {e}")
    finally: return isCompatible

# =============================================================================

def smartMain():
    """ Main entry point of the application """

    QCoreApplication.setOrganizationName(SmartLinkerOwner)
    QCoreApplication.setApplicationName(SmartLinkerName)
    QCoreApplication.setApplicationVersion(SmartLinkerVersion)
    
    # Basic platform / compatibility checks before attempting any GUI or CLI handling
    if not platform.system() == "Windows":
        print(f"{Fore.RED}CRITICAL: Only Windows systems are supported by {SmartLinkerName}...\nThe software process is stopping...{Style.RESET_ALL}")
        sys.exit()
    if not isSystemCompatible(19042):
        print(f"{Fore.RED}CRITICAL: {smart.getSystemInformation()["osName"]} {smart.getSystemInformation()["osVersion"]} build {smart.getSystemInformation()["osBuildNumber"]}"
            f" is not supported by {SmartLinkerName}...\nThe software process is stopping...{Style.RESET_ALL}")
        sys.exit()

    # If command-line arguments provided, hand them to ArgumentsProcessor first.
    # Show the SmartSelector GUI only when the parsed command is 'load' and
    # both smart_list and external_browser are not provided (i.e. user expects selector).
    if len(sys.argv) > 1:
        if ArgumentsProcessor is None:
            # Could not import the CLI handler; fall back to opening SmartLinker GUI
            app = QApplication(sys.argv)
            appWindow = SmartLinkerGUI(sys.argv[1:])
            appWindow.show()
            sys.exit(app.exec())

        if "load" not in sys.argv and "core" not in sys.argv:
            newArgs = sys.argv
            newArgs.insert(1, "load")
            sys.argv = newArgs

        try: proc = ArgumentsProcessor().args
        except SystemExit: # argparse may call SystemExit after printing help or on error; stop here
            return
        
        if proc.cmd == "load" and not proc.smart_list and not proc.external_browser:
            app = QApplication(sys.argv)
            appWindow = SmartSelectorGUI(sys.argv[1:])
            sys.exit(app.exec())

        # Other CLI commands were handled by ArgumentsProcessor (or nothing to do) -> exit
        return

    # No arguments: start the main GUI
    app = QApplication(sys.argv)
    appWindow = SmartLinkerGUI()
    appWindow.show()
    sys.exit(app.exec())

# =============================================================================

if __name__ == "__main__":
    smartMain()
