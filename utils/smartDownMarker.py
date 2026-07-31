from utils.SmartUtils import *

# =========================================================

TITLE = "Smart DownMarker (BETA)"

class CustomTitleBar(FluentWidgetTitleBar):
    """ Custom title bar """

    def __init__(self, parent):
        super().__init__(parent)
        
        self.minBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.maxBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.closeBtn.setNormalColor((QColor("white" if smart.isDarkMode() else "black")) if cfg.get(cfg.appTheme) == "Auto" else
                                   QColor("white") if cfg.get(cfg.appTheme) == "Dark" else QColor("black"))
        self.minBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor())
        self.minBtn.setPressedColor(QColor("white"))
        self.maxBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor())
        self.maxBtn.setPressedColor(QColor("white"))
        self.closeBtn.setHoverBackgroundColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentMode) == "Custom" else getSystemAccentColor())

class SmartDownMarkerGUI(FluentWidget):
    """ Class for the **Smart DownMarker** (or *Markdown Editor*) window """

    def __init__(self, mdFilePath: str, parent = None):
        super().__init__(parent=parent)
        # smart.clearCLI()
        RichCLI.print(smart.consoleScript())
        self.mdPath: str = mdFilePath
        self.mdTitleBar = CustomTitleBar(self)
        self.setTitleBar(self.mdTitleBar)
        self.setWindowIcon(smIco.renderIcon(smIco.MARKDOWN))
        self.setWindowTitle(f"{self.mdPath} | {TITLE}")
        self.resize(1280, 768)
        self.setMinimumSize(1120, 630)
        smart.centerWindow(self)
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        try:
            fontDB = QFontDatabase.addApplicationFont(smart.resourcePath("resources\\fonts\\Code.ttf"))
            fontEditFam = QFontDatabase.applicationFontFamilies(fontDB)[6]
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to load the editor font: {e}{Style.RESET_ALL}")
            fontEditFam = "Consolas"
        finally: self.fontEditor = fontEditFam
        try:
            fontDB = QFontDatabase.addApplicationFont(smart.resourcePath("resources\\fonts\\Interface.ttf"))
            fontUIFam = QFontDatabase.applicationFontFamilies(fontDB)[24]
        except Exception as e:
            print(f"{Fore.RED}Something went wrong while attempting to load the editor font: {e}{Style.RESET_ALL}")
            fontUIFam = "Segoe UI"
        finally: self.fontUI = fontUIFam
        self.fontEditor_QSS = f"font-family: '{self.fontEditor}', 'Consolas', 'Courier New', monospace;"
        self.fontUI_QSS = f"font-family: '{self.fontUI}', 'Segoe UI', sans-serif;"

        self.themeCtrl = ThemeController(self)
        self.tabWidget = TabWidget(self)
        self.validPath: bool = os.path.exists(self.mdPath)
        self.markHistory: dict[str, list[dict[str, str]]] = self.loadHistory()
        self.confirmSaveDlg = None
        self.historyManageDlg = None
        self.aboutDialog = None
        self.customCSSDlg = None
        self.customHomeDlg = None
        self.renderMD = MarkdownIt().use(tasklists_plugin).enable("table")
        self.content: str = ""
        self.contentMD = None
        self.htmlContent: str = ""
        self.editMode: bool = cfg.get(cfg.mdStartInEditMode)
        self.baseMD: str = self.loadHomepageContent()
        self.styleMD: str = self.loadStylesheet()
        self.cache: dict = self.configCache()

        self.tabWidget.setMovable(True)
        self.tabWidget.setScrollable(False)
        self.tabWidget.setTabShadowEnabled(True)
        self.tabWidget.setTabMaximumWidth(200)
        self.tabWidget.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        
        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        self.mdNew = Action(FICO.DOCUMENT, "New", triggered=lambda: self.newMDTab(self._currentTabIndex()))
        self.mdOpen = Action(FICO.FOLDER, "Open", triggered=lambda: self.openMDFile(self))
        self.openRecent = TransparentDropDownPushButton(FICO.HISTORY, "Open recent")
        self.openRecent.setFixedHeight(34)
        setFont(self.openRecent, 12)
        self.openRecent.setEnabled(bool(self.markHistory["MarkdownHistory"]))
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

        MDCLayout.addWidget(self.tabWidget)

        if os.path.exists(self.mdPath): self.loadMDFileInNewTab(self.mdPath, self)
        else: self.newMDTab()

        self.currentTabIndex = self.tabWidget.currentIndex()
        self.currentTab = self.tabWidget.currentWidget()
        assert isinstance(self.currentTab, TabInterface)
        self.currentEditor = self.currentTab.mdEditor
        self.currentDisplayer = self.currentTab.mdDisplayer

        self.tabWidget.currentChanged.connect(self.onCurrentTabChanged)
        self.tabWidget.tabCloseRequested.connect(self.closeMDTab)
        self.tabWidget.tabAddRequested.connect(self.newMDTab)
        self.tabWidget.tabBar.contextMenuEvent = lambda a0: print(self._paths())

        if self.markHistory["MarkdownHistory"]:
            self.historyList = RoundMenu(parent=self)
            for path in self.markHistory["MarkdownHistory"]:
                mdPath = path["path"]
                self.historyList.addAction(
                    Action(FICO.DOCUMENT, path["path"], triggered=lambda checked, text=mdPath, parent=self: (
                        self.loadMDFileInNewTab(text, parent, True) if self.currentTab.path or self.currentEditor.text() # type: ignore
                        else self.loadMDFileInTab(self.currentTabIndex, text, parent, True)
                    ))
                )
            self.historyList.addSeparator()
            self.historyList.addAction(
                Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=self: self.openHistoryManager(parent))
            )
            self.openRecent.setMenu(self.historyList)

        self.mdSave.setEnabled(False)
        self.mdSaveAs.setEnabled(self.editMode)
        self.mdUndo.setEnabled(self.editMode and self.currentEditor.isUndoAvailable())
        self.mdRedo.setEnabled(self.editMode and self.currentEditor.isRedoAvailable())
        self.mdCut.setEnabled(False)
        self.mdCopy.setEnabled(False)
        self.mdPaste.setEnabled(self.editMode and self.currentEditor.canPaste())
        self.mdFind.setEnabled(self.editMode)
        self.mdShare.setEnabled(self.validPath)
        self.mdInfo.setEnabled(self.validPath)

        """ self.mdSave.clicked.connect(lambda: self.saveMDFileAtTab(self.currentTabIndex, self.mdPath, self.currentEditor.text(), False, self))
        self.mdSaveAs.clicked.connect(lambda: self.saveMDFileAtTab(self.currentTabIndex, self.mdPath, self.currentEditor.text(), True, self))
        self.mdUndo.clicked.connect(self.currentEditor.undo if self.currentEditor else None)
        self.mdRedo.clicked.connect(self.currentEditor.redo if self.currentEditor else None)
        self.mdCut.clicked.connect(self.currentTab.editorCut)
        self.mdCopy.clicked.connect(self.currentTab.editorCopy)
        self.mdPaste.clicked.connect(self.currentEditor.paste if self.currentEditor else None)
        self.mdInfo.clicked.connect(lambda checked: self.openInfoDialog(self.currentTabIndex))
        self.mdHome.clicked.connect(lambda: self.backToHome(self.currentTabIndex)) """
        self.mdSettings.toggled.connect(lambda checked: self.toggleSettings(checked))

        # Settings
        self.settingsBox = QWidget()
        self.settingsBox.setObjectName("SettingsBox")
        self.settingsBox.setContentsMargins(0, 0, 0, 0)
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
        self.widgetDef = SettingsWidgets.SettingsWidgetDefinition()
        self.saveConfigOnExitDlg = None

        # Settings - General
        settingsContent.addWidget(SubtitleLabel("General"))
        self.widgetDef.optionStartInEditMode.checkedChanged.connect(lambda checked: self.configEditListener())
        settingsContent.addWidget(self.widgetDef.optionStartInEditMode)
        self.widgetDef.optionFixTheme.button.clicked.connect(self.fixTheme)
        settingsContent.addWidget(self.widgetDef.optionFixTheme)
        self.widgetDef.optionManageHistory.button.clicked.connect(lambda: self.openHistoryManager(self))
        settingsContent.addWidget(self.widgetDef.optionManageHistory)

        # Settings - Editor
        editorLabel = SubtitleLabel("Editor")
        editorLabel.setContentsMargins(0, 20, 0, 0)
        settingsContent.addWidget(editorLabel)
        self.fontConfig = SettingsWidgets.EditorFontConfigGroup(self)
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
        self.indentConfig = SettingsWidgets.IndentationConfigGroup(self)
        self.indentConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.indentConfig)
        self.selectColorConfig = SettingsWidgets.EditorSelectionConfigGroup(self)
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
        self.cssPropertiesConfig = SettingsWidgets.CSSPropertiesConfigGroup(self)
        self.cssPropertiesConfig.storageSelectButton.clicked.connect(self.selectLocalCSSSource)
        self.cssPropertiesConfig.customStyleEditButton.clicked.connect(lambda: self.openCustomCSSEditor(self))
        self.cssPropertiesConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.cssPropertiesConfig)
        self.homepageConfig = SettingsWidgets.HomePageConfigGroup(self)
        self.homepageConfig.storageSelectButton.clicked.connect(self.selectLocalHomepageSource)
        self.homepageConfig.customContentEditButton.clicked.connect(lambda: self.openCustomHomeEditor(self))
        self.homepageConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.homepageConfig)
        self.dragDropConfig = SettingsWidgets.DragAndDropEventsConfigGroup(self)
        self.dragDropConfig.configChanged.connect(self.configEditListener)
        settingsContent.addWidget(self.dragDropConfig)

        settingsContent.addStretch()
        MDCLayout.addWidget(self.settingsBox)
        mainLayout.addLayout(MDCLayout)

        self.titleBar.raise_()
        self.mdSave.setEnabled(False)
        self.applyTheme(cfg.get(cfg.appTheme))
        self.themeCtrl.themeChanged.connect(lambda text: self.applyTheme(cfg.get(cfg.appTheme)))

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

    def _paths(self) -> str:
        return f"self.paths = {self.tabsPaths()}"

    def _currentTabIndex(self) -> int:
        return self.tabWidget.currentIndex()

    def applyTheme(self, mode: str):
        setTheme(Theme.DARK)
        """ if mode == "Auto":
            setTheme(Theme.DARK if smart.isDarkModeEnabled() else Theme.LIGHT)
        elif mode == "Dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT) """
        
        self.setMicaEffectEnabled(cfg.get(cfg.micaEffect))

        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            assert isinstance(tab, TabInterface)
            tab.editorBox.setStyleSheet(f"#EditorBox {{ border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"}; }}")
            tab.editorSymbols.setStyleSheet(f"""
                SingleDirectionalScrollArea {{
                    border-radius: 0px;
                    border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                }}
            """)
            tab.mdContainer.setStyleSheet(f"""
                #Container {{
                    border: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                    border-bottom: none;
                    background: transparent;
                }}
            """)
            tab.displayNavBar.setStyleSheet(f"""
                QWidget#DisplayNavigation {{
                    border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                    background: transparent;
                }}
            """)

        self.settingsBox.setStyleSheet(f"""
            QWidget#SettingsBox {{
                background: transparent;
                border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
            }}
        """)

    def tabsPaths(self) -> list[str]:
        paths: list[str] = []

        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            assert isinstance(tab, TabInterface)

            paths.append(tab.path)

        return paths

    def onCurrentTabChanged(self, index: int):
        self.currentTab = self.tabWidget.widget(index)
        assert isinstance(self.currentTab, TabInterface)
        self.currentEditor = self.currentTab.mdEditor
        self.currentDisplayer = self.currentTab.mdDisplayer
        self.mdPath = self.currentTab.path

        self.setWindowTitle(
            f"{"• " if self.currentTab.canSave else ""}{self.currentTab.path if self.currentTab.path else "Untitled"} | {TITLE}"
        )

        self.mdSave.setEnabled(self.editMode and (self.currentTab.canSave or self.currentTab.canSaveContent()))
        self.mdUndo.setEnabled(self.editMode and (self.currentTab.canUndo or self.currentEditor.isUndoAvailable()))
        self.mdRedo.setEnabled(self.editMode and (self.currentTab.canRedo or self.currentEditor.isRedoAvailable()))
        self.mdCut.setEnabled(self.editMode and (self.currentTab.canCut or self.currentEditor.hasSelectedText()))
        self.mdCopy.setEnabled(self.editMode and (self.currentTab.canCopy or self.currentEditor.hasSelectedText()))
        self.mdPaste.setEnabled(self.editMode and (self.currentTab.canPaste or self.currentEditor.canPaste()))
        self.mdShare.setEnabled(self.currentTab.canShare or os.path.exists(self.currentTab.path))
        self.mdInfo.setEnabled(self.currentTab.canInfo or os.path.exists(self.currentTab.path))
        self.mdHome.setEnabled(not self.currentTab.isHome)

        if self.markHistory["MarkdownHistory"]:
            self.historyList = RoundMenu(parent=self)
            for path in self.markHistory["MarkdownHistory"]:
                mdPath = path["path"]
                self.historyList.addAction(
                    Action(FICO.DOCUMENT, path["path"], triggered=lambda checked, text=mdPath, parent=self: (
                        self.loadMDFileInNewTab(text, parent, True) if self.currentTab.path or self.currentEditor.text() # type: ignore
                        else self.loadMDFileInTab(index, text, parent, True)
                    ))
                )
            self.historyList.addSeparator()
            self.historyList.addAction(
                Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=self: self.openHistoryManager(parent))
            )
            self.openRecent.setMenu(self.historyList)

        self.mdSave.clicked.connect(lambda: self.saveMDFileAtTab(index, self.mdPath, self.currentEditor.text(), False, self))
        self.mdSaveAs.clicked.connect(lambda: self.saveMDFileAtTab(index, self.mdPath, self.currentEditor.text(), True, self))
        self.mdUndo.clicked.connect(self.currentEditor.undo if self.currentEditor else None)
        self.mdRedo.clicked.connect(self.currentEditor.redo if self.currentEditor else None)
        self.mdCut.clicked.connect(self.currentTab.editorCut)
        self.mdCopy.clicked.connect(self.currentTab.editorCopy)
        self.mdPaste.clicked.connect(self.currentEditor.paste if self.currentEditor else None)
        self.mdInfo.clicked.connect(lambda checked: self.openInfoDialog(index))
        self.mdHome.clicked.connect(lambda: self.backToHome(index))

    def newMDTab(self, afterIndex: int | None = None):
        self.mdPath = ""
        if afterIndex is not None:
            newTab = self.tabWidget.insertTab(
                afterIndex + 1,
                TabInterface("", "", self.baseMD, self.mdEdit.isChecked(), self),
                "Untitled",
                segSVG.MARKDOWN
            )
        else:
            newTab = self.tabWidget.addTab(
                TabInterface("", "", self.baseMD, self.mdEdit.isChecked(), self),
                "Untitled",
                segSVG.MARKDOWN
            )
        self.tabWidget.setCurrentIndex(newTab)
        self.backToHome(newTab)
    
    def closeMDTab(self, index: int):
        selectedTab = self.tabWidget.widget(index)
        assert isinstance(selectedTab, TabInterface)
        
        if selectedTab.canSave:
            def closeDialog(widget: TabWidget, dialog: MessageBox):
                widget.removeTab(index)
                dialog.reject()

            if self.confirmSaveDlg:
                self.confirmSaveDlg = None
            self.confirmSaveDlg = MessageBox(
                "Save changes before closing",
                "New changes have been made inside this tab. "
                "If you close it without saving, all those changes "
                "will be definitely lost.\n\nDo you want to save them "
                "before closing your tab?",
                self
            )
            self.confirmSaveDlg.yesButton.setText("Save changes and close")
            noButton = PushButton("Close without saving", self.confirmSaveDlg.buttonGroup)
            noButton.clicked.connect(lambda checked, dialog=self.confirmSaveDlg: closeDialog(self.tabWidget, dialog))
            self.confirmSaveDlg.buttonLayout.removeWidget(self.confirmSaveDlg.cancelButton)
            self.confirmSaveDlg.buttonLayout.addWidget(noButton, 1, Qt.AlignmentFlag.AlignVCenter)
            self.confirmSaveDlg.buttonLayout.addWidget(self.confirmSaveDlg.cancelButton, 1, Qt.AlignmentFlag.AlignVCenter)

            if self.confirmSaveDlg.exec():
                try:
                    self.saveMDFileAtTab(
                        index,
                        selectedTab.path,
                        selectedTab.mdEditor.text(),
                        self.tabWidget.tabText(index) == "Untitled",
                        self
                    )
                    self.tabWidget.removeTab(index)
                except Exception as e:
                    RichCLI.log(f"[red][b u]ERROR[/b u]: Failed to save changes: [i]{e}[/]")
                    smart.errorNotify(
                        "Oops! Something went wrong...",
                       f"An error occured while attempting to save your changes:\n{e}",
                       self
                    )
        
        else:
            self.tabWidget.removeTab(index)
        
        if self.tabWidget.count() == 0:
            self.newMDTab()
    
    def openMDFile(self, parent):
        """ Open a Markdown file from storage """
        path = smart.browseFileDialog(parent, "Open a file in the Markdown Viewer", "", "Markdown files (*.md; *.markdown)")
        if path:
            currentIndex = self.tabWidget.currentIndex()
            
            if self.tabsPaths()[currentIndex]:
                self.loadMDFileInNewTab(path, parent)
            else:
                self.loadMDFileInTab(currentIndex, path, parent)

    def loadMDFileInTab(self, tabIndex: int, path: str, parent, fromHistory: bool = False):
        paths = self.tabsPaths()
        path = os.path.normpath(path)
        if os.path.exists(path):
            if smart.isMarkdownExtension(path):
                if smart.getFileMimeType(path).startswith("text"):
                    if path not in paths:
                        self.mdPath = path
                        with open(path, encoding="utf-8") as mdReader:
                            self.content = mdReader.read()
                        self.contentMD = self.renderMD.render(self.content) if cfg.get(cfg.mdCssSource) != "Default" else self._renderGitMarkdown(self.content)
                        self.htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
                        
                        currentTab = self.tabWidget.widget(tabIndex)
                        assert isinstance(currentTab, TabInterface)
                        currentTab.path = path
                        currentTab.content = self.content
                        currentTab.viewContent = self.htmlContent
                        currentTab.mdEditor.setText(self.content)
                        currentTab.mdDisplayer.setHtml(self.htmlContent, QUrl("http://localhost"))
                        self.tabWidget.setCurrentWidget(currentTab)
                        self.markUpdate(tabIndex, False, parent)
                        with open(ROOT_PATH / "markdownContent.log", "w", encoding="utf-8") as mdWriter:
                            mdWriter.write(self.content)
                        with open(ROOT_PATH / "markdownHtml.log", "w", encoding="utf-8") as htmlWriter:
                            htmlWriter.write(self.htmlContent)
                    
                    else:
                        idx = paths.index(path)
                        selectedTab = self.tabWidget.widget(idx)
                        assert isinstance(selectedTab, TabInterface)
                        if selectedTab.path == paths[idx]:
                            self.tabWidget.setCurrentWidget(selectedTab)
                        else:
                            for i in range(self.tabWidget.count()):
                                tab = self.tabWidget.widget(i)
                                assert isinstance(tab, TabInterface)
                                if tab.path == paths[idx]:
                                    self.tabWidget.setCurrentWidget(tab)
                    
                else:
                    smart.warningNotify("Warning, be careful!", "The format of the provided file is not supported...", parent)
                    if fromHistory: self.removeFromHistory(path, parent)

            else:
                smart.warningNotify("Warning, be careful!", "The provided file is not recognized as a Markdown file...", parent)
                if fromHistory: self.removeFromHistory(path, parent)

        else:
            smart.warningNotify("Warning, be careful!", "The file at the provided path does not exist...", parent)
            if fromHistory: self.removeFromHistory(path, parent)

    def loadMDFileInNewTab(self, path: str, parent, fromHistory: bool = False):
        paths = self.tabsPaths()
        path = os.path.normpath(path)
        if os.path.exists(path):
            if smart.isMarkdownExtension(path):
                if smart.getFileMimeType(path).startswith("text"):
                    if path not in paths:
                        self.mdPath = path
                        with open(path, encoding="utf-8") as mdReader:
                            self.content = mdReader.read()
                        self.contentMD = self.renderMD.render(self.content) if cfg.get(cfg.mdCssSource) != "Default" else self._renderGitMarkdown(self.content)
                        self.htmlContent = f'<html>\n<head>\n<style>\n{self.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{self.contentMD}\n</body>\n</html>'
                        newTab = self.tabWidget.addTab(
                            TabInterface(path, self.content, self.htmlContent, self.mdEdit.isChecked(), self),
                            os.path.basename(path),
                            segSVG.MARKDOWN
                        )
                        self.tabWidget.setCurrentIndex(newTab)
                        self.markUpdate(newTab, True, parent)
                        with open(ROOT_PATH / "markdownContent.log", "w", encoding="utf-8") as mdWriter: mdWriter.write(self.content)
                        with open(ROOT_PATH / "markdownHtml.log", "w", encoding="utf-8") as htmlWriter: htmlWriter.write(self.htmlContent)
                    
                    else:
                        idx = paths.index(path)
                        selectedTab = self.tabWidget.widget(idx)
                        assert isinstance(selectedTab, TabInterface)
                        if selectedTab.path == paths[idx]:
                            self.tabWidget.setCurrentWidget(selectedTab)
                        else:
                            for i in range(self.tabWidget.count()):
                                tab = self.tabWidget.widget(i)
                                assert isinstance(tab, TabInterface)
                                if tab.path == paths[idx]:
                                    self.tabWidget.setCurrentWidget(tab)
                    
                else:
                    smart.warningNotify("Warning, be careful!", "The format of the provided file is not supported...", parent)
                    if fromHistory: self.removeFromHistory(path, parent)

            else:
                smart.warningNotify("Warning, be careful!", "The provided file is not recognized as a Markdown file...", parent)
                if fromHistory: self.removeFromHistory(path, parent)

        else:
            smart.warningNotify("Warning, be careful!", "The file at the provided path does not exist...", parent)
            if fromHistory: self.removeFromHistory(path, parent)

    def markUpdate(self, tabIndex: int, inNewTab: bool, parent):
        inHistory: bool = False
        selectedTab = self.tabWidget.widget(tabIndex)
        assert isinstance(selectedTab, TabInterface)
        self.setWindowTitle(f"{selectedTab.path} | {TITLE}")
        self.tabWidget.setTabIcon(tabIndex, segSVG.MARKDOWN)
        if not inNewTab:
            self.tabWidget.setTabText(tabIndex, os.path.basename(selectedTab.path))
        
        for histPath in self.markHistory["MarkdownHistory"]:
            if histPath["path"] == selectedTab.path:
                inHistory = True
                break
        
        if not inHistory:
            self.markHistory["MarkdownHistory"].append({"path": selectedTab.path})
            self.saveHistory(self.markHistory)
            self.markHistory = self.loadHistory()
            self.openRecent.setEnabled(True)
            self.historyList = RoundMenu(parent=self)
            for hPath in self.markHistory["MarkdownHistory"]:
                self.historyList.addAction(Action(FICO.DOCUMENT, hPath["path"], triggered=lambda checked, path=hPath["path"], parent=parent: self.loadMDFileInNewTab(path, parent, True)))
            
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=parent: self.openHistoryManager(parent)))
            self.openRecent.setMenu(self.historyList)
        
        selectedTab.canInfo = True
        self.mdInfo.setEnabled(selectedTab.canInfo)

    def saveMDFileAtTab(self, tabIndex: int, path: str, content: str, saveAs: bool, parent):
        selectedTab = self.tabWidget.widget(tabIndex)
        assert isinstance(selectedTab, TabInterface)
        validPath = os.path.exists(path)
        if saveAs or not validPath:
            newPath = os.path.normpath(
                smart.saveFileDialog(
                    parent,
                    f"Save a Markdown file from {TITLE}",
                    os.path.dirname(path) if validPath else "",
                    "Markdown files (*.md; *.markdown)"
                )
            )
            if newPath:
                with open(newPath, "w", encoding="utf-8") as mdWriter:
                    mdWriter.write(content)
                self.mdPath = newPath
                self.setWindowTitle(f"{newPath} | {TITLE}")
                self.tabWidget.setTabText(tabIndex, os.path.basename(newPath))
                smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
            print(newPath)
        
        else:
            with open(path, 'w', encoding="utf-8") as mdWriter:
                mdWriter.write(content)
            self.setWindowTitle(f"{self.windowTitle()[2:] if self.windowTitle().startswith('•') else self.windowTitle()}")
            smart.successNotify("Save complete!", "The file has been saved successfully!", parent)
            print(path)
        
        self.tabWidget.setTabIcon(tabIndex, segSVG.MARKDOWN)
        selectedTab.canSave = False
        self.mdSave.setEnabled(selectedTab.canSave)

    def loadStylesheet(self) -> str:
        if cfg.get(cfg.mdCssSource) == "Local":
            if os.path.exists(cfg.get(cfg.mdCssSourcePath)):
                with open(cfg.get(cfg.mdCssSourcePath), encoding="utf-8") as styleReader: return styleReader.read()
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()
                smart.warningNotify("Warning, be careful!", "Your local CSS resource cannot be found in your storage. Applying the default style...", self)
        
        elif cfg.get(cfg.mdCssSource) == "Custom":
            if cfg.get(cfg.mdCssProperties): return cfg.get(cfg.mdCssProperties)
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()
                smart.warningNotify("Warning, be careful!", "Your custom CSS properties are currently empty. Applying the default style...", self)
        
        else:
            with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: return styleReader.read()

    def loadHomepageContent(self) -> str:
        if cfg.get(cfg.mdHomepageSource) == "Local":
            if os.path.exists(cfg.get(cfg.mdHomepageSourcePath)):
                with open(cfg.get(cfg.mdHomepageSourcePath), encoding="utf-8") as baseReader: return baseReader.read()
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be careful!", "Your local homepage content cannot be found in your storage. Loading the default homepage...", self)
        
        elif cfg.get(cfg.mdCssSource) == "Custom":
            if cfg.get(cfg.mdCssProperties): return cfg.get(cfg.mdCssProperties)
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                smart.warningNotify("Warning, be careful!", "Your custom homepage properties are currently empty. Loading the default homepage...", self)
        
        else:
            with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader: return (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")

    def openInfoDialog(self, tabIndex: int):
        selectedTab = self.tabWidget.widget(tabIndex)
        assert isinstance(selectedTab, TabInterface)

        if selectedTab.canInfo:
            selectedTab.openInfoDialog()

    def backToHome(self, tabIndex: int):
        toHome: bool = True
        selectedTab = self.tabWidget.widget(tabIndex)
        assert isinstance(selectedTab, TabInterface)

        if selectedTab.canSave:
            def closeDialog(dialog: MessageBox):
                dialog.reject()

            if self.confirmSaveDlg:
                self.confirmSaveDlg = None
            self.confirmSaveDlg = MessageBox(
                "Save changes before going back to Home",
                "New changes have been made inside this tab. "
                "If you go back to Home it without saving, all those changes "
                "will be definitely lost.\n\nDo you want to save them "
                "before going back to Home?",
                self
            )
            self.confirmSaveDlg.yesButton.setText("Save changes and back to Home")
            noButton = PushButton("Back to Home without saving", self.confirmSaveDlg.buttonGroup)
            noButton.clicked.connect(lambda checked, dialog=self.confirmSaveDlg: closeDialog(dialog))
            self.confirmSaveDlg.buttonLayout.removeWidget(self.confirmSaveDlg.cancelButton)
            self.confirmSaveDlg.buttonLayout.addWidget(noButton, 1, Qt.AlignmentFlag.AlignVCenter)
            self.confirmSaveDlg.buttonLayout.addWidget(self.confirmSaveDlg.cancelButton, 1, Qt.AlignmentFlag.AlignVCenter)

            if self.confirmSaveDlg.exec():
                try:
                    self.saveMDFileAtTab(
                        tabIndex,
                        selectedTab.path,
                        selectedTab.mdEditor.text(),
                        self.tabWidget.tabText(tabIndex) == "Untitled",
                        self
                    )
                    toHome = True
                except Exception as e:
                    RichCLI.log(f"[red][b u]ERROR[/b u]: Failed to save changes: [i]{e}[/]")
                    smart.errorNotify(
                        "Oops! Something went wrong...",
                       f"An error occured while attempting to save your changes:\n{e}",
                       self
                    )
                    toHome = False
            else:
                toHome = False

        if toHome:
            selectedTab.path = ""
            selectedTab.content = ""
            selectedTab.viewContent = self.baseMD
            selectedTab.canSave = False
            selectedTab.canUndo = False
            selectedTab.canRedo = False
            selectedTab.canCut = False
            selectedTab.canCopy = False
            selectedTab.canPaste = selectedTab.mdEditor.canPaste()
            selectedTab.canShare = False
            selectedTab.canInfo = False
            selectedTab.isHome = True
            
            selectedTab.mdEditor.setText(selectedTab.content)
            selectedTab.mdDisplayer.setHtml(selectedTab.viewContent, QUrl("http://localhost"))
            self.tabWidget.setTabIcon(tabIndex, segSVG.MARKDOWN)
            self.tabWidget.setTabText(tabIndex, "Untitled")

            currentTab = self.tabWidget.currentIndex()
            if currentTab == tabIndex:
                self.setWindowTitle(f"Untitled | {TITLE}")
                self.mdSave.setEnabled(selectedTab.canSave)
                self.mdUndo.setEnabled(selectedTab.canUndo)
                self.mdRedo.setEnabled(selectedTab.canRedo)
                self.mdCut.setEnabled(selectedTab.canCut)
                self.mdCopy.setEnabled(selectedTab.canCopy)
                self.mdPaste.setEnabled(selectedTab.canPaste)
                self.mdShare.setEnabled(selectedTab.canShare)
                self.mdInfo.setEnabled(selectedTab.canInfo)

    def loadHistory(self):
        try:
            with open(Path(ROOT_PATH / "bin" / "markdown_history.dat"), "rb") as histReader: return pickle.load(histReader)
        except: return {"MarkdownHistory": []}
    
    def saveHistory(self, history):
        try:
            with open(Path(ROOT_PATH / "bin" / "markdown_history.dat"), "wb") as histWriter: pickle.dump(history, histWriter)
        except Exception as e:
            print(f"{Fore.RED}An error occured while attempting to save browser-related changes: {e}{Style.RESET_ALL}")
            smart.managerLog(f"ERROR: Failed to save browser-related changes: {e}")

    def openHistoryManager(self, parent):
        history = self.loadHistory()
        if self.historyManageDlg:
            self.historyManageDlg = None
        self.historyManageDlg = ManageHistoryDialog(history, parent)
        
        if self.historyManageDlg.exec(): # type: ignore
            try:
                self.saveHistory(self.historyManageDlg.tempHistory)
                self.markHistory = self.loadHistory()
                self.historyList = RoundMenu(parent=self)
                for hPath in self.markHistory["MarkdownHistory"]:
                    self.historyList.addAction(
                        Action(
                            FICO.DOCUMENT,
                            hPath["path"],
                            triggered=lambda checked, path=hPath["path"], parent=parent: self.loadMDFileInNewTab(path, parent, True)
                        )
                    )
                self.historyList.addSeparator()
                self.historyList.addAction(Action(FICO.SETTING, "Manage history", triggered=lambda checked, parent=parent: self.openHistoryManager(parent)))
                self.openRecent.setMenu(self.historyList)
                self.historyManageDlg = None
                
                """ mdHistory = [path["path"] for path in self.markHistory["MarkdownHistory"]]
                if self.mdPath not in mdHistory:
                    self.backToHome() """
                smart.successNotify("Save complete!", "The changes have been saved successfully!", parent)
                print(f"{Fore.GREEN}The history changes have been saved successfully!{Style.RESET_ALL}")
            
            except Exception as e:
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to save history changes: {e}", parent)
                print(f"{Fore.RED}An error occured while attempting to save history changes: {e}{Style.RESET_ALL}")

    def removeFromHistory(self, value: str, parent):
        self.markHistory = self.loadHistory()
        try:
            self.markHistory["MarkdownHistory"].remove({"path": value})
        except Exception as e:
            RichCLI.log("[red][b u]ERROR[/b u]: Failed to remove the invalid path " \
                       f"'[i u]{value}[/i u]' from your Markdown history:\n[i]{e}[/]")
            smart.errorNotify(
                "Oops! Something went wrong...",
                "An error occured while attempting to remove an invalid path " \
               f"from your Markdown history:\n{e}",
               self
            )
            return
        
        if self.markHistory["MarkdownHistory"]:
            self.historyList = RoundMenu(parent=self)
            for hPath in self.markHistory["MarkdownHistory"]:
                self.historyList.addAction(
                    Action(
                        FICO.DOCUMENT,
                        hPath["path"],
                        triggered=lambda savedPath=hPath["path"], parent=parent: self.loadMDFileInNewTab(savedPath, parent, True)
                    )
                )
            self.historyList.addSeparator()
            self.historyList.addAction(Action(FICO.SETTING, "Manage history"))
            self.openRecent.setMenu(self.historyList)
        else:
            self.openRecent.setEnabled(False)
            self.historyList.clear()
            smart.infoNotify("Empty history", "Your Markdown history is now empty.")

        self.saveHistory(self.markHistory)
        self.markHistory = self.loadHistory()

    def toggleEditMode(self, check: bool):
        self.editMode = check
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            assert isinstance(tab, TabInterface)
            tab.editorBox.setEnabled(check)
            tab.editorBox.setVisible(check)
            
            if not check:
                tab.canSave = False
                tab.canUndo = False
                tab.canRedo = False
                tab.canCut = False
                tab.canCopy = False
                tab.canPaste = False
            else:
                tab.canSave = tab.canSaveContent()
                tab.canUndo = tab.mdEditor.isUndoAvailable()
                tab.canRedo = tab.mdEditor.isRedoAvailable()
                tab.canCut = tab.mdEditor.hasSelectedText()
                tab.canCopy = tab.mdEditor.hasSelectedText()
                tab.canPaste = tab.mdEditor.canPaste()
        
        currentTab = self.tabWidget.currentWidget()
        assert isinstance(currentTab, TabInterface)
        self.mdSave.setEnabled(currentTab.canSave)
        self.mdSaveAs.setEnabled(check)
        self.mdUndo.setEnabled(currentTab.canUndo)
        self.mdRedo.setEnabled(currentTab.canRedo)
        self.mdCut.setEnabled(currentTab.canCut)
        self.mdCopy.setEnabled(currentTab.canCopy)
        self.mdPaste.setEnabled(currentTab.canPaste)
        self.mdFind.setEnabled(check)
        currentTab.editorUpdate()

    def toggleSettings(self, check: bool):
        def leave(tab: TabInterface):
            self.tabWidget.setEnabled(True)
            self.tabWidget.setVisible(True)
            self.settingsBox.setEnabled(False)
            self.settingsBox.setVisible(False)
            self.mdNew.setEnabled(True)
            self.mdOpen.setEnabled(True)
            self.openRecent.setEnabled(
                bool(self.markHistory["MarkdownHistory"])
                or bool(self.historyList.actions())
            )
            self.mdEdit.setEnabled(True)
            self.mdSave.setEnabled(self.editMode and tab.canSave)
            self.mdSaveAs.setEnabled(self.editMode)
            self.mdUndo.setEnabled(self.editMode and tab.canUndo)
            self.mdRedo.setEnabled(self.editMode and tab.canRedo)
            self.mdCut.setEnabled(self.editMode and tab.canCut)
            self.mdCopy.setEnabled(self.editMode and tab.canCopy)
            self.mdPaste.setEnabled(self.editMode and tab.canPaste)
            self.mdFind.setEnabled(self.editMode)
            self.mdShare.setEnabled(bool(tab.mdEditor.text()))
            self.mdInfo.setEnabled(os.path.exists(tab.path))
            self.mdHome.setEnabled(not tab.isHome)

        currentTab = self.tabWidget.currentWidget()
        assert isinstance(currentTab, TabInterface)
        self.pendingChanges = self.cache != self.configCache()
        
        if check:
            self.tabWidget.setEnabled(not check)
            self.tabWidget.setVisible(not check)
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
                    leave(currentTab)
                else:
                    leave(currentTab) # Discard and leave
            else: leave(currentTab)

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
            cfg.set(cfg.mdSelectionCustomColor, self.selectCustomColorDlg.color.name(QColor.NameFormat.HexArgb))
            self.configEditListener()

    def fixTheme(self):
        self.cache["Personalization"]["EnableMicaEffect"] = cfg.get(cfg.micaEffect)
        self.applyTheme(cfg.get(cfg.appTheme))
        """ if cfg.get(cfg.appTheme) == "Auto":
            setTheme(Theme.DARK if smart.isDarkMode() else Theme.LIGHT)
            self.setStyleSheet("background: white" if not smart.isDarkMode() else "")
            self.mdTitleBar.titleLabel.setStyleSheet(f"color: {"white" if smart.isDarkMode() else "black"}")
        else:
            smart.warningNotify("Warning, be careful!", "Your theme configuration does not follow your system...", self) """

    def selectLocalCSSSource(self):
        try:
            cssPath = smart.browseFileDialog(
                self,
                "Select a CSS file as your new viewer styling resource",
                "",
                "Cascade Style Sheets (*.css)"
            )
            if os.path.exists(cssPath):
                cfg.set(cfg.mdCssSourcePath, cssPath)
                self.cssPropertiesConfig.storagePathSublabel.setText(f"Current source path: {cfg.get(cfg.mdCssSourcePath).replace('/', '\\')}")
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
                cfg.set(cfg.mdHomepageSourcePath, homePath)
                self.homepageConfig.storagePathSublabel.setText(f"Current source path: {cfg.get(cfg.mdHomepageSourcePath).replace('/', '\\')}")
                self.homepageConfig.storagePathSublabel.setVisible(True)
                self.configEditListener()
        except Exception as e: smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to select your HTML file: {e}", self)

    def openCustomCSSEditor(self, parent):
        if self.customCSSDlg is None:
            self.customCSSDlg = SettingsWidgets.CSSCustomPropertiesDialog(
                str(cfg.get(cfg.mdCssProperties)),
                parent
            )
        else:
            self.customCSSDlg = None
            self.customCSSDlg = SettingsWidgets.CSSCustomPropertiesDialog(
                str(cfg.get(cfg.mdCssProperties)),
                parent
            )
        
        if self.customCSSDlg.exec():
            cfg.set(cfg.mdCssProperties, self.customCSSDlg.cssEdit.toPlainText())
            self.configEditListener()

    def openCustomHomeEditor(self, parent):
        if self.customHomeDlg is None:
            self.customHomeDlg = SettingsWidgets.HomepageCustomPropertiesDialog(
                str(cfg.get(cfg.mdHomepageProperties)),
                parent
            )
        else:
            self.customHomeDlg = None
            self.customHomeDlg = SettingsWidgets.HomepageCustomPropertiesDialog(
                str(cfg.get(cfg.mdHomepageProperties)),
                parent
            )
        
        if self.customHomeDlg.exec():
            cfg.set(cfg.mdHomepageProperties, self.customHomeDlg.homeEdit.toPlainText())
            self.configEditListener()

    def configCache(self) -> dict:
        if Path.exists(ROOT_PATH / "bin" / "config.json"):
            with open(ROOT_PATH / "bin" / "config.json") as configCacher:
                return json.load(configCacher)
        return {}

    def configEditListener(self):
        if Path.exists(ROOT_PATH / "bin" / "config.json"):
            with open(ROOT_PATH / "bin" / "config.json") as cfgReader:
                self.dragDropConfig.dragEnterEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
                self.dragDropConfig.dragLeaveEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
                self.dragDropConfig.dropEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
                self.dragDropConfig.dragEnterValidate.setEnabled(
                    cfg.get(cfg.mdHomepageSource) != "Default" and self.dragDropConfig.dragEnterEdit.text() != cfg.get(cfg.mdDragEnterJSFunction)
                )
                self.dragDropConfig.dragLeaveValidate.setEnabled(
                    cfg.get(cfg.mdHomepageSource) != "Default" and self.dragDropConfig.dragLeaveEdit.text() != cfg.get(cfg.mdDragLeaveJSFunction)
                )
                self.dragDropConfig.dropValidate.setEnabled(
                    cfg.get(cfg.mdHomepageSource) != "Default" and self.dragDropConfig.dropEdit.text() != cfg.get(cfg.mdDropJSFunction)
                )
                self.settingsApplyEdits.setEnabled(self.cache != json.load(cfgReader))
        else:
            smart.warningNotify("Warning, be careful!", "The Markdown configuration file cannot be found...", self)

    def configSave(self):
        print(f"Saving new configuration and applying changes to {TITLE}...")
        self.editorFont = QFont(
            cfg.get(cfg.mdFontFamily),
            cfg.get(cfg.mdFontSize),
            cfg.get(cfg.mdFontWeight)
        )
        
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            assert isinstance(tab, TabInterface)

            # Editor
            tab.mdEditor.setFont(self.editorFont)
            tab.mdEditor.setMarginLineNumbers(0, cfg.get(cfg.mdDisplayLineNumbers))
            tab.mdEditor.setMarginWidth(0, "0000" if cfg.get(cfg.mdDisplayLineNumbers) else 0)
            tab.mdEditor.setMarginsFont(self.editorFont)
            tab.mdEditor.setMarginsBackgroundColor(QColor("#282C34") if theme() == Theme.DARK else QColor("#E6E9EF"))
            tab.mdEditor.setMarginsForegroundColor(QColor("#4B5263") if theme() == Theme.DARK else QColor("#ACB0BE"))
            tab.editorSymbols.setEnabled(cfg.get(cfg.mdDisplaySymbolsBar))
            tab.editorSymbols.setVisible(cfg.get(cfg.mdDisplaySymbolsBar))
            tab.editorStatus.setVisible(cfg.get(cfg.mdDisplayStatusBar))
            tab.mdEditor.setLexer(tab.mdEditor.editorLexer if cfg.get(cfg.mdEnableSyntaxHighlighting) else None)
            tab.mdEditor.setWrapMode(QsciScintilla.WrapMode.WrapWord if cfg.get(cfg.mdEnableWordWrap) else QsciScintilla.WrapMode.WrapNone)
            tab.mdEditor.setCaretLineVisible(cfg.get(cfg.mdHighlightCurrentLine))
            tab.mdEditor.setIndentationWidth(cfg.get(cfg.mdIndentWidth))
            tab.mdEditor.setIndentationGuides(cfg.get(cfg.mdDisplayIndentGuides))
            tab.mdEditor.setAutoIndent(cfg.get(cfg.mdEnableAutoIndent))
            tab.mdEditor.setSelectionBackgroundColor(
                cfg.get(cfg.accentColor) if cfg.get(cfg.mdSelectionColorMode) == "Accent"
                else cfg.get(cfg.mdSelectionCustomColor)
            )

            # Viewer
                # Homepage
            if cfg.get(cfg.mdHomepageSource) == "Local":
                if os.path.exists(cfg.get(cfg.mdHomepageSourcePath)):
                    with open(cfg.get(cfg.mdHomepageSourcePath), encoding="utf-8") as baseReader:
                        self.baseMD = baseReader.read()
                else:
                    with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader:
                        self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                    smart.warningNotify("Warning, be careful!", "Your local homepage content cannot be found in your storage, the default homepage will be used...", self)
                    self.homepageConfig.sourceTypeCombo.setCurrentIndex(0)
                    cfg.set(cfg.mdHomepageSource, "Default")
            
            elif cfg.get(cfg.mdCssSource) == "Custom":
                if cfg.get(cfg.mdCssProperties):
                    self.baseMD = cfg.get(cfg.mdCssProperties)
                else:
                    with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader:
                        self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
                    smart.warningNotify("Warning, be careful!", "Your custom homepage properties are currently empty, the default homepage will be used...", self)
                    self.homepageConfig.sourceTypeCombo.setCurrentIndex(0)
                    cfg.set(cfg.mdHomepageSource, "Default")
            
            else:
                with open(smart.resourcePath("resources/assets/markdown-base-content.html"), encoding="utf-8") as baseReader:
                    self.baseMD = (baseReader.read().replace("Markdown Viewer", TITLE)).replace("Open a Markdown file", "Open")
            
            if tab.isHome:
                tab.mdDisplayer.setHtml(self.baseMD, QUrl("http://localhost"))

                # CSS
            if cfg.get(cfg.mdCssSource) == "Local":
                if os.path.exists(cfg.get(cfg.mdCssSourcePath)):
                    with open(cfg.get(cfg.mdCssSourcePath), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
                    if cfg.get(cfg.mdCssSource) != self.cache["Markdown-Viewer"]["CSSSource"] or \
                    (cfg.get(cfg.mdCssSource) == self.cache["Markdown-Viewer"]["CSSSource"] and cfg.get(cfg.mdCssSourcePath) != self.cache["Markdown-Viewer"]["CSSSourcePath"]):
                        smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)
                else:
                    with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader: self.styleMD = styleReader.read()
                    smart.warningNotify("Warning, be careful!", "Your local CSS resource cannot be found in your storage, the default style will be applied...", self)
                    self.cssPropertiesConfig.sourceTypeCombo.setCurrentIndex(0)
                    cfg.set(cfg.mdCssSource, "Default")
            
            elif cfg.get(cfg.mdCssSource) == "Custom":
                if cfg.get(cfg.mdCssProperties):
                    self.styleMD = cfg.get(cfg.mdCssProperties)
                    if cfg.get(cfg.mdCssSource) != self.cache["Markdown-Viewer"]["CSSSource"] or \
                    (cfg.get(cfg.mdCssSource) == self.cache["Markdown-Viewer"]["CSSSource"] and cfg.get(cfg.mdCssProperties) != self.cache["Markdown-Viewer"]["CSSProperties"]):
                        smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)
                else:
                    with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader:
                        self.styleMD = styleReader.read()
                    smart.warningNotify("Warning, be careful!", "Your custom CSS properties are currently empty, the default style will be applied...", self)
                    self.cssPropertiesConfig.sourceTypeCombo.setCurrentIndex(0)
                    cfg.set(cfg.mdCssSource, "Default")
            else:
                with open(smart.resourcePath("resources/assets/github-markdown.css"), encoding="utf-8") as styleReader:
                    self.styleMD = styleReader.read()
                if cfg.get(cfg.mdCssSource) != self.cache["Markdown-Viewer"]["CSSSource"]:
                    smart.infoNotify("Information", "The new style will be applied to the next Markdown files to be loaded.", self)

        self.cache = self.configCache()
        self.settingsApplyEdits.setEnabled(False)
        print(f"{Fore.GREEN}New configuration saved and changes applied to {TITLE}!{Style.RESET_ALL}")
        smart.successNotify("Configuration complete", "The changes have been saved and applied successfully!", self)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not getattr(self, "tabWidget", None):
            return

        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            assert isinstance(tab, TabInterface)
            
            if tab.editorBox:
                tab.editorBox.setFixedWidth(self.width() // 2)

    def eventFilter(self, obj, event):
        if hasattr(self, "tabWidget"):
            if obj == self and event.type() in [QEvent.Type.KeyPress, QEvent.Type.KeyRelease]:
                for i in range(self.tabWidget.count()):
                    tab = self.tabWidget.widget(i)
                    assert isinstance(tab, TabInterface)
                    tab.editorStatusUpdate()

        return super().eventFilter(obj, event)

    # Paramètres :
    ## Editeur :
    #### Couleur de syntaxe

class TabInterface(QWidget):
    """ Class for tab layout and content """

    def __init__(self, path: str, content: str, viewContent: str,
                 editMode: bool, owner: SmartDownMarkerGUI, parent = None):
        super().__init__(parent)
        self.tabParent = owner
        self.path = path
        self.content: str = content
        self.viewContent: str = viewContent
        self.canSave: bool = False
        self.canUndo: bool = False
        self.canRedo: bool = False
        self.canCut: bool = False
        self.canCopy: bool = False
        self.canPaste: bool = True
        self.canShare: bool = bool(self.content)
        self.canInfo: bool = os.path.exists(path)
        self.isHome: bool = not self.content
        self.symbols: list[str] = [
            '<', '>', '[', ']', '{', '}', '(', ')', '/', '\\', '"', "'", '.', ',', ';', ':', '-', '_', '=', '&', '|', '`', '?', '!', '@', '#', '^',
            '¨', '$', '%', '~', '°', '*', '+', '§', 'µ', '€'
        ]
        self.displayScrollX = 0
        self.displayScrollY = 0
        self.pendingDisplayScrollRestore: bool = False
        self.aboutDialog = None

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(0)
        # self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.editorBox = QWidget()
        self.editorBox.setObjectName("EditorBox")
        self.editorBox.setContentsMargins(0, 0, 0, 0)
        self.editorBox.setFixedWidth(self.tabParent.width() // 2)
        self.editorBox.setEnabled(editMode)
        self.editorBox.setVisible(editMode)
        editorLayout = QVBoxLayout(self.editorBox)
        editorLayout.setContentsMargins(0, 0, 0, 0)
        editorLayout.setSpacing(0)
        editorZone = QHBoxLayout()
        editorZone.setContentsMargins(0, 0, 0, 0)
        editorZone.setSpacing(0)
        
        # Editor
        self.mdEditor = MarkEditor(self)
        self.mdEditor.setText(self.content)
        self.mdEditor.installEventFilter(self)
        self.mdEditor.textChanged.connect(self.editorUpdate)
        self.mdEditor.cursorPositionChanged.connect(self.editorStatusUpdate)
        self.mdEditor.selectionChanged.connect(self.editorSelectionUpdate)

        self.editorSymbols = SingleDirectionScrollArea(self, Qt.Orientation.Horizontal)
        self.editorSymbols.setContentsMargins(0, 0, 0, 0)
        self.editorSymbols.setWidgetResizable(True)
        self.editorSymbols.setMaximumHeight(41)
        self.editorSymbols.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editorSymbols.enableTransparentBackground()
        self.editorSymbolsWidget = QWidget()
        self.editorSymbols.setWidget(self.editorSymbolsWidget)
        self.editorSymbolsLayout = QHBoxLayout(self.editorSymbolsWidget)
        self.editorSymbolsLayout.setContentsMargins(10, 10, 10, 10)
        self.editorSymbolsLayout.setSpacing(20)
        self.editorSymbolsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.symTab = CaptionLabel("Tab")
        self.symTab.setStyleSheet(f"{self.tabParent.fontEditor_QSS} font-size: 16px;")
        self.symTab.mousePressEvent = lambda ev: self.mdEditor.insertTab()
        self.editorSymbolsLayout.addWidget(self.symTab)
        for sym in self.symbols:
            symbol = CaptionLabel(sym)
            symbol.setStyleSheet(f"{self.tabParent.fontEditor_QSS} font-size: 16px;")
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
        self.statusLineCol.setStyleSheet(self.tabParent.fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusLineCol)
        self.editorStatusBox.addStretch()
        self.statusEncoding = CaptionLabel()
        self.statusEncoding.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusEncoding.setStyleSheet(self.tabParent.fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusEncoding)
        self.editorStatusBox.addStretch()
        self.statusCapsLock = CaptionLabel("Caps Lock")
        self.statusCapsLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusCapsLock.setStyleSheet(self.tabParent.fontUI_QSS)
        self.statusCapsLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x14) & 1))
        self.editorStatusBox.addWidget(self.statusCapsLock)
        self.statusNumLock = CaptionLabel("Num Lock")
        self.statusNumLock.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusNumLock.setStyleSheet(self.tabParent.fontUI_QSS)
        self.statusNumLock.setVisible(bool(ctypes.windll.user32.GetKeyState(0x90) & 1))
        self.editorStatusBox.addWidget(self.statusNumLock)
        self.editorStatusBox.addStretch()
        self.statusTotalChars = CaptionLabel()
        self.statusTotalChars.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalChars.setStyleSheet(self.tabParent.fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusTotalChars)
        self.statusTotalLines = CaptionLabel()
        self.statusTotalLines.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalLines.setStyleSheet(f"font-family: {self.tabParent.fontUI}, 'Segoe UI', sans-serif;")
        self.editorStatusBox.addWidget(self.statusTotalLines)
        self.statusTotalWords = CaptionLabel()
        self.statusTotalWords.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.statusTotalWords.setStyleSheet(self.tabParent.fontUI_QSS)
        self.editorStatusBox.addWidget(self.statusTotalWords)

        editorZone.addWidget(self.mdEditor)
        editorLayout.addLayout(editorZone)
        editorLayout.addWidget(self.editorSymbols)
        editorLayout.addWidget(self.editorStatus)
        self.hBoxLayout.addWidget(self.editorBox, 1)

        # Viewer
        self.mdContainer = QWidget(self)
        self.mdContainer.setObjectName("Container")
        self.mdContainer.setContentsMargins(0, 0, 0, 0)
        self.mdContainer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        displayLayout = QVBoxLayout(self.mdContainer)
        displayLayout.setContentsMargins(1, 1, 1, 0)
        displayLayout.setSpacing(0)
        self.mdDisplayer = MarkWebView(self)
        self.mdDisplayer.setAcceptDrops(True)
        self.mdDisplayer.loadFinished.connect(self._restorePreviewScrollPosition)
        self.mdDisplayer.setHtml(self.viewContent, QUrl("http://localhost"))
        displayLayout.addWidget(self.mdDisplayer)
        self.displayNavBar = DisplayNavigationBar(self)
        displayLayout.addWidget(self.displayNavBar)
        self.hBoxLayout.addWidget(self.mdContainer, 1)

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

    def canSaveContent(self) -> bool:
        text = self.mdEditor.text()
        validPath = os.path.exists(self.path)
        if text:
            if validPath:
                with open(self.path, 'r', encoding="utf-8") as origReader: origText = origReader.read()
                return not origText == text
        return False

    def editorCut(self):
        if self.mdEditor:
            self.mdEditor.cut()
            self.canPaste = self.mdEditor.canPaste()
            self.tabParent.mdPaste.setEnabled(self.canPaste)

    def editorCopy(self):
        if self.mdEditor:
            self.mdEditor.copy()
            self.canPaste = self.mdEditor.canPaste()
            self.tabParent.mdPaste.setEnabled(self.canPaste)

    def editorUpdate(self):
        currentTab = self.tabParent.tabWidget.currentIndex()
        self.content =  self.mdEditor.text()
        validPath = os.path.exists(self.path)
        if self.content:
            if validPath:
                self.canSave = self.canSaveContent()
            else:
                self.canSave = bool(self.content)
            self.isHome = False
            self.tabParent.mdSave.setEnabled(self.canSave)
            self.tabParent.setWindowTitle(
                f"{"• " if self.canSave else ""}{self.path if validPath else "Untitled"} | {TITLE}"
            )
            self.tabParent.tabWidget.setTabIcon(currentTab, FICO.SAVE if self.canSave else segSVG.MARKDOWN)
            markText = self.tabParent.renderMD.render(self.content) if cfg.get(cfg.mdCssSource) != "Default" else self.tabParent._renderGitMarkdown(self.content)
            self._savePreviewScrollPosition()
            self.pendingDisplayScrollRestore = True
            self.viewContent = f'<html>\n<head>\n<style>\n{self.tabParent.styleMD}</style>\n</head>\n\n<body class="markdown-body" style="padding: 20px;">\n{markText}\n</body>\n</html>'
            self.mdDisplayer.setHtml(self.viewContent, QUrl("http://localhost"))
            self.canUndo = self.mdEditor.isUndoAvailable() if self.tabParent.mdEdit.isChecked() else False
            self.canRedo = self.mdEditor.isRedoAvailable() if self.tabParent.mdEdit.isChecked() else False
            self.tabParent.mdUndo.setEnabled(self.canUndo)
            self.tabParent.mdRedo.setEnabled(self.canRedo)
        
        else:
            self.canSave = False if not validPath else self.canSaveContent()
            self.isHome = True
            self.mdDisplayer.setHtml(self.tabParent.baseMD, QUrl("http://localhost"))
            self.tabParent.mdSave.setEnabled(self.canSave)
            self.tabParent.setWindowTitle(f"{"• " if self.canSave else ""}{"Untitled" if not validPath else self.path} | {TITLE}")
            self.tabParent.tabWidget.setTabIcon(currentTab, FICO.SAVE if self.canSave else segSVG.MARKDOWN)
        
        self.tabParent.tabWidget.setTabIcon(currentTab, FICO.SAVE if self.canSave else segSVG.MARKDOWN)
        self.editorStatusUpdate()
    
    def editorSelectionUpdate(self):
        self.editorStatusUpdate()
        selectedChars = self.mdEditor.selectedText()
        self.canCut = bool(selectedChars)
        self.canCopy = bool(selectedChars)
        self.tabParent.mdCut.setEnabled(self.canCut)
        self.tabParent.mdCopy.setEnabled(self.canCopy)

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

    def openInfoDialog(self):
        if self.canInfo:
            if self.aboutDialog:
                self.aboutDialog = None
            self.aboutDialog = AboutDocumentDialog(self.path, self.tabParent)
            if self.aboutDialog.exec():
                self.aboutDialog = None

class MarkWebView(FramelessWebEngineView):
    """ Class for the Markdown viewer webview """
    
    def __init__(self, parent: TabInterface):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dropParent = parent
        self.currentTabID: int
        self.reqUrl: str
        self.isHome: bool = True
        self.isCurrentContent: bool = False
        self.isLoading: bool = False

        self.setLocale(smLocale)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True) # type: ignore

        self.page().linkHovered.connect(lambda link: RichCLI.log(f"Hovered link: {link}") if link else None) # type: ignore
        self.page().navigationRequested.connect(self.onNavigationRequested) # type: ignore
        self.loadStarted.connect(self.onLoadStarted)
        self.loadProgress.connect(self.onLoadProgress)
        self.loadFinished.connect(self.onLoadFinished)
        self.iconChanged.connect(self.onIconLoaded)

    def onNavigationRequested(self, request: QWebEngineNavigationRequest):
        """ :MarkWebView: Intercept and handle navigation requests based on `openExternalLinks` setting """
        self.reqUrl = request.url().toString()
        self.isHome = unquote(self.reqUrl).replace("data:text/html;charset=UTF-8,", "") == self.dropParent.tabParent.baseMD
        self.isCurrentContent = unquote(self.reqUrl).replace("data:text/html;charset=UTF-8,", "") == self.dropParent.viewContent
        
        self.dropParent.tabParent.mdHome.setEnabled(not self.isHome)
        
        if cfg.get(cfg.mdOpenExternalLinks):
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
                smart.warningNotify("Warning, be careful!", "Access to non-Markdown content is currently disabled...", self)

    def onLoadStarted(self):
        """ :MarkWebView: Handle load started event """
        if cfg.get(cfg.mdOpenExternalLinks):
            self.dropParent.displayNavBar.navProgress.setVisible(True)
            self.dropParent.displayNavBar.navProgress.setValue(0)
            self.dropParent.displayNavBar.navRefresh.setIcon(FICO.CLOSE)
            self.isLoading = True
    
    def onLoadProgress(self, progress: int):
        """ :MarkWebView: Handle load progress event """
        if cfg.get(cfg.mdOpenExternalLinks):
            self.dropParent.displayNavBar.navProgress.setValue(progress)
    
    def onLoadFinished(self):
        """ :MarkWebView: Handle load finished event """
        if cfg.get(cfg.mdOpenExternalLinks):
            self.dropParent.displayNavBar.navProgress.setVisible(False)
            self.dropParent.displayNavBar.navProgress.setValue(0)
            self.dropParent.displayNavBar.navRefresh.setIcon(segFont.fromName("Refresh"))
            self.isLoading = False

    def onIconLoaded(self, icon: QIcon):
        """ :MarkWebView: Handle icon loaded event """
        if cfg.get(cfg.mdOpenExternalLinks):
            self.dropParent.displayNavBar.navIcon.setIcon(icon)
            # self.dropParent.displayNavBar.navIcon.setVisible(not self.isHome and not self.isCurrentContent)

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        """ :MarkWebView: Handle drag enter event """
        if event.mimeData().hasUrls(): # type: ignore
            event.acceptProposedAction() # type: ignore
            if self.dropParent.isHome: self.page().runJavaScript(cfg.get(cfg.mdDragEnterJSFunction) or "onDragEnter()") # type: ignore
    
    def dragLeaveEvent(self, event: QDragLeaveEvent | None):
        """ :MarkWebView: Handle drag leave event """
        event.accept() # type: ignore
        if self.dropParent.isHome: self.page().runJavaScript(cfg.get(cfg.mdDragLeaveJSFunction) or "onDragLeave()") # type: ignore
    
    def dropEvent(self, event: QDropEvent | None):
        """ :MarkWebView: Handle drop event """
        self.currentTabID = self.dropParent.tabParent.tabWidget.currentIndex()
        if event.mimeData().hasUrls(): # type: ignore
            for url in event.mimeData().urls(): # type: ignore
                localPath = url.toLocalFile()
                if self.dropParent.isHome:
                    self.page().runJavaScript(cfg.get(cfg.mdDropJSFunction) or "onDrop()") # type: ignore
                self.dropParent.tabParent.loadMDFileInTab(self.currentTabID, localPath, self.dropParent)

    """ def contextMenuEvent(self, event: QContextMenuEvent | None):
        smart.infoNotify("Did you know?", "The viewer's context menu has been blocked.", self.dropParent) """

class DisplayNavigationBar(QWidget):
    """ Class for the navigation bar displayed under `MarkWebView` """

    def __init__(self, parent: TabInterface):
        super().__init__(parent)
        self.navParent = parent

        self.setObjectName("DisplayNavigation")
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumHeight(45)
        self.setStyleSheet(f"""
            QWidget#DisplayNavigation {{
                border-top: 1px solid {"#E3E6E9" if theme() == Theme.LIGHT else "#393939"};
                background: transparent;
            }}
        """)
        self.setVisible(cfg.get(cfg.mdOpenExternalLinks))
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
                "Warning, be careful!",
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
            self.navParent.tabParent
        )
        returnToMarkdownDlg.yesButton.setText("Return to Markdown content")
        returnToMarkdownDlg.cancelButton.setText("Continue browsing")
        if returnToMarkdownDlg.exec():
            self.navParent.mdDisplayer.setHtml(self.navParent.tabParent.baseMD, QUrl("http://localhost"))
            if self.navParent.viewContent:
                self.navParent.mdDisplayer.setHtml(self.navParent.viewContent, QUrl("http://localhost"))
            displayHistory = self.navParent.mdDisplayer.page().history() # type: ignore
            displayHistory.clear() # type: ignore
            history = [displayHistory.itemAt(i) for i in range(displayHistory.count())] # type: ignore
            for item in history:
                print(item.url().toString())

class MarkEditor(QsciScintilla):
    """ Class for the SmartLinker-adapted Markdown editor """

    def __init__(self, parent: TabInterface):
        super().__init__(parent)
        self.editParent = parent
        self.setStyleSheet(f"background: {"#282C34" if theme() == Theme.DARK else "#EFF1F5"};")
        self.setSelectionBackgroundColor(
            cfg.get(cfg.accentColor) if cfg.get(cfg.mdSelectionColorMode) == "Accent"
            else cfg.get(cfg.mdSelectionCustomColor)
        )
        
        # Font config
        self.editorFont = QFont(
            cfg.get(cfg.mdFontFamily),
            cfg.get(cfg.mdFontSize),
            cfg.get(cfg.mdFontWeight)
        )
        self.setFont(self.editorFont)

        # Syntax highlighting (lexer)
        self.editorLexer = QsciLexerMarkdown(self)
        self.editorLexer.setFont(self.editorFont)
        self.editorLexer.setColor(QColor("#ABB2BF") if theme() == Theme.DARK else QColor("#4C4F69"), 0)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header1)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header2)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header3)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header4)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header5)
        self.editorLexer.setColor(QColor("#E06C75") if theme() == Theme.DARK else QColor("#D20F39"), QsciLexerMarkdown.Header6)
        self.editorLexer.setColor(QColor("#D19A66") if theme() == Theme.DARK else QColor("#FE640B"), QsciLexerMarkdown.EmphasisUnderscores)
        self.editorLexer.setColor(QColor("#D19A66") if theme() == Theme.DARK else QColor("#FE640B"), QsciLexerMarkdown.StrongEmphasisUnderscores)
        self.editorLexer.setColor(QColor("#98C379") if theme() == Theme.DARK else QColor("#40A02B"), QsciLexerMarkdown.EmphasisAsterisks)
        self.editorLexer.setColor(QColor("#98C379") if theme() == Theme.DARK else QColor("#40A02B"), QsciLexerMarkdown.StrongEmphasisAsterisks)
        self.editorLexer.setColor(QColor("#5C6370") if theme() == Theme.DARK else QColor("#8C8FA1"), QsciLexerMarkdown.StrikeOut)
        self.editorLexer.setColor(QColor("#C678DD") if theme() == Theme.DARK else QColor("#8839EF"), QsciLexerMarkdown.Link)
        self.editorLexer.setColor(QColor("#61AFEF") if theme() == Theme.DARK else QColor("#1E66F5"), QsciLexerMarkdown.CodeBackticks)
        self.editorLexer.setColor(QColor("#E5C07B") if theme() == Theme.DARK else QColor("#DF8E1D"), QsciLexerMarkdown.CodeDoubleBackticks)
        self.editorLexer.setColor(QColor("#4082E4") if theme() == Theme.DARK else QColor("#2196F3"), QsciLexerMarkdown.CodeBlock)
        if cfg.get(cfg.mdEnableSyntaxHighlighting): self.setLexer(self.editorLexer)

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(cfg.get(cfg.mdIndentWidth))
        self.setIndentationGuides(cfg.get(cfg.mdDisplayIndentGuides))
        self.setAutoIndent(cfg.get(cfg.mdEnableAutoIndent))

        # Margin #0: number column
        self.setMarginWidth(0, "0000" if cfg.get(cfg.mdDisplayLineNumbers) else 0)
        self.setMarginLineNumbers(0, cfg.get(cfg.mdDisplayLineNumbers))
        self.setMarginsFont(self.editorFont)
        self.setMarginsBackgroundColor(QColor("#282C34") if theme() == Theme.DARK else QColor("#E6E9EF"))
        self.setMarginsForegroundColor(QColor("#4B5263") if theme() == Theme.DARK else QColor("#ACB0BE"))

        # Word wrap
        self.setWrapMode(self.WrapMode.WrapWord if cfg.get(cfg.mdEnableWordWrap) else self.WrapMode.WrapNone)
        
        # Current line highlighting (caret)
        self.setCaretLineVisible(cfg.get(cfg.mdHighlightCurrentLine))
        self.setCaretLineBackgroundColor(QColor("#4B5263") if theme() == Theme.DARK else QColor("#CFCFCF"))

        # Brace/Pair matching
        self.setBraceMatching(self.BraceMatch.StrictBraceMatch)

    def undo(self):
        super().undo()
        self.editParent.tabParent.mdUndo.setEnabled(self.editParent.tabParent.editMode and self.isUndoAvailable()) # type: ignore

    def redo(self):
        super().redo()
        self.editParent.tabParent.mdRedo.setEnabled(self.editParent.tabParent.editMode and self.isRedoAvailable()) # type: ignore

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
        self.markdownHistory = history
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

class AboutDocumentDialog(MessageBoxBase):
    """ Class for the `About the document` dialog box """

    class OverviewCard(SimpleCardWidget):

        def __init__(self, path: str, parent):
            super().__init__(parent)
            self.iconWidget = IconWidget(segSVG.MARKDOWN, self)
            self.titleLabel = SubtitleLabel(os.path.basename(path), self)
            self.pathLabel = CaptionLabel(path, self)

            self.hBoxLayout = QHBoxLayout(self)
            self.labelBox = QVBoxLayout()

            self.setFixedHeight(80)
            self.iconWidget.setFixedSize(40, 40)
            self.pathLabel.setTextColor(QColor("#606060"), QColor("#d2d2d2"))

            self.hBoxLayout.setContentsMargins(20, 11, 20, 11)
            self.hBoxLayout.setSpacing(15)
            self.hBoxLayout.addWidget(self.iconWidget)
            self.labelBox.setContentsMargins(0, 0, 0, 0)
            self.labelBox.setSpacing(0)
            self.labelBox.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
            self.labelBox.addWidget(self.pathLabel, 0, Qt.AlignmentFlag.AlignVCenter)
            self.labelBox.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.hBoxLayout.addLayout(self.labelBox)

    def __init__(self, path: str, parent: SmartDownMarkerGUI):
        super().__init__(parent)
        self.dialogParent = parent
        self.topLine = QHBoxLayout()
        self.icon = IconWidget(FICO.INFO, self)
        self.titleLabel = SubtitleLabel("About this document", self)
        self.topCard = self.OverviewCard(path, self)
        self.metadata = self.getMetadataFromPath(path)

        self.widget.setMinimumWidth(400)
        self.topLine.setContentsMargins(0, 0, 0, 0)
        self.topLine.setSpacing(15)
        self.topLine.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.icon.setFixedSize(24, 24)
        
        self.yesButton.clicked.connect(lambda: self.reject())
        self.cancelButton.setParent(None)
        self.buttonLayout.removeWidget(self.cancelButton)
        self.buttonLayout.removeWidget(self.yesButton)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.yesButton, 1)

        self.topLine.addWidget(self.icon)
        self.topLine.addWidget(self.titleLabel)

        self.viewLayout.addLayout(self.topLine)
        self.viewLayout.addWidget(self.topCard)

        self.addInfo(
            segFont.fromName("HardDrive"), "Size",
            f"{self.metadata["sizeHumanReadable"]} ({self.metadata["sizeBytes"]} B)"
        )
        self.addInfo(FICO.CALENDAR, "Last modified at", self.metadata["lastModifiedAt"])
        self.addInfo(FICO.VIEW, "Read-only", self.metadata["isReadOnly"])
        self.addInfo(FICO.MORE, "MIME type", self.metadata["mimeType"])

    def addInfo(self, icon: QIcon | str | FluentIconBase, name: str, value: str):
        """ :AboutDocumentDialog: Add a metadata of the file to the list """

        l = QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        l.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        i = IconWidget(icon or FICO.INFO)
        i.setFixedSize(16, 16)

        v = BodyLabel(str(value))
        v.setWordWrap(True)

        l.addWidget(i)
        l.addWidget(BodyLabel(name), 1)
        l.addWidget(v, 1)

        self.viewLayout.addLayout(l)

    def getMetadataFromPath(self, filePath: str) -> dict:
        """ :AboutDocumentDialog: Collect all metadata from the specified path's file into a `dict` """
        path = Path(filePath)
        meta = {}
        dateTime = datetime.datetime

        # -------------------
        # Filesystem metadata
        # -------------------
        statInfo = path.stat()

        meta["name"] = path.name
        meta["extension"] = path.suffix
        meta["absolutePath"] = str(path.resolve())
        meta["parentDir"] = str(path.parent.resolve())

        meta["sizeBytes"] = statInfo.st_size
        meta["sizeHumanReadable"] = f"{statInfo.st_size / 1024:.2f} KB"

        meta["createdAt"] = dateTime.fromtimestamp(statInfo.st_ctime).isoformat()
        meta["lastModifiedAt"] = dateTime.fromtimestamp(statInfo.st_mtime).isoformat()
        meta["lastAccessedAt"] = dateTime.fromtimestamp(statInfo.st_atime).isoformat()

        meta["isReadOnly"] = not os.access(filePath, os.W_OK)
        meta["permissions"] = stat.filemode(statInfo.st_mode)
        meta["isFile"] = path.is_file()
        meta["isSymlink"] = path.is_symlink()
        meta["mimeType"] = smart.getFileMimeType(filePath)

        # ----------------
        # Content metadata
        # ----------------
        with open(filePath, "rb") as binaRead:
            rawBytes = binaRead.read()

        # Detect line endings
        if b'\r\n' in rawBytes:
            meta["lineEnding"] = "CRLF (Windows)"
        elif b'\n' in rawBytes:
            meta["lineEnding"] = "LF (Unix)"
        elif b'\r' in rawBytes:
            meta["lineEnding"] = "CR (Old Mac)"
        else:
            meta["lineEnding"] = "None (Single line or empty)"

        # Detect encoding
        if rawBytes.startswith(b'\xef\xbb\xbf'):
            meta["detectedEncoding"] = "UTF-8-SIG (BOM)"
            encodingToUse = "utf-8-sig"
        else:
            try:
                rawBytes.decode("utf-8")
                meta["detectedEncoding"] = "UTF-8"
                encodingToUse = "utf-8"
            except UnicodeDecodeError:
                meta["detectedEncoding"] = "Likely Windows-1252 / Latin-1"
                encodingToUse = "cp1252"

        with open(filePath, encoding=encodingToUse) as f:
            content = f.read()
            lines = content.splitlines()

        meta["totalChars"] = len(content)
        meta["totalCharsNoSpaces"] = len(content.replace(" ", "").replace("\n", "").replace("\t", ""))
        meta["totalLines"] = len(lines)
        meta["totalWords"] = len(content.split())
        meta["emptyLines"] = sum(1 for line in lines if not line.strip())
        meta["longestLineLength"] = max((len(line) for line in lines), default=0)

        # Language/Content hints (top 5 most common words)
        wordsCleaned = [word.strip('.,!?()[]{}":;').lower() for word in content.split()]
        wordsCleaned = [w for w in wordsCleaned if w] # making sure to remove empty strings
        meta["top5Words"] = Counter(wordsCleaned).most_common(5)

        # -----------------
        # Identity metadata
        # -----------------
        meta["hashMD5"] = hashlib.md5(rawBytes).hexdigest()
        meta["hashSHA256"] = hashlib.sha256(rawBytes).hexdigest()

        return meta

class SettingsWidgets:

    class SettingsWidgetDefinition():
        """ Declaration class for the Settings screen widgets """

        def __init__(self):
            super().__init__()

            # General
            self.optionStartInEditMode = SwitchSettingCard(
                FICO.EDIT,
                "Start in Edit mode",
                f"You can choose whether {TITLE} should start directly in Edit mode.",
                cfg.mdStartInEditMode
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
                cfg.mdDisplayLineNumbers
            )

            self.optionShowSymbolsBar = SwitchSettingCard(
                segFont.fromName("EmojiTabMoreSymbols"),
                "Display the symbols bar",
                "You can choose whether the symbols bar can be displayed in the editor pane.",
                cfg.mdDisplaySymbolsBar
            )

            self.optionShowStatusBar = SwitchSettingCard(
                segFont.fromName("SIPRedock"),
                "Display the status bar",
                "You can choose whether the status bar can be displayed at the bottom of the editor pane.",
                cfg.mdDisplayStatusBar
            )

            self.optionEnableSyntaxHighlighting = SwitchSettingCard(
                segFont.fromName("Highlight"),
                "Enable syntax highlighting",
                "You can choose whether the editor can be syntax-highlighted based on Markdown syntax.",
                cfg.mdEnableSyntaxHighlighting
            )

            self.optionEnableWordWrap = SwitchSettingCard(
                segSVG.TEXT_WRAP,
                "Enable text wrapping",
                "You can choose whether the editor content can be wrapped to the next line.",
                cfg.mdEnableWordWrap
            )

            self.optionHighlightCurrentLine = SwitchSettingCard(
                segSVG.COLOR_LINE,
                "Highlight the current line",
                "You can choose whether the focused line in the editor can be highlighted.",
                cfg.mdHighlightCurrentLine
            )

            # Viewer
            self.optionOpenExternalLinks = SwitchSettingCard(
                segFont.fromName("Link"),
                "Access external links",
                f"Allow {TITLE} to access external links such as webpages, non-Markdown content"
                " and more via the viewer pane.",
                cfg.mdOpenExternalLinks
            )

    class EditorFontConfigGroup(ExpandGroupSettingCard):
        """ Class for Smart DownMarker font settings in the Editor section """
        configChanged = pyqtSignal()

        def __init__(self, parent = None):
            super().__init__(
                segFont.fromName("Font"), # type: ignore
                "Customize font settings",
                "Modify the editor's font family, size and weight properties",
                parent
            )
            self.familyList: list[str] = [
                "Ace Sans",
                "Agency FB",
                "Algerian",
                "Alte DIN 1451 Mittelschrift",
                "Arial",
                "Bahnschrift",
                "BankGothic",
                "Bauhaus 93",
                "Berlin Sans FB",
                "Calibri",
                "Capriola",
                "Cascadia Code",
                "Cascadia Mono",
                "Chalet",
                "Clock BoldSerif",
                "Clock RetroStripe",
                "Clock Stamp",
                "Clock2021",
                "Consolas",
                "Copperplate Gothic",
                "Dune Rise",
                "Figtree",
                "Forte",
                "Franklin Gothic",
                "Franklin Gothic Book",
                "Gill Sans MT",
                "Google Sans",
                "Harlow Solid",
                "Harrington",
                "JetBrains Mono",
                "JK Abode",
                "Masterpiece",
                "Mochiy Pop One",
                "Montserrat",
                "Montserrat Alternates",
                "NEON LED Light",
                "Nexa",
                "NFS font",
                "Nikkyou Sans",
                "Old English Text MT",
                "Pricedown",
                "Roboto",
                "Rockwell",
                "Samsung Sharp Sans",
                "Segoe UI",
                "Segoe UI Variable Display",
                "SignPainter-HouseScript",
                "SpecialAlphabets P04",
                "Stone",
                "Times New Roman",
                "Tourner",
                "Trebuchet MS",
                "Tw Cen MT",
                "Varino",
                "Velocity",
                "Verdana"
            ]
            self.isFamConfigInList: bool = cfg.get(cfg.mdFontFamily) in self.familyList
            if self.isFamConfigInList:
                for font in self.familyList:
                    if font == cfg.get(cfg.mdFontFamily):
                        self.currentFont = font
                        break
            else: self.currentFont = self.familyList[0]
            self.fontProp = f"""
                font-family: "{self.currentFont}";
                font-size: {cfg.get(cfg.mdFontSize)};
                font-weight: {cfg.get(cfg.mdFontWeight)};
            """

            # Font family
            self.familyCombo = ComboBox()
            for font in self.getSystemFonts(): self.familyCombo.addItem(font, segFont.fromName("Font"))
            self.familyCombo.setCurrentText(self.currentFont)
            self.familyCombo.currentTextChanged.connect(self.updatePreview)

            # Font size
            self.sizeSpin = SpinBox()
            self.sizeSpin.setValue(cfg.get(cfg.mdFontSize))
            self.sizeSpin.setMinimum(4)
            self.sizeSpin.valueChanged.connect(self.updatePreview)

            # Font weight
            self.weightSpin = SpinBox()
            self.weightSpin.setRange(100, 800)
            self.weightSpin.setValue(cfg.get(cfg.mdFontWeight))
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
            cfg.set(cfg.mdFontFamily, self.fontFamily)
            cfg.set(cfg.mdFontSize, self.fontSize)
            cfg.set(cfg.mdFontWeight, self.fontWeight)
            self.configChanged.emit()
        
        def getSystemFonts(self, asList: bool = True) -> list[str] | dict[str, str]:
            """ :EditorFontConfig: Get the system fonts as a list or dictionary

            Parameters
            ----------
            asList : bool, optional
                Whether to return the list of fonts as a list (*if `True`*) or a dictionary (*if `False`*), by default True

            Returns
            -------
            `list[str]` | `dict[str, str]`: The list of fonts or a dictionary of font families and their names
            """
            fonts = {}
            paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            ]

            for hive, subkey in paths:
                try:
                    with winreg.OpenKey(hive, subkey) as key:
                        for i in range(winreg.QueryInfoKey(key)[1]):
                            name, value, _ = winreg.EnumValue(key, i)
                            if name and value:
                                cleanName = name.split("(")[0].strip()
                                if cleanName: fonts[cleanName] = value
                except FileNotFoundError: continue
            
            if asList: return sorted(list(set(fonts.keys())))

            return dict(sorted(fonts.items()))

    class IndentationConfigGroup(ExpandGroupSettingCard):
        """ Class for Smart DownMarker indentation settings in the Editor section """
        configChanged = pyqtSignal()

        def __init__(self, parent = None):
            super().__init__(
                segFont.fromName("HorizontalTabKey"), # type: ignore
                "Customize indentation settings",
                "Modify the editor's indentation properties such as tab width and indentation guides visibility.",
                parent
            )

            # Tab width
            self.tabWidthSpin = SpinBox()
            self.tabWidthSpin.setValue(cfg.get(cfg.mdIndentWidth))
            self.tabWidthSpin.setRange(2, 8)
            self.tabWidthSpin.valueChanged.connect(self.updateConfig)

            # Indentation guides
            self.indentGuidesCheck = SwitchButton()
            self.indentGuidesCheck.setChecked(cfg.get(cfg.mdDisplayIndentGuides))
            self.indentGuidesCheck.checkedChanged.connect(self.updateConfig)

            # Auto-indent
            self.autoIndentCheck = SwitchButton()
            self.autoIndentCheck.setChecked(cfg.get(cfg.mdEnableAutoIndent))
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
            cfg.set(cfg.mdIndentWidth, self.tabWidthSpin.value())
            cfg.set(cfg.mdDisplayIndentGuides, self.indentGuidesCheck.isChecked())
            cfg.set(cfg.mdEnableAutoIndent, self.autoIndentCheck.isChecked())
            self.configChanged.emit()

    class EditorSelectionConfigGroup(ExpandGroupSettingCard):
        """ Class for Smart DownMarker selection settings in the Editor section """
        configChanged = pyqtSignal()

        def __init__(self, parent = None):
            super().__init__(
                FICO.PALETTE, # type: ignore
                "Customize selection settings",
                "Modify the editor's selection properties such as selection mode and custom color.",
                parent
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
            self.selectionColorModeCombo.setCurrentIndex(1 if cfg.get(cfg.mdSelectionColorMode) == "Custom" else 0)
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
            cfg.set(cfg.mdSelectionColorMode, "Custom" if self.selectionColorModeCombo.currentIndex() == 1 else "Accent")
            self.configChanged.emit()

    class CSSPropertiesConfigGroup(ExpandGroupSettingCard):
        """ Class for Smart DownMarker CSS properties in the Viewer section """
        configChanged = pyqtSignal()

        def __init__(self, parent):
            super().__init__(
                segSVG.STYLE_GUIDE, # type: ignore
                "Customize CSS properties",
                "Modify the viewer's rendering style properties "
                "(doesn't apply to webpages, stylized HTML documents or any CSS-incompatible non-static content)",
                parent
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
            self.sourceTypeCombo.setCurrentIndex(next(v for k, v in self.sourceIndexes.items() if cfg.get(cfg.mdCssSource) == k))
            self.sourceTypeCombo.currentIndexChanged.connect(self.updateConfig)

            # Storage source
            self.storagePath = QWidget()
            self.storagePath.setContentsMargins(0, 0, 0, 0)
            storagePathBox = QVBoxLayout(self.storagePath)
            storagePathBox.setContentsMargins(0, 0, 0, 0)
            storagePathBox.setSpacing(5)
            storagePathBox.addWidget(BodyLabel("Choose a file from your storage"))
            self.storagePathSublabel = CaptionLabel(
                f"Current source path: {cfg.get(cfg.mdCssSourcePath).replace('/', '\\')}{" (Inaccessible)" if not os.path.exists(cfg.get(cfg.mdCssSourcePath)) else ""}"
                if cfg.get(cfg.mdCssSourcePath) else "No path has been defined yet"
            )
            self.storagePathSublabel.setTextColor(QColor("gray"), QColor("gray"))
            self.storagePathSublabel.setVisible(bool(cfg.get(cfg.mdCssSourcePath)) and cfg.get(cfg.mdCssSourcePath) != "Default")
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
            cfg.set(cfg.mdCssSource, next(k for k, v in self.sourceIndexes.items() if v == self.sourceTypeCombo.currentIndex()))
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
            self.sourceTypeCombo.setCurrentIndex(next(v for k, v in self.sourceIndexes.items() if cfg.get(cfg.mdHomepageSource) == k))
            self.sourceTypeCombo.currentIndexChanged.connect(self.updateConfig)

            # Storage source
            self.storagePath = QWidget()
            self.storagePath.setContentsMargins(0, 0, 0, 0)
            storagePathBox = QVBoxLayout(self.storagePath)
            storagePathBox.setContentsMargins(0, 0, 0, 0)
            storagePathBox.setSpacing(5)
            storagePathBox.addWidget(BodyLabel("Choose a file from your storage"))
            self.storagePathSublabel = CaptionLabel(
                f"Current source path: {cfg.get(cfg.mdHomepageSourcePath).replace('/', '\\')}{" (Inaccessible)" if not os.path.exists(cfg.get(cfg.mdHomepageSourcePath)) else ""}"
                if cfg.get(cfg.mdHomepageSourcePath) else "No path has been defined yet"
            )
            self.storagePathSublabel.setTextColor(QColor("gray"), QColor("gray"))
            self.storagePathSublabel.setVisible(bool(cfg.get(cfg.mdHomepageSourcePath)) and cfg.get(cfg.mdHomepageSourcePath) != "Default")
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
            cfg.set(cfg.mdHomepageSource, next(k for k, v in self.sourceIndexes.items() if v == self.sourceTypeCombo.currentIndex()))
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
            self.cssEdit.setFontFamily(cfg.get(cfg.mdFontFamily))
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
            self.homeEdit.setFontFamily(cfg.get(cfg.mdFontFamily))
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

    class DragAndDropEventsConfigGroup(ExpandGroupSettingCard):
        """ Class for the homepage's drag-and-drop management in the Viewer section """
        configChanged = pyqtSignal()

        def __init__(self, parent):
            super().__init__(
                segFont.fromName("TouchPointer"), # type: ignore
                "Customize the homepage's drag-and-drop events",
                "Define the JavaScript functions which are called during different drag-and-drop events, "
                "according to their corresponding names from the current homepage content (case-sensitive).",
                parent
            )

            self.editFont = QFont(
                cfg.get(cfg.mdFontFamily),
                cfg.get(cfg.mdFontSize),
                cfg.get(cfg.mdFontWeight)
            )

            # Drag enter function
            self.dragEnterEdit = LineEdit()
            self.dragEnterEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
            self.dragEnterEdit.setText(cfg.get(cfg.mdDragEnterJSFunction))
            self.dragEnterEdit.setFixedWidth(300)
            self.dragEnterEdit.setFont(self.editFont)
            self.dragEnterEdit.textChanged.connect(lambda text: (
                self.dragEnterValidate.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default" and text != cfg.get(cfg.mdDragEnterJSFunction))
            ))
            self.dragEnterValidate = ToolButton(FICO.SAVE_AS)
            self.dragEnterValidate.setEnabled(
                cfg.get(cfg.mdHomepageSource) != "Default" and self.dragEnterEdit.text() != cfg.get(cfg.mdDragEnterJSFunction)
            )
            self.dragEnterValidate.clicked.connect(lambda checked: (
                cfg.set(cfg.mdDragEnterJSFunction, self.dragEnterEdit.text()),
                self.updateConfig()
            ))

            # Drag leave function
            self.dragLeaveEdit = LineEdit()
            self.dragLeaveEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
            self.dragLeaveEdit.setText(cfg.get(cfg.mdDragLeaveJSFunction))
            self.dragLeaveEdit.setFixedWidth(300)
            self.dragLeaveEdit.setFont(self.editFont)
            self.dragLeaveEdit.textChanged.connect(lambda text: (
                self.dragLeaveValidate.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default" and text != cfg.get(cfg.mdDragLeaveJSFunction))
            ))
            self.dragLeaveValidate = ToolButton(FICO.SAVE_AS)
            self.dragLeaveValidate.setEnabled(
                cfg.get(cfg.mdHomepageSource) != "Default" and self.dragLeaveEdit.text() != cfg.get(cfg.mdDragLeaveJSFunction)
            )
            self.dragLeaveValidate.clicked.connect(lambda checked: (
                cfg.set(cfg.mdDragLeaveJSFunction, self.dragLeaveEdit.text()),
                self.updateConfig()
            ))

            # Drop function
            self.dropEdit = LineEdit()
            self.dropEdit.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default")
            self.dropEdit.setText(cfg.get(cfg.mdDropJSFunction))
            self.dropEdit.setFixedWidth(300)
            self.dropEdit.setFont(self.editFont)
            self.dropEdit.textChanged.connect(lambda text: (
                self.dropValidate.setEnabled(cfg.get(cfg.mdHomepageSource) != "Default" and text != cfg.get(cfg.mdDropJSFunction))
            ))
            self.dropValidate = ToolButton(FICO.SAVE_AS)
            self.dropValidate.setEnabled(
                cfg.get(cfg.mdHomepageSource) != "Default" and self.dropEdit.text() != cfg.get(cfg.mdDropJSFunction)
            )
            self.dropValidate.clicked.connect(lambda checked: (
                cfg.set(cfg.mdDropJSFunction, self.dropEdit.text()),
                self.updateConfig()
            ))

            self.add(BodyLabel("When the drag is detected"), self.dragEnterEdit, self.dragEnterValidate)
            self.add(BodyLabel("When the drag is released/disappears"), self.dragLeaveEdit, self.dragLeaveValidate)
            self.add(BodyLabel("When the file is dropped"), self.dropEdit, self.dropValidate)
        
        def add(self, label, *widgets):
            """ :DragAndDropEventsConfigGroup: Add labels and config widgets to the group. """
            wid = QWidget()
            wid.setFixedHeight(60)
            widLayout = QHBoxLayout(wid)
            widLayout.setContentsMargins(48, 12, 48, 12)

            widLayout.addWidget(label)
            if widgets:
                widLayout.addStretch()
                for widget in widgets:
                    widLayout.addWidget(widget)
            
            self.addGroupWidget(wid)
        
        def updateConfig(self):
            cfg.set(cfg.mdDragEnterJSFunction, self.dragEnterEdit.text())
            cfg.set(cfg.mdDragLeaveJSFunction, self.dragLeaveEdit.text())
            cfg.set(cfg.mdDropJSFunction, self.dropEdit.text())
            self.configChanged.emit()

# Pour le chargement d'anciens onglets ouverts au démarrage, prévoir "MarkdownOpenTabs": list[dict[str, str]] dans markdown_history.dat
    # "index" : position dans la liste d'onglets
    # "name" : nom de chaque onglet
    # "path" : chemin de chaque onglet
    # "content" : contenu de l'éditeur de chaque onglet
    # "cursorPosition" : position du curseur dans l'éditeur de chaque onglet (si possible)
    # "history" : historique du Displayer de chaque onglet
    # "historyCurrent" : position dans l'historique avant sauvegarde & fermeture
    # Pour les états "canSave" de chaque onglet restauré :
        # Si chemin valide : comparer le contenu du fichier du chemin et celui de l'éditeur, "Vrai" si contenus non identiques
        # Si chemin invalide ou inexistant : "Vrai" si l'éditeur a du contenu
# (Possible - other) Rechercher s'il est possible de changer la page d'échec de chargement du Displayer en récupérant de la page de base le max d'éléments réutilisables possible
# Ajouter au DisplayNavigationBar une barre de statut pour liens survolés, niveau de zoom, nom et icône des liens ouverts
