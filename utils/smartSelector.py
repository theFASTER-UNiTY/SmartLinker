from utils.SmartUtils import *
from utils.smartDownMarker import SmartDownMarkerGUI as DownMarker

# ===========================================================================================================

myBrowsList = smart.loadBrowsers()
setThemeColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor())

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
        self.minBtn.setNormalColor(QColor("white" if theme() == Theme.DARK else "black"))
        self.closeBtn.setNormalColor(QColor("white" if theme() == Theme.DARK else "black"))
        # self.minBtn.setHoverColor(QColor("white"))
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
    """ Class for the Smart Selector window """

    def __init__(self, requestArgs: list[str], parent = None):
        super().__init__(parent)
        RichCLI.print(smart.consoleScript())
        smart.emptySelectorLog()
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon(smart.resourcePath("resources/icons/ico/icon.ico")))
        self.setWindowTitle(f"Smart Selector | {SmartLinkerName}")
        self.setStyleSheet(
            f"{"background: white;" if theme() == Theme.LIGHT else ""} " \
             "font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;"
        )
        
        self.themeCtrl = ThemeController(self)
        self.titleHeight = self.titleBar.height()
        self.lightSheetOnDark: str = "SingleDirectionScrollArea {background-color: rgba(242, 242, 242, 0.05); border: 1px solid rgba(242, 242, 242, 0.25)}"
        self.darkSheetOnLight: str = "SingleDirectionScrollArea {background-color: rgba(32, 32, 32, 0.05); border: 1px solid rgba(32, 32, 32, 0.25)}"
        self.runningBrowsers = 0
        self.bottomLightSheet: str = "background-color: #F3F3F3; border: 1px solid #E5E5E5"
        self.bottomDarkSheet: str = "background-color: #161616; border: 1px solid #000000" # original: #202020, #1D1D1D
        self.requestURL = requestArgs[1]

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, self.titleHeight, 0, 0)
        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(80, 0, 80, 0)
        mainTitleLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addLayout(mainTitleLine)
        mainIcon = IconWidget(QIcon(smart.resourcePath("resources/icons/ico/icon.ico")))
        mainIcon.setFixedSize(56, 56)
        mainTitleLine.addWidget(mainIcon, 0, Qt.AlignmentFlag.AlignCenter)
        mainTitleBox = QVBoxLayout()
        mainTitleBox.setContentsMargins(10, 20, 0, 20)
        mainTitleLine.addLayout(mainTitleBox)
        mainTitleBox.addWidget(TitleLabel("New URL loading request detected!"))
        self.mainSubtitle = CaptionLabel(f"Which browser do you want to load this URL request into?")
        self.mainSubtitle.setTextColor(QColor("gray"), QColor("gray"))
        self.mainSubtitle.setWordWrap(True)
        mainTitleBox.addWidget(self.mainSubtitle)
        self.mainScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        self.mainScroll.setWidgetResizable(True)
        self.mainScroll.setContentsMargins(0, 0, 0, 0)
        self.mainScroll.enableTransparentBackground()
        mainLayout.addWidget(self.mainScroll)
        mainScrollContent = QWidget()
        self.mainScroll.setWidget(mainScrollContent)
        mainScrollContent.setContentsMargins(40, 0, 40, 0)
        layout = QVBoxLayout(mainScrollContent)
        layout.setSpacing(10)

        # List of SmartList browsers
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
        RichCLI.print("\n=============================\n" \
               "Scanning running processes...\n" \
               "=============================\n")
        smart.selectorLog("Scanning running browsers...")
        if smart.isMarkdownExtension(self.requestURL) and smart.getFileMimeType(self.requestURL).startswith("text"):
            browsCard = BrowserCard(
                smIco.renderIcon(smIco.MARKDOWN, 56),
                "Smart DownMarker",
                "Embedded",
                self.requestURL,
                self
            )
            self.myBrowsLayout.addWidget(browsCard)
        if myBrowsList["MyBrowsers"]:
            for browser in myBrowsList["MyBrowsers"]:
                RichCLI.print(f"Browser in queue: [u]{os.path.basename(browser["path"])}[/]\n" \
                        "------------------------------------")
                smart.selectorLog(f"Browser in queue: {os.path.basename(browser["path"])}")
                if smart.isBrowserOpen(browser["path"]):
                    self.isRunning = True
                    self.runningBrowsers += 1
                    smart.selectorLog(f"'{os.path.basename(browser["path"])}' is running.")
                else:
                    self.isRunning = False
                    smart.selectorLog(f"'{os.path.basename(browser["path"])}' is not running.")
                browsCard = BrowserCard(
                    smart.getFileIcon(browser["path"]),
                    browser["name"],
                    "Running" if self.isRunning else "",
                    self.requestURL,
                    self
                )
                self.myBrowsLayout.addWidget(browsCard)
        if (cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual)):
            print(f"Browser in queue: [u]{os.path.basename(cfg.get(cfg.mainBrowserPath))}[/]\n" \
                   "------------------------------------")
            smart.selectorLog(f"Browser in queue: {os.path.basename(cfg.get(cfg.mainBrowserPath))}")
            if smart.isBrowserOpen(cfg.get(cfg.mainBrowserPath)):
                self.isRunning = True
                self.runningBrowsers += 1
            else: self.isRunning = False
            browsCard = BrowserCard(
                smart.getFileIcon(cfg.get(cfg.mainBrowserPath)),
                os.path.basename(cfg.get(cfg.mainBrowserPath)),
                "Manual - Running" if self.isRunning else "Manual",
                self.requestURL,
                self
            )
            self.myBrowsLayout.addWidget(browsCard)
        if cfg.get(cfg.showAddBrowserCard):
            browsCard = BrowserCard(
                FICO.ADD.qicon(),
                "Add a browser", "", "",
                self
            )
            self.myBrowsLayout.addWidget(browsCard)
        if not myBrowsList["MyBrowsers"] and not cfg.get(cfg.mainBrowserPath) and not cfg.get(cfg.showAddBrowserCard): self.myBrowsLayout.addWidget(self.myBrowsEmptyMsg, 0, Qt.AlignmentFlag.AlignCenter)
        RichCLI.print("-----------------------------------------------------\n" \
              f"[bold]{self.runningBrowsers if self.runningBrowsers else "No"} browser{"s[/] are" if self.runningBrowsers > 1 else "[/] is"} currently running.\n" \
              f"{"[bold blue]NOTE: [/b][italic]They may be the same browser.[/]\n" if self.runningBrowsers > 1 else ""}" \
               "-----------------------------------------------------\n")
        smart.selectorLog(
            f"Scanning running browsers terminated. {self.runningBrowsers if self.runningBrowsers else "No"} browser{"s are" if self.runningBrowsers > 1 else " is"} "
            f"currently running{" (they may be the same browser)" if self.runningBrowsers > 1 else ""}.")
        
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
        self.otherBrowsPathEdit.textChanged.connect(lambda text: self.otherBrowsPathChanged(text))
        otherBrowserLine.addWidget(self.otherBrowsPathEdit)
        self.otherBrowsPathBrowse = ToolButton(FICO.FOLDER)
        self.otherBrowsPathBrowse.setToolTip("Browse...")
        self.otherBrowsPathBrowse.installEventFilter(ToolTipFilter(self.otherBrowsPathBrowse))
        self.otherBrowsPathBrowse.clicked.connect(lambda: (
            self.otherBrowsPathEdit.setText(os.path.normpath(smart.browseFileDialog(self, "Select a browser to load the link into", "", "Executables (*.exe)")))
        ))
        otherBrowserLine.addWidget(self.otherBrowsPathBrowse)
        self.otherBrowsLoad = PushButton(FICO.LINK, "Load link")
        self.otherBrowsLoad.setEnabled(bool(self.otherBrowsPathEdit.text()))
        self.otherBrowsLoad.clicked.connect(self.loadToOtherBrowser)
        otherBrowserLine.addWidget(self.otherBrowsLoad)
        layout.addSpacing(10)
        self.previewInfoBar = InformationBar(
            "info",
            "The Smart Selector is currently in Preview Mode, so many features " \
            "are unavailable. You can only see what the Selector looks like, " \
            "based on its current configuration.",
            self
        )
        if self.isPreviewMode(): layout.addWidget(self.previewInfoBar)

        layout.addStretch(1)

        # Bottom area
        self.bottomContainer = QWidget()
        mainLayout.addWidget(self.bottomContainer)
        self.bottomContainer.setStyleSheet(self.bottomDarkSheet if theme() == Theme.DARK else self.bottomLightSheet)
        bottomLayout = QHBoxLayout(self.bottomContainer)
        bottomLayout.setContentsMargins(40, 30, 40, 30)
        bottomLayout.setSpacing(15)
        self.requestLinkEdit = LineEdit()
        self.requestLinkEdit.setText(
            self.requestURL if not self.isPreviewMode() else "Smart Selector in Preview mode"
        )
        self.requestLinkEdit.setReadOnly(True)
        bottomLayout.addWidget(self.requestLinkEdit)
        self.requestLinkCopy = PrimaryPushButton(FICO.COPY, "Copy link")
        self.requestLinkCopy.clicked.connect(self.copyLinkToClip)
        bottomLayout.addWidget(self.requestLinkCopy)
        self.restartBtn = ToolButton(segFont.fromName("UpdateRestore"))
        self.restartBtn.setToolTip("Restart the Smart Selector")
        self.restartBtn.installEventFilter(ToolTipFilter(self.restartBtn))
        self.restartBtn.clicked.connect(self.confirmRestart)
        bottomLayout.addWidget(self.restartBtn)
        self.managerBtn = ToolButton(smart.resourcePath("resources/icons/ico/icon.ico"))
        self.managerBtn.setToolTip("Open the Smart Manager")
        self.managerBtn.installEventFilter(ToolTipFilter(self.managerBtn))
        self.managerBtn.clicked.connect(self.openManager)
        bottomLayout.addWidget(self.managerBtn)
        
        self.titleBar.raise_()
        self.setMinimumSize(750, 550 if not self.isPreviewMode() else 650)
        self.resize(750, 550 if not self.isPreviewMode() else 650)
        self.requestLinkEdit.setEnabled(not self.isPreviewMode())
        self.requestLinkCopy.setEnabled(not self.isPreviewMode())
        self.restartBtn.setEnabled(not self.isPreviewMode())
        self.managerBtn.setEnabled(not self.isPreviewMode())
        self.themeCtrl.themeChanged.connect(lambda text: self.applyTheme(cfg.get(cfg.appTheme)))
        RichCLI.print(
            f"Loading {f"'[u i]{self.requestURL}[/]'" if not self.isPreviewMode() else "the Smart Selector in [smartpurple][b i]Preview Mode[/]"}...\n"
        )
        smart.selectorLog(f"Loading {f"'{self.requestURL}'" if not self.isPreviewMode() else "the Smart Selector in Preview Mode"}...")
        if self.runningBrowsers:
            self.show()
            if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.selectorSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.selectorSFXPath), "Smart Selector launch")
        elif cfg.get(cfg.mainBrowserPath):
            subprocess.Popen([cfg.get(cfg.mainBrowserPath), self.requestURL])
            sys.exit()
        else:
            self.show()
            if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.selectorSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.selectorSFXPath), "Smart Selector launch")

    def isPreviewMode(self) -> bool:
        """ Check if the Selector is in ***Preview** mode* """
        return self.requestURL == "/AsPreview"

    def previewNote(self):
            """ Send notifications if the Selector is in ***Preview** mode* while an action is performed """
            smart.infoNotify("Action unavailable", "The Smart Selector is currently in Preview mode.", self)
            RichCLI.log("[smartblue][b u]NOTE[/b u]: The Smart Selector is currently in [skyblue]Preview mode[/skyblue], the action is [#777777]unavailable[/#777777].[/]")
            smart.selectorLog("INFO: The Smart Selector is currently in Preview mode, the action is unavailable.")

    def applyTheme(self, mode):
        """ Apply theme automatically according to system and config """
        if mode == "Auto":
            setTheme(Theme.DARK if smart.isDarkModeEnabled() else Theme.LIGHT)
        elif mode == "Dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        
        self.titleBar.minBtn.setNormalColor(QColor("white" if theme() == Theme.DARK else "black"))
        self.titleBar.closeBtn.setNormalColor(QColor("white" if theme() == Theme.DARK else "black"))

        self.setStyleSheet(
            f"{"background: white;" if theme() == Theme.LIGHT else ""} " \
             "font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;"
        )
        self.mainScroll.enableTransparentBackground()
        self.myBrowsScroll.setStyleSheet(
            self.lightSheetOnDark if theme() == Theme.DARK else self.darkSheetOnLight
        )
        self.bottomContainer.setStyleSheet(
            self.bottomDarkSheet if theme() == Theme.DARK else self.bottomLightSheet
        )

    def otherBrowsPathChanged(self, text):
        """ Enable/disable the 'Load link' button depending on the text entry content """
        self.otherBrowsLoad.setEnabled(bool(text))
        self.otherBrowsLoad.installEventFilter(ToolTipFilter(self.otherBrowsLoad))
        if text and text.endswith(".exe") and os.path.exists(text):
            self.otherBrowsLoad.setIcon(smart.getFileIcon(text))
            self.otherBrowsLoad.setToolTip(f'Load link into "{os.path.basename(text)}"')
        else:
            self.otherBrowsLoad.setIcon(FICO.LINK)
            self.otherBrowsLoad.setToolTip(None)

    def loadToOtherBrowser(self):
        """ Load the forwarded link to another browser selected from storage """
        otherPath = self.otherBrowsPathEdit.text()
        if not self.isPreviewMode():
            if otherPath:
                if os.path.exists(otherPath):
                    try:
                        subprocess.Popen([otherPath, self.requestURL])
                        print(f"{Fore.BLUE}Selected external browser at path: '{otherPath}'{Style.RESET_ALL}")
                        smart.selectorLog(f"Selected external browser at path: '{otherPath}'")
                    except Exception as e:
                        smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(otherPath)}: {e}", self)
                        print(f"{Fore.RED}An error occured while attempting to load link into '{otherPath}': {e}{Style.RESET_ALL}")
                        smart.selectorLog(f"ERROR: Failed to load link into '{otherPath}': {e}")
                else:
                    smart.warningNotify("Warning, be careful!", "The given path to the external browser does not exist...", self)
                    print(f"{Fore.YELLOW}The given path to the external browser does not exist...{Style.RESET_ALL}")
                    smart.selectorLog("WARNING: The given path to the external browser does not exist...")
            
            else:
                smart.warningNotify("Warning, be careful!", "The external path entry is empty...", self)
                print(f"{Fore.YELLOW}The external path entry is empty...{Style.RESET_ALL}")
                smart.selectorLog("WARNING: The external path entry is empty...")

        else: self.previewNote()

    def copyLinkToClip(self):
        """ Copy the forwarded link to the system's clipboard """
        if not self.isPreviewMode():
            app = QApplication.instance()
            if app is None: app = QApplication(sys.argv)
            if type(app) == QApplication: clipboard = app.clipboard()
            if clipboard:
                clipboard.setText(self.requestLinkEdit.text())
                print(f"Copied to clipboard: {Fore.BLUE}'{clipboard.text()}'{Style.RESET_ALL}")
                smart.selectorLog(f"INFO: Copied link to clipboard: {clipboard.text()}")
                smart.successNotify("Copying complete!", "The forwarded link has been successfully copied to the clipboard!", self)
            else: self.copyLinkToClip()
        
        else: self.previewNote()

    def openManager(self):
        """ Open the Smart Manager """
        if not self.isPreviewMode():
            from smartLinker import SmartLinkerGUI as SManager
            self.managerWindow = SManager()
            self.managerWindow.show()
        else: self.previewNote()

    def confirmRestart(self):
        """ Open a confirmation dialog to restart the Smart Selector """
        if not self.isPreviewMode():
            restartDlg = MessageBox(
                "Restart confirmation",
                "Are you sure you really want to restart the Smart Selector?",
                self
            )
            restartDlg.yesButton.setText("Restart")
            restartDlg.cancelButton.setText("Cancel")
            if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
            if restartDlg.exec():
                try:
                    reArgs = sys.argv
                    reArgs.remove("load")
                    sys.argv = reArgs
                    smart.restartApp()
                    print("Restarting the Smart Selector...")
                    smart.selectorLog("Restarting the Smart Selector...")
                except Exception as e:
                    smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to restart SmartLinker: {e}", self)
                    print(f"{Fore.RED}An error occured while attempting to restart the Smart Selector: {e}{Style.RESET_ALL}")
                    smart.selectorLog(f"ERROR: Failed to restart the Smart Selector: {e}")
        
        else: self.previewNote()

class BrowserCard(ElevatedCardWidget):
    """ Class for listed browser(s) card """

    def __init__(self, icon: QIcon | str, name: str, status: str, reqURL: str, parent: SmartSelectorGUI):
        super().__init__(parent)
        self.cardParent = parent
        self.statusLabel = CaptionLabel(status)
        self.iconWidget = IconWidget(icon, self)
        self.label = BodyLabel(name, self)

        if self.statusLabel.text() == "Running":
            self.statusLabel.setStyleSheet(
                "padding: 3px; " \
               f"color: {themeColor().name(QColor.NameFormat.HexRgb)}; " \
               f"background-color: rgba({smart.convertToRGB(themeColor())}, 0.25); "
               f"border: 1px solid {themeColor().name(QColor.NameFormat.HexRgb)}; " \
                "border-radius: 10px;"
            )
        elif self.statusLabel.text() == "Embedded":
            self.statusLabel.setStyleSheet(
                "padding: 3px; " \
               f"color: gray; " \
               f"background-color: rgba({smart.convertToRGB(QColor("gray"))}, 0.25); "
               f"border: 1px solid gray; " \
                "border-radius: 10px;"
            )
        self.iconWidget.setFixedSize(56, 56)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clicked.connect(lambda: self.cardSelect(name, reqURL, parent))

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        self.setFixedSize(168, 176)

    def cardSelect(self, name, link, parent):
        if not self.cardParent.isPreviewMode():
            failedAttempts = 0
            manualCount = 1 if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual) else 0
            if name == "Smart DownMarker":
                mdWindow = DownMarker(link)
                mdWindow.show()
                print(f"{Fore.GREEN}Successfully loaded '{link}' into the Smart DownMarker{Style.RESET_ALL}")
                smart.selectorLog(f"SUCCESS: '{link}' has been successfully loaded into the Smart DownMarker.")
                if bool(cfg.get(cfg.closeOnBrowserSelect)): parent.close() # type: ignore
            
            elif name == "Add a browser":
                RichCLI.print("[#777][b u]NOTE[/b u]: [i]This feature is coming soon to your Smart Selector...[/]")

            elif myBrowsList["MyBrowsers"]:
                for browser in myBrowsList["MyBrowsers"]:
                    if browser["name"] == name:
                        if browser["path"]:
                            try:
                                subprocess.Popen([browser["path"], link])
                                print(f"{Fore.GREEN}Successfully loaded '{link}' into: {name}{Style.RESET_ALL}")
                                smart.selectorLog(f"SUCCESS: '{link}' has been successfully loaded into {name}.")
                                if bool(cfg.get(cfg.closeOnBrowserSelect)): sys.exit()
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {name}:\n{e}", parent)
                                print(f"{Fore.RED}Something went wrong when attempting to load your link into {name}:\n{e}{Style.RESET_ALL}")
                                smart.selectorLog(f"ERROR: Failed loading {link} into {name}: {e}")
                            break
                        
                        else:
                            smart.warningNotify("Warning, be careful!", f"The path to {name} as registered in your SmartList is empty...", parent)
                            print(f"{Fore.YELLOW}WARNING!!! The path to {name} as registered in your SmartList is empty...{Style.RESET_ALL}")
                            smart.selectorLog(f"WARNING: The path to {name} as registered in the SmartList is empty...")
                            break
                    
                    elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                        if os.path.basename(cfg.get(cfg.mainBrowserPath)) == name:
                            try:
                                subprocess.Popen([cfg.get(cfg.mainBrowserPath), link])
                                print(f"{Fore.GREEN}Successfully loaded '{link}' into: {os.path.basename(cfg.get(cfg.mainBrowserPath))}{Style.RESET_ALL}")
                                smart.selectorLog(f"SUCCESS: '{link}' has been successfully loaded into {name}.")
                                if bool(cfg.get(cfg.closeOnBrowserSelect)): sys.exit()
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(cfg.get(cfg.mainBrowserPath))}:\n{e}", parent)
                                print(f"{Fore.RED}Something went wrong when attempting to load {link} into {os.path.basename(cfg.get(cfg.mainBrowserPath))}:\n{e}{Style.RESET_ALL}")
                                smart.selectorLog(f"ERROR: Failed loading {link} into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}")
                            break
                    
                    else:
                        failedAttempts += 1
                        if failedAttempts == len(myBrowsList["MyBrowsers"]) + manualCount:
                            smart.warningNotify("Warning, be careful!", f"The name '{name}' is not registered into your SmartList, or {name} cannot be found in your SmartList...", parent)
                            print(f"{Fore.YELLOW}WARNING!!! The name '{name}' is not registered into your SmartList, or {name} cannot be found in your SmartList...{Style.RESET_ALL}")
                            smart.selectorLog(f"WARNING: The name '{name}' is not registered into the SmartList, or cannot be found in the SmartList...")
        
        else: self.cardParent.previewNote()

class InformationBar(QWidget):
    """ Class for the information snack bar """

    def __init__(self, type: str, description: str, parent: SmartSelectorGUI):
        super().__init__(parent)
        self.barParent = parent
        self.barType: str = type or "info"

        self.styles = {
            "info": {
                "icon": FICO.INFO,
                "title": "Information",
                "primary": "#2196F3",
            },
            "warning": {
                "icon": segFont.fromName("Warning"),
                "title": "Warning",
                "primary": "#FCAF00",
            }
        }

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("InfoBar")
        self.setStyleSheet(f"""
            QWidget#InfoBar {{
                border: 1px solid {self.styles[self.barType]["primary"]};
                border-radius: 10px;
                background-color: rgba({smart.convertToRGB(self.styles[self.barType]["primary"])}, 0.15);
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)

        labelBox = QVBoxLayout()
        labelBox.setContentsMargins(0, 0, 0, 0)
        labelBox.setSpacing(5)

        self.barIcon = IconWidget(
            self.styles[self.barType]["icon"].colored(
                QColor(self.styles[self.barType]["primary"]),
                QColor(self.styles[self.barType]["primary"])
            )
        )
        self.barIcon.setFixedSize(16, 16)

        self.barTitle = BodyLabel(self.styles[self.barType]["title"])
        self.barTitle.setTextColor(QColor(self.styles[self.barType]["primary"]), QColor(self.styles[self.barType]["primary"]))
        self.barTitle.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        setFont(self.barTitle, weight=QFont.Weight.Bold)

        self.barDesc = CaptionLabel(description)
        self.barDesc.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.barDesc.setWordWrap(True)

        layout.addWidget(self.barIcon)
        layout.addLayout(labelBox)
        labelBox.addWidget(self.barTitle)
        labelBox.addWidget(self.barDesc)
    
    def type(self) -> str:
        """ :InformationBar: Get the information snack bar type """

        return self.barType
    
    def title(self) -> str:
        """ :InformationBar: Get the information snack bar title """

        return self.barTitle.text()
    
    def description(self) -> str:
        """ :InformationBar: Get the information snack bar description """

        return self.barDesc.text()
    
    def icon(self) -> QIcon:
        """ :InformationBar: Get the information snack bar icon """

        return QIcon(self.barIcon._icon)
    
    def setType(self, type: str):
        """ :InformationBar: Set the information snack bar type """

        if type == "warning":
            self.setStyleSheet(f"""
                #InfoBar {{
                    border: 1px solid {self.styles["warning"]["primary"]};
                    border-radius: 10px;
                    background-color: rgba({smart.convertToRGB(self.styles["warning"]["primary"])}, 0.15);
                }}
            """)
            self.barTitle.setText(self.styles["warning"]["title"])
            self.barIcon.setIcon(
                self.styles["warning"]["icon"].colored(
                    QColor(self.styles["warning"]["primary"]),
                    QColor(self.styles["warning"]["primary"])
                )
            )

        else:
            self.setStyleSheet(f"""
                #InfoBar {{
                    border: 1px solid {self.styles["info"]["primary"]};
                    border-radius: 10px;
                    background-color: rgba({smart.convertToRGB(self.styles["info"]["primary"])}, 0.25);
                }}
            """)
            self.barTitle.setText(self.styles["info"]["title"])
            self.barIcon.setIcon(
                self.styles["info"]["icon"].colored(
                    QColor(self.styles["info"]["primary"]),
                    QColor(self.styles["info"]["primary"])
                )
            )

    def setCustomTitle(self, text: str):
        """ :InformationBar: Set the information snack bar custom title """

        self.barTitle.setText(text)

    def setDescription(self, text: str):
        """ :InformationBar: Set the information snack bar description """

        self.barDesc.setText(text)
    
    def setCustomIcon(self, icon: str | QIcon | FluentIconBase):
        """ :InformationBar: Set the information snack bar custom icon """

        if not isinstance(icon, FluentIconBase):
            self.barIcon.setIcon(icon)
        else:
            self.barIcon.setIcon(
                icon.colored(
                    QColor(self.styles[self.barType]["primary"]),
                    QColor(self.styles[self.barType]["primary"])
                )
            )
