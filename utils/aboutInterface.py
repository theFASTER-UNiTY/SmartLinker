from utils.SmartUtils import *

class AboutInterface(QWidget):
    """ Main class for the 'About' interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("About-SmartLinker")
        self.lastChecked = f"Last checked: {cfg.get(cfg.lastCheckedDate)}{f" (Latest version: {cfg.get(cfg.updateVersion)})" if cfg.get(cfg.updateAvailable) else ""}" if cfg.get(cfg.lastCheckedDate) \
                        else "Click on the following button to check for the latest updates."
        self.feedbackBrowserDlg = None
        self.linkBrowserDlg = None
        self.myBrowsList = smart.loadBrowsers()

        mainAboutLayout = QVBoxLayout(self)
        mainAboutLayout.setContentsMargins(0, 20, 0, 0)
        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(40, 0, 0, 0)
        mainAboutLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("About", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainTitleLine.addWidget(self.title)
        mainAboutScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainAboutLayout.addWidget(mainAboutScroll)
        mainAboutScroll.setWidgetResizable(True)
        mainAboutScroll.enableTransparentBackground()
        mainAboutScrollContent = QWidget()
        mainAboutScroll.setWidget(mainAboutScrollContent)
        mainAboutScroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainAboutScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid #FFFFFF")
        mainAboutScrollContent.setContentsMargins(40, 0, 40, 0)
        layout = QVBoxLayout(mainAboutScrollContent)
        layout.setSpacing(5)

        aboutMainLine = QHBoxLayout()
        layout.addLayout(aboutMainLine)
        aboutLogo = IconWidget(QIcon(smart.resourcePath("resources/images/icons/icon.ico")))
        aboutLogo.setFixedSize(64, 64)
        aboutMainLine.addWidget(aboutLogo)
        aboutTextBox = QVBoxLayout()
        aboutTextBox.setContentsMargins(10, 20, 0, 20)
        aboutMainLine.addLayout(aboutTextBox)
        aboutTitle = TitleLabel("SmartLinker - Mastering URL Handling")
        aboutSubtitle = CaptionLabel(f"© 2025 {SmartLinkerAuthor}")
        aboutSubtitle.setStyleSheet("color: gray")
        aboutTextBox.addWidget(aboutTitle)
        aboutTextBox.addWidget(aboutSubtitle)
        self.aboutVersion = PrimaryPushSettingCard(
            "Check for updates",
            FICO.INFO,
            "Current version: " + SmartLinkerVersion,
            self.lastChecked
        )
        layout.addWidget(self.aboutVersion)
        self.aboutCheckUpdates = SwitchSettingCard(
            FICO.UPDATE,
            "Check for updates when the software starts",
            "You will get automatically notified when a new, better and more featured version will be released.",
            cfg.checkUpdatesOnStart
        )
        self.aboutCheckUpdates.switchButton.setOnText("Enabled")
        self.aboutCheckUpdates.switchButton.setOffText("Disabled")
        self.aboutCheckUpdates.switchButton.checkedChanged.connect(lambda checked: (
            self.aboutCheckUpdates.switchButton.setOnText("Enabled"),
            self.aboutCheckUpdates.switchButton.setOffText("Disabled"),
        ))
        layout.addWidget(self.aboutCheckUpdates)
        self.aboutFeedback = HyperlinkCard(
            "",
            "Provide feedback",
            FICO.FEEDBACK,
            "Tell us what you think",
            "You can help us improve the overall experience by providing feedback."
        )
        self.aboutFeedback.linkButton.clicked.connect(lambda: self.feedbackBrowserSelect(parent))
        layout.addWidget(self.aboutFeedback)
        self.aboutInformation = AboutAppGroup()
        layout.addWidget(self.aboutInformation)
        self.aboutResources = ResourcesGroup()
        self.aboutResources.pyQtBtn.clicked.connect(lambda: self.linkBrowserSelect("https://www.pythonguis.com/pyqt6/", "Python GUIs", "website", QIcon(smart.resourcePath("resources/images/icons/pyqt6_icon.ico")), parent))
        self.aboutResources.pyQtBtn2.clicked.connect(lambda: self.linkBrowserSelect("https://doc.qt.io/qtforpython-6/", "Qt Documentation", "website", QIcon(smart.resourcePath("resources/images/icons/qtforpython_icon.ico")), parent))
        self.aboutResources.qFluentBtn.clicked.connect(lambda: self.linkBrowserSelect("https://www.qfluentwidgets.com/", "QFluentWidgets", "website", QIcon(smart.resourcePath("resources/images/icons/qfluentwidgets_icon.ico")), parent))
        self.aboutResources.qFluentBtn2.clicked.connect(lambda: self.linkBrowserSelect("https://github.com/zhiyiYo/PyQt-Fluent-Widgets", "QFluentWidgets", "GitHub repository", FICO.GITHUB, parent))
        self.aboutResources.flaticonBtn.clicked.connect(lambda: self.linkBrowserSelect("https://www.flaticon.com/", "Flaticon", "website", QIcon(smart.resourcePath("resources/images/icons/flaticon_icon.ico")), parent))
        layout.addWidget(self.aboutResources)

        layout.addStretch(1)

        self.updateSnack = QWidget()
        self.updateSnack.setObjectName("ASnackBase")
        self.updateSnack.setStyleSheet(f"#ASnackBase {{background-color: rgba({smart.convertToRGB(themeColor().name())}, 0.25); margin: 10px; margin-top: 0; border-radius: 5px}}")
        mainAboutLayout.addWidget(self.updateSnack)
        self.updateSnack.setVisible(bool(cfg.get(cfg.updateAvailable))) 
        self.updateSnack.setEnabled(bool(cfg.get(cfg.updateAvailable))) 
        self.updateSnackLayout = QHBoxLayout(self.updateSnack)
        self.updateSnackLayout.setContentsMargins(30, 15, 30, 25)
        self.updateSnackIcon = IconWidget(FICO.IOT)
        self.updateSnackIcon.setFixedSize(40, 40)
        self.updateSnackLayout.setSpacing(20)
        self.updateSnackLayout.addWidget(self.updateSnackIcon)
        self.updateSnackLabelBox = QVBoxLayout()
        self.updateSnackLabelBox.setContentsMargins(0, 0, 0, 0)
        self.updateSnackLabelBox.setSpacing(0)
        self.updateSnackLabel = SubtitleLabel("A new update is available for download!")
        self.updateSnackLabelBox.addWidget(self.updateSnackLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.updateSnackSublabel = CaptionLabel(f"You can now download the latest version of {SmartLinkerName} from the official GitHub repository.")
        self.updateSnackSublabel.setTextColor(QColor("#606060"), QColor("#D2D2D2"))
        self.updateSnackLabelBox.addWidget(self.updateSnackSublabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.updateSnackLayout.addLayout(self.updateSnackLabelBox)
        self.updateSnackLayout.addStretch(1)
        self.updateSnackButton = PrimaryPushButton(FICO.DOWNLOAD, "Download now")
        self.updateSnackButton.clicked.connect(lambda: self.linkBrowserSelect(f"{SmartLinkerGitRepoURL}/releases", "GitHub releases", "page", FICO.DOWNLOAD, parent))
        self.updateSnackLayout.addWidget(self.updateSnackButton)

    def feedbackBrowserSelect(self, parent):
        """ Open a dialog to select which browser you want to load the feedback page into """
        if not self.feedbackBrowserDlg:
            self.feedbackBrowserDlg = BrowserSelectDialog("Send feedback with...", FICO.FEEDBACK, parent)
            self.feedbackBrowserDlg.yesButton.setText("Send feedback")
        if self.feedbackBrowserDlg.exec():
            failedAttempts = 0
            feedbackURL = f"{SmartLinkerGitRepoURL}/issues/new?template=feedback.yml"
            if not self.feedbackBrowserDlg.browserCombo.currentText() == "Other browser":
                print(f"Opening the feedback section of GitHub repository into {self.feedbackBrowserDlg.browserCombo.currentText()}...")
                smart.managerLog(f"Opening the feedback section of GitHub repository into {self.feedbackBrowserDlg.browserCombo.currentText()}...")
                for browser in self.myBrowsList["MyBrowsers"]:
                    if browser["name"] == self.feedbackBrowserDlg.browserCombo.currentText():
                        if browser["path"]:
                            try:
                                subprocess.Popen([browser["path"], feedbackURL])
                                print(f"{Fore.GREEN}The feedback section of GitHub repository has been successfully loaded into {browser["name"]}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: The feedback section of GitHub repository has been successfully loaded into {browser["name"]}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the feedback section of GitHub repository into {browser["name"]}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to open the feedback section of GitHub repository into {browser["name"]}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while opening the feedback section of GitHub repository into {browser["name"]}: {e}")
                            break
                        else:
                            smart.warningNotify("Warning, be careful!", f"The path to {browser["name"]} as registered in your SmartList is empty...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The path to {browser["name"]} as registered in your SmartList is empty...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The path to {browser["name"]} as registered in the SmartList is empty...")
                            break
                    elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                        if os.path.basename(cfg.get(cfg.mainBrowserPath)) == self.feedbackBrowserDlg.browserCombo.currentText():
                            try:
                                subprocess.Popen([cfg.get(cfg.mainBrowserPath), feedbackURL])
                                print(f"{Fore.GREEN}The feedback section of GitHub repository has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: The feedback section of GitHub repository has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the feedback section of GitHub repository into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to open the feedback section of GitHub repository into {cfg.get(cfg.mainBrowserPath)}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while opening the feedback section of GitHub repository into {cfg.get(cfg.mainBrowserPath)}: {e}")
                            break
                    else:
                        failedAttempts += 1
                        if failedAttempts == self.feedbackBrowserDlg.browserCombo.count():
                            smart.warningNotify("Warning, be careful!", f"The name '{self.feedbackBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.feedbackBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The name '{self.feedbackBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.feedbackBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The name '{self.feedbackBrowserDlg.browserCombo.currentText()}' is not registered into the SmartList, or {self.feedbackBrowserDlg.browserCombo.currentText()} cannot be found in the SmartList...")
            else:
                print(f"Opening the feedback section of GitHub repository into {os.path.basename(self.feedbackBrowserDlg.otherBrowsEdit.text())}...")
                smart.managerLog(f"Opening the feedback section of GitHub repository into {os.path.basename(self.feedbackBrowserDlg.otherBrowsEdit.text())}...")
                try:
                    subprocess.Popen([self.feedbackBrowserDlg.otherBrowsEdit.text(), feedbackURL])
                    print(f"{Fore.GREEN}The feedback section of GitHub repository has been successfully loaded into another browser: '{self.feedbackBrowserDlg.otherBrowsEdit.text()}'{Style.RESET_ALL}")
                    smart.managerLog(f"SUCCESS: The feedback section of GitHub repository has been successfully loaded into other browser '{self.feedbackBrowserDlg.otherBrowsEdit.text()}'")
                except Exception as e:
                    smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the feedback section of GitHub repository into {os.path.basename(self.feedbackBrowserDlg.otherBrowsEdit.text())}: {e}", parent)
                    print(f"{Fore.RED}An error occured while attempting to open the feedback section of GitHub repository into '{os.path.basename(self.feedbackBrowserDlg.otherBrowsEdit.text())}': {e}{Style.RESET_ALL}")
                    smart.managerLog(f"ERROR: Failed to open the feedback section of GitHub repository into browser at path '{self.feedbackBrowserDlg.otherBrowsEdit.text()}': {e}")

    def linkBrowserSelect(self, url: str, title: str, linkType: str, icon: QIcon | FICO | FluentFontIconBase, parent):
        """ Open a dialog to select which browser you want to load a link into """
        if not self.linkBrowserDlg:
            self.linkBrowserDlg = BrowserSelectDialog(f"Open {title} with...", icon, parent)
        else:
            self.linkBrowserDlg = None
            self.linkBrowserDlg = BrowserSelectDialog(f"Open {title} with...", icon, parent)
        self.linkBrowserDlg.yesButton.setText(f"Open {title}")
        if self.linkBrowserDlg.exec():
            failedAttempts = 0
            if not self.linkBrowserDlg.browserCombo.currentText() == "Other browser":
                print(f"Opening the {title} {linkType} into {self.linkBrowserDlg.browserCombo.currentText()}...")
                smart.managerLog(f"Opening the {title} {linkType} into {self.linkBrowserDlg.browserCombo.currentText()}...")
                for browser in self.myBrowsList["MyBrowsers"]:
                    if browser["name"] == self.linkBrowserDlg.browserCombo.currentText():
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
                        if os.path.basename(cfg.get(cfg.mainBrowserPath)) == self.linkBrowserDlg.browserCombo.currentText():
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
                        if failedAttempts == self.linkBrowserDlg.browserCombo.count():
                            smart.warningNotify("Warning, be careful!", f"The name '{self.linkBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.linkBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The name '{self.linkBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.linkBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The name '{self.linkBrowserDlg.browserCombo.currentText()}' is not registered into the SmartList, or {self.linkBrowserDlg.browserCombo.currentText()} cannot be found in the SmartList...")
            else:
                print(f"Opening the {title} {linkType} into {os.path.basename(self.linkBrowserDlg.otherBrowsEdit.text())}...")
                smart.managerLog(f"Opening the {title} {linkType} into {os.path.basename(self.linkBrowserDlg.otherBrowsEdit.text())}...")
                try:
                    subprocess.Popen([self.linkBrowserDlg.otherBrowsEdit.text(), url])
                    print(f"{Fore.GREEN}The {title} {linkType} has been successfully loaded into another browser: '{self.linkBrowserDlg.otherBrowsEdit.text()}'{Style.RESET_ALL}")
                    smart.managerLog(f"SUCCESS: The {title} {linkType} has been successfully loaded into other browser '{self.linkBrowserDlg.otherBrowsEdit.text()}'")
                except Exception as e:
                    smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to open the {title} {linkType} into {os.path.basename(self.linkBrowserDlg.otherBrowsEdit.text())}: {e}", parent)
                    print(f"{Fore.RED}An error occured while attempting to open the {title} {linkType} into '{os.path.basename(self.linkBrowserDlg.otherBrowsEdit.text())}': {e}{Style.RESET_ALL}")
                    smart.managerLog(f"ERROR: Failed to open the {title} {linkType} into browser at path '{self.linkBrowserDlg.otherBrowsEdit.text()}': {e}")

class AboutAppGroup(SimpleExpandGroupSettingCard):
    """ Class for the informative text about SmartLinker in the About section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.QUESTION,
            "What exactly is SmartLinker?",
            "If you ever want to know about SmartLinker itself, just check out our little resume."
        )

        # Information
        self.aboutInfo = BodyLabel(
            "SmartLinker - Mastering URL Handling is an easy-to-use URL handler that allows you to manage conveniently and customize the way documents and web links are opened in web browsers. " \
            "Its main purpose is to help those who have many (a lot of) browsers installed on their computers and not enough hardware resources to manage them all at once.\n \n" \
            "For example, let's assume that there are five (5) browsers installed on your computer and some of them are already running. If your system's default one isn't at the same time, Windows will try to open a link you would want to visit (or maybe a local file of almost any type) with that known-as-default web browser, which would be useless since others can do the same job, and would overload your PC for nothing.\n \n" \
            "We already know how much RAM and CPU web browsers nowadays need and use to run a lot of integrated stuff like extensions, and to manage open tabs that many people are used to open in number. " \
            "Our little software is also meant to avoid that risk of overloading your system and overheating your piece of hardware unnecessarily.\n \n" \
            "So, to be simple, SmartLinker helps you redirect any browsing-based requests to any browser you have already running, and opens a new process of your preferred one for you if no one is. That way, you have full control on how your browsing experience is handled by your system."
        )
        self.aboutInfo.setWordWrap(True)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add_group(self.aboutInfo)

    def add_group(self, label):
        """ :AboutApp: Add informative text to the group. """
        wid = QWidget()
        wid.setFixedHeight(self.aboutInfo.sizeHint().height())
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)

        self.addGroupWidget(wid)

class ResourcesGroup(ExpandGroupSettingCard):
    """ Class for the Resources group in the About section """
    
    def __init__(self, parent=None):
        super().__init__(
            SegoeFontIcon.fromName("plugin"), # type: ignore
            "Resources",
        )
        self.creditsLabel = BodyLabel("For this software to work correctly, the following resources have been used:")
        self.creditsLabel.setContentsMargins(0, 0, 0, 10)

        # List of resources
        self.pyQtLine = QHBoxLayout()
        self.pyQtLine.setSpacing(10)
        self.pyQtLabel = BodyLabel("PyQt6 - The official Qt library for Python")
        self.pyQtLabel.setWordWrap(True)
        # self.pyQtLabel.setTextColor(themeColor())
        self.pyQtBtn = ToolButton(QIcon(smart.resourcePath("resources/images/icons/pyqt6_icon.ico")))
        self.pyQtBtn.setToolTip("Python GUIs website")
        self.pyQtBtn.installEventFilter(ToolTipFilter(self.pyQtBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.pyQtBtn2 = ToolButton(QIcon(smart.resourcePath("resources/images/icons/qtforpython_icon.ico")))
        self.pyQtBtn2.setToolTip("Qt Documentation website")
        self.pyQtBtn2.installEventFilter(ToolTipFilter(self.pyQtBtn2, showDelay=300, position=ToolTipPosition.TOP))
        self.pyQtLine.addWidget(self.pyQtLabel)
        self.pyQtLine.addWidget(self.pyQtBtn)
        self.pyQtLine.addWidget(self.pyQtBtn2)
        self.qFluentLine = QHBoxLayout()
        self.qFluentLine.setSpacing(10)
        self.qFluentLabel = BodyLabel("zhiyiYo/QFluentWidgets - A Qt-based GUI library for Python inspired by Windows 11's Fluent Design")
        self.qFluentLabel.setWordWrap(True)
        # self.qFluentLabel.setTextColor(themeColor())
        self.qFluentBtn = ToolButton(QIcon(smart.resourcePath("resources/images/icons/qfluentwidgets_icon.ico")))
        self.qFluentBtn.setToolTip("QFluentWidgets website")
        self.qFluentBtn.installEventFilter(ToolTipFilter(self.qFluentBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.qFluentBtn2 = ToolButton(FICO.GITHUB)
        self.qFluentBtn2.setToolTip("QFluentWidgets GitHub repository")
        self.qFluentBtn2.installEventFilter(ToolTipFilter(self.qFluentBtn2, showDelay=300, position=ToolTipPosition.TOP))
        self.qFluentLine.addWidget(self.qFluentLabel)
        self.qFluentLine.addWidget(self.qFluentBtn)
        self.qFluentLine.addWidget(self.qFluentBtn2)
        self.flaticonLine = QHBoxLayout()
        self.flaticonLine.setSpacing(10)
        self.flaticonLabel = BodyLabel("Flaticon - The largest database of free icons available in multiple formats")
        self.flaticonLabel.setWordWrap(True)
        # self.flaticonLabel.setTextColor(themeColor())
        self.flaticonBtn = ToolButton(QIcon(smart.resourcePath("resources/images/icons/flaticon_icon.ico")))
        self.flaticonBtn.setToolTip("Flaticon website")
        self.flaticonBtn.installEventFilter(ToolTipFilter(self.flaticonBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.flaticonLine.addWidget(self.flaticonLabel)
        self.flaticonLine.addWidget(self.flaticonBtn)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add_group()

    def add_group(self):
        """ :Resources: Add resources elements to the group. """
        wid = QWidget()
        # wid.setFixedHeight(60)
        widLayout = QVBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(self.creditsLabel)
        widLayout.addLayout(self.pyQtLine)
        widLayout.addLayout(self.qFluentLine)
        widLayout.addLayout(self.flaticonLine)

        self.addGroupWidget(wid)

class BrowserSelectDialog(MessageBoxBase):
    """ Class for the browser selection dialog box """

    def __init__(self, title: str, icon: QIcon | FICO | FluentFontIconBase, parent=None):
        super().__init__(parent)
        self.myBrowsList = smart.loadBrowsers()
        self.titleLabel = SubtitleLabel(title, self)
        self.browsIcon = IconWidget(icon)
        self.otherBrowsLine = QHBoxLayout()
        self.otherBrowsEdit = LineEdit()
        self.otherBrowsBrowse = ToolButton(FICO.FOLDER)

        self.browsIcon.setFixedSize(64, 64)
        self.browserCombo = ComboBox()
        self.browserCombo.setPlaceholderText("Select a SmartList browser")
        for browser in self.myBrowsList["MyBrowsers"]:
            self.browserCombo.addItem(browser["name"], smart.getFileIcon(browser["path"]))
        if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
            self.browserCombo.addItem(os.path.basename(cfg.get(cfg.mainBrowserPath)), smart.getFileIcon(cfg.get(cfg.mainBrowserPath)))
        self.browserCombo.addItem("Other browser", FICO.APPLICATION)
        if not self.browserCombo.currentText() == "Other browser":
            for browser in self.myBrowsList["MyBrowsers"]:
                if browser["name"] == self.browserCombo.currentText():
                    self.browsIcon.setIcon(smart.getFileIcon(browser["path"]))
                    break
                else: self.browsIcon.setIcon(icon)
        else: self.browsIcon.setIcon(FICO.APPLICATION)
        self.otherBrowsLine.setSpacing(10)
        self.otherBrowsEdit.setVisible(self.browserCombo.currentText() == "Other browser")
        self.otherBrowsEdit.setClearButtonEnabled(True)
        self.otherBrowsEdit.setPlaceholderText("Other browser path")
        self.otherBrowsBrowse.setVisible(self.browserCombo.currentText() == "Other browser")
        self.otherBrowsBrowse.setToolTip("Browse...")
        self.otherBrowsBrowse.installEventFilter(ToolTipFilter(self.otherBrowsBrowse))

        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))
        self.otherBrowsLine.addWidget(self.otherBrowsEdit)
        self.otherBrowsLine.addWidget(self.otherBrowsBrowse)

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.browsIcon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.browserCombo)
        self.viewLayout.addLayout(self.otherBrowsLine)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.setHidden(True)

        self.widget.setMinimumWidth(350)
        self.browserCombo.currentTextChanged.connect(lambda text: self.comboChangeListener(text))
        self.otherBrowsEdit.textChanged.connect(lambda text: (
            self.otherPathChangeListener(text),
            self.warningLabel.setHidden(True)
        ))
        self.otherBrowsBrowse.clicked.connect(lambda: self.otherBrowsEdit.setText(smart.browseFileDialog(parent, "Select another browser to load the link", "", "Executables (*.exe)")))

    def comboChangeListener(self, text):
        """ :BrowserSelect: Make actions whenever the current text of the combo is changed """
        if self.browserCombo.count() > 0:
            if not text == "Other browser":
                self.otherBrowsEdit.setHidden(True)
                self.otherBrowsBrowse.setHidden(True)
                for browser in self.myBrowsList["MyBrowsers"]:
                    if browser["name"] == text:
                        self.browsIcon.setIcon(smart.getFileIcon(browser["path"]))
                        break
                    else: self.browsIcon.setIcon(FICO.LINK)
            else:
                self.otherBrowsEdit.setHidden(False)
                self.otherBrowsBrowse.setHidden(False)
                if self.otherBrowsEdit.text() and os.path.exists(self.otherBrowsEdit.text()):
                    self.browsIcon.setIcon(smart.getFileIcon(self.otherBrowsEdit.text()))        
                else: self.browsIcon.setIcon(FICO.APPLICATION)
        else:
            self.warningLabel.setText("No browser is currently available...")
            self.warningLabel.setHidden(False)
    
    def otherPathChangeListener(self, text):
        """ :BrowserSelect: Make actions whenever the path entry content is changed """
        if self.browserCombo.currentIndex() == self.browserCombo.count() - 1:
            if text and os.path.exists(text): self.browsIcon.setIcon(smart.getFileIcon(text))
            else: self.browsIcon.setIcon(FICO.APPLICATION)

    def validate(self):
        if not self.browserCombo.currentIndex() == self.browserCombo.count() - 1:
            self.warningLabel.setHidden(True)
            return True
        else:
            if self.otherBrowsEdit.text() and os.path.exists(self.otherBrowsEdit.text()):
                self.warningLabel.setHidden(True)
                return True
            else:
                self.warningLabel.setText("The other browser path is not valid.")
                self.warningLabel.setHidden(False)
                return False

# HTML icon attribution - <a href="https://www.flaticon.com/free-icons/development" title="development icons">Development icons created by Bharat Icons - Flaticon</a>
