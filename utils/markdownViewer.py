from utils.SmartUtils import *

class MarkdownViewer(QWidget):
    """ Main class for the Markdown file/data viewer """

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setObjectName("MarkdownViewer")
        self.name = "Markdown Viewer"
        self.baseSub = "Your embedded SmartLinker-friendly Markdown viewer"
        self.renderMD = MarkdownIt().enable("table")
        self.markHistory = self.loadHistory()
        self.isHome: bool = True
        self.contentMD = None
        with open(smart.resourcePath("resources/assets/markdown-base-content.html")) as htmlReader: self.baseMD = htmlReader.read()
        with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()

        mainMDLayout = QVBoxLayout(self)
        mainMDLayout.setContentsMargins(0, 20, 0, 0)
        
        mdLayout = QVBoxLayout()
        mdLayout.setContentsMargins(50, 0, 0, 0)
        mdLayout.setSpacing(10)

        mainMDLayout.addLayout(mdLayout)

        mainTopLine = QHBoxLayout()
        mainTopLine.setContentsMargins(0, 0, 40, 10)
        mainTopLine.setSpacing(10)
        
        mdLayout.addLayout(mainTopLine)
        
        mainTitleLine = QVBoxLayout()
        mainTitleLine.setContentsMargins(0, 0, 0, 0)
        mainTitleLine.setSpacing(0)
        mainTopLine.addLayout(mainTitleLine)
        
        self.title = SubtitleLabel(self.name)
        mainTitleLine.addWidget(self.title)
        
        self.subtitle = CaptionLabel(self.baseSub)
        self.subtitle.setStyleSheet("color: gray")
        mainTitleLine.addWidget(self.subtitle)
        
        mainTopLine.addStretch()
        
        self.home = ToolButton(FICO.HOME)
        self.home.setToolTip("Back to homepage")
        self.home.installEventFilter(ToolTipFilter(self.home))
        self.home.setEnabled(False)
        self.home.clicked.connect(self.backToHome)
        mainTopLine.addWidget(self.home)
        
        self.openFile = PushButton(FICO.FOLDER, "Open a Markdown file")
        self.openFile.clicked.connect(lambda: self.openMDFile(self))
        mainTopLine.addWidget(self.openFile)
        
        self.history = DropDownPushButton(FICO.HISTORY, "Open from history")
        if self.markHistory["MarkdownHistory"]:
            self.history.setEnabled(True)
            self.historyList = RoundMenu(parent=self)
            for path in self.markHistory["MarkdownHistory"]:
                mdPath = path["path"]
                self.historyList.addAction(Action(FICO.DOCUMENT, path["path"], triggered=lambda checked, text=mdPath, parent=parent: self.loadMDFile(text, parent, True)))
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history"))
            self.history.setMenu(self.historyList)
        else: self.history.setEnabled(False)
        mainTopLine.addWidget(self.history)
        
        self.info = ToolButton(FICO.INFO)
        self.info.setToolTip("About the document")
        self.info.installEventFilter(ToolTipFilter(self.info))
        self.info.setEnabled(False)
        mainTopLine.addWidget(self.info)
        
        self.mdContainer = QWidget(self)
        self.mdContainer.setObjectName("Container")
        self.mdContainer.setContentsMargins(1, 1, 0, 0)
        self.mdContainer.setStyleSheet(f"""
            QWidget#Container {{
                border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
                border-left: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
                {f'border-bottom: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};'
                 if cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners) else ""}
                background: transparent;
            }}
        """)
        
        MDCLayout = QVBoxLayout(self.mdContainer)
        MDCLayout.setContentsMargins(0, 0, 0, 0)
        MDCLayout.setSpacing(0)

        self.browserMD = MarkWebView(self)
        self.browserMD.setAcceptDrops(True)
        self.browserMD.setHtml(self.baseMD, QUrl("http://localhost"))
        MDCLayout.addWidget(self.browserMD)

        mdLayout.addWidget(self.mdContainer)
        
        self.updateSnack = UpdateSnack("MDSnackBase", self)
        self.updateSnack.setStyleSheet(f"#MDSnackBase {{background-color: rgba({smart.convertToRGB(themeColor().name())}, 0.25)}}")
        mainMDLayout.addWidget(self.updateSnack)
    
    def openMDFile(self, parent):
        """ Open a Markdown file from storage """
        title = self.title.text()
        path = smart.browseFileDialog(parent, "Open a file in the Markdown Viewer", "", "Markdown files (*.md; *.markdown)")
        if not path: self.title.setText(title)
        else: self.loadMDFile(path, parent)

    def loadMDFile(self, path: str, parent, history: bool = False):
        path = path.replace("/", "\\")
        if os.path.exists(path):
            if smart.isMarkdownExtension(path):
                if smart.getFileMimeType(path).startswith("text"):
                    self.markUpdate(True, path, parent)
                    with open(path, encoding="utf-8") as mdReader: self.contentMD = self.renderMD.render(mdReader.read())
                    htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
                    self.browserMD.setHtml(htmlContent, QUrl("http://localhost"))
                    self.isHome = False
                    print(path)
                    with open("markdownHtml.log", "w", encoding="utf-8") as htmlWriter: htmlWriter.write(htmlContent)
                else:
                    smart.warningNotify("Warning, be careful!", "The format of the provided file is not supported...", parent)
                    smart.managerLog(f"WARNING: Incompatible format of the provided file: {path}")
                    print(f"{Fore.YELLOW}WARNING!! The format of the provided file is not supported...{Style.RESET_ALL}")
                    if history: self.removeFromHistory(path, parent)
            else:
                smart.warningNotify("Warning, be careful!", "The provided file is not recognized as a Markdown file...", parent)
                smart.managerLog(f"WARNING: Provided file not recognized as a Markdown file: {path}")
                print(f"{Fore.YELLOW}WARNING!! The provided file is not recognized as a Markdown file...{Style.RESET_ALL}")
                if history: self.removeFromHistory(path, parent)
    
    def markUpdate(self, exists: bool, path: str, parent):
        pathExists: bool = False
        if exists:
            print(f"{os.path.basename(path)} - {self.name}")
            self.title.setText(f"{os.path.basename(path)} - {self.name}")
            self.subtitle.setText(path)
            self.subtitle.setVisible(True)
            for mdPath in self.markHistory["MarkdownHistory"]:
                if mdPath["path"] == path:
                    pathExists = True
                    break
            if not pathExists:
                self.markHistory["MarkdownHistory"].append({"path": path})
                self.saveHistory(self.markHistory)
                self.markHistory = self.loadHistory()
                self.history.setEnabled(True)
                self.historyList = RoundMenu(parent=self)
                for hPath in self.markHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda: self.loadMDFile(hPath["path"], parent)))
                self.historyList.addSeparator()
                self.historyList.addAction(Action(FICO.SETTING, "Manage history"))
                self.history.setMenu(self.historyList)
            self.home.setEnabled(True)
            self.info.setEnabled(True)
        else:
            self.home.setEnabled(False)
            self.info.setEnabled(False)

    def backToHome(self):
        self.isHome = True
        self.title.setText("Markdown Viewer")
        self.subtitle.setText("Your embedded SmartLinker-friendly Markdown viewer")
        self.home.setEnabled(False)
        self.info.setEnabled(False)
        self.browserMD.setHtml(self.baseMD, QUrl("http://localhost"))

    def loadHistory(self):
        try:
            with open(smart.resourcePath("bin/markdown_history.dat"), "rb") as histReader: return pickle.load(histReader)
        except: return {"MarkdownHistory": []}
    
    def saveHistory(self, history):
        try:
            with open(smart.resourcePath("bin/markdown_history.dat"), "wb") as histWriter: pickle.dump(history, histWriter)
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to save browser-related changes: {e}{Style.RESET_ALL}")
            smart.managerLog(f"ERROR: Failed to save browser-related changes: {e}")

    def removeFromHistory(self, value: str, parent):
        self.markHistory = self.loadHistory()
        self.newHistory = {"MarkdownHistory": []}
        for path in self.markHistory["MarkdownHistory"]:
            if path and path["path"] != value:
                self.newHistory["MarkdownHistory"].append({"path": path["path"].replace("/", "\\")})
        if self.newHistory["MarkdownHistory"]:
            self.historyList = RoundMenu(parent=self)
            for hPath in self.newHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda savedPath=hPath["path"], parent=parent: self.loadMDFile(savedPath, parent, True)))
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history"))
            self.history.setMenu(self.historyList)
        else:
            self.history.setEnabled(False)
            self.historyList.clear()
            smart.infoNotify("Empty history", "Your Markdown history is now empty.")
            self.backToHome()
        self.saveHistory(self.newHistory)
        self.markHistory = self.loadHistory()

class MarkWebView(FramelessWebEngineView):
    """ Class for the Markdown viewer webview """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dropParent = parent
    
    def dragEnterEvent(self, e: QDragEnterEvent | None):
        if e.mimeData().hasUrls():                                                  # type: ignore
            e.acceptProposedAction()                                                # type: ignore
            if self.dropParent.isHome: self.page().runJavaScript("onDragEnter()")       # type: ignore
    
    def dragLeaveEvent(self, e: QDragLeaveEvent | None):
        e.accept()                                                                  # type: ignore
        if self.dropParent.isHome: self.page().runJavaScript("onDragLeave()")           # type: ignore

    
    def dropEvent(self, e: QDropEvent | None):
        if e.mimeData().hasUrls():                                                  # type: ignore
            for url in event.mimeData().urls():                                         # type: ignore
                localPath = url.toLocalFile()
                if self.dropParent.isHome: self.page().runJavaScript("onDrop()")        # type: ignore
                self.dropParent.loadMDFile(localPath)
