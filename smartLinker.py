from utils.SmartUtils import *
from utils.settingsInterface import SettingsInterface as Settings
from utils.mybrowsersInterface import MyBrowsersInterface as MyBrowsers
from utils.aboutInterface import AboutInterface as About, BrowserSelectDialog
from utils.smartSelector import SmartSelectorGUI

# =============================================================================

class SmartLinkerGUI(FluentWindow):
    """ Class for the SmartLinker Manager (main) window """

    def __init__(self, parent=None):
        super().__init__(parent)
        print(smart.consoleScript())
        self.setWindowTitle("SmartLinker - Mastering URL Handling")
        self.setWindowIcon(QIcon(smart.resourcePath("resources/images/icons/icon.ico")))
        self.resize(1100, 700)
        self.setMinimumWidth(1040)
        self.move(40, 25)
        self.setStyleSheet('font-family: "Segoe UI Variable", "Segoe UI", sans-serif;')
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        smart.emptyManagerLog()

        self.latestVersion = smart.getLatestVersionTag() if bool(cfg.get(cfg.checkUpdatesOnStart) and smart.checkConnectivity()) else ""
        self.myBrowsers = smart.loadBrowsers()
        self.removeKeysDlg = None
        self.listSelectDlg = None
        self.aboutIconBadge = None
        self.updateDownloadDlg = None
        self.updateCheckToolTip = None
        self.browserDlg = None

        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.startupSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.startupSFXPath), "startup")
        if bool(cfg.get(cfg.showSplash)):
            self.splash = SplashScreen(smart.resourcePath("resources/images/icons/icon_splash.ico"), self)
            self.splash.setIconSize(QSize(125, 125))
            self.show()
            self.createSubInterfaces()
            self.splash.finish()
        else:
            self.mybrowsInterface = MyBrowsers(self)
            self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
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
        
        self.mybrowsInterface.updateSnackButton.clicked.connect(lambda: self.browserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, self))
        if self.settingInterface.widgetDef.optionMicaEffect:
            self.settingInterface.widgetDef.optionMicaEffect.setEnabled(smart.isSoftwareCompatible(22000))
            self.settingInterface.widgetDef.optionMicaEffect.setVisible(smart.isSoftwareCompatible(22000))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.clicked.connect(lambda: self.settingInterface.cardManualSelect(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.clicked.connect(lambda: self.settingInterface.cardSetFromList(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.removeMainButton.clicked.connect(lambda: self.settingInterface.cardRemove(self))
        self.settingInterface.widgetDef.optionTheme.buttonGroup.buttonClicked.connect(lambda button: self.toggleTheme(button))
        self.settingInterface.optionAccentColor.accentCombo.currentTextChanged.connect(lambda text: self.settingInterface.optionAccentColor.selectButton.setEnabled(bool(text == "Custom accent color")))
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
        self.settingInterface.advancedRestart.button.clicked.connect(self.confirmRestart)
        self.settingInterface.advancedStop.button.clicked.connect(self.confirmStop)
        self.settingInterface.updateSnackButton.clicked.connect(lambda: self.browserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, self))
        self.aboutInterface.aboutVersion.button.clicked.connect(lambda: self.checkForUpdates(self))
        cfg.appTheme.valueChanged.connect(lambda value: (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.getRed(themeColor())}, {smart.getGreen(themeColor())}, {smart.getBlue(themeColor())}, 0.25)}}"), # type: ignore
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.getRed(themeColor())}, {smart.getGreen(themeColor())}, {smart.getBlue(themeColor())}, 0.25)}}"), # type: ignore
            self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.getRed(themeColor())}, {smart.getGreen(themeColor())}, {smart.getBlue(themeColor())}, 0.25); margin: 10px; margin-top: 0; border-radius: 5px}}"), # type: ignore
            """ self.aboutInterface.aboutResources.pyQtLabel.setTextColor(themeColor(), cfg.get(cfg.accentColor) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor()),
            self.aboutInterface.aboutResources.qFluentLabel.setTextColor(themeColor(), cfg.get(cfg.accentColor) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor()),
            self.aboutInterface.aboutResources.flaticonLabel.setTextColor(themeColor(), cfg.get(cfg.accentColor) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor()) """
        ))
        cfg.accentMode.valueChanged.connect(lambda value: (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.getRed(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getGreen(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getBlue(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25)}}"),
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.getRed(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getGreen(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getBlue(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25)}}"),
            self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.getRed(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getGreen(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, {smart.getBlue(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor())}, 0.25); margin: 10px; margin-top: 0; border-radius: 5px}}"),
            """ self.aboutInterface.aboutResources.pyQtLabel.setTextColor(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor(), cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor()),
            self.aboutInterface.aboutResources.qFluentLabel.setTextColor(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor(), cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor()),
            self.aboutInterface.aboutResources.flaticonLabel.setTextColor(cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor(), cfg.get(cfg.accentColor) if value == "Custom" else getSystemAccentColor()) """
        ))
        cfg.accentColor.valueChanged.connect(lambda value: (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.getRed(value)}, {smart.getGreen(value)}, {smart.getBlue(value)}, 0.25)}}"),
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.getRed(value)}, {smart.getGreen(value)}, {smart.getBlue(value)}, 0.25)}}"),
            self.aboutInterface.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.getRed(value)}, {smart.getGreen(value)}, {smart.getBlue(value)}, 0.25); margin: 10px; margin-top: 0; border-radius: 5px}}"),
            """ self.aboutInterface.aboutResources.pyQtLabel.setTextColor(QColor(value), QColor(value)),
            self.aboutInterface.aboutResources.qFluentLabel.setTextColor(QColor(value), QColor(value)),
            self.aboutInterface.aboutResources.flaticonLabel.setTextColor(QColor(value), QColor(value)) """
        ))

    def createSubInterfaces(self):
        """ Initialize sub-interfaces when splash screen is enabled """
        loop = QEventLoop(self)
        QTimer.singleShot(cfg.get(cfg.splashDuration), loop.quit)
        loop.exec()
        self.mybrowsInterface = MyBrowsers(self)
        self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
        self.settingInterface = Settings(self)
        self.addSubInterface(self.settingInterface, FICO.SETTING, "Settings", NavigationItemPosition.BOTTOM)
        self.aboutInterface = About(self)
        self.addSubInterface(self.aboutInterface, FICO.INFO, "About", NavigationItemPosition.BOTTOM)

    def toggleTheme(self, button):
        """ Toggle the interface theme """
        if button.text() == "Use system setting":
            setTheme(Theme.AUTO)
            self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath("resources/images/icons/icon_outline_black.ico"))) if not smart.isDarkModeEnabled() \
            else self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath("resources/images/icons/icon_outline.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.lightSheetOnDark if smart.isDarkModeEnabled() else self.mybrowsInterface.darkSheetOnLight)
        elif button.text() == "Dark":
            setTheme(Theme.DARK)
            self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath("resources/images/icons/icon_outline.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.lightSheetOnDark)
        else:
            setTheme(Theme.LIGHT)
            self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath("resources/images/icons/icon_outline_black.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.darkSheetOnLight)

    def checkForUpdates(self, parent):
        """ Connect to the GitHub repository to check for the latest available update """
        self.lastChecked = self.aboutInterface.aboutVersion.contentLabel.text()
        self.aboutInterface.aboutVersion.iconLabel.setIcon(FICO.SYNC)
        self.aboutInterface.aboutVersion.setTitle("Checking for updates...")
        self.aboutInterface.aboutVersion.setContent("Please wait a moment...")
        self.aboutInterface.aboutVersion.button.setVisible(False)
        self.aboutInterface.aboutVersion.setEnabled(False)
        isConnected = smart.checkConnectivity()
        if isConnected:
            self.latestVersion = smart.getLatestVersionTag()
            checkTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            
            if not self.latestVersion:
                self.lastChecked = f"Last checked: {checkTime} (Failed to check for updates)"
                print(f"{Fore.YELLOW}No version tags have been found...{Style.RESET_ALL}")
                smart.managerLog("WARNING: No version tags have been found...")
                smart.warningNotify("Warning, be careful!", "The latest version could not be found...", self)
            
            elif Version(self.latestVersion) > Version(SmartLinkerVersion):
                self.lastChecked = f"Last checked: {checkTime} (Latest version: {self.latestVersion})"
                cfg.set(cfg.updateAvailable, True)
                cfg.set(cfg.updateVersion, self.latestVersion)
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
                self.settingInterface.updateSnack.setVisible(True)
                self.settingInterface.updateSnack.setEnabled(True)
                self.aboutInterface.updateSnack.setVisible(True)
                self.aboutInterface.updateSnack.setEnabled(True)
                print(f"{Fore.BLUE}The latest version of {SmartLinkerName} is now available: {self.latestVersion}{Style.RESET_ALL}")
                smart.managerLog(f"INFO: The latest version of {SmartLinkerName} is now available: {self.latestVersion}")
            
            else:
                self.lastChecked = f"Last checked: {checkTime}"
                cfg.set(cfg.updateAvailable, False)
                cfg.set(cfg.updateVersion, "")
                self.mybrowsInterface.updateSnack.setVisible(False)
                self.mybrowsInterface.updateSnack.setEnabled(False)
                self.settingInterface.updateSnack.setVisible(False)
                self.settingInterface.updateSnack.setEnabled(False)
                self.aboutInterface.updateSnack.setVisible(False)
                self.aboutInterface.updateSnack.setEnabled(False)
                print(f"{Fore.BLUE}{SmartLinkerName} is currently up-to-date.{Style.RESET_ALL}")
                smart.managerLog(f"INFO: {SmartLinkerName} is currently up-to-date.")
                smart.infoNotify(f"{SmartLinkerName} is up-to-date", "This is currently the latest update available.", self)

            cfg.set(cfg.lastCheckedDate, checkTime)
        else:
            print(f"{Fore.YELLOW}Please check your internet connection, then try again...{Style.RESET_ALL}")
            smart.managerLog("WARNING: Unable to connect to the Internet...")
            smart.warningNotify("Warning, be careful!", "Please check your internet connection, then try again...", self)
        self.aboutInterface.aboutVersion.iconLabel.setIcon(FICO.INFO)
        self.aboutInterface.aboutVersion.setTitle(f"Current version: {SmartLinkerVersion}")
        self.aboutInterface.aboutVersion.setContent(self.lastChecked)
        self.aboutInterface.aboutVersion.button.setVisible(True)
        self.aboutInterface.aboutVersion.setEnabled(True)
        if self.updateDownloadDlg and self.updateDownloadDlg.exec():
            # print(f'Opening GitHub releases page with link: "{SmartLinkerGitRepoURL}/releases"...')
            # smart.managerLog(f'Opening GitHub releases page with link: "{SmartLinkerGitRepoURL}/releases"...')
            # webbrowser.open(f"{SmartLinkerGitRepoURL}/releases")
            self.browserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, self)

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
        smart.playSound(soundStreamer, cfg.get(cfg.infoSFXPath), "update confirmation dialog")

    def browserSelect(self, url: str, title: str, linkType: str, icon: QIcon | FICO | FluentFontIconBase, parent):
        """ Open a dialog to select the browser you would want to load a link into """
        if not self.browserDlg:
            self.browserDlg = BrowserSelectDialog(f"Open {title} with...", icon, parent)
        else:
            self.browserDlg = None
            self.browserDlg = BrowserSelectDialog(f"Open {title} with...", icon, parent)
        self.browserDlg.yesButton.setText(f"Open {title}")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName(SmartLinkerOwner)
    app.setApplicationName(SmartLinkerName)
    app.setApplicationVersion(SmartLinkerVersion)
    if not platform.system() == "Windows":
        print(f"{Fore.RED}CRITICAL: Only Windows systems are supported by {SmartLinkerName}...\nThe software process is stopping...{Style.RESET_ALL}")
        sys.exit()
    if not isSystemCompatible(19042):
        print(f"{Fore.RED}CRITICAL: {smart.getSystemInformation()["osName"]} {smart.getSystemInformation()["osVersion"]} build {smart.getSystemInformation()["osBuildNumber"]}" \
            f" is not supported by {SmartLinkerName}...\nThe software process is stopping...{Style.RESET_ALL}")
        sys.exit()
    if len(sys.argv) > 1: appWindow = SmartSelectorGUI(sys.argv[1:])
    else:
        appWindow = SmartLinkerGUI()
        appWindow.show()
    sys.exit(app.exec())