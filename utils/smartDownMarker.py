from utils.SmartUtils import *

# =========================================================

class CustomTitleBar(StandardTitleBar):
    """ Custom title bar """

    def __init__(self, parent):
        super().__init__(parent)
        
        self.minBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.maxBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.closeBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.minBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))
        self.minBtn.setPressedColor(QColor("white"))
        self.maxBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))
        self.maxBtn.setPressedColor(QColor("white"))
        self.closeBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else QColor(cfg.get(cfg.qAccentColor)))

class SmartDownMarkerGUI(FramelessWindow):
    """ Class for the **SmartDown** (or *Markdown Viewer*) window """

    def __init__(self, mdFilePath: str, parent = None):
        super().__init__(parent=parent)
        self.mdPath = mdFilePath if mdFilePath else "Untitled"
        self.title = "Smart DownMarker"
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(smIco.renderIcon(smIco.MARKDOWN))
        self.setWindowTitle(f"{self.mdPath} - {self.title} | {SmartLinkerName}")
        self.resize(1280, 720)
        self.setMinimumSize(1120, 630)
        self.move(40, 25)
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        self.setStyleSheet((("background: white" if not smart.isDarkMode() else "") if cfg.get(cfg.appTheme) == "Auto" else
                           "" if cfg.get(cfg.appTheme) == "Dark" else "background: white") if not cfg.get(cfg.micaEffect) else "")
        try:
            fontDB = QFontDatabase.addApplicationFont(smart.resourcePath("resources\\fonts\\CascadiaCode.ttf"))
            fontEditFam = QFontDatabase.applicationFontFamilies(fontDB)[6]
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to load the editor font: {e}{Style.RESET_ALL}")
            fontEditFam = "Consolas"
        finally: fontEditor = fontEditFam
        try:
            fontDB = QFontDatabase.addApplicationFont(smart.resourcePath("resources\\fonts\\SegoeFont.ttf"))
            fontUIFam = QFontDatabase.applicationFontFamilies(fontDB)[12]
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to load the editor font: {e}{Style.RESET_ALL}")
            fontUIFam = "Segoe UI"
        finally: fontUI = fontUIFam
        fontEditor_QSS = f"font-family: {fontEditor}, 'Consolas', 'Courier New', monospace;"
        fontUI_QSS = f"font-family: {fontUI}, 'Segoe UI', sans-serif;"

        self.validPath = os.path.exists(self.mdPath)
        self.markHistory = self.loadHistory()
        self.historyManageDlg = None
        self.renderMD = MarkdownIt().enable("table")
        self.content = ""
        self.contentMD = None
        self.isHome: bool = True
        self.editMode: bool = False
        self.symbols = [
            '<', '>', '[', ']', '{', '}', '(', ')', '/', '\\', '"', "'", '.', ',', ';', ':', '-', '_', '=', '&', '|', '`', '?', '!', '@', '#', '^',
            '¨', '$', '%', '~', '°', '*', '+', '§', 'µ'
        ]
        with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: self.baseMD = (baseReader.read().replace("Markdown Viewer", self.title)).replace("Open a Markdown file", "Open")
        with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        
        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        self.mdNew = Action(FICO.DOCUMENT, "New", triggered=self.newMDFile)
        self.mdOpen = Action(FICO.FOLDER, "Open", triggered=lambda: self.openMDFile(self))
        self.openRecent = TransparentDropDownPushButton(FICO.HISTORY, "Open recent")
        self.openRecent.setFixedHeight(34)
        setFont(self.openRecent, 12)
        if self.markHistory["MarkdownHistory"]:
            self.openRecent.setEnabled(True)
            self.historyList = RoundMenu(parent=self)
            for path in self.markHistory["MarkdownHistory"]:
                mdPath = path["path"]
                self.historyList.addAction(Action(FICO.DOCUMENT, path["path"], triggered=lambda checked, text=mdPath, parent=self: self.loadMDFile(text, parent)))
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=self: self.openHistoryManager(parent)))
            self.openRecent.setMenu(self.historyList)
        else: self.openRecent.setEnabled(False)
        self.mdEdit = Action(FICO.EDIT, "Edit", checkable=True, triggered=lambda checked: self.toggleEditMode(checked))
        self.mdEdit.setChecked(False)
        self.mdSave = TransparentToolButton(FICO.SAVE)
        self.mdSave.setFixedHeight(34)
        self.mdSave.setToolTip("Save")
        self.mdSave.installEventFilter(ToolTipFilter(self.mdSave))
        self.mdSave.setEnabled(False)
        self.mdSaveAs = TransparentToolButton(FICO.SAVE_AS)
        self.mdSaveAs.setFixedHeight(34)
        self.mdSaveAs.setToolTip("Save as...")
        self.mdSaveAs.installEventFilter(ToolTipFilter(self.mdSaveAs))
        self.mdSaveAs.setEnabled(False)
        self.mdUndo = TransparentToolButton(SegoeFontIcon.fromName("undo"))
        self.mdUndo.setFixedHeight(34)
        self.mdUndo.setToolTip("Undo")
        self.mdUndo.installEventFilter(ToolTipFilter(self.mdUndo))
        self.mdUndo.setEnabled(False)
        self.mdRedo = TransparentToolButton(SegoeFontIcon.fromName("redo"))
        self.mdRedo.setFixedHeight(34)
        self.mdRedo.setToolTip("Redo")
        self.mdRedo.installEventFilter(ToolTipFilter(self.mdRedo))
        self.mdRedo.setEnabled(False)
        self.mdCut = TransparentToolButton(FICO.CUT)
        self.mdCut.setFixedHeight(34)
        self.mdCut.setToolTip("Cut")
        self.mdCut.installEventFilter(ToolTipFilter(self.mdCut))
        self.mdCut.setEnabled(False)
        self.mdCopy = TransparentToolButton(FICO.COPY)
        self.mdCopy.setFixedHeight(34)
        self.mdCopy.setToolTip("Copy")
        self.mdCopy.installEventFilter(ToolTipFilter(self.mdCopy))
        self.mdCopy.setEnabled(False)
        self.mdPaste = TransparentToolButton(FICO.PASTE)
        self.mdPaste.setFixedHeight(34)
        self.mdPaste.setToolTip("Paste")
        self.mdPaste.installEventFilter(ToolTipFilter(self.mdPaste))
        self.mdPaste.setEnabled(False)
        self.mdShare = Action(FICO.SHARE, "Share")
        self.mdShare.setEnabled(self.validPath)
        self.mdInfo = TransparentToolButton(FICO.INFO)
        self.mdInfo.setFixedHeight(34)
        self.mdInfo.setToolTip("About the document")
        self.mdInfo.installEventFilter(ToolTipFilter(self.mdInfo))
        self.mdInfo.setEnabled(bool(self.validPath))
        self.mdHome = TransparentToolButton(FICO.HOME)
        self.mdHome.setFixedHeight(34)
        self.mdHome.setToolTip("Back to home")
        self.mdHome.installEventFilter(ToolTipFilter(self.mdHome))
        self.mdHome.setEnabled(not self.isHome)
        self.mdSettings = TransparentToggleToolButton(FICO.SETTING)
        self.mdSettings.setFixedHeight(34)
        self.mdSettings.setChecked(False)
        self.mdSettings.setToolTip("Settings")
        self.mdSettings.installEventFilter(ToolTipFilter(self.mdSettings))
        
        self.commandBar.addActions([self.mdNew, self.mdOpen])
        self.commandBar.addWidget(self.openRecent)
        self.commandBar.addSeparator()
        self.commandBar.addAction(self.mdEdit)
        self.commandBar.addWidget(self.mdSave)
        self.commandBar.addWidget(self.mdSaveAs)
        self.commandBar.addWidget(self.mdUndo)
        self.commandBar.addWidget(self.mdRedo)
        self.commandBar.addWidget(self.mdCut)
        self.commandBar.addWidget(self.mdCopy)
        self.commandBar.addWidget(self.mdPaste)
        self.commandBar.addAction(self.mdShare)
        self.commandBar.addWidget(self.mdInfo)
        self.commandBar.addSeparator()
        self.commandBar.addWidget(self.mdHome)
        self.commandBar.addWidget(self.mdSettings)

        mainLayout.addWidget(self.commandBar)

        MDCLayout = QHBoxLayout()
        MDCLayout.setContentsMargins(0, 0, 0, 0)
        MDCLayout.setSpacing(0)

        self.editorBox = QWidget()
        self.editorBox.setObjectName("EditorBox")
        self.editorBox.setContentsMargins(0, 0, 0, 0)
        self.editorBox.setStyleSheet(f"#EditorBox {{ border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"}; }}")
        self.editorBox.setFixedWidth(self.width() // 2)
        self.editorBox.setEnabled(self.mdEdit.isChecked())
        self.editorBox.setVisible(self.mdEdit.isChecked())
        editorLayout = QVBoxLayout(self.editorBox)
        editorLayout.setContentsMargins(0, 0, 0, 0)
        editorLayout.setSpacing(0)
        editorZone = QHBoxLayout()
        editorZone.setContentsMargins(0, 0, 0, 0)
        editorZone.setSpacing(0)
        
        self.mdEditor = MarkEditor(fontEditor)
        self.mdEditor.installEventFilter(self)
        self.mdEditor.textChanged.connect(self.editorUpdate)
        self.mdEditor.cursorPositionChanged.connect(self.editorStatusUpdate)
        self.mdEditor.selectionChanged.connect(self.editorSelectionUpdate)

        self.mdSave.clicked.connect(lambda: self.saveMDFile(self.mdPath, self.mdEditor.text(), False, self))
        self.mdSaveAs.clicked.connect(lambda: self.saveMDFile(self.mdPath, self.mdEditor.text(), True, self))
        self.mdUndo.clicked.connect(self.mdEditor.undo if self.mdEditor else None)
        self.mdRedo.clicked.connect(self.mdEditor.redo if self.mdEditor else None)
        self.mdCut.clicked.connect(lambda: (
            self.mdEditor.cut() if self.mdEditor else None,
            self.mdPaste.setEnabled(self.mdEditor.canPaste())
        ))
        self.mdCopy.clicked.connect(lambda: (
            self.mdEditor.copy if self.mdEditor else None,
            self.mdPaste.setEnabled(self.mdEditor.canPaste())
        ))
        self.mdPaste.clicked.connect(self.mdEditor.paste if self.mdEditor else None)
        self.mdHome.clicked.connect(self.backToHome)
        self.mdSettings.toggled.connect(lambda checked: self.toggleSettings(checked))

        self.editorSymbols = SingleDirectionScrollArea(self, Qt.Orientation.Horizontal)
        self.editorSymbols.setContentsMargins(0, 0, 0, 0)
        self.editorSymbols.setWidgetResizable(True)
        self.editorSymbols.setMaximumHeight(41)
        self.editorSymbols.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editorSymbols.enableTransparentBackground()
        self.editorSymbols.setStyleSheet(f"""
            SingleDirectionalScrollArea {{
                border-radius: 0px;
                border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
            }}
        """)
        self.editorSymbolsWidget = QWidget()
        self.editorSymbols.setWidget(self.editorSymbolsWidget)
        self.editorSymbolsLayout = QHBoxLayout(self.editorSymbolsWidget)
        self.editorSymbolsLayout.setContentsMargins(10, 10, 10, 10)
        self.editorSymbolsLayout.setSpacing(20)
        self.editorSymbolsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.symTab = CaptionLabel("Tab")
        self.symTab.setStyleSheet(f"{fontEditor_QSS} font-size: 16px;")
        self.symTab.mousePressEvent = lambda ev: self.mdEditor.insertTab()
        self.editorSymbolsLayout.addWidget(self.symTab)
        for sym in self.symbols:
            symbol = CaptionLabel(sym)
            symbol.setStyleSheet(f"{fontEditor_QSS} font-size: 16px;")
            symbol.mousePressEvent = lambda ev, symbol=sym: self.mdEditor.insertAt(symbol, *self.mdEditor.getCursorPosition())
            self.editorSymbolsLayout.addWidget(symbol)
        
        self.editorStatus = QHBoxLayout()
        self.editorStatus.setContentsMargins(10, 0, 10, 10)
        self.editorStatus.setSpacing(20)
        self.statusLineCol = CaptionLabel()
        self.statusLineCol.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusLineCol.setStyleSheet(fontUI_QSS)
        self.editorStatus.addWidget(self.statusLineCol)
        self.editorStatus.addStretch()
        self.statusEncoding = CaptionLabel()
        self.statusEncoding.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusEncoding.setStyleSheet(fontUI_QSS)
        self.editorStatus.addWidget(self.statusEncoding)
        self.editorStatus.addStretch()
        self.statusCapsLock = CaptionLabel("Caps Lock")
        self.statusCapsLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusCapsLock.setStyleSheet(fontUI_QSS)
        self.statusCapsLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x14) & 1))
        self.editorStatus.addWidget(self.statusCapsLock)
        self.statusNumLock = CaptionLabel("Num Lock")
        self.statusNumLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusNumLock.setStyleSheet(fontUI_QSS)
        self.statusNumLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x90) & 1))
        self.editorStatus.addWidget(self.statusNumLock)
        self.editorStatus.addStretch()
        self.statusTotalChars = CaptionLabel()
        self.statusTotalChars.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalChars.setStyleSheet(fontUI_QSS)
        self.editorStatus.addWidget(self.statusTotalChars)
        self.statusTotalLines = CaptionLabel()
        self.statusTotalLines.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalLines.setStyleSheet(f"font-family: {fontUI}, 'Segoe UI', sans-serif;")
        self.editorStatus.addWidget(self.statusTotalLines)
        self.statusTotalWords = CaptionLabel()
        self.statusTotalWords.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalWords.setStyleSheet(fontUI_QSS)
        self.editorStatus.addWidget(self.statusTotalWords)

        editorZone.addWidget(self.mdEditor)
        editorLayout.addLayout(editorZone)
        editorLayout.addWidget(self.editorSymbols)
        editorLayout.addLayout(self.editorStatus)
        MDCLayout.addWidget(self.editorBox)

        self.mdContainer = QWidget(self)
        self.mdContainer.setObjectName("Container")
        self.mdContainer.setContentsMargins(0, 0, 0, 0)
        self.mdContainer.setStyleSheet(f"""
            #Container {{
                border: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
                border-bottom: none;
                background: transparent;
            }}
        """)
        displayLayout = QVBoxLayout(self.mdContainer)
        displayLayout.setContentsMargins(1, 1, 1, 0)
        self.mdDisplayer = MarkWebView(self)
        self.mdDisplayer.setAcceptDrops(True)
        self.mdDisplayer.setHtml(self.baseMD, QUrl())
        displayLayout.addWidget(self.mdDisplayer)
        MDCLayout.addWidget(self.mdContainer)

        mainLayout.addLayout(MDCLayout)

        self.titleBar.raise_()
        self.mdSave.setEnabled(False)
        self.loadMDFile(self.mdPath, self)

    def newMDFile(self):
        if self.canSave() or self.windowTitle().startswith("*"):
            print("Unsaved!")
            self.backToHome()
        else: self.backToHome()
    
    def openMDFile(self, parent):
        """ Open a Markdown file from storage """
        title = self.mdPath
        path = smart.browseFileDialog(parent, "Open a file in the Markdown Viewer", "", "Markdown files (*.md; *.markdown)")
        if not path: self.setWindowTitle(f"{title} - {self.title} | {SmartLinkerName}")
        else: self.loadMDFile(path, parent)

    def loadMDFile(self, path: str, parent, history: bool = False):
        if os.path.exists(path):
            if path.endswith(".md") or path.endswith(".markdown"):
                if smart.getFileMimeType(path).startswith("text"):
                    with open(path, encoding="utf-8") as mdReader: self.content = mdReader.read()
                    self.contentMD = self.renderMD.render(self.content)
                    htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
                    self.mdEditor.setText(self.content)
                    self.mdDisplayer.setHtml(htmlContent, QUrl())
                    self.isHome = False
                    self.mdHome.setEnabled(True)
                    self.mdInfo.setEnabled(True)
                    print(path.replace("/", "\\"))
                    self.mdPath = path.replace("/", "\\")
                    self.setWindowTitle(f"{self.mdPath} - {self.title} | {SmartLinkerName}")
                    with open("markdownContent.log", "w", encoding="utf-8") as mdWriter: mdWriter.write(self.content)
                    with open("markdownHtml.log", "w", encoding="utf-8") as htmlWriter: htmlWriter.write(htmlContent)
                else:
                    smart.warningNotify("Warning, be careful!", "The format of the provided file is not supported...", parent)
                    if history: self.removeFromHistory(path, parent)
            else:
                smart.warningNotify("Warning, be careful!", "The provided file is not recognised as a Markdown file...", parent)
                if history: self.removeFromHistory(path, parent)

    def saveMDFile(self, path: str, content: str, saveAs: bool, parent):
        self.validPath = os.path.exists(self.mdPath)
        if saveAs or not self.validPath:
            newPath = smart.saveFileDialog(parent, f"Save a Markdown file from {SmartLinkerName}", os.path.dirname(self.mdPath) if self.validPath else "", "Markdown files (*.md; *.markdown)").replace("/", "\\")
            if newPath:
                with open(newPath, "w", encoding="utf-8") as mdWriter: mdWriter.write(content)
                self.mdPath = newPath
                self.setWindowTitle(f"{self.mdPath} - {self.title} | {SmartLinkerName}")
                smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
            print(newPath)
        else:
            with open(self.mdPath, 'w', encoding="utf-8") as mdWriter: mdWriter.write(content)
            self.setWindowTitle(f"{self.windowTitle()[1:] if self.windowTitle().startswith('*') else self.windowTitle()}")
            print(path)
            smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
        self.mdSave.setEnabled(False)

    def backToHome(self):
        self.mdPath = "Untitled"
        self.validPath = False
        self.isHome = True
        self.mdHome.setEnabled(False)
        self.mdUndo.setEnabled(False)
        self.mdRedo.setEnabled(False)
        self.mdInfo.setEnabled(False)
        self.mdEditor.setText("")
        self.mdDisplayer.setHtml(self.baseMD, QUrl())
        self.setWindowTitle(f"Untitled - {self.title} | {SmartLinkerName}")

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

    def openHistoryManager(self, parent):
        history = self.loadHistory()
        if not self.historyManageDlg: self.historyManageDlg = ManageHistoryDialog(history, parent)
        else:
            self.historyManageDlg = None
            self.openHistoryManager(parent)
        self.historyManageDlg.exec() # type: ignore

    def removeFromHistory(self, value: str, parent):
        self.markHistory = self.loadHistory()
        self.newHistory = {"MarkdownHistory":[]}
        for path in self.markHistory["MarkdownHistory"]:
            if path["path"] != value:
                self.newHistory["MarkdownHistory"].append({"path": path["path"].replace("/", "\\")})
        if self.newHistory["MarkdownHistory"]:
            self.historyList = RoundMenu(parent=self)
            for hPath in self.newHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda savedPath=hPath["path"], parent=parent: self.loadMDFile(savedPath, parent, True)))
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history"))
            self.openRecent.setMenu(self.historyList)
        else:
            self.openRecent.setEnabled(False)
            self.historyList.clear()
            smart.infoNotify("Empty history", "Your Markdown history is now empty.")
            self.backToHome()
        self.saveHistory(self.newHistory)
        self.markHistory = self.loadHistory()

    def toggleEditMode(self, check: bool):
        self.editMode = check
        self.editorBox.setEnabled(check)
        self.editorBox.setVisible(check)
        if not check:
            self.mdSave.setEnabled(False)
            self.mdSaveAs.setEnabled(False)
            self.mdUndo.setEnabled(False)
            self.mdRedo.setEnabled(False)
            self.mdCut.setEnabled(False)
            self.mdCopy.setEnabled(False)
            self.mdPaste.setEnabled(False)
        else:
            # self.mdSave.setEnabled(True)
            self.mdSaveAs.setEnabled(True)
            self.mdUndo.setEnabled(self.mdEditor.isUndoAvailable())
            self.mdRedo.setEnabled(self.mdEditor.isRedoAvailable())
            self.mdCut.setEnabled(self.mdEditor.hasSelectedText())
            self.mdCopy.setEnabled(self.mdEditor.hasSelectedText())
            self.mdPaste.setEnabled(self.mdEditor.canPaste())
        self.editorUpdate()

    def toggleSettings(self, check: bool):
        self.mdDisplayer.setEnabled(not check)
        self.mdDisplayer.setVisible(not check)
        self.mdNew.setEnabled(not check)
        self.mdOpen.setEnabled(not check)
        self.openRecent.setEnabled(not check)
        self.mdEdit.setEnabled(not check)
        if check:
            self.mdSave.setEnabled(False)
            self.mdSaveAs.setEnabled(False)
            self.mdUndo.setEnabled(False)
            self.mdRedo.setEnabled(False)
            self.mdCut.setEnabled(False)
            self.mdCopy.setEnabled(False)
            self.mdPaste.setEnabled(False)
            self.mdShare.setEnabled(False)
            self.mdInfo.setEnabled(False)
            self.mdHome.setEnabled(False)
            self.editorBox.setEnabled(False)
            self.editorBox.setVisible(False)
        else:
            self.mdSave.setEnabled(self.editMode and self.canSave())
            self.mdSaveAs.setEnabled(self.editMode)
            self.mdUndo.setEnabled(self.editMode and self.mdEditor.isUndoAvailable())
            self.mdRedo.setEnabled(self.editMode and self.mdEditor.isRedoAvailable())
            self.mdCut.setEnabled(self.editMode and self.mdEditor.hasSelectedText())
            self.mdCopy.setEnabled(self.editMode and self.mdEditor.hasSelectedText())
            self.mdPaste.setEnabled(self.editMode and self.mdEditor.canPaste())
            self.mdShare.setEnabled(self.validPath)
            self.mdInfo.setEnabled(self.validPath)
            self.mdHome.setEnabled(not self.isHome)
            self.editorBox.setEnabled(self.editMode)
            self.editorBox.setVisible(self.editMode)

    def editorUpdate(self):
        text =  self.mdEditor.text()
        self.validPath = os.path.exists(self.mdPath)
        if text:
            if self.validPath:
                self.mdSave.setEnabled(self.canSave())
                self.setWindowTitle(f"{"*" if self.canSave() else ""}{self.mdPath} - {self.title} | {SmartLinkerName}")
            else:
                self.mdSave.setEnabled(bool(text))
                self.setWindowTitle(f"*Untitled - {self.title} | {SmartLinkerName}")
            markText = self.renderMD.render(text)
            htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{markText}\n</body>\n</html>'
            self.mdDisplayer.setHtml(htmlContent, QUrl())
            self.mdUndo.setEnabled(self.mdEditor.isUndoAvailable() if self.mdEdit.isChecked() else False)
            self.mdRedo.setEnabled(self.mdEditor.isRedoAvailable() if self.mdEdit.isChecked() else False)
            self.mdHome.setEnabled(True)
        else:
            self.mdDisplayer.setHtml(self.baseMD, QUrl())
            self.mdSave.setEnabled(False if not self.validPath else self.canSave())
            self.mdHome.setEnabled(False)
            self.setWindowTitle(f"{'*' if self.canSave() else ''}{"Untitled" if not self.validPath else self.mdPath} - {self.title} | {SmartLinkerName}")
        self.editorStatusUpdate()
    
    def editorSelectionUpdate(self):
        self.editorStatusUpdate()
        selectedChars = self.mdEditor.selectedText()
        if selectedChars:
            self.mdCut.setEnabled(True)
            self.mdCopy.setEnabled(True)
        else:
            self.mdCut.setEnabled(False)
            self.mdCopy.setEnabled(False)

    def editorStatusUpdate(self):
        self.statusCapsLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x14) & 1))
        self.statusNumLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x90) & 1))

        text = self.mdEditor.text()

        line, col = self.mdEditor.getCursorPosition()
        encod = "UTF-8"

        totalChars = len(text)
        selectedChars = len(self.mdEditor.selectedText())
        lineChars = self.mdEditor.lineLength(line)
        totalLines = self.mdEditor.lines()
        totalWords = len(text.split())
        
        self.statusLineCol.setText(f'Ln {line + 1}, Col {col + 1}{f' ({selectedChars} selected)' if selectedChars else ''}')
        self.statusEncoding.setText(encod)
        self.statusTotalChars.setText(f'{totalChars} ch. (on line: {lineChars})')
        self.statusTotalLines.setText(f'{totalLines} line{"s" if totalLines > 1 else ""}')
        self.statusTotalWords.setText(f'{totalWords} word{"s" if totalWords > 1 else ""}')

    def canSave(self) -> bool:
        text = self.mdEditor.text()
        self.validPath = os.path.exists(self.mdPath)
        if text:
            if self.validPath:
                with open(self.mdPath, 'r', encoding="utf-8") as origReader: origText = origReader.read()
                return not origText == text
        return False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.editorBox.setFixedWidth(self.width() // 2)

    def eventFilter(self, obj, event):
        if obj == self.mdEditor and event.type() in [QEvent.Type.KeyPress, QEvent.Type.KeyRelease]: self.editorStatusUpdate()
        return super().eventFilter(obj, event)

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
                self.dropParent.loadMDFile(localPath, self.dropParent)

class MarkEditor(QsciScintilla):
    """ Class for the SmartLinker-adapted Markdown editor """

    def __init__(self, font: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {"#282C34" if smart.isDarkMode() else "#EFF1F5"};")
        self.setSelectionBackgroundColor(cfg.get(cfg.accentColor))
        
        # Font config
        self.editorFont = QFont(font, 12)
        self.setFont(self.editorFont)

        # Syntax highlighting (lexer)
        self.editorLexer = QsciLexerMarkdown(self)
        self.editorLexer.setFont(self.editorFont)
        self.editorLexer.setColor(QColor("#ABB2BF") if smart.isDarkMode() else QColor("#4C4F69"), 0)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header1)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header2)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header3)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header4)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header5)
        self.editorLexer.setColor(QColor("#E06C75") if smart.isDarkMode() else QColor("#D20F39"), QsciLexerMarkdown.Header6)
        self.editorLexer.setColor(QColor("#D19A66") if smart.isDarkMode() else QColor("#FE640B"), QsciLexerMarkdown.EmphasisUnderscores)
        self.editorLexer.setColor(QColor("#D19A66") if smart.isDarkMode() else QColor("#FE640B"), QsciLexerMarkdown.StrongEmphasisUnderscores)
        self.editorLexer.setColor(QColor("#98C379") if smart.isDarkMode() else QColor("#40A02B"), QsciLexerMarkdown.EmphasisAsterisks)
        self.editorLexer.setColor(QColor("#98C379") if smart.isDarkMode() else QColor("#40A02B"), QsciLexerMarkdown.StrongEmphasisAsterisks)
        self.editorLexer.setColor(QColor("#5C6370") if smart.isDarkMode() else QColor("#8C8FA1"), QsciLexerMarkdown.StrikeOut)
        self.editorLexer.setColor(QColor("#C678DD") if smart.isDarkMode() else QColor("#8839EF"), QsciLexerMarkdown.Link)
        self.editorLexer.setColor(QColor("#61AFEF") if smart.isDarkMode() else QColor("#1E66F5"), QsciLexerMarkdown.CodeBackticks)
        self.editorLexer.setColor(QColor("#E5C07B") if smart.isDarkMode() else QColor("#DF8E1D"), QsciLexerMarkdown.CodeDoubleBackticks)
        self.setLexer(self.editorLexer)

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationWidth(4)
        self.setAutoIndent(True)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)

        # Margin #0: number line
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsFont(self.editorFont)
        self.setMarginsBackgroundColor(QColor("#282C34") if smart.isDarkMode() else QColor("#E6E9EF"))
        self.setMarginsForegroundColor(QColor("#4B5263") if smart.isDarkMode() else QColor("#ACB0BE"))

        # Margin #2: code folding symbols
        """ self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(2, 20)
        self.setMarginSensitivity(2, True)
        self.setMarginBackgroundColor(2, QColor("#282C34") if not smart.isDarkMode() else QColor("#E6E9EF")) """

        # Current line highlighting (caret)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#4B5263") if smart.isDarkMode() else QColor("#ACB0BE"))

        # Brace/Pair matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

    def canPaste(self):
        return QApplication.clipboard().mimeData().hasText()    # type: ignore

    def insertTab(self):
        line, col = self.getCursorPosition()
        if self.hasSelectedText(): self.indent(line)
        else: self.insertAt("\t", line, col)

class ManageHistoryDialog(MessageBoxBase):
    """ Class for the "Manage history" dialog box """

    def __init__(self, history: dict[str, list], parent=None):
        super().__init__(parent)
        self.markdownHistory = history

        self.topLine = QHBoxLayout()
        self.topLine.setContentsMargins(0, 0, 0, 0)
        self.topLine.setSpacing(15)
        # self.topLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon = IconWidget(FICO.HISTORY)
        self.icon.setFixedSize(24, 24)
        self.title = TitleLabel("Manage your history")
        self.description = BodyLabel("Select from the list below the different Markdown file paths you want to work on.", self)
        self.description.setWordWrap(True)

        historyBtnLayout = QHBoxLayout()
        # historyBtnLayout.setContentsMargins(0, 0, 0, 0)
        # historyBtnLayout.setSpacing(5)
        self.openBtn = PrimaryPushButton(FICO.LINK, "Load file", self)
        self.openBtn.setEnabled(False)
        self.removeBtn = PushButton(FICO.REMOVE, "Remove", self)
        self.removeBtn.setEnabled(False)
        self.selectAllBtn = PushButton(SegoeFontIcon.fromName("selectAll"), "Select All", self)
        self.deselectAllBtn = PushButton(SegoeFontIcon.fromName("grid"), "Deselect All", self)
        self.deselectAllBtn.setEnabled(False)
        historyBtnLayout.addWidget(self.openBtn)
        historyBtnLayout.addWidget(self.removeBtn)
        historyBtnLayout.addWidget(self.selectAllBtn)
        historyBtnLayout.addWidget(self.deselectAllBtn)

        self.historyList = ListWidget()
        self.historyList.setMinimumHeight(150)
        self.historyList.setAlternatingRowColors(True)
        self.historyList.setSelectRightClickedRow(True)
        self.historyList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        for path in self.markdownHistory["MarkdownHistory"]: self.historyList.addItem(path["path"])

        # self.openBtn.clicked.connect()
        # self.removeBtn.clicked.connect()
        self.selectAllBtn.clicked.connect(self.selectAll)
        self.deselectAllBtn.clicked.connect(self.deselectAll)
        self.historyList.itemSelectionChanged.connect(lambda: (
            self.openBtn.setEnabled(len(self.historyList.selectedItems()) == 1),
            self.removeBtn.setEnabled(len(self.historyList.selectedItems()) > 0),
            self.deselectAllBtn.setEnabled(len(self.historyList.selectedItems()) > 0)
        ))

        self.viewLayout.setSpacing(20)
        
        self.viewLayout.addLayout(self.topLine)
        self.topLine.addWidget(self.icon)
        self.topLine.addWidget(self.title)
        self.viewLayout.addWidget(self.description)
        self.viewLayout.addLayout(historyBtnLayout)
        self.viewLayout.addWidget(self.historyList)

        self.yesButton.setText("Save changes")
        self.yesButton.setEnabled(False)
        self.widget.setMinimumWidth(500)

    def selectAll(self):
        self.historyList.selectAll()
    
    def deselectAll(self):
        self.historyList.clearSelection()
