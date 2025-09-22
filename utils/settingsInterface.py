__version__ = "1.0.0"
__author__ = "#theF∆STER™ CODE&BU!LD"

import subprocess
import winreg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, FluentIcon as FICO, SingleDirectionScrollArea, SubtitleLabel, PushSettingCard,
    PrimaryPushSettingCard, ExpandGroupSettingCard, PushButton, ComboBox, BodyLabel,
    OptionsSettingCard, SwitchSettingCard, themeColor, ColorDialog, setThemeColor,
    Theme, theme, MessageBox, CardWidget, IconWidget, CaptionLabel, ToolButton, ToolTipFilter,
    MessageBoxBase, SwitchButton, IndicatorPosition, SpinBox
)
from qframelesswindow.utils import getSystemAccentColor
from utils.SmartUtils import *

myBrowsList = smartLoadBrowsers()

class SettingsInterface(QWidget):
    """ Main class for the 'Settings' interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Settings")

        mainSetLayout = QVBoxLayout(self)
        # mainSetLayout.setContentsMargins(0, 60, 0, 0) # for split fluent window
        mainSetLayout.setContentsMargins(0, 20, 0, 0) # for fluent window
        mainTitleLine = QHBoxLayout()
        # mainTitleLine.setContentsMargins(80, 0, 0, 0) # for split fluent window
        mainTitleLine.setContentsMargins(40, 0, 0, 0) # for fluent window
        mainSetLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("Settings", self)
        self.title.setFont(smartSegoeTitle())
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.title.setContentsMargins(0, 0, 0, 50)
        mainTitleLine.addWidget(self.title)
        mainSetScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainSetLayout.addWidget(mainSetScroll)
        mainSetScroll.setWidgetResizable(True)
        # mainSetScroll.setContentsMargins(0, 0, 80, 0) # for split fluent window
        mainSetScroll.setContentsMargins(0, 0, 40, 0) # for fluent window
        mainSetScroll.enableTransparentBackground()
        mainSetScrollContent = QWidget()
        mainSetScroll.setWidget(mainSetScrollContent)
        mainSetScroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainSetScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid #FFFFFF")
        # mainSetScrollContent.setContentsMargins(80, 0, 80, 0) # for split fluent window
        mainSetScrollContent.setContentsMargins(40, 0, 40, 0) # for fluent window
        layout = QVBoxLayout(mainSetScrollContent)
        layout.setSpacing(5)
        self.widgetDef = SettingWidgetDefinition()
        self.mainFromListDlg = None
        self.mainRemoveDlg = None

        # General
        generalLabel = SubtitleLabel("General")
        generalLabel.setFont(smartSegoeSubtitle())
        generalLabel.setContentsMargins(0, 0, 0, 0)
        generalLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(generalLabel)
        layout.addWidget(self.widgetDef.optionSetAsDefault)
        # layout.addWidget(self.widgetDef.optionMainBrowserManual) # for split fluent window
        self.optionMainBrowser = MainBrowserSelectGroup()
        # layout.addWidget(self.optionMainBrowser) # for split fluent window
        layout.addWidget(self.widgetDef.optionMainBrowserCard) # for fluent window

        # Personalization - Logo blue: #28ABFA, Logo purple: #793BCC
        personalizeLabel = SubtitleLabel("Look & Feel")
        personalizeLabel.setFont(smartSegoeSubtitle())
        personalizeLabel.setContentsMargins(0, 40, 0, 0)
        personalizeLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(personalizeLabel)
        layout.addWidget(self.widgetDef.optionTheme)
        # cfg.appTheme.valueChanged.connect(print)
        self.optionAccentColor = ThemeColorSelectGroup()
        self.optionCustomAccentColorDlg = None
        self.optionAccentColor.selectButton.clicked.connect(lambda: self.openColorDialog(parent))
        layout.addWidget(self.optionAccentColor)
        layout.addWidget(self.widgetDef.optionMicaEffect)
        layout.addWidget(self.widgetDef.optionShowCommandBar)
        self.optionShowSplash = SplashSettingGroup()
        layout.addWidget(self.optionShowSplash)

        # Smart Selector
        selectorLabel = SubtitleLabel("Smart Selector")
        selectorLabel.setFont(smartSegoeSubtitle())
        selectorLabel.setContentsMargins(0, 40, 0, 0)
        selectorLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(selectorLabel)
        layout.addWidget(self.widgetDef.optionCloseOnSelect)

        # Debugging
        debuggingLabel = SubtitleLabel("Debugging")
        debuggingLabel.setFont(smartSegoeSubtitle())
        debuggingLabel.setContentsMargins(0, 40, 0, 0)
        debuggingLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(debuggingLabel)
        self.debugDelRegKeys = PushSettingCard(
            "Delete",
            FICO.DELETE,
            f"Delete {SmartLinkerName} registry keys",
            "In case you need to remove all the registry keys related to this software, this is the safest way to proceed."
        )
        layout.addWidget(self.debugDelRegKeys)
        self.debugRestart = PushSettingCard(
            "Restart",
            FICO.SYNC,
            f"Restart {SmartLinkerName}",
            "If you need for some reason to restart the software, this is the easiest way to proceed."
        )
        layout.addWidget(self.debugRestart)
        self.debugStop = PushSettingCard(
            "Stop process",
            FICO.POWER_BUTTON,
            f"Stop {SmartLinkerName}",
            "If you need for some reason to stop the software process, this is the safest way to proceed."
        )
        layout.addWidget(self.debugStop)

        layout.addStretch(1)
        
        self.updateSnack = QWidget()
        self.updateSnack.setStyleSheet(f'background-color: "{smartHexConvert(cfg.get(cfg.qAccentColor))}"')
        if bool(cfg.get(cfg.updateAvailable)): mainSetLayout.addWidget(self.updateSnack)
        self.updateSnackLayout = QHBoxLayout(self.updateSnack)
        self.updateSnackLayout.setContentsMargins(20, 10, 20, 10)
        self.updateSnackIcon = IconWidget(FICO.IOT)
        self.updateSnackIcon.setFixedSize(32, 32)
        self.updateSnackLayout.setSpacing(20)
        self.updateSnackLayout.addWidget(self.updateSnackIcon)
        self.updateSnackLabel = BodyLabel("A new update is available for download!")
        self.updateSnackLabel.setStyleSheet("font-size: 20px; font-weight: bold")
        self.updateSnackLayout.addWidget(self.updateSnackLabel)
        self.updateSnackLayout.addStretch(1)
        self.updateSnackButton = PushButton(FICO.DOWNLOAD, "Download now")
        self.updateSnackLayout.addWidget(self.updateSnackButton)

    def manualSelect(self, parent):
        self.manualPath = smartBrowseFileDialog(parent, "Select your main browser from storage", "", "Executables (*.exe)")
        if self.manualPath:
            cfg.set(cfg.mainBrowser, "")
            cfg.set(cfg.mainBrowserPath, self.manualPath)
            cfg.set(cfg.mainBrowserIsManual, True)
            self.widgetDef.optionMainBrowserManual.iconLabel.setIcon(smartGetFileIcon(self.manualPath))
            self.widgetDef.optionMainBrowserManual.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {os.path.basename(self.manualPath)} if no browser is running.")
            self.widgetDef.optionMainBrowserManual.button.setText("Reselect from storage")
            self.optionMainBrowser.selectLabel.setText("Your current main browser has been set manually")
            if myBrowsList["MyBrowsers"]: self.optionMainBrowser.selectButton.setText(f"Set {self.optionMainBrowser.mybrowsCombo.currentText()} as your main browser")
            self.optionMainBrowser.selectButton.setEnabled(bool(myBrowsList["MyBrowsers"]))
            smartSuccessNotify(self, "Manual selection complete!", f"Your main browser has been successfully set to '{os.path.basename(self.manualPath)}'.")
            print(f"Manual browser path: '{self.manualPath}'")

    def cardManualSelect(self, parent):
        self.cardManualPath = smartBrowseFileDialog(parent, "Select your main browser from storage", "", "Executables (*.exe)")
        if self.cardManualPath:
            cfg.set(cfg.mainBrowser, "")
            cfg.set(cfg.mainBrowserPath, self.cardManualPath)
            cfg.set(cfg.mainBrowserIsManual, True)
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(True)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(smartGetFileIcon(self.cardManualPath))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Your main browser has been set manually")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {os.path.basename(self.cardManualPath)} if no browser is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Reselect from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smartSuccessNotify(self, "Manual selection complete!", f"Your main browser has been successfully set to '{os.path.basename(self.cardManualPath)}'.")
            print(f"{Fore.GREEN}Your main browser has been successfully set from storage at path: '{self.cardManualPath}'{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Main browser set from storage at path: '{self.cardManualPath}'")

    def cardSetFromList(self, parent):
        if not self.mainFromListDlg:
            self.mainFromListDlg = SelectFromListDialog(parent)
        if self.mainFromListDlg.exec():
            self.myBrowsers = smartLoadBrowsers()
            for browser in self.myBrowsers["MyBrowsers"]:
                if browser["name"] == self.mainFromListDlg.browsCombo.currentText():
                    cfg.set(cfg.mainBrowser, self.mainFromListDlg.browsCombo.currentText())
                    cfg.set(cfg.mainBrowserPath, browser["path"])
                    cfg.set(cfg.mainBrowserIsManual, False)
                    break
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(True)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(smartGetFileIcon(cfg.get(cfg.mainBrowserPath)))
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Your main browser has been set from your SmartList")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText(f"{SmartLinkerName} will redirect your web requests to {self.mainFromListDlg.browsCombo.currentText()} if no browser is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Reselect from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smartSuccessNotify(self, "SmartList selection complete!", f"{self.mainFromListDlg.browsCombo.currentText()} has been successfully set as your main browser.")
            print(f"{Fore.GREEN}Your main browser has been successfully set from your SmartList: {self.mainFromListDlg.browsCombo.currentText()}{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Main browser set from SmartList: {self.mainFromListDlg.browsCombo.currentText()}")

    def cardRemove(self, parent):
        if not self.mainRemoveDlg:
            self.mainRemoveDlg = MessageBox(
                "Confirm main browser removal",
                "Your main browser will be reverted to 'None', " \
                "and you will always have to select a browser when forwarding a link, running or not.\n\n" \
                "Do you still want to proceed?",
                parent
            )
            self.mainRemoveDlg.yesButton.setText("Remove")
        if self.mainRemoveDlg.exec():
            cfg.set(cfg.mainBrowser, "")
            cfg.set(cfg.mainBrowserPath, "")
            cfg.set(cfg.mainBrowserIsManual, False)
            self.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(False)
            self.widgetDef.optionMainBrowserCard.iconWidget.setIcon(FICO.APPLICATION)
            self.widgetDef.optionMainBrowserCard.titleLabel.setText("Configure your main browser")
            self.widgetDef.optionMainBrowserCard.contentLabel.setText("You can either set a browser from your storage or SmartList as your main browser if no one is running.")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
            self.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromStorageToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            self.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
            self.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.widgetDef.optionMainBrowserCard.fromListToolTip)
            smartSuccessNotify(self, "Removal complete!", "Your main browser configuration has been reverted to 'None'.")
            print(f"{Fore.GREEN}Your main browser configuration has been successfully reverted to 'None'{Style.RESET_ALL}")
            smartLog("SUCCESS: Main browser reverted to 'None'")

    def openColorDialog(self, parent):
        """ Open a dialog to change the accent color of SmartLinker. """
        if not self.optionCustomAccentColorDlg:
            self.optionCustomAccentColorDlg = ColorDialog(
                themeColor(),
                "Choose your preferred color",
                parent,
                enableAlpha=False
            )
            self.optionCustomAccentColorDlg.editLabel.setText("Edit HEX color")
            # self.optionCustomAccentColorDlg.colorChanged.connect(lambda color: setThemeColor(color))
        if self.optionCustomAccentColorDlg.exec():
            cfg.set(cfg.accentColor, self.optionCustomAccentColorDlg.color.name())
            cfg.set(cfg.qAccentColor, self.optionCustomAccentColorDlg.color.name())
            setThemeColor(self.optionCustomAccentColorDlg.color)           

    def setAsDefaultBrowser(self):
        smartExePath = os.path.dirname(sys.executable)
        try:
            # Save the app's display name
            print(f"Pending operation: Saving the app's display name: {SmartLinkerName}...")
            smartLog(f"Saving the app's display name: {SmartLinkerName}...")
            subprocess.call(
                f'reg add "HKCU\\Software\\Clients\\StartMenuInternet\\{SmartLinkerName}" /v "" /t REG_SZ /d "{SmartLinkerName}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}{SmartLinkerName}'s name saved successfully!{Style.RESET_ALL}")
            smartLog(f"{SmartLinkerName}'s name saved successfully!")
            # Save the command for opening URLs
            print(f"Pending operation: Saving the command for opening URLs: '{smartExePath} --url=%%1'")
            smartLog(f"SUCCESS: Saving the command for opening URLs: '{smartExePath} --url=%%1'")
            subprocess.call(
                f'reg add "HKCU\\Software\\Clients\\StartMenuInternet\\{SmartLinkerName}\\shell\\open\\command" /v "" /t REG_SZ /d "{smartExePath} --url=%%1" /f',
                shell=True
            )
            print(f"{Fore.GREEN}Opening URLs command saved successfully!{Style.RESET_ALL}")
            smartLog("SUCCESS: Opening URLs command saved successfully!")
            # Save the app capabilities
            print(f"Pending operation: Saving {SmartLinkerName}'s capabilities...")
            smartLog(f"Saving {SmartLinkerName}'s capabilities...")
            subprocess.call(
                f'reg add "HKCU\\Software\\{SmartLinkerName}\\Capabilities" /v "ApplicationDescription" /t REG_SZ /d "An easy-to-use URL handler that allows you to manage conveniently and customize the way documents and web links are opened in web browsers." /f',
                shell=True
            )
            print(f"{Fore.GREEN}Operation completed successfully: registering {SmartLinkerName}'s description{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Registering {SmartLinkerName}'s description complete!")
            subprocess.call(
                f'reg add "HKCU\\Software\\{SmartLinkerName}\\Capabilities" /v "ApplicationName" /t REG_SZ /d "{SmartLinkerName}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}Operation completed successfully: saving {SmartLinkerName}'s name{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Saving {SmartLinkerName}'s name complete!")
            subprocess.call(
                f'reg add "HKCU\\Software\\{SmartLinkerName}\\Capabilities\\ApplicationDescription" /v "" /t REG_SZ /d "An easy-to-use URL handler that allows you to manage conveniently and customize the way documents and web links are opened in web browsers." /f',
                shell=True
            )
            print(f"{Fore.GREEN}Operation completed successfully: saving {SmartLinkerName}'s description{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Saving {SmartLinkerName}'s description complete!")
            # Save the HTTP and HTTPS protocols
            print(f"Pending operation: Saving {SmartLinkerName}'s protocols...")
            smartLog(f"Saving {SmartLinkerName}'s protocols...")
            subprocess.call(
                f'reg add "HKCU\\Software\\{SmartLinkerName}\\Capabilities\\URLAssociations" /v "http" /t REG_SZ /d "{SmartLinkerID}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}Operation completed successfully: saving {SmartLinkerName}'s HTTP protocol{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Saving {SmartLinkerName}'s HTTP protocol complete!")
            subprocess.call(
                f'reg add "HKCU\\Software\\{SmartLinkerName}\\Capabilities\\URLAssociations" /v "https" /t REG_SZ /d "{SmartLinkerID}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}Operation completed successfully: saving {SmartLinkerName}'s HTTPS protocol{Style.RESET_ALL}")
            smartLog(f"SUCCESS: Saving {SmartLinkerName}'s HTTPS protocol complete!")
            # Update the registry information for Windows to acknowledge the changes
            print("Pending operation: Updating the registry information for Windows to acknowledge the changes...")
            smartLog("Updating the registry information for Windows to acknowledge the changes...")
            subprocess.call(
                f'reg add "HKCU\\Software\\RegisteredApplications" /v "{SmartLinkerName}" /t REG_SZ /d "Software\\{SmartLinkerName}\\Capabilities" /f',
                shell=True
            )
            print(f"{Fore.GREEN}Registry information updated successfully!{Style.RESET_ALL}")
            smartLog("SUCCESS: Registry information updated successfully!")
            setAsMainDlg = MessageBox(
                "Set as default browser",
                f"Do you really want to set {SmartLinkerName} as your system's main browser?",
                self
            )
            setAsMainDlg.yesButton.setText("Set as default")
            setAsMainDlg.cancelButton.setText("Cancel")
            if setAsMainDlg.exec():
                print("Pending operation: Backing up the actual default browser ID...")
                smartLog("Backing up the actual default browser ID...")
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
                ) as httpRegKey:
                    httpValue, _ = winreg.QueryValueEx(httpRegKey, "ProgId")
                    subprocess.call(
                        f'reg add "HKCU\\Software\\{SmartLinkerName}\\backup" /v "PreviousDefaultHttpId" /t REG_SZ /d "{httpValue}" /f',
                        shell=True
                    )
                    with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        f"Software\\{SmartLinkerName}\\backup"
                    ) as bakKey:
                        httpBakKey, _ = winreg.QueryValueEx(bakKey, "PreviousDefaultHttpId")
                        print(f"{Fore.GREEN}The default browser ID for HTTP protocol has been successfully backed up!{Style.RESET_ALL}" if httpBakKey == httpValue else f"{Fore.RED}The operation for backing up the HTTP protocol's default browser ID failed...{Style.RESET_ALL}")
                        smartLog("SUCCESS: The default browser ID for HTTP protocol has been successfully backed up!" if httpBakKey == httpValue else "WARNING: Failed to backup the HTTP protocol's default browser ID...")
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
                ) as httpsRegKey:
                    httpsValue, _ = winreg.QueryValueEx(httpsRegKey, "ProgId")
                    subprocess.call(
                        f'reg add "HKCU\\Software\\{SmartLinkerName}\\backup" /v "PreviousDefaultHttpsId" /t REG_SZ /d "{httpsValue}" /f',
                        shell=True
                    )
                    with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        f"Software\\{SmartLinkerName}\\backup"
                    ) as bakKey:
                        httpsBakKey, _ = winreg.QueryValueEx(bakKey, "PreviousDefaultHttpsId")
                        print(f"{Fore.GREEN}The default browser ID for HTTPS protocol has been successfully backed up!{Style.RESET_ALL}" if httpsBakKey == httpsValue else f"{Fore.RED}The operation for backing up the HTTPS protocol's default browser ID failed...{Style.RESET_ALL}")
                        smartLog("SUCCESS: The default browser ID for HTTPS protocol has been successfully backed up!" if httpBakKey == httpValue else "WARNING: Failed to backup the HTTPS protocol's default browser ID...")
                print("Pending operation: Updating the registry information...")
                smartLog("Updating the registry information...")
                """ subprocess.call(
                    f'reg delete "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice" /v "ProgId" /f',
                    shell=True
                )
                subprocess.call(
                    f'reg delete "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice" /v "ProgId" /f',
                    shell=True
                ) """
                subprocess.call(
                    f'reg add "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice" /v "ProgId" /t REG_SZ /d "{SmartLinkerID}" /f',
                    shell=True
                )
                subprocess.call(
                    f'reg add "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice" /v "ProgId" /t REG_SZ /d "{SmartLinkerID}" /f',
                    shell=True
                )
                if smartIsSystemDefault(self, SmartLinkerID):
                    print(f"{Fore.GREEN}{SmartLinkerName} is now your current default browser!{Style.RESET_ALL}")
                    smartLog(f"SUCCESS: {SmartLinkerName} is now your current default browser!")
                    self.widgetDef.optionSetAsDefault.button.setEnabled(False)
                    self.widgetDef.optionSetAsDefault.button.setVisible(False)
                    self.widgetDef.optionSetAsDefault.iconLabel.setIcon(FICO.COMPLETED)
                    self.widgetDef.optionSetAsDefault.titleLabel.setText("Thank you for making me your personal favorite!")
                    self.widgetDef.optionSetAsDefault.contentLabel.setText(f"{SmartLinkerName} is currently your system's default web browser.")
                else:
                    print(f"{Fore.YELLOW}WARNING!! {SmartLinkerName} is still not your system's default browser... You will need to set is as default manually.\n" \
                          f"{Fore.BLUE}Opening Windows settings...{Style.RESET_ALL}")
                    smartLog(f"WARNING: {SmartLinkerName} is still not the system's default browser... The user will need to set is as default manually.")
                    subprocess.Popen(['start', 'ms-settings:defaultapps-byprotocol'], shell=True)
            else:
                smartInfoNotify(self, "In case you missed...", f"{SmartLinkerName} is not your system's default browser yet...")
                smartLog(f"{SmartLinkerName} is not your system's default browser yet...")
        except Exception as e:
            smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to set {SmartLinkerName} as the default browser:\n{e}")
            print(f"{Fore.RED}Something went wrong while attempting to set {SmartLinkerName} as the default browser: {e}{Style.RESET_ALL}")
            smartLog(f"ERROR: Failed to set {SmartLinkerName} as the default browser: {e}")

    def removeDefaultBrowserKeys(self):
        try:
            # Restore the backed up IDs
            print("Pending operation: Restoring the previous default browser IDs...")
            smartLog("Restoring the previous default browser IDs...")
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                f'Software\\{SmartLinkerName}\\backup'
            ) as bakKey:
                httpResKey, _ = winreg.QueryValueEx(bakKey, "PreviousDefaultHttpId")
                subprocess.call(
                    f'reg add "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice" /v "ProgId" /t REG_SZ /d "{httpResKey}" /f',
                    shell=True
                )
                httpsResKey, _ = winreg.QueryValueEx(bakKey, "PreviousDefaultHttpsId")
                subprocess.call(
                    f'reg add "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice" /v "ProgId" /t REG_SZ /d "{httpsResKey}" /f',
                    shell=True
                )
            print(f"{Fore.GREEN}The previous IDs have been restored successfully!{Style.RESET_ALL}")
            smartLog("SUCCESS: The previous IDs have been restored successfully!")
        except Exception as e:
            # smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to restore the previous default browser ID: {e}")
            print(f"{Fore.RED}Something went wrong while attempting to restore the previous default browser ID: {e}{Style.RESET_ALL}")
            smartLog(f"ERROR: Failed to to restore the previous default browser ID: {e}")
        try:
            # Delete the main app key
            print(f"Pending operation: Deleting {SmartLinkerName}'s main key...")
            smartLog(f"Deleting {SmartLinkerName}'s main key...")
            subprocess.call(
                f'reg delete "HKCU\\Software\\Clients\\StartMenuInternet\\{SmartLinkerName}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}The main key has been successfully deleted!{Style.RESET_ALL}")
            smartLog("SUCCESS: The main key has been successfully deleted!")
            # Delete the app capabilities
            print(f"Pending operation: Removing {SmartLinkerName}'s capabilities...")
            smartLog(f"Removing {SmartLinkerName}'s capabilities...")
            subprocess.call(
                f'reg delete "HKCU\\Software\\{SmartLinkerName}" /f',
                shell=True
            )
            print(f"{Fore.GREEN}{SmartLinkerName}'s capabilities have been successfully removed!{Style.RESET_ALL}")
            smartLog(f"SUCCESS: {SmartLinkerName}'s capabilities have been successfully removed!")
            # Update the registry information
            print("Pending operation: Updating the registry information...")
            smartLog("Updating the registry information...")
            subprocess.call(
                f'reg delete "HKCU\\Software\\RegisteredApplications" /v "{SmartLinkerName}" /f',
                shell=True
            )
            smartSuccessNotify(self, "Deletion complete!", f"All {SmartLinkerName}-related registry keys have been successfully deleted!")
            print(f"{Fore.GREEN}All {SmartLinkerName}-related registry keys have been successfully deleted!{Style.RESET_ALL}")
            smartLog(f"SUCCESS: All {SmartLinkerName}-related registry keys have been successfully deleted!")
            self.widgetDef.optionSetAsDefault.button.setEnabled(True)
            self.widgetDef.optionSetAsDefault.button.setVisible(True)
            self.widgetDef.optionSetAsDefault.iconLabel.setIcon(QIcon(smartResourcePath("resources/images/icons/icon_monochrome.ico") if theme() == Theme.DARK else smartResourcePath("resources/images/icons/icon_monochrome_black.ico")))
            self.widgetDef.optionSetAsDefault.titleLabel.setText("Make me your default browser")
            self.widgetDef.optionSetAsDefault.contentLabel.setText(f"For {SmartLinkerName} to work correctly, you need to set it as your system's default web browser.")
        except Exception as e:
            smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to delete {SmartLinkerName}'s registry keys:\n{e}")
            print(f"{Fore.RED}Something went wrong while attempting to delete {SmartLinkerName}'s registry keys: {e}{Style.RESET_ALL}")
            smartLog(f"ERROR: Failed to delete {SmartLinkerName}'s registry keys: {e}")

class SettingWidgetDefinition():
    """ Declaration class of SettingsInterface main widgets """

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
        self.optionSetAsDefault = PrimaryPushSettingCard(
            text="Set as default browser",
            icon=QIcon(smartResourcePath("resources/images/icons/icon_monochrome.ico") if theme() == Theme.DARK else
                       smartResourcePath("resources/images/icons/icon_monochrome_black.ico")) if not smartIsSystemDefault(self, SmartLinkerID) else
                    FICO.COMPLETED,
            title="Make me your default browser" if not smartIsSystemDefault(self, SmartLinkerID) else "Thank you for making me your personal favorite!",
            content=f"For {SmartLinkerName} to work correctly, you need to set it as your system's default web browser." if not smartIsSystemDefault(self, SmartLinkerID) else f"{SmartLinkerName} is currently your system's default web browser."
        )
        self.optionSetAsDefault.button.setEnabled(not smartIsSystemDefault(self, SmartLinkerID))
        self.optionSetAsDefault.button.setHidden(smartIsSystemDefault(self, SmartLinkerID))
        self.optionMainBrowserManual = PushSettingCard(
            self.manualButtonText,
            smartGetFileIcon(cfg.get(cfg.mainBrowserPath)) if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual) else FICO.APPLICATION,
            "Configure your main browser manually",
            self.manualContent
        )
        self.mainBrowsName = os.path.basename(cfg.get(cfg.mainBrowserPath)) if cfg.get(cfg.mainBrowserIsManual) else cfg.get(cfg.mainBrowser)
        self.optionMainBrowserCard = MainBrowsersCard(
            smartGetFileIcon(cfg.get(cfg.mainBrowserPath)) if cfg.get(cfg.mainBrowserPath) else FICO.APPLICATION,
            f"Your main browser has been set {"manually" if cfg.get(cfg.mainBrowserIsManual) else "from your SmartList"}" if cfg.get(cfg.mainBrowserPath) else \
            "Configure your main browser",
            f"{SmartLinkerName} will redirect your web requests to {self.mainBrowsName} if no browser is running." if cfg.get(cfg.mainBrowserPath) else \
            "You can either set a browser from your storage or SmartList as your main browser if no one is running."
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

        # Smart Selector
        self.optionCloseOnSelect = SwitchSettingCard(
            FICO.EMBED,
            "Close window on browser selection",
            "If enabled, the Smart Selector window will close once a browser is selected for the forwarded link to be loaded.",
            cfg.closeOnBrowserSelect
        )

class MainBrowserSelectGroup(ExpandGroupSettingCard):
    """ Setting card group for main browser selection """

    def __init__(self, parent=None):
        super().__init__(
            FICO.GLOBE,
            "Configure your main browser from your SmartList",
            "You can set one of your SmartList browsers as your main browser if no one is running."
        )

        # Select button
        self.selectButton = PushButton("Set as main browser")
        self.selectLabel = BodyLabel("")
        self.selectButton.setMinimumWidth(150)
        self.selectButton.setEnabled(bool(myBrowsList["MyBrowsers"]))

        # My browsers list
        self.mybrowsLabel = BodyLabel("Choose from your SmartList")
        self.mybrowsRefresh = PushButton("Refresh browsers")
        self.mybrowsRefresh.setFixedWidth(150)
        self.mybrowsCombo = ComboBox()
        self.mybrowsCombo.setEnabled(bool(myBrowsList["MyBrowsers"]))
        if myBrowsList["MyBrowsers"]:
            for browser in myBrowsList["MyBrowsers"]:
                self.mybrowsCombo.addItem(browser["name"], smartGetFileIcon(browser["path"]))
            self.mybrowsCombo.setEnabled(True)
        else:
            self.mybrowsCombo.setPlaceholderText("SmartList is empty")
            self.mybrowsCombo.setEnabled(False)
        self.mybrowsCombo.setFixedWidth(180)

        if not self.mybrowsCombo.count() > 0:
            self.selectLabel.setText("There is no browsers in your SmartList yet...")
            self.selectButton.setEnabled(False)
            self.selectButton.setHidden(True)
        else:
            self.selectLabel.setText(f"Set {self.mybrowsCombo.currentText()} as your main browser")
            self.selectButton.setEnabled(True)
            self.selectButton.setHidden(False)
            if cfg.get(cfg.mainBrowserPath):
                if cfg.get(cfg.mainBrowserIsManual):
                    self.selectLabel.setText("Your current browser has been set manually")
                    self.selectButton.setText(f"Set {self.mybrowsCombo.currentText()} as your main browser") # if len(myBrowsList["MyBrowsers"]) > 0 and self.mybrowsCombo.currentText() else "No browsers available")
                else:
                    self.selectLabel.setText(f"{cfg.get(cfg.mainBrowser)} is your current main browser")
                    self.selectButton.setEnabled(not self.selectLabel.text().startswith(self.mybrowsCombo.currentText()))
                    self.selectButton.setText("Main browser set" if self.selectLabel.text().startswith(self.mybrowsCombo.currentText()) else "Set as main browser")
            else:
                self.selectLabel.setText("No main browser has been set yet")
                self.selectButton.setEnabled(False)
                self.selectButton.setText("Set as main browser") # if len(myBrowsList["MyBrowsers"]) > 0 and self.mybrowsCombo.currentText() else "No browsers available")
        self.mybrowsCombo.currentTextChanged.connect(lambda text: self.comboChangeListener(text))
        # self.selectButton.clicked.connect(lambda: self.setFromList(self.mybrowsCombo.currentText()))

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add_group(self.selectLabel, self.selectButton)
        self.add_group(self.mybrowsLabel, self.mybrowsCombo, self.mybrowsRefresh)

    def add_group(self, label, widget, widget2=None):
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        widLayout.addStretch(1)
        if widget2 is not None: widLayout.addWidget(widget2)
        widLayout.addWidget(widget)

        self.addGroupWidget(wid)

    def comboChangeListener(self, text):
        if cfg.get(cfg.mainBrowserPath):
            if cfg.get(cfg.mainBrowserIsManual):
                self.selectButton.setText(f"Set {text} as your main browser" if len(myBrowsList["MyBrowsers"]) > 0 and text else "No browsers available")
            else:
                self.selectButton.setEnabled(not self.selectLabel.text().startswith(text))
                self.selectButton.setText("Main browser set" if self.selectLabel.text().startswith(text) else "Set as main browser")
        else:
            self.selectButton.setEnabled(False)
            # self.selectLabel.setText(f"You can set {text} as main browser" if len(myBrowsList["MyBrowsers"]) > 0 and text else "There is no browsers in your SmartList yet...")

    def refreshBrowsersCombo(self, parent, combo: ComboBox):
        combo.clear()
        myBrowsList = smartLoadBrowsers()
        for browser in myBrowsList["MyBrowsers"]:
            combo.addItem(browser["name"], smartGetFileIcon(browser["path"]))
        smartInfoNotify(parent, "SmartList refreshed", "The list of browsers has been refreshed successfully.")
        self.selectButton.setEnabled(len(myBrowsList["MyBrowsers"]) > 0)
        self.mybrowsCombo.setEnabled(len(myBrowsList["MyBrowsers"]) > 0)
        if not myBrowsList["MyBrowsers"]: self.mybrowsCombo.setPlaceholderText("SmartList is empty")
        self.comboChangeListener(combo.currentText())

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
        """ Add accent mode and color elements to the group. """
        wid = QWidget()
        wid.setFixedHeight(60)
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)
        widLayout.addStretch(1)
        widLayout.addWidget(widget)

        self.addGroupWidget(wid)

    def changeAccentMode(self, text):
        """ Change the current accent mode and color according to the selection. """
        if text == "Custom accent color":
            cfg.set(cfg.accentMode, "Custom")
            setThemeColor(QColor(cfg.get(cfg.accentColor)) if cfg.get(cfg.accentColor) else QColor(cfg.get(cfg.qAccentColor)))
        else:
            cfg.set(cfg.accentMode, "System")
            setThemeColor(getSystemAccentColor(), save=True)

class SplashSettingGroup(ExpandGroupSettingCard):
    """ Class for SmartLinker's splash screen configuration in the Look & Feel section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.FLAG,
            "Toggle the splash flag",
            f"If enabled, a splash screen is displayed when opening the {SmartLinkerName} window."
        )

        # First group
        self.switchLabel = BodyLabel("Enable splash screen display")
        self.switchButton = SwitchButton(parent=self, indicatorPos=IndicatorPosition.RIGHT)
        self.switchButton.setChecked(cfg.get(cfg.showSplash))
        self.switchButton.checkedChanged.connect(lambda checked: (
            self.durationSpin.setEnabled(checked),
            cfg.set(cfg.showSplash, checked)
        ))
        # self.switchButton.setOnText("On")

        # Second group
        self.durationLabel = BodyLabel("Set display duration (in milliseconds)")
        self.durationSpin = SpinBox()
        self.durationSpin.setRange(0, 10000)
        self.durationSpin.setValue(cfg.get(cfg.splashDuration))
        self.durationSpin.valueChanged.connect(lambda value: cfg.set(cfg.splashDuration, value))
        self.durationSpin.setEnabled(cfg.get(cfg.showSplash))

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add each group to the setting card
        self.add(self.switchLabel, self.switchButton)
        self.add(self.durationLabel, self.durationSpin)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        # Add the widget group to the setting card
        self.addGroupWidget(w)

class MainBrowsersCard(CardWidget):
    """ Class for the the main browser configuration card """

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.fromStorageButton = ToolButton(FICO.FOLDER, self)
        self.fromListButton = ToolButton(smartResourcePath("resources/images/icons/icon.ico"), self)
        self.removeMainButton = ToolButton(FICO.REMOVE_FROM, self)
        self.fromStorageToolTip = ToolTipFilter(self.fromStorageButton)
        self.fromListToolTip = ToolTipFilter(self.fromListButton)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(84)
        self.setClickEnabled(False)
        self.iconWidget.setFixedSize(44, 44)
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Select from your SmartList', self)
        self.icon = IconWidget(FICO.GLOBE)
        self.browsCombo = ComboBox()
        self.infoLabel = CaptionLabel()

        self.icon.setFixedSize(64, 64)
        self.browsCombo.setPlaceholderText("Select a SmartList browser")
        for browser in myBrowsList["MyBrowsers"]:
            self.browsCombo.addItem(browser["name"], smartGetFileIcon(browser["path"]))
        if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
            self.browsCombo.addItem(os.path.basename(cfg.get(cfg.mainBrowserPath)), smartGetFileIcon(cfg.get(cfg.mainBrowserPath)))

        for browser in myBrowsList["MyBrowsers"]:
            if browser["name"] == self.browsCombo.currentText():
                self.icon.setIcon(smartGetFileIcon(browser["path"]))
                break
        self.infoLabel.setText(f"{self.browsCombo.currentText()} will be set as your main browser.")
        self.infoLabel.setTextColor(QColor("blue"), QColor("#2196F3"))
        self.yesButton.setText("Set as main browser")

        self.browsCombo.currentTextChanged.connect(lambda text: self.comboTextChangeListener(text))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.browsCombo)
        self.viewLayout.addWidget(self.infoLabel, 0, Qt.AlignmentFlag.AlignCenter)

        self.widget.setMinimumWidth(350)

    def comboTextChangeListener(self, text: str):
        self.infoLabel.setText(f"{text} will be set as your main browser.")
        for browser in myBrowsList["MyBrowsers"]:
            if browser["name"] == text:
                self.icon.setIcon(smartGetFileIcon(browser["path"]))
                break

    def validate(self):
        if not self.browsCombo.currentText() or self.browsCombo.count == 0: return False
        return True
