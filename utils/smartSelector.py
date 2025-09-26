from utils.SmartUtils import *

# ===========================================================================================================

myBrowsList = smartLoadBrowsers()
if len(sys.argv) > 1: requestURL = sys.argv[1]
setThemeColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))

class CustomTitleBar(TitleBar):
    """ Custom title bar """

    def __init__(self, parent):
        super().__init__(parent)

        """ Can only be used with StandardTitleBar
        self.iconLabel.hide()
        self.titleLabel.hide() """
        self.maxBtn.hide()
        self._isDoubleClickEnabled = False

        # customize the style of title bar button
        self.minBtn.setNormalColor((QColor("white" if smartIsDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.closeBtn.setNormalColor((QColor("white" if smartIsDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        # self.minBtn.setHoverColor()
        self.minBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))
        self.minBtn.setPressedColor(QColor("white"))
        # self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.closeBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))

        # use qss to customize title bar button
        """ self.maxBtn.setStyleSheet(
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        ) """

class SmartSelectorGUI(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        print(smartConsoleScript())
        self.lightSheetOnDark: str = "SingleDirectionScrollArea {background-color: rgba(242, 242, 242, 0.05); border: 1px solid rgba(242, 242, 242, 0.25)}"
        self.darkSheetOnLight: str = "SingleDirectionScrollArea {background-color: rgba(32, 32, 32, 0.05); border: 1px solid rgba(32, 32, 32, 0.25)}"
        self.runningBrowsers = 0
        smartEmptySelectorLog()
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon(smartResourcePath("resources/images/icons/icon.ico")))
        self.setWindowTitle("Smart Selector | SmartLinker")
        self.setStyleSheet(("background: white" if not smartIsDarkMode() else "") if cfg.get(cfg.appTheme) == "Auto" else
                           "" if cfg.get(cfg.appTheme) == "Dark" else "background: white")
        self.titleHeight = self.titleBar.height()
        self.setMinimumSize(750, 550)
        self.bottomLightSheet: str = "background-color: #F3F3F3; border: 1px solid #E5E5E5"
        self.bottomDarkSheet: str = "background-color: #161616; border: 1px solid #000000" # original: #202020, #1D1D1D

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, self.titleHeight, 0, 0)
        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(80, 0, 80, 0)
        mainTitleLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addLayout(mainTitleLine)
        mainIcon = IconWidget(QIcon(smartResourcePath("resources/images/icons/icon.ico")))
        mainIcon.setFixedSize(56, 56)
        mainTitleLine.addWidget(mainIcon)
        mainTitleBox = QVBoxLayout()
        mainTitleBox.setContentsMargins(10, 20, 0, 20)
        mainTitleLine.addLayout(mainTitleBox)
        mainTitleBox.addWidget(TitleLabel("New URL loading request detected!"))
        self.mainSubtitle = CaptionLabel(f"Which browser do you want to load '{requestURL}' into?")
        self.mainSubtitle.setStyleSheet("color: gray")
        mainTitleBox.addWidget(self.mainSubtitle)
        mainScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainScroll.setWidgetResizable(True)
        mainScroll.setContentsMargins(0, 0, 0, 0)
        mainScroll.enableTransparentBackground()
        mainLayout.addWidget(mainScroll)
        mainScrollContent = QWidget()
        mainScroll.setWidget(mainScrollContent)
        mainScrollContent.setContentsMargins(40, 0, 40, 0)
        layout = QVBoxLayout(mainScrollContent)
        layout.setSpacing(10)

        # List of opened SmartList browsers
        self.myBrowsScroll = SingleDirectionScrollArea(self, Qt.Orientation.Horizontal)
        self.myBrowsScroll.setWidgetResizable(True)
        self.myBrowsScroll.setContentsMargins(0, 0, 0, 0)
        self.myBrowsScroll.setStyleSheet(self.lightSheetOnDark if theme() == Theme.DARK else self.darkSheetOnLight)
        layout.addWidget(self.myBrowsScroll)
        self.myBrowsScrollContent = QWidget()
        self.myBrowsScroll.setWidget(self.myBrowsScrollContent)
        self.myBrowsLayout = QHBoxLayout(self.myBrowsScrollContent)
        self.myBrowsLayout.setSpacing(10)
        self.myBrowsEmptyMsg = BodyLabel("No web browsers have been added yet... You can still load your URL into a browser selected from your storage.")
        self.myBrowsEmptyMsg.setContentsMargins(0, 30, 0, 30)
        self.myBrowsEmptyMsg.setWordWrap(True)
        self.myBrowsEmptyMsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        print("\n=============================\n" \
              "Scanning running processes...\n" \
              "=============================\n")
        smartSelectorLog("Scanning running browsers...")
        if myBrowsList["MyBrowsers"]:
            for browser in myBrowsList["MyBrowsers"]:
                print(f"Browser in queue: {os.path.basename(browser["path"])}\n" \
                       "------------------------------------")
                smartSelectorLog(f"Browser in queue: {os.path.basename(browser["path"])}")
                if smartIsBrowserOpen(browser["path"]):
                    self.isRunning = True
                    self.runningBrowsers += 1
                    smartSelectorLog(f"'{os.path.basename(browser["path"])}' is running.")
                else:
                    self.isRunning = False
                    smartSelectorLog(f"'{os.path.basename(browser["path"])}' is not running.")
                browsCard = BrowserCard(
                    smartGetFileIcon(browser["path"]),
                    browser["name"],
                    "Running" if self.isRunning else "",
                    self
                )
                # browsCard.clicked.connect(lambda checked, name=browser["name"], reqURL=requestURL: self.cardSelect(name, reqURL))
                self.myBrowsLayout.addWidget(browsCard)
        if (cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual)):
            print(f"Browser in queue: {os.path.basename(cfg.get(cfg.mainBrowserPath))}\n" \
                   "------------------------------------")
            smartSelectorLog(f"Browser in queue: {os.path.basename(cfg.get(cfg.mainBrowserPath))}")
            if smartIsBrowserOpen(cfg.get(cfg.mainBrowserPath)):
                self.isRunning = True
                self.runningBrowsers += 1
            else: self.isRunning = False
            browsCard = BrowserCard(
                smartGetFileIcon(cfg.get(cfg.mainBrowserPath)),
                os.path.basename(cfg.get(cfg.mainBrowserPath)),
                "Manual - Running" if self.isRunning else "Manual",
                self
            )
            # browsCard.clicked.connect(lambda checked, name=browser["name"], reqURL=requestURL: self.cardSelect(name, reqURL))
            self.myBrowsLayout.addWidget(browsCard)
        if not myBrowsList["MyBrowsers"] and not cfg.get(cfg.mainBrowserPath): self.myBrowsLayout.addWidget(self.myBrowsEmptyMsg, 0, Qt.AlignmentFlag.AlignCenter)
        print("-----------------------------------------------------\n" \
             f"{self.runningBrowsers} browser{"s are" if self.runningBrowsers != 1 else " is"} actually running.\n" \
             f"{"NOTE: They may be the same browser.\n" if self.runningBrowsers > 1 else ""}" \
              "-----------------------------------------------------\n")
        smartSelectorLog(f"Scanning running browsers terminated. {self.runningBrowsers} browser{"s are" if self.runningBrowsers != 1 else " is"} actually running{" (they may be the same browser)" if self.runningBrowsers > 1 else ""}.")
        
        layout.addStretch(1)

        layout.addSpacing(10)
        layout.addWidget(BodyLabel("If you ever want to choose another browser from your storage, this is the easiest way:"))
        otherBrowserLine = QHBoxLayout()
        otherBrowserLine.setContentsMargins(0, 0, 0, 0)
        otherBrowserLine.setSpacing(10)
        layout.addLayout(otherBrowserLine)
        self.otherBrowsPathEdit = LineEdit()
        self.otherBrowsPathEdit.setPlaceholderText("Other browser path")
        self.otherBrowsPathEdit.setClearButtonEnabled(True)
        self.otherBrowsPathEdit.textChanged.connect(lambda text: self.otherBrowsLoad.setEnabled(bool(text)))
        otherBrowserLine.addWidget(self.otherBrowsPathEdit)
        self.otherBrowsPathBrowse = ToolButton(FICO.FOLDER)
        self.otherBrowsPathBrowse.setToolTip("Browse...")
        self.otherBrowsPathBrowse.installEventFilter(ToolTipFilter(self.otherBrowsPathBrowse))
        self.otherBrowsPathBrowse.clicked.connect(lambda: self.otherBrowsPathEdit.setText(smartBrowseFileDialog(self, "Select a browser to load the link into", "", "Executables (*.exe)")))
        otherBrowserLine.addWidget(self.otherBrowsPathBrowse)
        self.otherBrowsLoad = PushButton(FICO.LINK, "Load link")
        self.otherBrowsLoad.setEnabled(bool(self.otherBrowsPathEdit.text()))
        self.otherBrowsLoad.clicked.connect(self.loadToOtherBrowser)
        otherBrowserLine.addWidget(self.otherBrowsLoad)
        layout.addSpacing(10)
        self.closeOnLoadCheck = SwitchButton()
        self.closeOnLoadCheck.setStyleSheet("border: 0px solid transparent")
        self.closeOnLoadCheck.setChecked(cfg.get(cfg.closeOnBrowserSelect))
        self.closeOnLoadCheck.setOffText("Do not close window on browser select")
        self.closeOnLoadCheck.setOnText("Close window on browser select")
        self.closeOnLoadCheck.checkedChanged.connect(lambda checked: (
            cfg.set(cfg.closeOnBrowserSelect, checked)
        ))

        layout.addStretch(1)

        # Bottom bar
        bottomContainer = QWidget()
        mainLayout.addWidget(bottomContainer)
        bottomContainer.setStyleSheet((self.bottomDarkSheet if smartIsDarkMode() else self.bottomLightSheet) if cfg.get(cfg.appTheme) == "Auto" else
                                      self.bottomDarkSheet if cfg.get(cfg.appTheme) == "Dark" else self.bottomLightSheet)
        bottomLayout = QHBoxLayout(bottomContainer)
        bottomLayout.setContentsMargins(40, 30, 40, 30)
        bottomLayout.setSpacing(15)
        self.requestLinkEdit = LineEdit()
        self.requestLinkEdit.setText(requestURL)
        self.requestLinkEdit.setReadOnly(True)
        bottomLayout.addWidget(self.requestLinkEdit)
        self.requestLinkCopy = PrimaryPushButton(FICO.COPY, "Copy link")
        self.requestLinkCopy.clicked.connect(self.copyLinkToClip)
        bottomLayout.addWidget(self.requestLinkCopy)
        self.restartBtn = ToolButton(FICO.SYNC)
        self.restartBtn.setToolTip("Restart the Smart Selector")
        self.restartBtn.installEventFilter(ToolTipFilter(self.restartBtn))
        self.restartBtn.clicked.connect(self.confirmRestart)
        bottomLayout.addWidget(self.restartBtn)
        
        self.titleBar.raise_()
        print(f"Loading '{requestURL}'...\n")
        smartSelectorLog(f"Loading '{requestURL}'...")
        if self.runningBrowsers: self.show()
        elif cfg.get(cfg.mainBrowserPath):
            subprocess.Popen([cfg.get(cfg.mainBrowserPath), requestURL])
            sys.exit()
        else: self.show()

    def removeMaximizeFlags(self):
        flags = self.windowFlags()
        flags &= ~Qt.WindowType.WindowMaximizeButtonHint
        #flags &= ~Qt.WindowType.WindowResizable
        self.setWindowFlags(flags)

    def cardSelect(self, name, link):
        if myBrowsList["MyBrowsers"]:
            for browser in myBrowsList["MyBrowsers"]:
                if browser["name"] == name:
                    if browser["path"]:
                        try:
                            subprocess.Popen([browser["path"], link])
                            print(f"{Fore.GREEN}'{requestURL}' has been successfully loaded into {browser["name"]}.{Style.RESET_ALL}")
                        except Exception as e:
                            smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to load your link into {browser["name"]}: {e}")
                            print(f"{Fore.RED}An error occured while attempting to load your link into {browser["name"]}: {e}{Style.RESET_ALL}")
                        break
                    else:
                        smartWarningNotify(self, "Warning, be careful!", f"The path to {browser["name"]} as registered in your SmartList is empty...")
                        print(f"{Fore.YELLOW}The path to {browser["name"]} as registered in your SmartList is empty...{Style.RESET_ALL}")
                        break
                elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                    if os.path.basename(cfg.get(cfg.mainBrowserPath)) == name:
                        try: subprocess.Popen([cfg.get(cfg.mainBrowserPath), link])
                        except Exception as e: smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}")
                        break
                else: smartWarningNotify(self, "Warning, be careful!", f"The name '{name}' is not registered into your SmartList, or {name} cannot be found in your SmartList...")

    def loadToOtherBrowser(self):
        otherPath = self.otherBrowsPathEdit.text()
        if otherPath:
            if os.path.exists(otherPath):
                try:
                    subprocess.Popen([otherPath, requestURL])
                    print(f"{Fore.BLUE}Selected external browser at path: '{otherPath}'{Style.RESET_ALL}")
                    smartSelectorLog(f"Selected external browser at path: '{otherPath}'")
                except Exception as e: smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(otherPath)}: {e}")
            else: smartWarningNotify(self, "Warning, be careful!", "The given path to the external browser does not exist...")
        else: smartWarningNotify(self, "Warning, be careful!", "The external path entry is empty...")

    def copyLinkToClip(self):
        app = QApplication.instance()
        if app is None: app = QApplication(sys.argv)
        if type(app) == QApplication: clipboard = app.clipboard()
        if clipboard:
            clipboard.setText(self.requestLinkEdit.text())
            print(f"Copied to clipboard: {Fore.BLUE}'{clipboard.text()}'{Style.RESET_ALL}")
            smartSuccessNotify(self, "Copying complete!", "The forwarded link has been successfully copied to the clipboard!")
        else: self.copyLinkToClip

    def confirmRestart(self):
        restartDlg = MessageBox(
            "Restart confirmation",
            "Are you sure you really want to restart the Smart Selector?",
            self
        )
        restartDlg.yesButton.setText("Restart")
        restartDlg.cancelButton.setText("Cancel")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smartPlaySound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if restartDlg.exec():
            try:
                smartRestartApp()
                print("Restarting the Smart Selector...")
                smartSelectorLog("Restarting the Smart Selector...")
            except Exception as e:
                smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to restart SmartLinker: {e}")
                print(f"{Fore.RED}An error occured while attempting to restart the Smart Selector: {e}{Style.RESET_ALL}")
                smartSelectorLog(f"ERROR: Failed to restart the Smart Selector: {e}")

class BrowserCard(ElevatedCardWidget):
    def __init__(self, icon: QIcon | str, name: str, status: str, parent=None):
        super().__init__(parent)
        self.statusLabel = CaptionLabel(status)
        self.iconWidget = IconWidget(icon, self)
        self.label = CaptionLabel(name, self)
        self.selectButton = PrimaryPushButton("Load here")

        self.iconWidget.setFixedSize(56, 56)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selectButton.clicked.connect(lambda: self.cardSelect(name, requestURL, parent))

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.vBoxLayout.addWidget(self.selectButton, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        self.setFixedSize(168, 176)

    def cardSelect(self, name, link, parent=None):
        failedAttempts = 0
        manualCount = 1 if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual) else 0
        if myBrowsList["MyBrowsers"]:
            for browser in myBrowsList["MyBrowsers"]:
                if browser["name"] == name:
                    if browser["path"]:
                        try:
                            subprocess.Popen([browser["path"], link])
                            print(f"{Fore.GREEN}Successfully loaded '{link}' into: {name}{Style.RESET_ALL}")
                            smartSelectorLog(f"SUCCESS: '{link}' has been successfully loaded into {name}.")
                            if bool(cfg.get(cfg.closeOnBrowserSelect)): sys.exit()
                        except Exception as e:
                            smartErrorNotify(parent, "Oops! Something went wrong...", f"An error occured while attempting to load your link into {name}:\n{e}")
                            print(f"{Fore.RED}Something went wrong when attempting to load your link into {name}:\n{e}{Style.RESET_ALL}")
                            smartSelectorLog(f"ERROR: Failed loading {link} into {name}: {e}")
                        break
                    else:
                        smartWarningNotify(parent, "Warning, be careful!", f"The path to {name} as registered in your SmartList is empty...")
                        print(f"{Fore.YELLOW}WARNING!!! The path to {name} as registered in your SmartList is empty...{Style.RESET_ALL}")
                        smartSelectorLog(f"WARNING: The path to {name} as registered in the SmartList is empty...")
                        break
                elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                    if os.path.basename(cfg.get(cfg.mainBrowserPath)) == name:
                        try:
                            subprocess.Popen([cfg.get(cfg.mainBrowserPath), link])
                            print(f"{Fore.GREEN}Successfully loaded '{link}' into: {os.path.basename(cfg.get(cfg.mainBrowserPath))}{Style.RESET_ALL}")
                            smartSelectorLog(f"SUCCESS: '{link}' has been successfully loaded into {name}.")
                            if bool(cfg.get(cfg.closeOnBrowserSelect)): sys.exit()
                        except Exception as e:
                            smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(cfg.get(cfg.mainBrowserPath))}:\n{e}")
                            print(f"{Fore.RED}Something went wrong when attempting to load {link} into {os.path.basename(cfg.get(cfg.mainBrowserPath))}:\n{e}{Style.RESET_ALL}")
                            smartSelectorLog(f"ERROR: Failed loading {link} into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}")
                        break
                else:
                    failedAttempts += 1
                    if failedAttempts == len(myBrowsList["MyBrowsers"]) + manualCount:
                        smartWarningNotify(parent, "Warning, be careful!", f"The name '{name}' is not registered into your SmartList, or {name} cannot be found in your SmartList...")
                        print(f"{Fore.YELLOW}WARNING!!! The name '{name}' is not registered into your SmartList, or {name} cannot be found in your SmartList...{Style.RESET_ALL}")
                        smartSelectorLog(f"WARNING: The name '{name}' is not registered into the SmartList, or cannot be found in the SmartList...")
