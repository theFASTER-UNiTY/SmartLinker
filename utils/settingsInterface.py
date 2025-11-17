from utils.SmartUtils import *

myBrowsList = smart.loadBrowsers()

class SettingsInterface(QWidget):
    """ Main class for the "Settings" interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        mainSetLayout = QVBoxLayout(self)
        mainSetLayout.setContentsMargins(0, 20, 0, 0)
        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(40, 0, 0, 0)
        mainSetLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("Settings", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainTitleLine.addWidget(self.title)
        mainSetScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainSetLayout.addWidget(mainSetScroll)
        mainSetScroll.setWidgetResizable(True)
        mainSetScroll.setContentsMargins(0, 0, 40, 0)
        mainSetScroll.enableTransparentBackground()
        mainSetScrollContent = QWidget()
        mainSetScroll.setWidget(mainSetScrollContent)
        mainSetScroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainSetScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid #FFFFFF")
        mainSetScrollContent.setContentsMargins(40, 0, 40, 0)
        layout = QVBoxLayout(mainSetScrollContent)
        layout.setSpacing(5)
        self.widgetDef = SettingWidgetDefinition()
        self.mainFromListDlg = None
        self.mainRemoveDlg = None

        # General
        generalLabel = SubtitleLabel("General")
        generalLabel.setContentsMargins(0, 0, 0, 0)
        generalLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(generalLabel)
        layout.addWidget(self.widgetDef.optionMainBrowserCard)
        layout.addWidget(self.widgetDef.optionMainRefresh)
        self.widgetDef.optionMainRefresh.button.clicked.connect(lambda: self.cardRefresh(parent))

        # Personalization - Logo blue: #28ABFA, Logo purple: #793BCC
        personalizeLabel = SubtitleLabel("Look & Feel")
        personalizeLabel.setContentsMargins(0, 40, 0, 0)
        personalizeLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(personalizeLabel)
        layout.addWidget(self.widgetDef.optionTheme)
        self.optionAccentColor = ThemeColorSelectGroup()
        self.optionCustomAccentColorDlg = None
        self.optionAccentColor.selectButton.clicked.connect(lambda: self.openColorDialog(parent))
        layout.addWidget(self.optionAccentColor)
        layout.addWidget(self.widgetDef.optionMicaEffect)
        layout.addWidget(self.widgetDef.optionShowCommandBar)
        self.optionShowSplash = FlagsSettingGroup(self)
        layout.addWidget(self.optionShowSplash)

        # Sound
        soundLabel = SubtitleLabel("Sound")
        soundLabel.setContentsMargins(0, 40, 0, 0)
        soundLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(soundLabel)
        layout.addWidget(self.widgetDef.optionSoundEffects)
        self.widgetDef.optionSoundEffects.switchButton.checkedChanged.connect(lambda checked: self.toggleSoundsAvailability(checked))
        self.optionSoundConfig = SoundFxConfigGroup(self)
        layout.addWidget(self.optionSoundConfig)

        # Smart Selector
        selectorLabel = SubtitleLabel("Smart Selector")
        selectorLabel.setContentsMargins(0, 40, 0, 0)
        selectorLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(selectorLabel)
        layout.addWidget(self.widgetDef.optionCloseOnSelect)

        # Advanced
        advancedLabel = SubtitleLabel("Advanced")
        advancedLabel.setContentsMargins(0, 40, 0, 0)
        advancedLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(advancedLabel)
        self.advancedTempClean = PushSettingCard(
            "Clean",
            FICO.DELETE,
            f"Clean temporary files",
            f"Some temporary files have been left over by {SmartLinkerName}. Click here to clean them up."
        )
        layout.addWidget(self.advancedTempClean)
        self.advancedRestart = PushSettingCard(
            "Restart",
            SegoeFontIcon.fromName("reboot"),
            f"Restart {SmartLinkerName}",
            "If you need for some reason to restart the software, this is the easiest way to proceed."
        )
        layout.addWidget(self.advancedRestart)
        self.advancedStop = PushSettingCard(
            "Stop process",
            FICO.POWER_BUTTON,
            f"Stop {SmartLinkerName}",
            "If you need for some reason to stop the software process, this is the safest way to proceed."
        )
        layout.addWidget(self.advancedStop)
        if os.path.exists(smart.resourcePath(".temp")) and os.listdir(smart.resourcePath(".temp")):
            self.advancedTempClean.setEnabled(True)
            self.advancedTempClean.setVisible(True)
            self.advancedTempClean.button.clicked.connect(lambda: self.cleanTempFiles(parent))
        else:
            self.advancedTempClean.setEnabled(False)
            self.advancedTempClean.setVisible(False)
        layout.addStretch(1)
        
        self.updateSnack = QWidget()
        self.updateSnack.setObjectName("SSnackBase")
        self.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smart.convertToRGB(themeColor().name())}, 0.25)}}")
        mainSetLayout.addWidget(self.updateSnack)
        self.updateSnack.setVisible(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners)))
        self.updateSnack.setEnabled(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners)))
        self.updateSnackLayout = QHBoxLayout(self.updateSnack)
        self.updateSnackLayout.setContentsMargins(20, 10, 20, 10)
        self.updateSnackIcon = IconWidget(FICO.IOT)
        self.updateSnackIcon.setFixedSize(32, 32)
        self.updateSnackLayout.setSpacing(20)
        self.updateSnackLayout.addWidget(self.updateSnackIcon)
        self.updateSnackLabel = StrongBodyLabel("A new update is available for download!")
        self.updateSnackLayout.addWidget(self.updateSnackLabel)
        self.updateSnackLayout.addStretch(1)
        self.updateSnackButton = PrimaryPushButton(FICO.DOWNLOAD, "Download now")
        self.updateSnackLayout.addWidget(self.updateSnackButton)

    def cardManualSelect(self, parent):
        """ :SettingsInterface: Open a dialog to select main browser from your storage """
        self.cardManualPath = smart.browseFileDialog(parent, "Select your main browser from storage", "", "Executables (*.exe)")
        if self.cardManualPath:
            cfg.set(cfg.mainBrowser, "")
            cfg.set(cfg.mainBrowserPath, self.cardManualPath)
            cfg.set(cfg.mainBrowserIsManual, True)
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(True)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(smart.getFileIcon(self.cardManualPath))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Your main browser has been set manually")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {os.path.basename(self.cardManualPath)} if no browser is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Reselect from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smart.successNotify("Manual selection complete!", f"Your main browser has been successfully set to '{os.path.basename(self.cardManualPath)}'.", parent)
            print(f"{Fore.GREEN}Your main browser has been successfully set from storage at path: '{self.cardManualPath}'{Style.RESET_ALL}")
            smart.managerLog(f"SUCCESS: Main browser set from storage at path: '{self.cardManualPath}'")

    def cardSetFromList(self, parent):
        """ :SettingsInterface: Open a dialog to select main browser from your SmartList """
        if not self.mainFromListDlg:
            self.mainFromListDlg = SelectFromListDialog(smart.loadBrowsers(), parent)
        if self.mainFromListDlg.exec():
            for browser in myBrowsList["MyBrowsers"]:
                if browser["name"] == self.mainFromListDlg.browsCombo.currentText():
                    cfg.set(cfg.mainBrowser, self.mainFromListDlg.browsCombo.currentText())
                    cfg.set(cfg.mainBrowserPath, browser["path"])
                    cfg.set(cfg.mainBrowserIsManual, False)
                    break
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(True)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(smart.getFileIcon(cfg.get(cfg.mainBrowserPath)))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Your main browser has been set from your SmartList")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {self.mainFromListDlg.browsCombo.currentText()} if no browser is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Reselect from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smart.successNotify("SmartList selection complete!", f"{self.mainFromListDlg.browsCombo.currentText()} has been successfully set as your main browser.", parent)
            print(f"{Fore.GREEN}Your main browser has been successfully set from your SmartList: {self.mainFromListDlg.browsCombo.currentText()}{Style.RESET_ALL}")
            smart.managerLog(f"SUCCESS: Main browser set from SmartList: {self.mainFromListDlg.browsCombo.currentText()}")

    def cardRefresh(self, parent):
        myBrowsList = smart.loadBrowsers()
        if cfg.get(cfg.mainBrowserPath):
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(smart.getFileIcon(cfg.get(cfg.mainBrowserPath)))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText(f"Your main browser has been set {"from your SmartList" if not cfg.get(cfg.mainBrowserIsManual) else "manually"}")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {cfg.get(cfg.mainBrowser) if not cfg.get(cfg.mainBrowserIsManual) else os.path.basename(cfg.get(cfg.mainBrowserPath))} if no browser is running.")
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(True)
        else:
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath(f"resources/images/icons/icon_outline{"" if theme() == Theme.DARK else "_black"}.ico")))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Configure your main browser")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText("You can either set a browser from your storage or SmartList as your main browser if no one is running.")
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(False)
        self.widgetDef.optionMainBrowserCard.fromListButton.setEnabled(bool(myBrowsList["MyBrowsers"]))
        smart.infoNotify("Main browser card refreshed!", "Your main browser card has been successfully refreshed!", parent)

    def cardRemove(self, parent):
        """ :SettingsInterface: Open a confirmation dialog to remove the main browser """
        if not self.mainRemoveDlg:
            self.mainRemoveDlg = MessageBox(
                "Confirm main browser removal",
                "Your main browser will be reverted to 'None', " \
                "and you will always have to select a browser when forwarding a link, running or not.\n\n" \
                "Do you still want to proceed?",
                parent
            )
            self.mainRemoveDlg.yesButton.setText("Remove")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if self.mainRemoveDlg.exec():
            cfg.set(cfg.mainBrowser, "")
            cfg.set(cfg.mainBrowserPath, "")
            cfg.set(cfg.mainBrowserIsManual, False)
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(False)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(QIcon(smart.resourcePath(f"resources/images/icons/icon_outline{"" if theme() == Theme.DARK else "_black"}.ico")))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Configure your main browser")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText("You can either set a browser from your storage or SmartList as your main browser if no one is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smart.successNotify("Removal complete!", "Your main browser configuration has been reverted to 'None'.", parent)
            print(f"{Fore.GREEN}Your main browser configuration has been successfully reverted to 'None'{Style.RESET_ALL}")
            smart.managerLog("SUCCESS: Main browser reverted to 'None'")

    def openColorDialog(self, parent):
        """ :SettingsInterface: Open a dialog to change the accent color of SmartLinker. """
        if not self.optionCustomAccentColorDlg:
            self.optionCustomAccentColorDlg = ColorDialog(
                themeColor(),
                "Choose your preferred color",
                parent,
                enableAlpha=False
            )
            self.optionCustomAccentColorDlg.editLabel.setText("Edit HEX color")
        if self.optionCustomAccentColorDlg.exec():
            setThemeColor(self.optionCustomAccentColorDlg.color, save=True)           
            cfg.set(cfg.accentColor, self.optionCustomAccentColorDlg.color.name())

    def toggleSoundsAvailability(self, checked):
        """ :SettingsInterface: Adjust the sounds options according to the sound effect toggle and individual sound paths """
        self.optionSoundConfig.startupPlayBtn.setEnabled(checked and bool(cfg.get(cfg.startupSFXPath)))
        self.optionSoundConfig.startupPickBtn.setEnabled(checked)
        self.optionSoundConfig.startupRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.startupSFXPath)))
        self.optionSoundConfig.infoPlayBtn.setEnabled(checked and bool(cfg.get(cfg.infoSFXPath)))
        self.optionSoundConfig.infoPickBtn.setEnabled(checked)
        self.optionSoundConfig.infoRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.infoSFXPath)))
        self.optionSoundConfig.successPlayBtn.setEnabled(checked and bool(cfg.get(cfg.successSFXPath)))
        self.optionSoundConfig.successPickBtn.setEnabled(checked)
        self.optionSoundConfig.successRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.successSFXPath)))
        self.optionSoundConfig.warningPlayBtn.setEnabled(checked and bool(cfg.get(cfg.warningSFXPath)))
        self.optionSoundConfig.warningPickBtn.setEnabled(checked)
        self.optionSoundConfig.warningRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.warningSFXPath)))
        self.optionSoundConfig.errorPlayBtn.setEnabled(checked and bool(cfg.get(cfg.errorSFXPath)))
        self.optionSoundConfig.errorPickBtn.setEnabled(checked)
        self.optionSoundConfig.errorRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.errorSFXPath)))
        self.optionSoundConfig.questionPlayBtn.setEnabled(checked and bool(cfg.get(cfg.questionSFXPath)))
        self.optionSoundConfig.questionPickBtn.setEnabled(checked)
        self.optionSoundConfig.questionRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.questionSFXPath)))
        self.optionSoundConfig.selectorPlayBtn.setEnabled(checked and bool(cfg.get(cfg.selectorSFXPath)))
        self.optionSoundConfig.selectorPickBtn.setEnabled(checked)
        self.optionSoundConfig.selectorRemoveBtn.setEnabled(checked and bool(cfg.get(cfg.selectorSFXPath)))

    def cleanTempFiles(self, parent):
        """ :SettingsInterface: Clean temporary files left over by SmartLinker """
        try:
            shutil.rmtree(smart.resourcePath(".temp"))
            self.advancedTempClean.setEnabled(False)
            self.advancedTempClean.setVisible(False)
            print(f"{Fore.GREEN}Temporary files have been successfully cleaned!{Style.RESET_ALL}")
            smart.managerLog("SUCCESS: Temporary files successfully cleaned!")
            smart.successNotify("Clean complete!", "All temporary files have been successfully removed.", parent)
        except Exception as e:
            print(f"{Fore.RED}Error cleaning temporary files: {e}{Style.RESET_ALL}")
            smart.managerLog(f"ERROR: Failed to clean temporary files: {e}")
            smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to clean temporary files: {e}", parent)

class SettingWidgetDefinition():
    """ Declaration class for some of SettingsInterface widgets """

    def __init__(self, parent=None):
        super().__init__()
        if cfg.get(cfg.mainBrowserPath):
            if cfg.get(cfg.mainBrowserIsManual):
                self.manualContent = f"{SmartLinkerName} will redirect your web requests to {os.path.basename(cfg.get(cfg.mainBrowserPath))} if no browser is running."
                self.manualButtonText = "Reselect from storage"
            else:
                self.manualContent = f"Your current main browser has been set from your SmartList ({cfg.get(cfg.mainBrowser)})."
                self.manualButtonText = "Select from storage"
        else:
            self.manualContent = f"{SmartLinkerName} will redirect your web requests to your main browser if no browser is running."
            self.manualButtonText = "Select from storage"

        # General
        self.optionMainBrowserCard = MainBrowsersCard(
            smart.getFileIcon(cfg.get(cfg.mainBrowserPath)) if cfg.get(cfg.mainBrowserPath) else \
                QIcon(smart.resourcePath(f"resources/images/icons/icon_outline{"" if theme() == Theme.DARK else "_black"}.ico")),
            f"Your main browser has been set {"manually" if cfg.get(cfg.mainBrowserIsManual) else "from your SmartList"}" if cfg.get(cfg.mainBrowserPath) else \
            "Configure your main browser",
            f"{SmartLinkerName} will redirect your web requests to {os.path.basename(cfg.get(cfg.mainBrowserPath)) if cfg.get(cfg.mainBrowserIsManual) else cfg.get(cfg.mainBrowser)} if no browser is running." if cfg.get(cfg.mainBrowserPath) else \
            "You can either set a browser from your storage or SmartList as your main browser if no one is running."
        )
        self.optionMainRefresh = PushSettingCard(
            "Refresh",
            SegoeFontIcon.fromName("refresh"),
            "Refresh main browser card",
            "In case your main browser card above is not synchronized with some changes, you can make it unified again with this option."
        )

        # Personalization
        self.optionTheme = OptionsSettingCard(
            cfg.appTheme,
            FICO.BRUSH,
            "Set the application theme",
            f"Change the main theme of {SmartLinkerName}",
            texts=["Light", "Dark", "Use system setting"]
        )
        self.optionMicaEffect = SwitchSettingCard(
            FICO.TRANSPARENT,
            "Enable Mica effect",
            "You can toggle 'Mica', one of Windows 11's Fluent Design visual effects.",
            cfg.micaEffect
        )
        self.optionShowCommandBar = SwitchSettingCard(
            FICO.MENU,
            "Display the action bar",
            "If enabled, the action bar is displayed below the SmartList instead of the standard tiles.",
            cfg.showCommandBar
        )

        # Sound
        self.optionSoundEffects = SwitchSettingCard(
            FICO.MUSIC,
            "Enable sound effects",
            f"You have the possibility to enhance your auditive experience with {SmartLinkerName}, just by enabling this feature.",
            cfg.enableSoundEffects
        )

        # Smart Selector
        self.optionCloseOnSelect = SwitchSettingCard(
            FICO.EMBED,
            "Close window on browser selection",
            "If enabled, the Smart Selector window will close once a browser is selected for the forwarded link to be loaded.",
            cfg.closeOnBrowserSelect
        )

class ThemeColorSelectGroup(ExpandGroupSettingCard):
    """ Class for SmartLinker's accent mode and color in the Look & Feel section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.PALETTE,
            "Customize the theme color",
            f"Change the accent color of {SmartLinkerName}"
        )

        # Accent mode combo
        self.accentLabel = BodyLabel("Choose an accent mode")
        self.accentCombo = ComboBox()
        self.accentCombo.addItems(["System accent color", "Custom accent color"])
        self.accentCombo.setFixedWidth(180)
        self.accentCombo.setCurrentIndex(1 if cfg.get(cfg.accentMode) == "Custom" else 0)
        self.accentCombo.currentTextChanged.connect(lambda text: self.changeAccentMode(text))

        # Custom color button
        self.selectButton = PushButton("Pick my color")
        self.selectButton.setEnabled(bool(self.accentCombo.currentText() == "Custom accent color"))
        self.selectLabel = BodyLabel("Select your custom accent color")
        self.selectButton.setFixedWidth(150)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)


        self.add_group(self.accentLabel, self.accentCombo)
        self.add_group(self.selectLabel, self.selectButton)

    def add_group(self, label, widget):
        """ :ThemeColorSelect: Add accent mode and color elements to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        widLayout.addStretch(1)
        widLayout.addWidget(widget)

        self.addGroupWidget(wid)

    def changeAccentMode(self, text):
        """ :ThemeColorSelect: Change the current accent mode and color according to the selection. """
        if text == "Custom accent color":
            cfg.set(cfg.accentMode, "Custom")
            setThemeColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentColor) else QColor(cfg.get(cfg.qAccentColor)), save=True)
        else:
            cfg.set(cfg.accentMode, "System")
            setThemeColor(getSystemAccentColor(), save=True)

class FlagsSettingGroup(ExpandGroupSettingCard):
    """ Class for SmartLinker's appearance flags configuration in the Look & Feel section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.FLAG,
            "Customize appearance flags",
            f"Customize the {SmartLinkerName} experience by modifying visual features as you wish. (* Restart required)"
        )

        # First group - Splash toggle
        self.splashSwitchLabel = BodyLabel("Enable splash screen display")
        self.splashSwitchButton = SwitchButton(parent=self, indicatorPos=IndicatorPosition.RIGHT)
        self.splashSwitchButton.setChecked(cfg.get(cfg.showSplash))
        self.splashSwitchButton.checkedChanged.connect(lambda checked: (
            self.splashDurationSpin.setEnabled(checked),
            cfg.set(cfg.showSplash, checked)
        ))

        # Second group - Splash duration
        self.splashDurationLabel = BodyLabel("Set display duration (in milliseconds)")
        self.splashDurationSpin = SpinBox()
        self.splashDurationSpin.setRange(0, 10000)
        self.splashDurationSpin.setValue(cfg.get(cfg.splashDuration))
        self.splashDurationSpin.valueChanged.connect(lambda value: (
            cfg.set(cfg.splashDuration, value)
        ))
        self.splashDurationSpin.setEnabled(cfg.get(cfg.showSplash))

        # Third group - Update banners
        self.updateBannerSwitchLabel = BodyLabel("Enable update banners display (About screen excluded)*")
        self.updateBannerSwitchButton = SwitchButton(parent=self, indicatorPos=IndicatorPosition.RIGHT)
        self.updateBannerSwitchButton.setChecked(cfg.get(cfg.showUpdateBanners))
        self.updateBannerSwitchButton.checkedChanged.connect(lambda checked: (
            cfg.set(cfg.showUpdateBanners, checked),
            smart.infoNotify("Restart required", f"You need to relaunch {SmartLinkerName} for the changes to take effect.", parent)
        ))

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add each group to the setting card
        self.add(self.splashSwitchLabel, self.splashSwitchButton)
        self.add(self.splashDurationLabel, self.splashDurationSpin)
        self.add(self.updateBannerSwitchLabel, self.updateBannerSwitchButton)

    def add(self, label, widget):
        """ :FlagsSetting: Add appearance flag elements to the group. """
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)

class MainBrowsersCard(CardWidget):
    """ Class for the the main browser configuration card """

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = SubtitleLabel(title, self)
        self.contentLabel = BodyLabel(content, self)
        self.fromStorageButton = ToolButton(FICO.FOLDER, self)
        self.fromListButton = ToolButton(smart.resourcePath("resources/images/icons/icon-0.ico"), self)
        self.removeMainButton = ToolButton(FICO.REMOVE_FROM, self)
        self.fromStorageToolTip = ToolTipFilter(self.fromStorageButton)
        self.fromListToolTip = ToolTipFilter(self.fromListButton)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(96)
        self.setClickEnabled(False)
        self.iconWidget.setFixedSize(56, 56)
        self.contentLabel.setTextColor(QColor("#606060"), QColor("#d2d2d2"))
        self.fromStorageButton.setToolTip("Reselect from your storage" if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual) else "Select from your storage")
        self.fromStorageButton.installEventFilter(self.fromStorageToolTip)
        self.fromListButton.setToolTip("Reselect from your SmartList" if cfg.get(cfg.mainBrowserPath) and not cfg.get(cfg.mainBrowserIsManual) else "Select from your SmartList")
        self.fromListButton.installEventFilter(self.fromListToolTip)
        self.fromListButton.setEnabled(bool(myBrowsList["MyBrowsers"]))
        self.removeMainButton.setToolTip("Remove main browser")
        self.removeMainButton.installEventFilter(ToolTipFilter(self.removeMainButton))
        self.removeMainButton.setEnabled(bool(cfg.get(cfg.mainBrowserPath)))

        self.hBoxLayout.setContentsMargins(20, 11, 20, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.fromStorageButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addWidget(self.fromListButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addWidget(self.removeMainButton, 0, Qt.AlignmentFlag.AlignRight)

class SelectFromListDialog(MessageBoxBase):
    """ Class for the main browser selection from SmartList dialog """

    def __init__(self, browsers, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Select from your SmartList', self)
        self.icon = IconWidget(FICO.GLOBE)
        self.browsCombo = ComboBox()
        self.infoLabel = CaptionLabel()

        self.icon.setFixedSize(64, 64)
        self.browsCombo.setPlaceholderText("Select a SmartList browser")
        myBrowsList = browsers
        for browser in myBrowsList["MyBrowsers"]:
            self.browsCombo.addItem(browser["name"], smart.getFileIcon(browser["path"]))
        if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
            self.browsCombo.addItem(os.path.basename(cfg.get(cfg.mainBrowserPath)), smart.getFileIcon(cfg.get(cfg.mainBrowserPath)))

        for browser in myBrowsList["MyBrowsers"]:
            if browser["name"] == self.browsCombo.currentText():
                self.icon.setIcon(smart.getFileIcon(browser["path"]))
                break
        self.yesButton.setEnabled(self.browsCombo.count() > 0)
        self.yesButton.setVisible(self.browsCombo.count() > 0)
        self.yesButton.setText("Set as main browser")
        if self.browsCombo.count() < 1:
            self.infoLabel.setText("Your SmartList is currently empty...")
            self.infoLabel.setTextColor(QColor("red"), QColor("#F44336"))
        else:
            self.infoLabel.setText(f"{self.browsCombo.currentText()} will be set as your main browser.")
            self.infoLabel.setTextColor(QColor("blue"), QColor("#2196F3"))

        self.browsCombo.currentTextChanged.connect(lambda text: self.comboTextChangeListener(text))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.browsCombo)
        self.viewLayout.addWidget(self.infoLabel, 0, Qt.AlignmentFlag.AlignCenter)

        self.widget.setMinimumWidth(350)

    def comboTextChangeListener(self, text: str):
        """ :SelectFromList: Make actions whenever the current text of the combo is changed """
        self.infoLabel.setText(f"{text} will be set as your main browser.")
        for browser in myBrowsList["MyBrowsers"]:
            if browser["name"] == text:
                self.icon.setIcon(smart.getFileIcon(browser["path"]))
                break

    def validate(self):
        if not self.browsCombo.currentText() or self.browsCombo.count == 0: return False
        return True

class SoundFxConfigGroup(ExpandGroupSettingCard):
    """ Class for SmartLinker's sound effects configuration in the Sound section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.MIX_VOLUMES,
            "Configure sound effects",
            "You can customize the available sounds all the way you want, right here.",
            parent
        )
        self.soundSample = None
        self.soundRemoveDlg = None
        
        # First group - Startup SFX
        self.startupLabel = BodyLabel(f"At {SmartLinkerName} startup")
        self.startupPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.startupPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.startupSFXPath)))
        self.startupPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.startupSFXPath), "startup"))
        self.startupPickBtn = ToolButton(FICO.FOLDER)
        self.startupPickBtn.setToolTip("Select a custom sound")
        self.startupPickBtn.installEventFilter(ToolTipFilter(self.startupPickBtn))
        self.startupPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.startupPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.startupSFXPath, f"Select {SmartLinkerName} startup SFX", "The startup sound has been successfully modified!", parent),
            self.startupPlayBtn.setEnabled(bool(cfg.get(cfg.startupSFXPath))),
            self.startupRemoveBtn.setEnabled(bool(cfg.get(cfg.startupSFXPath)))
        ))
        self.startupRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.startupRemoveBtn.setToolTip("Remove sound")
        self.startupRemoveBtn.installEventFilter(ToolTipFilter(self.startupRemoveBtn))
        self.startupRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.startupSFXPath)))
        self.startupRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("startup", cfg.startupSFXPath, parent),
            self.startupPlayBtn.setEnabled(False),
            self.startupRemoveBtn.setEnabled(False)
        ))

        # Second group - Success notification
        self.successLabel = BodyLabel("Notification - success")
        self.successPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.successPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath)))
        self.successPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.successSFXPath), "success"))
        self.successPickBtn = ToolButton(FICO.FOLDER)
        self.successPickBtn.setToolTip("Select a custom sound")
        self.successPickBtn.installEventFilter(ToolTipFilter(self.successPickBtn))
        self.successPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.successPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.successSFXPath, f"Select {SmartLinkerName} success notification SFX", "The success notification sound has been successfully modified!", parent),
            self.successPlayBtn.setEnabled(bool(cfg.get(cfg.successSFXPath))),
            self.successRemoveBtn.setEnabled(bool(cfg.get(cfg.successSFXPath)))
        ))
        self.successRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.successRemoveBtn.setToolTip("Remove sound")
        self.successRemoveBtn.installEventFilter(ToolTipFilter(self.successRemoveBtn))
        self.successRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.successSFXPath)))
        self.successRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("success notification", cfg.successSFXPath, parent),
            self.successPlayBtn.setEnabled(False),
            self.successRemoveBtn.setEnabled(False)
        ))

        # Third group - Information notification
        self.infoLabel = BodyLabel(f"Notification - information")
        self.infoPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.infoPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.infoSFXPath)))
        self.infoPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.infoSFXPath), "information"))
        self.infoPickBtn = ToolButton(FICO.FOLDER)
        self.infoPickBtn.setToolTip("Select a custom sound")
        self.infoPickBtn.installEventFilter(ToolTipFilter(self.infoPickBtn))
        self.infoPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.infoPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.infoSFXPath, f"Select {SmartLinkerName} information notification SFX", "The information notification sound has been successfully modified!", parent),
            self.infoPlayBtn.setEnabled(bool(cfg.get(cfg.infoSFXPath))),
            self.infoRemoveBtn.setEnabled(bool(cfg.get(cfg.infoSFXPath)))
        ))
        self.infoRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.infoRemoveBtn.setToolTip("Remove sound")
        self.infoRemoveBtn.installEventFilter(ToolTipFilter(self.infoRemoveBtn))
        self.infoRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.infoSFXPath)))
        self.infoRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("information notification", cfg.infoSFXPath, parent),
            self.infoPlayBtn.setEnabled(False),
            self.infoRemoveBtn.setEnabled(False)
        ))

        # Fourth group - Warning notification
        self.warningLabel = BodyLabel("Notification - warning")
        self.warningPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.warningPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.warningSFXPath)))
        self.warningPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.warningSFXPath), "warning"))
        self.warningPickBtn = ToolButton(FICO.FOLDER)
        self.warningPickBtn.setToolTip("Select a custom sound")
        self.warningPickBtn.installEventFilter(ToolTipFilter(self.warningPickBtn))
        self.warningPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.warningPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.warningSFXPath, f"Select {SmartLinkerName} warning notification SFX", "The warning notification sound has been successfully modified!", parent),
            self.warningPlayBtn.setEnabled(bool(cfg.get(cfg.warningSFXPath))),
            self.warningRemoveBtn.setEnabled(bool(cfg.get(cfg.warningSFXPath)))
        ))
        self.warningRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.warningRemoveBtn.setToolTip("Remove sound")
        self.warningRemoveBtn.installEventFilter(ToolTipFilter(self.warningRemoveBtn))
        self.warningRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.warningSFXPath)))
        self.warningRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("warning notification", cfg.warningSFXPath, parent),
            self.warningPlayBtn.setEnabled(False),
            self.warningRemoveBtn.setEnabled(False)
        ))

        # Fifth group - Error notification
        self.errorLabel = BodyLabel(f"Notification - error")
        self.errorPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.errorPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)))
        self.errorPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.errorSFXPath), "error"))
        self.errorPickBtn = ToolButton(FICO.FOLDER)
        self.errorPickBtn.setToolTip("Select a custom sound")
        self.errorPickBtn.installEventFilter(ToolTipFilter(self.errorPickBtn))
        self.errorPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.errorPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.errorSFXPath, f"Select {SmartLinkerName} error notification SFX", "The error notification sound has been successfully modified!", parent),
            self.errorPlayBtn.setEnabled(bool(cfg.get(cfg.errorSFXPath))),
            self.errorRemoveBtn.setEnabled(bool(cfg.get(cfg.errorSFXPath)))
        ))
        self.errorRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.errorRemoveBtn.setToolTip("Remove sound")
        self.errorRemoveBtn.installEventFilter(ToolTipFilter(self.errorRemoveBtn))
        self.errorRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.errorSFXPath)))
        self.errorRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("error notification", cfg.errorSFXPath, parent),
            self.errorPlayBtn.setEnabled(False),
            self.errorRemoveBtn.setEnabled(False)
        ))

        # Sixth group - Confirmation dialog
        self.questionLabel = BodyLabel("At confirmation dialog popup")
        self.questionPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.questionPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)))
        self.questionPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog"))
        self.questionPickBtn = ToolButton(FICO.FOLDER)
        self.questionPickBtn.setToolTip("Select a custom sound")
        self.questionPickBtn.installEventFilter(ToolTipFilter(self.questionPickBtn))
        self.questionPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.questionPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.questionSFXPath, f"Select {SmartLinkerName} confirmation dialog notification SFX", "The confirmation dialog popup sound has been successfully modified!", parent),
            self.questionPlayBtn.setEnabled(bool(cfg.get(cfg.questionSFXPath))),
            self.questionRemoveBtn.setEnabled(bool(cfg.get(cfg.questionSFXPath)))
        ))
        self.questionRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.questionRemoveBtn.setToolTip("Remove sound")
        self.questionRemoveBtn.installEventFilter(ToolTipFilter(self.questionRemoveBtn))
        self.questionRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)))
        self.questionRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("confirmation dialog", cfg.questionSFXPath, parent),
            self.questionPlayBtn.setEnabled(False),
            self.questionRemoveBtn.setEnabled(False)
        ))

        # Seventh group - Smart Selector window
        self.selectorLabel = BodyLabel("At Smart Selector launch")
        self.selectorPlayBtn = PushButton(FICO.PLAY, "Play sound")
        self.selectorPlayBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.selectorSFXPath)))
        self.selectorPlayBtn.clicked.connect(lambda: smart.playSound(soundStreamer, cfg.get(cfg.selectorSFXPath), "Smart Selector launch"))
        self.selectorPickBtn = ToolButton(FICO.FOLDER)
        self.selectorPickBtn.setToolTip("Select a custom sound")
        self.selectorPickBtn.installEventFilter(ToolTipFilter(self.selectorPickBtn))
        self.selectorPickBtn.setEnabled(cfg.get(cfg.enableSoundEffects))
        self.selectorPickBtn.clicked.connect(lambda: (
            self.soundConfigure(cfg.selectorSFXPath, f"Select Smart Selector launch SFX", "The Smart Selector launch sound has been successfully modified!", parent),
            self.selectorPlayBtn.setEnabled(bool(cfg.get(cfg.selectorSFXPath))),
            self.selectorRemoveBtn.setEnabled(bool(cfg.get(cfg.selectorSFXPath)))
        ))
        self.selectorRemoveBtn = ToolButton(FICO.REMOVE_FROM)
        self.selectorRemoveBtn.setToolTip("Remove sound")
        self.selectorRemoveBtn.installEventFilter(ToolTipFilter(self.selectorRemoveBtn))
        self.selectorRemoveBtn.setEnabled(bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.selectorSFXPath)))
        self.selectorRemoveBtn.clicked.connect(lambda: (
            self.soundRemove("Smart Selector launch", cfg.selectorSFXPath, parent),
            self.selectorPlayBtn.setEnabled(False),
            self.selectorRemoveBtn.setEnabled(False)
        ))

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add(self.startupLabel, self.startupPlayBtn, self.startupPickBtn, self.startupRemoveBtn)
        self.add(self.infoLabel, self.infoPlayBtn, self.infoPickBtn, self.infoRemoveBtn)
        self.add(self.successLabel, self.successPlayBtn, self.successPickBtn, self.successRemoveBtn)
        self.add(self.warningLabel, self.warningPlayBtn, self.warningPickBtn, self.warningRemoveBtn)
        self.add(self.errorLabel, self.errorPlayBtn, self.errorPickBtn, self.errorRemoveBtn)
        self.add(self.questionLabel, self.questionPlayBtn, self.questionPickBtn, self.questionRemoveBtn)
        self.add(self.selectorLabel, self.selectorPlayBtn, self.selectorPickBtn, self.selectorRemoveBtn)

    def add(self, label, play, pick, remove):
        """ :SoundFXConfig: Add sound management-related elements to the group """
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(play)
        layout.addWidget(pick)
        layout.addWidget(remove)

        self.addGroupWidget(w)

    def soundConfigure(self, config, dialogTitle, successMsg, parent):
        """ :SoundFXConfig: Configure a sound effect and save it into the configuration file """
        cfg.set(config, smart.browseFileDialog(parent, dialogTitle, smart.resourcePath("resources/sounds"), "Audio files (*.mp3; *.ogg; *.wav)"))
        if cfg.get(config): smart.successNotify("Sound set!", successMsg, parent)

    def soundRemove(self, soundType: str, config, parent):
        """ :SoundFXConfig: Open a confirmation dialog to remove a configured sound effect """
        if not self.soundRemoveDlg:
            self.soundRemoveDlg = MessageBox(
                "Remove sound effect",
                f"If you proceed, the {soundType} sound effect will be removed and you will have to set another sound later.",
                parent
            )
            self.soundRemoveDlg.yesButton.setText("Remove")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if self.soundRemoveDlg.exec():
            cfg.set(config, "")
            print(f"{Fore.GREEN}The {soundType} sound effect has been successfully removed!{Style.RESET_ALL}")
            smart.managerLog(f"SUCCESS: The {soundType} sound effect has been successfully removed!")
            smart.successNotify("Removal complete!", f"The {soundType} sound has been successfully removed!", parent)
