from utils.SmartUtils import *

# =========================================================

TITLE = "Smart DownMarker (BETA)"

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
    """ Class for the **Smart DownMarker** (or *Markdown Viewer*) window """

    def __init__(self, mdFilePath: str, parent = None):
        super().__init__(parent=parent)
        self.mdPath = mdFilePath if mdFilePath else "Untitled"
        self.mdTitleBar = CustomTitleBar(self)
        self.setTitleBar(self.mdTitleBar)
        self.setWindowIcon(smIco.renderIcon(smIco.MARKDOWN))
        self.setWindowTitle(f"{self.mdPath} - {TITLE} | {SmartLinkerName}")
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

        self.validPath: bool = os.path.exists(self.mdPath)
        self.markHistory = self.loadHistory()
        self.historyManageDlg = None
        self.customCSSDlg = None
        self.customHomeDlg = None
        self.renderMD = MarkdownIt().use(tasklists_plugin).enable("table")
        self.content = ""
        self.contentMD = None
        self.htmlContent = None
        self.isHome: bool = True
        self.editMode: bool = markCfg.get(markCfg.startInEditMode)
        self.symbols = [
            '<', '>', '[', ']', '{', '}', '(', ')', '/', '\\', '"', "'", '.', ',', ';', ':', '-', '_', '=', '&', '|', '`', '?', '!', '@', '#', '^',
            '¨', '$', '%', '~', '°', '*', '+', '§', 'µ', '€'
        ]
        self.baseMD: str = self.loadHomepageContent()
        self.styleMD: str = self.loadStylesheet()
        self.cache: str = self.configCache()
        self.displayScrollX = 0
        self.displayScrollY = 0
        self.pendingDisplayScrollRestore: bool = False

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
        self.mdEdit.setChecked(self.editMode)
        self.mdSave = TransparentToolButton(FICO.SAVE)
        self.mdSave.setFixedHeight(34)
        self.mdSave.setToolTip("Save")
        self.mdSave.installEventFilter(ToolTipFilter(self.mdSave))
        self.mdSaveAs = TransparentToolButton(FICO.SAVE_AS)
        self.mdSaveAs.setFixedHeight(34)
        self.mdSaveAs.setToolTip("Save as...")
        self.mdSaveAs.installEventFilter(ToolTipFilter(self.mdSaveAs))
        self.mdUndo = TransparentToolButton(segFont.fromName("Undo"))
        self.mdUndo.setFixedHeight(34)
        self.mdUndo.setToolTip("Undo (Ctrl+Z)")
        self.mdUndo.installEventFilter(ToolTipFilter(self.mdUndo))
        self.mdRedo = TransparentToolButton(segFont.fromName("Redo"))
        self.mdRedo.setFixedHeight(34)
        self.mdRedo.setToolTip("Redo (Ctrl+Y)")
        self.mdRedo.installEventFilter(ToolTipFilter(self.mdRedo))
        self.mdCut = TransparentToolButton(FICO.CUT)
        self.mdCut.setFixedHeight(34)
        self.mdCut.setToolTip("Cut (Ctrl+X)")
        self.mdCut.installEventFilter(ToolTipFilter(self.mdCut))
        self.mdCopy = TransparentToolButton(FICO.COPY)
        self.mdCopy.setFixedHeight(34)
        self.mdCopy.setToolTip("Copy (Ctrl+C)")
        self.mdCopy.installEventFilter(ToolTipFilter(self.mdCopy))
        self.mdPaste = TransparentToolButton(FICO.PASTE)
        self.mdPaste.setFixedHeight(34)
        self.mdPaste.setToolTip("Paste (Ctrl+V)")
        self.mdPaste.installEventFilter(ToolTipFilter(self.mdPaste))
        self.mdFind = TransparentToolButton(FICO.SEARCH)
        self.mdFind.setFixedHeight(34)
        self.mdFind.setToolTip("Find (Ctrl+F)")
        self.mdFind.installEventFilter(ToolTipFilter(self.mdFind))
        self.mdShare = Action(FICO.SHARE, "Share")
        self.mdInfo = TransparentToolButton(FICO.INFO)
        self.mdInfo.setFixedHeight(34)
        self.mdInfo.setToolTip("About the document")
        self.mdInfo.installEventFilter(ToolTipFilter(self.mdInfo))
        self.mdHome = TransparentToolButton(FICO.HOME)
        self.mdHome.setFixedHeight(34)
        self.mdHome.setToolTip("Back to home")
        self.mdHome.installEventFilter(ToolTipFilter(self.mdHome))
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
        self.commandBar.addWidget(self.mdFind)
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
        editorLayout = QVBoxLayout(self.editorBox)
        editorLayout.setContentsMargins(0, 0, 0, 0)
        editorLayout.setSpacing(0)
        editorZone = QHBoxLayout()
        editorZone.setContentsMargins(0, 0, 0, 0)
        editorZone.setSpacing(0)
        
        # Editor
        self.mdEditor = MarkEditor(self)
        self.mdEditor.installEventFilter(self)
        self.mdEditor.textChanged.connect(self.editorUpdate)
        self.mdEditor.cursorPositionChanged.connect(self.editorStatusUpdate)
        self.mdEditor.selectionChanged.connect(self.editorSelectionUpdate)

        self.mdSave.setEnabled(False)
        self.mdSaveAs.setEnabled(self.editMode)
        self.mdUndo.setEnabled(self.editMode and self.mdEditor.isUndoAvailable())
        self.mdRedo.setEnabled(self.editMode and self.mdEditor.isRedoAvailable())
        self.mdCut.setEnabled(False)
        self.mdCopy.setEnabled(False)
        self.mdPaste.setEnabled(self.editMode and self.mdEditor.canPaste())
        self.mdFind.setEnabled(self.editMode)
        self.mdShare.setEnabled(self.validPath)
        self.mdInfo.setEnabled(bool(self.validPath) or bool(self.mdEditor.text()))
        # self.mdHome.setEnabled(not self.isHome)

        self.mdSave.clicked.connect(lambda: self.saveMDFile(self.mdPath, self.mdEditor.text(), False, self))
        self.mdSaveAs.clicked.connect(lambda: self.saveMDFile(self.mdPath, self.mdEditor.text(), True, self))
        self.mdUndo.clicked.connect(self.mdEditor.undo if self.mdEditor else None)
        self.mdRedo.clicked.connect(self.mdEditor.redo if self.mdEditor else None)
        self.mdCut.clicked.connect(lambda: (
            self.mdEditor.cut() if self.mdEditor else None,
            self.mdPaste.setEnabled(self.mdEditor.canPaste())
        ))
        self.mdCopy.clicked.connect(lambda: (
            self.mdEditor.copy() if self.mdEditor else None,
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
        
        self.editorStatus = QWidget()
        self.editorStatus.setObjectName("StatusBar")
        self.editorStatus.setContentsMargins(0, 0, 0, 0)
        self.editorStatus.setMaximumHeight(40)
        self.editorStatus.setStyleSheet("QWidget#StatusBar { background: transparent; }")
        self.editorStatusBox = QHBoxLayout(self.editorStatus)
        self.editorStatusBox.setContentsMargins(10, 10, 10, 10)
        self.editorStatusBox.setSpacing(20)
        self.statusLineCol = CaptionLabel()
        self.statusLineCol.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusLineCol.setStyleSheet(fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusLineCol)
        self.editorStatusBox.addStretch()
        self.statusEncoding = CaptionLabel()
        self.statusEncoding.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusEncoding.setStyleSheet(fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusEncoding)
        self.editorStatusBox.addStretch()
        self.statusCapsLock = CaptionLabel("Caps Lock")
        self.statusCapsLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusCapsLock.setStyleSheet(fontUI_QSS)
        self.statusCapsLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x14) & 1))
        self.editorStatusBox.addWidget(self.statusCapsLock)
        self.statusNumLock = CaptionLabel("Num Lock")
        self.statusNumLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusNumLock.setStyleSheet(fontUI_QSS)
        self.statusNumLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x90) & 1))
        self.editorStatusBox.addWidget(self.statusNumLock)
        self.editorStatusBox.addStretch()
        self.statusTotalChars = CaptionLabel()
        self.statusTotalChars.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalChars.setStyleSheet(fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusTotalChars)
        self.statusTotalLines = CaptionLabel()
        self.statusTotalLines.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalLines.setStyleSheet(f"font-family: {fontUI}, 'Segoe UI', sans-serif;")
        self.editorStatusBox.addWidget(self.statusTotalLines)
        self.statusTotalWords = CaptionLabel()
        self.statusTotalWords.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalWords.setStyleSheet(fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusTotalWords)

        editorZone.addWidget(self.mdEditor)
        editorLayout.addLayout(editorZone)
        editorLayout.addWidget(self.editorSymbols)
        editorLayout.addWidget(self.editorStatus)
        MDCLayout.addWidget(self.editorBox)

        # Viewer
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
        displayLayout.setSpacing(0)
        self.mdDisplayer = MarkWebView(self)
        self.mdDisplayer.setAcceptDrops(True)
        self.mdDisplayer.loadFinished.connect(self._restorePreviewScrollPosition)
        self.mdDisplayer.setHtml(self.baseMD, QUrl("http://localhost"))
        displayLayout.addWidget(self.mdDisplayer)
        self.displayNavBar = DisplayNavigationBar(self)
        displayLayout.addWidget(self.displayNavBar)

        MDCLayout.addWidget(self.mdContainer)

        # Settings
        self.settingsBox = QWidget()
        self.settingsBox.setObjectName("SettingsBox")
        self.settingsBox.setContentsMargins(0, 0, 0, 0)
        self.settingsBox.setStyleSheet(f"""
            QWidget#SettingsBox {{
                background: transparent;
                border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
            }}
        """)
        self.settingsBox.setEnabled(self.mdSettings.isChecked())
        self.settingsBox.setVisible(self.mdSettings.isChecked())
        settingsLayout = QVBoxLayout(self.settingsBox)
        settingsLayout.setContentsMargins(0, 20, 0, 0)
        settingsTitleLine = QHBoxLayout()
        settingsTitleLine.setContentsMargins(80, 0, 80, 20)
        settingsLayout.addLayout(settingsTitleLine)
        settingsTitle = TitleLabel("Settings", self.settingsBox)
        settingsTitle.setAlignment(Qt.AlignmentFlag.AlignTop)
        settingsTitleLine.addWidget(settingsTitle)
        settingsTitleLine.addStretch()
        self.settingsApplyEdits = PrimaryPushButton(FICO.SAVE, "Save and apply changes", self.settingsBox)
        self.settingsApplyEdits.setEnabled(False)
        self.settingsApplyEdits.clicked.connect(self.configSave)
        settingsTitleLine.addWidget(self.settingsApplyEdits)
        settingsScroll = SingleDirectionScrollArea(self.settingsBox, Qt.Orientation.Vertical)
        settingsScroll.setWidgetResizable(True)
        settingsScroll.setContentsMargins(0, 0, 80, 0)
        settingsScroll.enableTransparentBackground()
        settingsLayout.addWidget(settingsScroll)
        setScrollContainer = QWidget()
        setScrollContainer.setContentsMargins(80, 0, 80, 0)
        settingsScroll.setWidget(setScrollContainer)
        settingsScroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        settingsScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: none")
        settingsContent = QVBoxLayout(setScrollContainer)
        settingsContent.setSpacing(5)
        self.widgetDef = SettingsWidgetDefinition()
        self.saveConfigOnExitDlg = None

        # Settings - General
        settingsContent.addWidget(SubtitleLabel("General"))
        self.widgetDef.optionStartInEditMode.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionStartInEditMode)
        #self.widgetDef.optionFixTheme.setVisible(cfg.get(cfg.appTheme) == "Auto")
        self.widgetDef.optionFixTheme.button.clicked.connect(self.fixTheme)
        settingsContent.addWidget(self.widgetDef.optionFixTheme)
        self.widgetDef.optionManageHistory.button.clicked.connect(lambda: self.openHistoryManager(self))
        settingsContent.addWidget(self.widgetDef.optionManageHistory)

        # Settings - Editor
        editorLabel = SubtitleLabel("Editor")
        editorLabel.setContentsMargins(0, 20, 0, 0)
        settingsContent.addWidget(editorLabel)
        self.fontConfig = EditorFontConfigGroup(self)
        self.fontConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.fontConfig)
        self.widgetDef.optionShowLineNumbers.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionShowLineNumbers)
        self.widgetDef.optionShowSymbolsBar.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionShowSymbolsBar)
        self.widgetDef.optionShowStatusBar.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionShowStatusBar)
        self.widgetDef.optionEnableSyntaxHighlighting.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionEnableSyntaxHighlighting)
        self.widgetDef.optionEnableWordWrap.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionEnableWordWrap)
        self.widgetDef.optionHighlightCurrentLine.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionHighlightCurrentLine)
        self.indentConfig = IndentationConfigGroup(self)
        self.indentConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.indentConfig)
        self.selectColorConfig = EditorSelectionConfigGroup(self)
        self.selectColorConfig.selectButton.clicked.connect(lambda: self.openColorDialog(self))
        self.selectColorConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.selectColorConfig)
        self.selectCustomColorDlg = None

        # Settings - Viewer
        viewerLabel = SubtitleLabel("Viewer")
        viewerLabel.setContentsMargins(0, 20, 0, 0)
        settingsContent.addWidget(viewerLabel)
        self.widgetDef.optionOpenExternalLinks.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionOpenExternalLinks)
        self.cssPropertiesConfig = CSSPropertiesConfigGroup(self)
        self.cssPropertiesConfig.storageSelectButton.clicked.connect(self.selectLocalCSSSource)
        self.cssPropertiesConfig.customStyleEditButton.clicked.connect(lambda: self.openCustomCSSEditor(self))
        self.cssPropertiesConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.cssPropertiesConfig)
        self.homepageConfig = HomePageConfigGroup(self)
        self.homepageConfig.storageSelectButton.clicked.connect(self.selectLocalHomepageSource)
        self.homepageConfig.customContentEditButton.clicked.connect(lambda: self.openCustomHomeEditor(self))
        self.homepageConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.homepageConfig)

        settingsContent.addStretch()
        MDCLayout.addWidget(self.settingsBox)
        mainLayout.addLayout(MDCLayout)

        self.titleBar.raise_()
        self.mdSave.setEnabled(False)
        self.editorBox.setVisible(self.mdEdit.isChecked())
        self.loadMDFile(self.mdPath, self)

    def _renderGitMarkdown(self, text: str) -> str:
        return self.renderMD.render(self._convertGithubAlerts(text))

    def _convertGithubAlerts(self, text: str) -> str:
        if not text:
            return text

        lines = text.splitlines()
        output = []
        i = 0
        titles = {
            "note": "Note",
            "tip": "Tip",
            "important": "Important",
            "warning": "Warning",
            "caution": "Caution",
        }

        while i < len(lines):
            line = lines[i]
            match = re.match(r"^\s*>\s*\[!([A-Za-z]+)\]\s*$", line)

            if match:
                alertType = match.group(1).lower()
                alertTitle = titles.get(alertType, alertType.title())

                output.append(f'<div class="markdown-alert markdown-alert-{alertType}">')
                output.append(f'<p class="markdown-alert-title">{alertTitle}</p>')

                i += 1
                bodyLines = []

                while i < len(lines):
                    nextLine = lines[i]

                    if not nextLine.strip():
                        bodyLines.append("")
                        i += 1
                        continue

                    if re.match(r"^\s*>", nextLine):
                        bodyLines.append(re.sub(r"^\s*>\s?", "", nextLine))
                        i += 1
                        continue

                    break

                if bodyLines:
                    body = "\n".join(bodyLines).strip()
                    if body:
                        output.append(self._renderGitMarkdown(body))

                output.append("</div>")
                continue

            output.append(line)
            i += 1

        return "\n".join(output)

    def _savePreviewScrollPosition(self):
        page = self.mdDisplayer.page()
        if page is None:
            return
        try:
            page.runJavaScript("window.scrollX", lambda value: setattr(self, "displayScrollX", int(value or 0)))
            page.runJavaScript("window.scrollY", lambda value: setattr(self, "displayScrollY", int(value or 0)))
        except Exception:
            self.displayScrollX = 0
            self.displayScrollY = 0

    def _restorePreviewScrollPosition(self, ok: bool = True):
        if not ok or not getattr(self, "pendingDisplayScrollRestore", False):
            return
        self.pendingDisplayScrollRestore = False
        page = self.mdDisplayer.page()
        if page is None:
            return
        try:
            page.runJavaScript(f"window.scrollTo({self.displayScrollX}, {self.displayScrollY});")
        except Exception:
            pass

    def newMDFile(self):
        if self.canSave() or self.windowTitle().startswith("*"):
            print("Unsaved!")
            self.backToHome()
        else: self.backToHome()
    
    def openMDFile(self, parent):
        """ Open a Markdown file from storage """
        title = self.mdPath
        path = smart.browseFileDialog(parent, "Open a file in the Markdown Viewer", "", "Markdown files (*.md; *.markdown)")
        if not path: self.setWindowTitle(f"{title} - {TITLE} | {SmartLinkerName}")
        else: self.loadMDFile(path, parent)

    def loadMDFile(self, path: str, parent, history: bool = False):
        path = path.replace("/", "\\")
        if os.path.exists(path):
            if smart.isMarkdownExtension(path):
                if smart.getFileMimeType(path).startswith("text"):
                    self.mdPath = path
                    print(self.mdPath)
                    with open(path, encoding="utf-8") as mdReader: self.content = mdReader.read()
                    self.contentMD = self.renderMD.render(self.content) if markCfg.get(markCfg.cssSource) != "Default" else self._renderGitMarkdown(self.content)
                    self.htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
                    self.mdEditor.setText(self.content)
                    self.mdDisplayer.setHtml(self.htmlContent, QUrl("http://localhost"))
                    self.isHome = False
                    self.markUpdate(True, self.mdPath, parent)
                    with open("markdownContent.log", "w", encoding="utf-8") as mdWriter: mdWriter.write(self.content)
                    with open("markdownHtml.log", "w", encoding="utf-8") as htmlWriter: htmlWriter.write(self.htmlContent)
                else:
                    smart.warningNotify("Warning, be careful!", "The format of the provided file is not supported...", parent)
                    if history: self.removeFromHistory(path, parent)
            else:
                smart.warningNotify("Warning, be careful!", "The provided file is not recognized as a Markdown file...", parent)
                if history: self.removeFromHistory(path, parent)

    def markUpdate(self, exists: bool, path: str, parent):
        pathExists: bool = False
        if exists:
            self.setWindowTitle(f"{path} - {TITLE} | {SmartLinkerName}")
            for mdPath in self.markHistory["MarkdownHistory"]:
                if mdPath["path"] == path:
                    pathExists = True
                    break
            if not pathExists:
                self.markHistory["MarkdownHistory"].append({"path": path})
                self.saveHistory(self.markHistory)
                self.markHistory = self.loadHistory()
                self.openRecent.setEnabled(True)
                self.historyList = RoundMenu(parent=self)
                for hPath in self.markHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda checked, path=hPath["path"], parent=parent: self.loadMDFile(path, parent)))
                self.historyList.addSeparator()
                self.historyList.addAction(Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=parent: self.openHistoryManager(parent)))
                self.openRecent.setMenu(self.historyList)
            # self.mdHome.setEnabled(True)
            self.mdInfo.setEnabled(True)
        else:
            # self.mdHome.setEnabled(False)
            self.mdInfo.setEnabled(False)

    def saveMDFile(self, path: str, content: str, saveAs: bool, parent):
        self.validPath = os.path.exists(self.mdPath)
        if saveAs or not self.validPath:
            newPath = smart.saveFileDialog(parent, f"Save a Markdown file from {SmartLinkerName}", os.path.dirname(self.mdPath) if self.validPath else "", "Markdown files (*.md; *.markdown)").replace("/", "\\")
            if newPath:
                with open(newPath, "w", encoding="utf-8") as mdWriter: mdWriter.write(content)
                self.mdPath = newPath
                self.setWindowTitle(f"{self.mdPath} - {TITLE} | {SmartLinkerName}")
                smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
            print(newPath)
        else:
            with open(self.mdPath, 'w', encoding="utf-8") as mdWriter: mdWriter.write(content)
            self.setWindowTitle(f"{self.windowTitle()[1:] if self.windowTitle().startswith('*') else self.windowTitle()}")
            print(path)
            smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
        self.mdSave.setEnabled(False)

    def loadStylesheet(self) -> str:
        if markCfg.get(markCfg.cssSource) == "Local":
            if os.path.exists(markCfg.get(markCfg.cssSourcePath)):
                with open(markCfg.get(markCfg.cssSourcePath), encoding="utf-8") as styleReader: return styleReader.read()
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()
                smart.warningNotify("Warning, be cautious!", "Your local CSS resource cannot be found in your storage. Applying the default style...", self)
        elif markCfg.get(markCfg.cssSource) == "Custom":
            if markCfg.get(markCfg.cssProperties): return markCfg.get(markCfg.cssProperties)
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()
                smart.warningNotify("Warning, be cautious!", "Your custom CSS properties are currently empty. Applying the default style...", self)
        else:
            with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()

    def loadHomepageContent(self) -> str:
        if markCfg.get(markCfg.homepageSource) == "Local":
            if os.path.exists(markCfg.get(markCfg.homepageSourcePath)):
                with open(markCfg.get(markCfg.homepageSourcePath), encoding="utf-8") as baseReader: return baseReader.read()
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be cautious!", "Your local homepage content cannot be found in your storage. Loading the default homepage...", self)
        elif markCfg.get(markCfg.cssSource) == "Custom":
            if markCfg.get(markCfg.cssProperties): return markCfg.get(markCfg.cssProperties)
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be cautious!", "Your custom homepage properties are currently empty. Loading the default homepage...", self)
        else:
            with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")

    def backToHome(self):
        self.mdPath = "Untitled"
        self.validPath = False
        self.isHome = True
        # self.mdHome.setEnabled(False)
        self.mdUndo.setEnabled(False)
        self.mdRedo.setEnabled(False)
        self.mdInfo.setEnabled(False)
        self.mdEditor.setText("")
        self.mdDisplayer.setHtml(self.baseMD, QUrl("http://localhost"))
        self.setWindowTitle(f"Untitled - {TITLE} | {SmartLinkerName}")

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
        if self.historyManageDlg is None: self.historyManageDlg = ManageHistoryDialog(history, parent)
        else:
            self.historyManageDlg = None
            self.historyManageDlg = ManageHistoryDialog(history, parent)
        if self.historyManageDlg.exec(): # type: ignore
            try:
                self.saveHistory(self.historyManageDlg.tempHistory)
                self.markHistory = self.loadHistory()
                self.historyList = RoundMenu(parent=self)
                for hPath in self.markHistory["MarkdownHistory"]: self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda checked, path=hPath["path"], parent=parent: self.loadMDFile(path, parent)))
                self.historyList.addSeparator()
                self.historyList.addAction(Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=parent: self.openHistoryManager(parent)))
                self.openRecent.setMenu(self.historyList)
                self.historyManageDlg = None
                mdHistory = [path["path"] for path in self.markHistory["MarkdownHistory"]]
                if self.mdPath not in mdHistory: self.backToHome()
                smart.successNotify("Save complete!", "The changes have been saved successfully!", parent)
                print(f"{Fore.GREEN}The history changes have been saved successfully!{Style.RESET_ALL}")
            except Exception as e:
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to save history changes: {e}", parent)
                print(f"{Fore.RED}An error occured while attempting to save history changes: {e}{Style.RESET_ALL}")

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
            self.mdFind.setEnabled(False)
        else:
            self.mdSave.setEnabled(self.canSave())
            self.mdSaveAs.setEnabled(True)
            self.mdUndo.setEnabled(self.mdEditor.isUndoAvailable())
            self.mdRedo.setEnabled(self.mdEditor.isRedoAvailable())
            self.mdCut.setEnabled(self.mdEditor.hasSelectedText())
            self.mdCopy.setEnabled(self.mdEditor.hasSelectedText())
            self.mdPaste.setEnabled(self.mdEditor.canPaste())
            self.mdFind.setEnabled(True)
        self.editorUpdate()

    def toggleSettings(self, check: bool):
        def leave():
            self.mdContainer.setEnabled(True)
            self.mdContainer.setVisible(True)
            self.settingsBox.setEnabled(False)
            self.settingsBox.setVisible(False)
            self.mdNew.setEnabled(True)
            self.mdOpen.setEnabled(True)
            self.openRecent.setEnabled(True)
            self.mdEdit.setEnabled(True)
            self.mdSave.setEnabled(self.editMode and self.canSave())
            self.mdSaveAs.setEnabled(self.editMode)
            self.mdUndo.setEnabled(self.editMode and self.mdEditor.isUndoAvailable())
            self.mdRedo.setEnabled(self.editMode and self.mdEditor.isRedoAvailable())
            self.mdCut.setEnabled(self.editMode and self.mdEditor.hasSelectedText())
            self.mdCopy.setEnabled(self.editMode and self.mdEditor.hasSelectedText())
            self.mdPaste.setEnabled(self.editMode and self.mdEditor.canPaste())
            self.mdFind.setEnabled(self.editMode)
            self.mdShare.setEnabled(self.validPath)
            self.mdInfo.setEnabled(self.validPath)
            self.mdHome.setEnabled(not self.isHome)
            self.editorBox.setEnabled(self.editMode)
            self.editorBox.setVisible(self.editMode)

        self.pendingChanges = self.cache != self.configCache()
        if check:
            self.mdContainer.setEnabled(not check)
            self.mdContainer.setVisible(not check)
            self.settingsBox.setEnabled(check)
            self.settingsBox.setVisible(check)
            self.mdNew.setEnabled(not check)
            self.mdOpen.setEnabled(not check)
            self.openRecent.setEnabled(not check)
            self.mdEdit.setEnabled(not check)
            self.mdSave.setEnabled(not check)
            self.mdSaveAs.setEnabled(not check)
            self.mdUndo.setEnabled(not check)
            self.mdRedo.setEnabled(not check)
            self.mdCut.setEnabled(not check)
            self.mdCopy.setEnabled(not check)
            self.mdPaste.setEnabled(not check)
            self.mdFind.setEnabled(not check)
            self.mdShare.setEnabled(not check)
            self.mdInfo.setEnabled(not check)
            self.mdHome.setEnabled(not check)
            self.editorBox.setEnabled(not check)
            self.editorBox.setVisible(not check)
        else:
            self.saveConfigOnExitDlg = None
            if self.pendingChanges:
                self.saveConfigOnExitDlg = MessageBox(
                    "WARNING: Unsaved settings changes",
                    "Some settings have been changed but not saved yet. If you close the settings, "
                    "all your changes will be discarded.\n\nDo you want to save and apply them now?",
                    self
                )
                self.saveConfigOnExitDlg.yesButton.setText("Save and apply changes")
                self.saveConfigOnExitDlg.cancelButton.setText("Discard changes")
                if self.saveConfigOnExitDlg.exec():
                    self.configSave()
                    leave()
                else:
                    leave() # Discard and leave
            else: leave()

    def editorUpdate(self):
        text =  self.mdEditor.text()
        self.validPath = os.path.exists(self.mdPath)
        if text:
            if self.validPath:
                self.mdSave.setEnabled(self.canSave())
                self.setWindowTitle(f"{"*" if self.canSave() else ""}{self.mdPath} - {TITLE} | {SmartLinkerName}")
            else:
                self.mdSave.setEnabled(bool(text))
                self.setWindowTitle(f"*Untitled - {TITLE} | {SmartLinkerName}")
            self.isHome = False
            markText = self.renderMD.render(text) if markCfg.get(markCfg.cssSource) != "Default" else self._renderGitMarkdown(text)
            self._savePreviewScrollPosition()
            self.pendingDisplayScrollRestore = True
            self.htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{markText}\n</body>\n</html>'
            self.mdDisplayer.setHtml(self.htmlContent, QUrl("http://localhost"))
            self.mdUndo.setEnabled(self.mdEditor.isUndoAvailable() if self.mdEdit.isChecked() else False)
            self.mdRedo.setEnabled(self.mdEditor.isRedoAvailable() if self.mdEdit.isChecked() else False)
        else:
            self.isHome = True
            self.mdDisplayer.setHtml(self.baseMD, QUrl("http://localhost"))
            self.mdSave.setEnabled(False if not self.validPath else self.canSave())
            self.setWindowTitle(f"{'*' if self.canSave() else ''}{"Untitled" if not self.validPath else self.mdPath} - {TITLE} | {SmartLinkerName}")
        # self.mdHome.setEnabled(not self.isHome)
        self.editorStatusUpdate()
    
    def editorSelectionUpdate(self):
        self.editorStatusUpdate()
        selectedChars = self.mdEditor.selectedText()
        self.mdCut.setEnabled(bool(selectedChars))
        self.mdCopy.setEnabled(bool(selectedChars))

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

    def openColorDialog(self, parent):
        """ Open a dialog to change the editor's selection custom color. """
        if not self.selectCustomColorDlg:
            self.selectCustomColorDlg = ColorDialog(
                themeColor(),
                "Choose your preferred color",
                parent,
                enableAlpha=True
            )
            self.selectCustomColorDlg.editLabel.setText("Edit HEX color")
        if self.selectCustomColorDlg.exec():
            markCfg.set(markCfg.selectionCustomColor, self.selectCustomColorDlg.color.name(QColor.NameFormat.HexArgb))
            self.configEditListener()

    def fixTheme(self):
        if cfg.get(cfg.appTheme) == "Auto":
            setTheme(Theme.DARK if smart.isDarkMode() else Theme.LIGHT)
            self.setStyleSheet("background: white" if not smart.isDarkMode() else "")
            self.mdTitleBar.titleLabel.setStyleSheet(f"color: {"white" if smart.isDarkMode() else "black"}")
        else:
            smart.warningNotify("Warning, be cautious!", "Your theme configuration does not follow your system...", self)

    def selectLocalCSSSource(self):
        try:
            cssPath = smart.browseFileDialog(
                self,
                "Select a CSS file as your new viewer styling resource",
                "",
                "Cascade Style Sheets (*.css)"
            )
            if os.path.exists(cssPath):
                markCfg.set(markCfg.cssSourcePath, cssPath)
                self.cssPropertiesConfig.storagePathSublabel.setText(f"Current source path: {markCfg.get(markCfg.cssSourcePath).replace('/', '\\')}")
                self.cssPropertiesConfig.storagePathSublabel.setVisible(True)
                self.configEditListener()
        except Exception as e: smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to select your CSS file: {e}", self)

    def selectLocalHomepageSource(self):
        try:
            homePath = smart.browseFileDialog(
                self,
                "Select an HTML file as your new landing page",
                "",
                "HTML files (*.html; *.htm; *.xhtml; *.xht)"
            )
            if os.path.exists(homePath):
                markCfg.set(markCfg.homepageSourcePath, homePath)
                self.homepageConfig.storagePathSublabel.setText(f"Current source path: {markCfg.get(markCfg.homepageSourcePath).replace('/', '\\')}")
                self.homepageConfig.storagePathSublabel.setVisible(True)
                self.configEditListener()
        except Exception as e: smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to select your HTML file: {e}", self)

    def openCustomCSSEditor(self, parent):
        if self.customCSSDlg is None:
            self.customCSSDlg = CSSCustomPropertiesDialog(
                str(markCfg.get(markCfg.cssProperties)),
                parent
            )
        else:
            self.customCSSDlg = None
            self.customCSSDlg = CSSCustomPropertiesDialog(
                str(markCfg.get(markCfg.cssProperties)),
                parent
            )
        
        if self.customCSSDlg.exec():
            markCfg.set(markCfg.cssProperties, self.customCSSDlg.cssEdit.toPlainText())
            self.configEditListener()

    def openCustomHomeEditor(self, parent):
        if self.customHomeDlg is None:
            self.customHomeDlg = HomepageCustomPropertiesDialog(
                str(markCfg.get(markCfg.homepageProperties)),
                parent
            )
        else:
            self.customHomeDlg = None
            self.customHomeDlg = HomepageCustomPropertiesDialog(
                str(markCfg.get(markCfg.homepageProperties)),
                parent
            )
        
        if self.customHomeDlg.exec():
            markCfg.set(markCfg.homepageProperties, self.customHomeDlg.homeEdit.toPlainText())
            self.configEditListener()

    def configCache(self) -> str:
        if os.path.exists(smart.resourcePath("bin/markdown_config.json")):
            with open(smart.resourcePath("bin/markdown_config.json")) as configCacher: return configCacher.read()
        return ""

    def configEditListener(self):
        if os.path.exists(smart.resourcePath("bin/markdown_config.json")):
            with open(smart.resourcePath("bin/markdown_config.json")) as cfgReader: self.settingsApplyEdits.setEnabled(self.cache != cfgReader.read())
        else: smart.warningNotify("Warning, be careful!", "The Markdown configuration file cannot be found...", self)

    def configSave(self):
        print(f"Saving new configuration and applying changes to {TITLE}...")
        cacheDict = json.loads(self.cache)

        # Editor
        self.editorFont = QFont(
            markCfg.get(markCfg.fontFamily),
            markCfg.get(markCfg.fontSize),
            markCfg.get(markCfg.fontWeight)
        )
        self.mdEditor.setFont(self.editorFont)
        self.mdEditor.setMarginLineNumbers(0, markCfg.get(markCfg.displayLineNumbers))
        self.mdEditor.setMarginWidth(0, "0000" if markCfg.get(markCfg.displayLineNumbers) else 0)
        self.mdEditor.setMarginsFont(self.editorFont)
        self.editorSymbols.setEnabled(markCfg.get(markCfg.displaySymbolsBar))
        self.editorSymbols.setVisible(markCfg.get(markCfg.displaySymbolsBar))
        self.editorStatus.setVisible(markCfg.get(markCfg.displayStatusBar))
        self.mdEditor.setLexer(self.mdEditor.editorLexer if markCfg.get(markCfg.enableSyntaxHighlighting) else None)
        self.mdEditor.setWrapMode(QsciScintilla.WrapMode.WrapWord if markCfg.get(markCfg.enableWordWrap) else QsciScintilla.WrapMode.WrapNone)
        self.mdEditor.setCaretLineVisible(markCfg.get(markCfg.highlightCurrentLine))
        self.mdEditor.setIndentationWidth(markCfg.get(markCfg.indentWidth))
        self.mdEditor.setIndentationGuides(markCfg.get(markCfg.displayIndentGuides))
        self.mdEditor.setAutoIndent(markCfg.get(markCfg.enableAutoIndent))
        self.mdEditor.setSelectionBackgroundColor(
            cfg.get(cfg.accentColor) if markCfg.get(markCfg.selectionColorMode) == "Accent"
            else markCfg.get(markCfg.selectionCustomColor)
        )

        # Viewer
        if markCfg.get(markCfg.homepageSource) == "Local":
            if os.path.exists(markCfg.get(markCfg.homepageSourcePath)):
                with open(markCfg.get(markCfg.homepageSourcePath), encoding="utf-8") as baseReader: self.baseMD = baseReader.read()
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be cautious!", "Your local homepage content cannot be found in your storage, the default homepage will be used...", self)
                self.homepageConfig.sourceTypeCombo.setCurrentIndex(0)
                markCfg.set(markCfg.homepageSource, "Default")
        elif markCfg.get(markCfg.cssSource) == "Custom":
            if markCfg.get(markCfg.cssProperties): self.baseMD = markCfg.get(markCfg.cssProperties)
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be cautious!", "Your custom homepage properties are currently empty, the default homepage will be used...", self)
                self.homepageConfig.sourceTypeCombo.setCurrentIndex(0)
                markCfg.set(markCfg.homepageSource, "Default")
        else:
            with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
        if self.isHome: self.mdDisplayer.setHtml(self.baseMD, QUrl("http://localhost"))
            # ------
        if markCfg.get(markCfg.cssSource) == "Local":
            if os.path.exists(markCfg.get(markCfg.cssSourcePath)):
                with open(markCfg.get(markCfg.cssSourcePath), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
                if markCfg.get(markCfg.cssSource) != cacheDict["Viewer"]["CSSSource"] or \
                (markCfg.get(markCfg.cssSource) == cacheDict["Viewer"]["CSSSource"] and markCfg.get(markCfg.cssSourcePath) != cacheDict["Viewer"]["CSSSourcePath"]):
                    smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
                smart.warningNotify("Warning, be cautious!", "Your local CSS resource cannot be found in your storage, the default style will be applied...", self)
                self.cssPropertiesConfig.sourceTypeCombo.setCurrentIndex(0)
                markCfg.set(markCfg.cssSource, "Default")
        elif markCfg.get(markCfg.cssSource) == "Custom":
            if markCfg.get(markCfg.cssProperties):
                self.styleMD = markCfg.get(markCfg.cssProperties)
                if markCfg.get(markCfg.cssSource) != cacheDict["Viewer"]["CSSSource"] or \
                (markCfg.get(markCfg.cssSource) == cacheDict["Viewer"]["CSSSource"] and markCfg.get(markCfg.cssProperties) != cacheDict["Viewer"]["CSSProperties"]):
                    smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
                smart.warningNotify("Warning, be cautious!", "Your custom CSS properties are currently empty, the default style will be applied...", self)
                self.cssPropertiesConfig.sourceTypeCombo.setCurrentIndex(0)
                markCfg.set(markCfg.cssSource, "Default")
        else:
            with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
            if markCfg.get(markCfg.cssSource) != cacheDict["Viewer"]["CSSSource"]: smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)


        self.cache = self.configCache()
        self.settingsApplyEdits.setEnabled(False)
        print(f"{Fore.GREEN}New configuration saved and changes applied to {TITLE}!{Style.RESET_ALL}")
        smart.successNotify("Configuration complete", "The changes have been saved and applied successfully!", self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.editorBox.setFixedWidth(self.width() // 2)

    def eventFilter(self, obj, event):
        if obj == self.mdEditor and event.type() in [QEvent.Type.KeyPress, QEvent.Type.KeyRelease]: self.editorStatusUpdate()
        return super().eventFilter(obj, event)

    # Paramètres :
    ## Editeur :
    #### Couleur de syntaxe

class MarkWebView(FramelessWebEngineView):
    """ Class for the Markdown viewer webview """
    
    def __init__(self, parent: SmartDownMarkerGUI):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dropParent = parent
        self.reqUrl: str
        self.isHome: bool = True
        self.isCurrentContent: bool = False
        self.isLoading: bool = False

        self.settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True) # type: ignore

        self.page().navigationRequested.connect(self.onNavigationRequested) # type: ignore
        self.loadStarted.connect(self.onLoadStarted)
        self.loadProgress.connect(self.onLoadProgress)
        self.loadFinished.connect(self.onLoadFinished)
        self.iconChanged.connect(self.onIconLoaded)

    def onNavigationRequested(self, request: QWebEngineNavigationRequest):
        """ :MarkWebView: Intercept and handle navigation requests based on `openExternalLinks` setting """
        self.reqUrl = request.url().toString()
        self.isHome = unquote(self.reqUrl).replace("data:text/html;charset=UTF-8,", "") == self.dropParent.baseMD
        self.isCurrentContent = unquote(self.reqUrl).replace("data:text/html;charset=UTF-8,", "") == self.dropParent.htmlContent
        
        self.dropParent.mdHome.setEnabled(not self.isHome)
        
        if markCfg.get(markCfg.openExternalLinks):
            request.accept()
            self.dropParent.displayNavBar.navSearch.setText(self.reqUrl)
            self.dropParent.displayNavBar.setEnabled(not self.isHome and not self.isCurrentContent)
            self.dropParent.displayNavBar.setVisible(not self.isHome and not self.isCurrentContent)
            self.dropParent.displayNavBar.navBack.setEnabled(self.history().canGoBack()) # type: ignore
            self.dropParent.displayNavBar.navForward.setEnabled(self.history().canGoForward()) # type: ignore
            self.dropParent.displayNavBar.navIcon.setVisible(not self.isHome and not self.isCurrentContent)
        elif self.reqUrl.startswith("file://") and smart.getFileMimeType(self.reqUrl).startswith("text") and (smart.isMarkdownExtension(self.reqUrl)):
            request.accept()
            self.dropParent.displayNavBar.navSearch.setText(self.reqUrl)
        else:
            if self.isHome:
                request.accept()
                self.dropParent.displayNavBar.navSearch.setText(self.reqUrl)
            elif self.isCurrentContent:
                request.accept()
                self.dropParent.displayNavBar.navSearch.setText(self.reqUrl)
            else:
                request.reject()
                smart.warningNotify("Warning, be cautious!", "Access to non-Markdown content is currently disabled...", self)

    def onLoadStarted(self):
        """ :MarkWebView: Handle load started event """
        if markCfg.get(markCfg.openExternalLinks):
            self.dropParent.displayNavBar.navProgress.setVisible(True)
            self.dropParent.displayNavBar.navProgress.setValue(0)
            self.dropParent.displayNavBar.navRefresh.setIcon(FICO.CLOSE)
            self.isLoading = True
    
    def onLoadProgress(self, progress: int):
        """ :MarkWebView: Handle load progress event """
        if markCfg.get(markCfg.openExternalLinks):
            self.dropParent.displayNavBar.navProgress.setValue(progress)
    
    def onLoadFinished(self):
        """ :MarkWebView: Handle load finished event """
        if markCfg.get(markCfg.openExternalLinks):
            self.dropParent.displayNavBar.navProgress.setVisible(False)
            self.dropParent.displayNavBar.navProgress.setValue(0)
            self.dropParent.displayNavBar.navRefresh.setIcon(segFont.fromName("Refresh"))
            self.isLoading = False

    def onIconLoaded(self, icon: QIcon):
        """ :MarkWebView: Handle icon loaded event """
        if markCfg.get(markCfg.openExternalLinks):
            self.dropParent.displayNavBar.navIcon.setIcon(icon)
            # self.dropParent.displayNavBar.navIcon.setVisible(not self.isHome and not self.isCurrentContent)

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        """ :MarkWebView: Handle drag enter event """
        if event.mimeData().hasUrls(): # type: ignore
            event.acceptProposedAction() # type: ignore
            if self.dropParent.isHome: self.page().runJavaScript("onDragEnter()") # type: ignore
    
    def dragLeaveEvent(self, event: QDragLeaveEvent | None):
        """ :MarkWebView: Handle drag leave event """
        event.accept()                                                                  # type: ignore
        if self.dropParent.isHome: self.page().runJavaScript("onDragLeave()")           # type: ignore
    
    def dropEvent(self, event: QDropEvent | None):
        """ :MarkWebView: Handle drop event """
        if event.mimeData().hasUrls():                                                  # type: ignore
            for url in event.mimeData().urls():                                         # type: ignore
                localPath = url.toLocalFile()
                if self.dropParent.isHome: self.page().runJavaScript("onDrop()")        # type: ignore
                self.dropParent.loadMDFile(localPath, self.dropParent)

    """ def contextMenuEvent(self, event: QContextMenuEvent | None):
        smart.infoNotify("Did you know?", "The viewer's context menu has been blocked.", self.dropParent) """

class DisplayNavigationBar(QWidget):
    """ Class for the navigation bar displayed under `MarkWebView` """

    def __init__(self, parent: SmartDownMarkerGUI):
        super().__init__(parent)
        self.navParent = parent

        self.setObjectName("DisplayNavigation")
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumHeight(45)
        self.setStyleSheet(f"""
            QWidget#DisplayNavigation {{
                border-top: 1px solid {"#E3E6E9" if not smart.isDarkMode() else "#393939"};
                background: transparent;
            }}
        """)
        self.setVisible(markCfg.get(markCfg.openExternalLinks))
        self.navBox = QVBoxLayout(self)
        self.navBox.setContentsMargins(0, 0, 0, 0)
        self.navBox.setSpacing(0)
        self.navBoxBar = QHBoxLayout()
        self.navBoxBar.setContentsMargins(10, 5, 10, 5)
        self.navBoxBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.navBoxBar.setSpacing(5)

        self.navProgress = ProgressBar(self)
        self.navProgress.setRange(0, 100)

        self.navBack = TransparentToolButton(FICO.LEFT_ARROW)
        self.navBack.setToolTip("Previous (Alt+Left Arrow)")
        self.navBack.installEventFilter(ToolTipFilter(self.navBack))
        self.navForward = TransparentToolButton(FICO.RIGHT_ARROW)
        self.navForward.setToolTip("Next (Alt+Right Arrow)")
        self.navForward.installEventFilter(ToolTipFilter(self.navForward))
        self.navRefresh = TransparentToolButton(segFont.fromName("Refresh"))
        self.navRefresh.setToolTip("Refresh (F5 | Ctrl+R)")
        self.navRefresh.installEventFilter(ToolTipFilter(self.navRefresh))
        self.navIcon = IconWidget(FICO.IMAGE_EXPORT)
        self.navSearch = SearchLineEdit()
        self.navSearch.setPlaceholderText("Enter a valid URL address")
        self.navFind = TransparentToolButton(segFont.fromName("SearchAndApps"))
        self.navFind.setToolTip("Find in page (F3)")
        self.navFind.installEventFilter(ToolTipFilter(self.navFind))
        self.navClose = TransparentToolButton(segFont.fromName("Reply"))
        self.navClose.setToolTip("Return to Markdown content")
        self.navClose.installEventFilter(ToolTipFilter(self.navClose))

        self.navProgress.setVisible(False)
        self.navBack.setEnabled(False)
        self.navForward.setEnabled(False)
        self.navIcon.setVisible(True)

        self.navBack.clicked.connect(self.navParent.mdDisplayer.back)
        self.navForward.clicked.connect(self.navParent.mdDisplayer.forward)
        self.navRefresh.clicked.connect(lambda:
            self.navParent.mdDisplayer.reload() if not self.navParent.mdDisplayer.isLoading
            else self.navParent.mdDisplayer.stop()
        )
        self.navSearch.returnPressed.connect(self.checkSearchRequest)
        self.navSearch.searchSignal.connect(self.checkSearchRequest)
        self.navClose.clicked.connect(self.returnToMarkdown)

        self.navBox.addWidget(self.navProgress)
        self.navBox.addLayout(self.navBoxBar)
        self.navBoxBar.addWidget(self.navBack)
        self.navBoxBar.addWidget(self.navForward)
        self.navBoxBar.addWidget(self.navRefresh)
        self.navBoxBar.addWidget(self.navIcon)
        self.navBoxBar.addWidget(self.navSearch)
        self.navBoxBar.addWidget(self.navFind)
        self.navBoxBar.addWidget(self.navClose)
    
    def checkSearchRequest(self):
        """ :DisplayNavigationBar: Check if the search request is a valid URL or not.
        
        If the search request is not a valid URL, alert the user that
        only URLs are allowed, not search in general. For general search,
        they should use the browsing interface instead.
        """
        urlText = self.navSearch.text()

        if not urlText: return

        parsedUrl = urlparse(urlText)

        # Check if it's a valid URL
        isValidUrl = parsedUrl.scheme in ["http", "https", "file", "ftp"]

        # If no scheme, try common patterns (domain, localhost, etc.)
        if not isValidUrl and ("." in urlText or urlText.startswith("localhost")):
            urlText = "http://" + urlText
            parsed = urlparse(urlText)
            isValidUrl = parsed.scheme in ["http", "https"]
        
        # Alert if invalid URL
        if not isValidUrl:
            smart.warningNotify(
                "Warning, be cautious!",
                "Only URLs are allowed. For general search, please use the browsing interface instead.",
                self.navParent
            )
            return
        
        # Load the URL in the viewer
        try: self.navParent.mdDisplayer.load(QUrl(urlText))
        except Exception as e:
            smart.errorNotify(
                "Oops! Something went wrong...",
                f"An error occured while attempting to load the specified URL: {e}",
                self.navParent
            )

    def returnToMarkdown(self):
        """ :DisplayNavigationBar: Return to the Markdown content in the viewer """
        returnToMarkdownDlg = None
        returnToMarkdownDlg = MessageBox(
            "Return to Markdown content",
            "If you go back to rendering your current Markdown content, your browsing history " \
            "will be discarded and you will not be able to return to the previous page.\n\n" \
            "Do you really want to continue?",
            self.navParent
        )
        returnToMarkdownDlg.yesButton.setText("Return to Markdown content")
        returnToMarkdownDlg.cancelButton.setText("Continue browsing")
        if returnToMarkdownDlg.exec():
            displayHistory = self.navParent.mdDisplayer.page().history() # type: ignore
            displayHistory.clear() # type: ignore
            self.navParent.mdDisplayer.setHtml(self.navParent.baseMD, QUrl("http://localhost"))
            if self.navParent.htmlContent: self.navParent.mdDisplayer.setHtml(self.navParent.htmlContent, QUrl("http://localhost"))
            displayHistory = self.navParent.mdDisplayer.page().history() # type: ignore
            displayHistory.clear() # type: ignore
            history = [displayHistory.itemAt(i) for i in range(displayHistory.count())] # type: ignore
            for item in history: print(item.url().toString())

class MarkEditor(QsciScintilla):
    """ Class for the SmartLinker-adapted Markdown editor """

    def __init__(self, parent = None):
        super().__init__(parent)
        self.editParent = parent
        self.setStyleSheet(f"background: {"#282C34" if smart.isDarkMode() else "#EFF1F5"};")
        self.setSelectionBackgroundColor(
            cfg.get(cfg.accentColor) if markCfg.get(markCfg.selectionColorMode) == "Accent"
            else markCfg.get(markCfg.selectionCustomColor)
        )
        
        # Font config
        self.editorFont = QFont(
            markCfg.get(markCfg.fontFamily),
            markCfg.get(markCfg.fontSize),
            markCfg.get(markCfg.fontWeight)
        )
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
        self.editorLexer.setColor(QColor("#4082E4") if smart.isDarkMode() else QColor("#2196F3"), QsciLexerMarkdown.CodeBlock)
        if markCfg.get(markCfg.enableSyntaxHighlighting): self.setLexer(self.editorLexer)

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(markCfg.get(markCfg.indentWidth))
        self.setIndentationGuides(markCfg.get(markCfg.displayIndentGuides))
        self.setAutoIndent(markCfg.get(markCfg.enableAutoIndent))

        # Margin #0: number column
        self.setMarginWidth(0, "0000" if markCfg.get(markCfg.displayLineNumbers) else 0)
        self.setMarginLineNumbers(0, markCfg.get(markCfg.displayLineNumbers))
        self.setMarginsFont(self.editorFont)
        self.setMarginsBackgroundColor(QColor("#282C34") if smart.isDarkMode() else QColor("#E6E9EF"))
        self.setMarginsForegroundColor(QColor("#4B5263") if smart.isDarkMode() else QColor("#ACB0BE"))

        # Word wrap
        self.setWrapMode(self.WrapMode.WrapWord if markCfg.get(markCfg.enableWordWrap) else self.WrapMode.WrapNone)
        
        # Current line highlighting (caret)
        self.setCaretLineVisible(markCfg.get(markCfg.highlightCurrentLine))
        self.setCaretLineBackgroundColor(QColor("#4B5263") if smart.isDarkMode() else QColor("#CFCFCF"))

        # Brace/Pair matching
        self.setBraceMatching(self.BraceMatch.StrictBraceMatch)

    def undo(self) -> None:
        super().undo()
        self.editParent.mdUndo.setEnabled(self.editParent.editMode and self.isUndoAvailable()) # type: ignore

    def redo(self) -> None:
        super().redo()
        self.editParent.mdRedo.setEnabled(self.editParent.editMode and self.isRedoAvailable()) # type: ignore

    def canPaste(self):
        return QApplication.clipboard().mimeData().hasText()    # type: ignore

    def insertTab(self):
        line, col = self.getCursorPosition()
        if self.hasSelectedText(): self.indent(line)
        else: self.insertAt("\t", line, col)

class ManageHistoryDialog(MessageBoxBase):
    """ Class for the `Manage history` dialog box """

    def __init__(self, history: dict[str, list[dict[str, str]]], parent):
        super().__init__(parent)
        self.dialogParent = parent
        self.markdownHistory,  = history
        self.tempHistory = history.copy()
        self.removeMsg: str = ""
        self.changes: bool = self.tempHistory != self.markdownHistory

        self.topLine = QHBoxLayout()
        self.topLine.setContentsMargins(0, 0, 0, 0)
        self.topLine.setSpacing(15)
        self.icon = IconWidget(FICO.HISTORY)
        self.icon.setFixedSize(24, 24)
        self.description = BodyLabel(
            "Select from the list below the different Markdown file paths "
            "you want to work on.",
            self
        )
        self.description.setWordWrap(True)

        historyBtnLayout = QHBoxLayout()
        self.openBtn = PrimaryPushButton(FICO.LINK, "Load file", self)
        self.openBtn.setEnabled(False)
        self.removeBtn = PushButton(FICO.REMOVE, "Remove", self)
        self.removeBtn.setEnabled(False)
        self.selectAllBtn = PushButton(segFont.fromName("SelectAll"), "Select All", self)
        self.selectAllBtn.setEnabled(bool(self.tempHistory["MarkdownHistory"]))
        self.deselectAllBtn = PushButton(segFont.fromName("ClearSelection"), "Deselect All", self)
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
        for path in self.tempHistory["MarkdownHistory"]: self.historyList.addItem(path["path"])

        self.openBtn.clicked.connect(lambda: self.open(parent))
        self.removeBtn.clicked.connect(lambda: self.remove(self))
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
        self.topLine.addWidget(TitleLabel("Manage your history"))
        self.viewLayout.addWidget(self.description)
        self.viewLayout.addLayout(historyBtnLayout)
        self.viewLayout.addWidget(self.historyList)

        self.yesButton.setText("Apply and save changes")
        self.yesButton.setEnabled(self.changes)
        self.widget.setMinimumWidth(500)

    def open(self, parent):
        if len(self.historyList.selectedItems()) == 1:
            selectedItem = self.historyList.selectedItems()[0]
            self.dialogParent.loadMDFile(selectedItem.text(), parent)

    def remove(self, parent):
        if len(self.historyList.selectedItems()) > 0:
            if len(self.historyList.selectedItems()) > 1:
                self.removeMsg = "The following paths will be removed from your history:\n\n"
                for item in self.historyList.selectedItems(): self.removeMsg = f"{self.removeMsg}- {item.text()}\n"
                self.removeMsg = f"{self.removeMsg}\nDo you really want to continue?"
            else:
                self.removeMsg = f'Do you really want to remove the path "{self.historyList.selectedItems()[0].text()}" from your history?'
            
            removeDlg = None
            removeDlg = MessageBox("Remove from history", self.removeMsg, parent)
            removeDlg.yesButton.setText("Remove")
            if removeDlg.exec():
                selectedPaths = [item.text() for item in self.historyList.selectedItems()]
                newTempHist = [path for path in self.tempHistory["MarkdownHistory"] if path["path"] not in selectedPaths]
                self.tempHistory["MarkdownHistory"] = newTempHist
                self.historyList.clear()
                newTempHist = []
                for path in self.tempHistory["MarkdownHistory"]: self.historyList.addItem(path["path"])
                self.changes = self.tempHistory != self.markdownHistory
                self.yesButton.setEnabled(self.changes)
                self.historyList.clearSelection()
                
    def selectAll(self):
        self.historyList.selectAll()
    
    def deselectAll(self):
        self.historyList.clearSelection()

    def validate(self) -> bool:
        return self.changes

class SettingsWidgetDefinition():
    """ Declaration class for the Settings screen widgets """

    def __init__(self):
        super().__init__()

        # General
        self.optionStartInEditMode = SwitchSettingCard(
            FICO.EDIT,
            "Start in Edit mode",
            f"You can choose whether {TITLE} should start directly in Edit mode.",
            markCfg.startInEditMode
        )

        self.optionFixTheme = PushSettingCard(
            "Fix theme",
            segFont.fromName("Repair"),
            "Fix currrent theme",
            f"If {SmartLinkerName} theme configuration follows your system, "
            "this option helps you reapply the theme according to the one applied system-wide."
        )

        self.optionManageHistory = PushSettingCard(
            "Manage history",
            FICO.HISTORY,
            "Manage your Markdown history",
            f"You can load or remove any Markdown file already opened in {SmartLinkerName} or {TITLE}."
        )

        # Editor
        self.optionShowLineNumbers = SwitchSettingCard(
            segSVG.NUMBER_SYMBOL,
            "Display the line numbers",
            "You can choose whether the line numbers can be displayed in the editor pane.",
            markCfg.displayLineNumbers
        )

        self.optionShowSymbolsBar = SwitchSettingCard(
            segFont.fromName("EmojiTabMoreSymbols"),
            "Display the symbols bar",
            "You can choose whether the symbols bar can be displayed in the editor pane.",
            markCfg.displaySymbolsBar
        )

        self.optionShowStatusBar = SwitchSettingCard(
            segFont.fromName("SIPRedock"),
            "Display the status bar",
            "You can choose whether the status bar can be displayed at the bottom of the editor pane.",
            markCfg.displayStatusBar
        )

        self.optionEnableSyntaxHighlighting = SwitchSettingCard(
            segFont.fromName("Highlight"),
            "Enable syntax highlighting",
            "You can choose whether the editor can be syntax-highlighted based on Markdown syntax.",
            markCfg.enableSyntaxHighlighting
        )

        self.optionEnableWordWrap = SwitchSettingCard(
            segSVG.TEXT_WRAP,
            "Enable text wrapping",
            "You can choose whether the editor content can be wrapped to the next line.",
            markCfg.enableWordWrap
        )

        self.optionHighlightCurrentLine = SwitchSettingCard(
            segSVG.COLOR_LINE,
            "Highlight the current line",
            "You can choose whether the focused line in the editor can be highlighted.",
            markCfg.highlightCurrentLine
        )

        # Viewer
        self.optionOpenExternalLinks = SwitchSettingCard(
            segFont.fromName("Link"),
            "Access external links",
            f"Allow {TITLE} to access external links such as webpages, non-Markdown content"
            " and more via the viewer pane.",
            markCfg.openExternalLinks
        )

class EditorFontConfigGroup(ExpandGroupSettingCard):
    """ Class for Smart DownMarker font settings in the Editor section """
    configChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(
            segFont.fromName("Font"), # type: ignore
            "Customize font settings",
            "Modify the editor's font family, size and weight properties"
        )
        self.fontProp = f"""
            font-family: "{markCfg.get(markCfg.fontFamily)}";
            font-size: {markCfg.get(markCfg.fontSize)};
            font-weight: {markCfg.get(markCfg.fontWeight)};
        """

        # Font family
        self.familyCombo = ComboBox()
        self.familyCombo.addItems([markCfg.get(markCfg.fontFamily)])
        self.familyCombo.currentTextChanged.connect(self.updatePreview)

        # Font size
        self.sizeSpin = SpinBox()
        self.sizeSpin.setValue(markCfg.get(markCfg.fontSize))
        self.sizeSpin.setMinimum(4)
        self.sizeSpin.valueChanged.connect(self.updatePreview)

        # Font weight
        self.weightSpin = SpinBox()
        self.weightSpin.setRange(100, 800)
        self.weightSpin.setValue(markCfg.get(markCfg.fontWeight))
        self.weightSpin.setSingleStep(100)
        self.weightSpin.valueChanged.connect(self.updatePreview)

        # Preview text
        self.fontPreview = BodyLabel("The quick brown fox jumps over the lazy dog.")
        self.fontPreview.setStyleSheet(self.fontProp)

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add(BodyLabel("Choose a font"), self.familyCombo)
        self.add(BodyLabel("Set font size"), self.sizeSpin)
        self.add(BodyLabel("Set font weight"), self.weightSpin)
        self.add(BodyLabel("Font preview"), self.fontPreview)
    
    def add(self, label, widget = None):
        """ :EditorFontConfig: Add labels and config widgets to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        if widget:
            widLayout.addStretch()
            widLayout.addWidget(widget)
        
        self.addGroupWidget(wid)
    
    def updatePreview(self):
        self.fontFamily = self.familyCombo.currentText()
        self.fontSize = self.sizeSpin.value()
        self.fontWeight = self.weightSpin.value()
        self.fontProp = f"""
            font-family: "{self.fontFamily}";
            font-size: {self.fontSize}px;
            font-weight: {self.fontWeight}
        """

        self.fontPreview.setStyleSheet(self.fontProp)
        markCfg.set(markCfg.fontFamily, self.fontFamily)
        markCfg.set(markCfg.fontSize, self.fontSize)
        markCfg.set(markCfg.fontWeight, self.fontWeight)
        self.configChanged.emit()

class IndentationConfigGroup(ExpandGroupSettingCard):
    """ Class for Smart DownMarker indentation settings in the Editor section """
    configChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(
            segFont.fromName("HorizontalTabKey"), # type: ignore
            "Customize indentation settings",
            "Modify the editor's indentation properties such as tab width and indentation guides visibility."
        )

        # Tab width
        self.tabWidthSpin = SpinBox()
        self.tabWidthSpin.setValue(markCfg.get(markCfg.indentWidth))
        self.tabWidthSpin.setRange(2, 8)
        self.tabWidthSpin.valueChanged.connect(self.updateConfig)

        # Indentation guides
        self.indentGuidesCheck = SwitchButton()
        self.indentGuidesCheck.setChecked(markCfg.get(markCfg.displayIndentGuides))
        self.indentGuidesCheck.checkedChanged.connect(self.updateConfig)

        # Auto-indent
        self.autoIndentCheck = SwitchButton()
        self.autoIndentCheck.setChecked(markCfg.get(markCfg.enableAutoIndent))
        self.autoIndentCheck.checkedChanged.connect(self.updateConfig)

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add(BodyLabel("Set tab width (from 2 to 8)"), self.tabWidthSpin)
        self.add(BodyLabel("Display indentation guides"), self.indentGuidesCheck)
        self.add(BodyLabel("Enable auto-indentation"), self.autoIndentCheck)

    def add(self, label, widget = None):
        """ :IndentationConfigGroup: Add labels and config widgets to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        if widget:
            widLayout.addStretch()
            widLayout.addWidget(widget)
        
        self.addGroupWidget(wid)
    
    def updateConfig(self):
        markCfg.set(markCfg.indentWidth, self.tabWidthSpin.value())
        markCfg.set(markCfg.displayIndentGuides, self.indentGuidesCheck.isChecked())
        markCfg.set(markCfg.enableAutoIndent, self.autoIndentCheck.isChecked())
        self.configChanged.emit()

class EditorSelectionConfigGroup(ExpandGroupSettingCard):
    """ Class for Smart DownMarker selection settings in the Editor section """
    configChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(
            FICO.PALETTE, # type: ignore
            "Customize selection settings",
            "Modify the editor's selection properties such as selection mode and custom color."
        )

        colorModes = {
            "System accent color": segFont.fromName("System"),
            "Custom accent color": segFont.fromName("Edit")
        }

        # Selection color mode
        self.selectionColorModeCombo = ComboBox()
        # self.selectionColorModeCombo.addItems(["System accent color", "Custom accent color"])
        for k, v in colorModes.items(): self.selectionColorModeCombo.addItem(k, v)
        self.selectionColorModeCombo.setFixedWidth(180)
        self.selectionColorModeCombo.setCurrentIndex(1 if markCfg.get(markCfg.selectionColorMode) == "Custom" else 0)
        self.selectionColorModeCombo.currentTextChanged.connect(self.updateConfig)

        # Selection custom color
        self.selectButton = PushButton(FICO.PALETTE, "Pick my color")
        self.selectButton.setEnabled(bool(self.selectionColorModeCombo.currentText() == "Custom accent color"))
        self.selectButton.setFixedWidth(150)

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add(BodyLabel("Set selection color mode"), self.selectionColorModeCombo)
        self.add(BodyLabel("Select selection custom color"), self.selectButton)
    
    def add(self, label, widget = None):
        """ :EditorSelectionConfigGroup: Add labels and config widgets to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        if widget:
            widLayout.addStretch()
            widLayout.addWidget(widget)
        
        self.addGroupWidget(wid)
    
    def updateConfig(self):
        self.selectButton.setEnabled(self.selectionColorModeCombo.currentIndex() == 1)
        markCfg.set(markCfg.selectionColorMode, "Custom" if self.selectionColorModeCombo.currentIndex() == 1 else "Accent")
        self.configChanged.emit()

class CSSPropertiesConfigGroup(ExpandGroupSettingCard):
    """ Class for Smart DownMarker CSS properties in the Viewer section """
    configChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(
            segSVG.STYLE_GUIDE, # type: ignore
            "Customize CSS properties",
            "Modify the viewer's rendering style properties "
            "(doesn't apply to webpages, stylized HTML documents or any CSS-incompatible non-static content)"
        )

        self.sourceTypes = {
            "Embedded default": segFont.fromName("AppIconDefault"),
            "From local storage": segFont.fromName("HardDrive"),
            "Custom": segFont.fromName("TextEdit")
        }
        self.sourceIndexes = {"Default": 0, "Local": 1, "Custom": 2}

        # Stylesheet source type
        self.sourceTypeCombo = ComboBox()
        for k, v in self.sourceTypes.items(): self.sourceTypeCombo.addItem(k, v)
        self.sourceTypeCombo.setFixedWidth(180)
        self.sourceTypeCombo.setCurrentIndex(next(v for k, v in self.sourceIndexes.items() if markCfg.get(markCfg.cssSource) == k))
        self.sourceTypeCombo.currentIndexChanged.connect(self.updateConfig)

        # Storage source
        self.storagePath = QWidget()
        self.storagePath.setContentsMargins(0, 0, 0, 0)
        storagePathBox = QVBoxLayout(self.storagePath)
        storagePathBox.setContentsMargins(0, 0, 0, 0)
        storagePathBox.setSpacing(5)
        storagePathBox.addWidget(BodyLabel("Choose a file from your storage"))
        self.storagePathSublabel = CaptionLabel(
            f"Current source path: {markCfg.get(markCfg.cssSourcePath).replace('/', '\\')}{" (Inaccessible)" if not os.path.exists(markCfg.get(markCfg.cssSourcePath)) else ""}"
            if markCfg.get(markCfg.cssSourcePath) else "No path has been defined yet"
        )
        self.storagePathSublabel.setTextColor(QColor("gray"), QColor("gray"))
        self.storagePathSublabel.setVisible(bool(markCfg.get(markCfg.cssSourcePath)) and markCfg.get(markCfg.cssSourcePath) != "Default")
        storagePathBox.addWidget(self.storagePathSublabel)
        self.storageSelectButton = PushButton(FICO.FOLDER, "Browse")
        self.storageSelectButton.setFixedWidth(150)
        self.storageSelectButton.setEnabled(self.sourceTypeCombo.currentIndex() == 1)

        # Custom source
        self.customStyleEditButton = PushButton(FICO.EDIT, "Edit style")
        self.customStyleEditButton.setFixedWidth(150)
        self.customStyleEditButton.setEnabled(self.sourceTypeCombo.currentIndex() == 2)

        self.add(BodyLabel("Select a source type"), self.sourceTypeCombo)
        self.add(self.storagePath, self.storageSelectButton)
        self.add(BodyLabel("Customize the viewer style manually"), self.customStyleEditButton)
    
    def add(self, label, widget = None):
        """ :CSSPropertiesConfigGroup: Add labels and config widgets to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        if widget:
            widLayout.addStretch()
            widLayout.addWidget(widget)
        
        self.addGroupWidget(wid)
    
    def updateConfig(self):
        markCfg.set(markCfg.cssSource, next(k for k, v in self.sourceIndexes.items() if v == self.sourceTypeCombo.currentIndex()))
        self.storageSelectButton.setEnabled(self.sourceTypeCombo.currentIndex() == 1)
        self.customStyleEditButton.setEnabled(self.sourceTypeCombo.currentIndex() == 2)
        self.configChanged.emit()

class HomePageConfigGroup(ExpandGroupSettingCard):
    """ Class for Smart DownMarker homepage settings in the Viewer section """
    configChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(
            FICO.HOME, # type: ignore
            "Customize homepage settings",
            "Modify the viewer's homepage properties such as source type and custom content."
        )

        self.sourceTypes = {
            "Embedded default": segFont.fromName("AppIconDefault"),
            "From local storage": segFont.fromName("HardDrive"),
            "Custom": segFont.fromName("TextEdit")
        }
        self.sourceIndexes = {"Default": 0, "Local": 1, "Custom": 2}

        # Homepage source type
        self.sourceTypeCombo = ComboBox()
        for k, v in self.sourceTypes.items(): self.sourceTypeCombo.addItem(k, v)
        self.sourceTypeCombo.setFixedWidth(180)
        self.sourceTypeCombo.setCurrentIndex(next(v for k, v in self.sourceIndexes.items() if markCfg.get(markCfg.homepageSource) == k))
        self.sourceTypeCombo.currentIndexChanged.connect(self.updateConfig)

        # Storage source
        self.storagePath = QWidget()
        self.storagePath.setContentsMargins(0, 0, 0, 0)
        storagePathBox = QVBoxLayout(self.storagePath)
        storagePathBox.setContentsMargins(0, 0, 0, 0)
        storagePathBox.setSpacing(5)
        storagePathBox.addWidget(BodyLabel("Choose a file from your storage"))
        self.storagePathSublabel = CaptionLabel(
            f"Current source path: {markCfg.get(markCfg.homepageSourcePath).replace('/', '\\')}{" (Inaccessible)" if not os.path.exists(markCfg.get(markCfg.homepageSourcePath)) else ""}"
            if markCfg.get(markCfg.homepageSourcePath) else "No path has been defined yet"
        )
        self.storagePathSublabel.setStyleSheet("color: gray;")
        self.storagePathSublabel.setVisible(bool(markCfg.get(markCfg.homepageSourcePath)) and markCfg.get(markCfg.homepageSourcePath) != "Default")
        storagePathBox.addWidget(self.storagePathSublabel)
        self.storageSelectButton = PushButton(FICO.FOLDER, "Browse")
        self.storageSelectButton.setFixedWidth(150)
        self.storageSelectButton.setEnabled(self.sourceTypeCombo.currentIndex() == 1)

        # Custom source
        self.customContentEditButton = PushButton(FICO.EDIT, "Edit content")
        self.customContentEditButton.setFixedWidth(150)
        self.customContentEditButton.setEnabled(self.sourceTypeCombo.currentIndex() == 2)

        self.add(BodyLabel("Select a source type"), self.sourceTypeCombo)
        self.add(self.storagePath, self.storageSelectButton)
        self.add(BodyLabel("Customize the homepage content manually"), self.customContentEditButton)
    
    def add(self, label, widget = None):
        """ :HomePageConfigGroup: Add labels and config widgets to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        if widget:
            widLayout.addStretch()
            widLayout.addWidget(widget)
        
        self.addGroupWidget(wid)
    
    def updateConfig(self):
        markCfg.set(markCfg.homepageSource, next(k for k, v in self.sourceIndexes.items() if v == self.sourceTypeCombo.currentIndex()))
        self.storageSelectButton.setEnabled(self.sourceTypeCombo.currentIndex() == 1)
        self.customContentEditButton.setEnabled(self.sourceTypeCombo.currentIndex() == 2)
        self.configChanged.emit()

class CSSCustomPropertiesDialog(MessageBoxBase):
    """ Class for the `Customize the viewer style` dialog box """

    def __init__(self, stylesheet: str, parent):
        super().__init__(parent)
        self.dialogParent = parent
        self.customCSS = stylesheet if stylesheet else self.dialogParent.styleMD
        self.tempCSS = self.customCSS
        self.changes: bool = self.customCSS != self.tempCSS

        self.topLine = QHBoxLayout()
        self.topLine.setContentsMargins(0, 0, 0, 0)
        self.topLine.setSpacing(15)
        self.icon = IconWidget(smIco.renderIcon(smIco.CSS))
        self.icon.setFixedSize(32, 32)
        self.description = BodyLabel(
            "You can edit manually the CSS properties that will be applied to "
            f"the Markdown content rendered by the {TITLE} viewer.",
            self
        )
        self.description.setWordWrap(True)

        self.cssEdit = TextEdit(self)
        self.cssEdit.setMinimumHeight(300)
        self.cssEdit.setAcceptRichText(False)
        self.cssEdit.setFontFamily(markCfg.get(markCfg.fontFamily))
        self.cssEdit.setPlaceholderText("Your custom style sheet properties will appear here...")
        self.cssEdit.setPlainText(self.tempCSS)
        self.cssEdit.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
        self.cssEdit.textChanged.connect(self.editListener)
        self.cssEdit.selectionChanged.connect(self.editListener)

        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.cssUndo = Action(segFont.fromName("Undo"), "Undo", triggered=lambda: self.cssEdit.undo())
        self.cssRedo = Action(segFont.fromName("Redo"), "Redo", triggered=lambda: self.cssEdit.redo())
        self.cssCut = Action(FICO.CUT, "Cut", triggered=lambda: self.cssEdit.cut())
        self.cssCopy = Action(FICO.COPY, "Copy", triggered=lambda: self.cssEdit.copy())
        self.cssPaste = Action(FICO.PASTE, "Paste", triggered=lambda: self.cssEdit.paste())
        self.toggleWrap = Action(segSVG.TEXT_WRAP, "Word wrap", triggered=self.toggleWordWrap)

        self.cssUndo.setEnabled(self.cssEdit.document().isUndoAvailable()) # type: ignore
        self.cssRedo.setEnabled(self.cssEdit.document().isRedoAvailable()) # type: ignore
        self.cssCut.setEnabled(self.cssEdit.textCursor().hasSelection())
        self.cssCopy.setEnabled(self.cssEdit.textCursor().hasSelection())
        self.cssPaste.setEnabled(self.cssEdit.canPaste())

        self.commandBar.addActions([
            self.cssUndo, self.cssRedo, self.cssCut,
            self.cssCopy, self.cssPaste
        ])
        self.commandBar.addSeparator()
        self.commandBar.addAction(self.toggleWrap)

        self.viewLayout.setSpacing(20)

        self.viewLayout.addLayout(self.topLine)
        self.topLine.addWidget(self.icon)
        self.topLine.addWidget(TitleLabel("Customize the viewer style"))
        self.viewLayout.addWidget(self.description)
        self.viewLayout.addWidget(self.commandBar)
        self.viewLayout.addWidget(self.cssEdit)

        self.yesButton.setText("Save and apply changes")
        self.yesButton.setEnabled(self.changes)
        self.widget.setMinimumWidth(700)
    
    def editListener(self):
        self.tempCSS = self.cssEdit.toPlainText()
        self.changes = self.tempCSS != self.customCSS
        self.cssUndo.setEnabled(self.cssEdit.document().isUndoAvailable()) # type: ignore
        self.cssRedo.setEnabled(self.cssEdit.document().isRedoAvailable()) # type: ignore
        self.cssCut.setEnabled(self.cssEdit.textCursor().hasSelection())
        self.cssCopy.setEnabled(self.cssEdit.textCursor().hasSelection())
        self.cssPaste.setEnabled(self.cssEdit.canPaste())
        self.yesButton.setEnabled(self.changes)
    
    def toggleWordWrap(self):
        accentColor = QColor(cfg.get(cfg.accentColor))
        if self.cssEdit.lineWrapMode() != TextEdit.LineWrapMode.NoWrap:
            self.cssEdit.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
            self.toggleWrap.setIcon(segSVG.TEXT_WRAP)
        else:
            self.cssEdit.setLineWrapMode(TextEdit.LineWrapMode.WidgetWidth)
            self.toggleWrap.setIcon(segSVG.TEXT_WRAP.colored(accentColor, accentColor))

class HomepageCustomPropertiesDialog(MessageBoxBase):
    """ Class for the `Customize the viewer homepage` dialog box """

    def __init__(self, content: str, parent):
        super().__init__(parent)
        self.dialogParent = parent
        self.customHome = content if content else self.dialogParent.baseMD
        self.tempHome = self.customHome
        self.changes: bool = self.customHome != self.tempHome

        self.topLine = QHBoxLayout()
        self.topLine.setContentsMargins(0, 0, 0, 0)
        self.topLine.setSpacing(15)
        self.icon = IconWidget(smIco.renderIcon(smIco.HTML))
        self.icon.setFixedSize(32, 32)
        self.description = BodyLabel(
            "You can edit manually the HTML content that will be displayed as "
            f"the {TITLE} viewer's homepage."
        )
        self.description.setWordWrap(True)

        self.homeEdit = TextEdit(self)
        self.homeEdit.setMinimumHeight(300)
        self.homeEdit.setAcceptRichText(False)
        self.homeEdit.setFontFamily(markCfg.get(markCfg.fontFamily))
        self.homeEdit.setPlaceholderText("Your custom homepage content will appear here...")
        self.homeEdit.setPlainText(self.tempHome)
        self.homeEdit.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
        self.homeEdit.textChanged.connect(self.editListener)
        self.homeEdit.selectionChanged.connect(self.editListener)

        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.homeUndo = Action(segFont.fromName("Undo"), "Undo", triggered=lambda: self.homeEdit.undo())
        self.homeRedo = Action(segFont.fromName("Redo"), "Redo", triggered=lambda: self.homeEdit.redo())
        self.homeCut = Action(FICO.CUT, "Cut", triggered=lambda: self.homeEdit.cut())
        self.homeCopy = Action(FICO.COPY, "Copy", triggered=lambda: self.homeEdit.copy())
        self.homePaste = Action(FICO.PASTE, "Paste", triggered=lambda: self.homeEdit.paste())
        self.toggleWrap = Action(segSVG.TEXT_WRAP, "Word wrap", triggered=self.toggleWordWrap)

        self.homeUndo.setEnabled(self.homeEdit.document().isUndoAvailable()) # type: ignore
        self.homeRedo.setEnabled(self.homeEdit.document().isRedoAvailable()) # type: ignore
        self.homeCut.setEnabled(self.homeEdit.textCursor().hasSelection())
        self.homeCopy.setEnabled(self.homeEdit.textCursor().hasSelection())
        self.homePaste.setEnabled(self.homeEdit.canPaste())

        self.commandBar.addActions([
            self.homeUndo, self.homeRedo, self.homeCut,
            self.homeCopy, self.homePaste
        ])
        self.commandBar.addSeparator()
        self.commandBar.addAction(self.toggleWrap)

        self.viewLayout.setSpacing(20)

        self.viewLayout.addLayout(self.topLine)
        self.topLine.addWidget(self.icon)
        self.topLine.addWidget(TitleLabel("Customize the viewer homepage"))
        self.viewLayout.addWidget(self.description)
        self.viewLayout.addWidget(self.commandBar)
        self.viewLayout.addWidget(self.homeEdit)

        self.yesButton.setText("Save and apply changes")
        self.yesButton.setEnabled(self.changes)
        self.widget.setMinimumWidth(700)
    
    def editListener(self):
        self.tempHome = self.homeEdit.toPlainText()
        self.changes = self.tempHome != self.customHome
        self.homeUndo.setEnabled(self.homeEdit.document().isUndoAvailable()) # type: ignore
        self.homeRedo.setEnabled(self.homeEdit.document().isRedoAvailable()) # type: ignore
        self.homeCut.setEnabled(self.homeEdit.textCursor().hasSelection())
        self.homeCopy.setEnabled(self.homeEdit.textCursor().hasSelection())
        self.homePaste.setEnabled(self.homeEdit.canPaste())
        self.yesButton.setEnabled(self.changes)
    
    def toggleWordWrap(self):
        accentColor = QColor(cfg.get(cfg.accentColor))
        if self.homeEdit.lineWrapMode() != TextEdit.LineWrapMode.NoWrap:
            self.homeEdit.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
            self.toggleWrap.setIcon(segSVG.TEXT_WRAP)
        else:
            self.homeEdit.setLineWrapMode(TextEdit.LineWrapMode.WidgetWidth)
            self.toggleWrap.setIcon(segSVG.TEXT_WRAP.colored(accentColor, accentColor))
