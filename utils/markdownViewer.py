from utils.SmartUtils import *

class MarkdownViewer(QWidget):
    """ Main class for the Markdown file/data viewer """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Markdown-Viewer")
        self.name = "SmartDown"
        self.renderMD = MarkdownIt().enable("table")
        self.markHistory = self.loadHistory()
        self.isHome: bool = True
        self.contentMD = None
        with open(smart.resourcePath("resources/assets/markdown-base-content.html")) as htmlReader: self.baseMD = htmlReader.read()
        with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()

        mainMDLayout = QVBoxLayout(self)
        mainMDLayout.setContentsMargins(50, 20, 0, 0)
        mainMDLayout.setSpacing(10)

        mainTopLine = QHBoxLayout()
        mainTopLine.setContentsMargins(0, 0, 40, 20)
        mainTopLine.setSpacing(10)
        
        mainMDLayout.addLayout(mainTopLine)
        
        mainTitleLine = QVBoxLayout()
        mainTitleLine.setContentsMargins(0, 0, 0, 0)
        mainTitleLine.setSpacing(0)
        mainTopLine.addLayout(mainTitleLine)
        
        self.title = ElidableSubtitleLabel(self.name)
        mainTitleLine.addWidget(self.title)
        
        self.subtitle = CaptionLabel("Subtitle")
        self.subtitle.setStyleSheet("color: gray")
        self.subtitle.setVisible(False)
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
                self.historyList.addAction(Action(FICO.DOCUMENT, path["path"], triggered=lambda checked, text=mdPath: self.loadMDFile(text)))
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
        self.mdContainer.setContentsMargins(0, 0, 0, 0)
        self.mdContainer.setStyleSheet(f"background: transparent; border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"}; border-left: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};")
        
        MDCLayout = QVBoxLayout(self.mdContainer)
        MDCLayout.setContentsMargins(1, 1, 0, 0)
        MDCLayout.setSpacing(0)

        self.browserMD = MarkWebView(self)
        self.browserMD.setAcceptDrops(True)
        self.browserMD.setHtml(self.baseMD, QUrl())
        MDCLayout.addWidget(self.browserMD)

        mainMDLayout.addWidget(self.mdContainer)
    
    def openMDFile(self, parent):
        """ Open a Markdown file from storage """
        title = self.title.text()
        path = smart.browseFileDialog(parent, "Open a file in the Markdown Viewer", "", "Markdown files (*.md; *.markdown)")
        if not path: self.title.setText(title)
        else: self.loadMDFile(path)

    def loadMDFile(self, path: str):
        fileExists: bool = False
        if os.path.exists(path):
            fileExists = True
            self.markUpdate(fileExists, path)
            with open(path, encoding="utf-8") as mdReader: self.contentMD = self.renderMD.render(mdReader.read())
            htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
            self.browserMD.setHtml(htmlContent, QUrl())
            self.isHome = False
            print(path.replace("/", "\\"))
            with open("markdownHtml.log", "w", encoding="utf-8") as htmlWriter: htmlWriter.write(htmlContent)
        # Retirer un chemin de l'historique à la sélection si le fichier est introuvable au chemin spécifié + notif d'erreur/avertissement
        # Notif d'erreur/avertissement si fichier ≠ .md/.markdown
    
    def markUpdate(self, exists: bool, path: str):
        pathExists: bool = False
        if exists:
            self.title.setText(f"{os.path.basename(path)} - {self.name}")
            self.subtitle.setText(path.replace("/", "\\"))
            self.subtitle.setVisible(True)
            for mdPath in self.markHistory["MarkdownHistory"]:
                if mdPath["path"] == path.replace("/", "\\"):
                    pathExists = True
                    break
            if not pathExists:
                self.markHistory["MarkdownHistory"].append({"path": path.replace("/", "\\")})
                self.saveHistory(self.markHistory)
                self.markHistory = self.loadHistory()
                self.history.setEnabled(True)
                self.historyList = RoundMenu(parent=self)
                for hPath in self.markHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda: self.openMDFile(hPath["path"])))
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
        self.subtitle.setText("")
        self.subtitle.setVisible(False)
        self.home.setEnabled(False)
        self.info.setEnabled(False)
        self.browserMD.setHtml(self.baseMD, QUrl())

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

class MarkWebView(FramelessWebEngineView):
    """ Class for the Markdown viewer webview """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dropParent = parent
    
    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event.mimeData().hasUrls():                                                  # type: ignore
            event.acceptProposedAction()                                                # type: ignore
            if self.dropParent.isHome: self.page().runJavaScript("onDragEnter()")       # type: ignore
    
    def dragLeaveEvent(self, event: QDragLeaveEvent | None):
        event.accept()                                                                  # type: ignore
        if self.dropParent.isHome: self.page().runJavaScript("onDragLeave()")           # type: ignore

    
    def dropEvent(self, event: QDropEvent | None):
        if event.mimeData().hasUrls():                                                  # type: ignore
            for url in event.mimeData().urls():                                         # type: ignore
                localPath = url.toLocalFile()
                if self.dropParent.isHome: self.page().runJavaScript("onDrop()")        # type: ignore
                self.dropParent.loadMDFile(localPath)
