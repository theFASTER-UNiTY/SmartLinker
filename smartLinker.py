import os
import sys

from PyQt6.QtCore import QEventLoop, QTimer, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow, Theme, setTheme, NavigationItemPosition, MessageBox,
    FluentIcon as FICO, SplashScreen, themeColor, theme
)
from utils.SmartUtils import *
from utils.settingsInterface import SettingsInterface as Settings
from utils.mybrowsersInterface import MyBrowsersInterface as MyBrowsers
from utils.aboutInterface import AboutInterface as About
from utils.smartSelector import SmartSelectorGUI

# =============================================================================

latestVersion = smartGetLatestVersionTag()

class SmartLinkerGUI(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.centerWindow()
        self.setWindowTitle("SmartLinker - Mastering URL Handling")
        self.setWindowIcon(QIcon(smartResourcePath("resources/images/icons/icon.ico")))
        self.resize(1100, 700)
        self.setMinimumWidth(950)
        self.move(40, 25)
        self.setStyleSheet('font-family: "Segoe UI Variable", "Segoe UI", sans-serif;')
        if cfg.get(cfg.appTheme) == "Dark": setTheme(Theme.DARK)
        elif cfg.get(cfg.appTheme) == "Light": setTheme(Theme.LIGHT)
        else: setTheme(Theme.AUTO)
        self.myBrowsers = smartLoadBrowsers()
        cfg.set(cfg.qAccentColor, getSystemAccentColor())
        smartEmptyLog()

        self.removeKeysDlg = None
        self.listSelectDlg = None

        if latestVersion:
            if Version(latestVersion) > Version(SmartLinkerVersion):
                cfg.set(cfg.updateAvailable, True)
                cfg.set(cfg.updateVersion, latestVersion)
            else: cfg.set(cfg.updateAvailable, False)
        if bool(cfg.get(cfg.showSplash)):
            self.splash = SplashScreen(self.windowIcon(), self)
            self.splash.setIconSize(QSize(105, 105))
            self.show()
            self.createSubInterfaces()
            self.splash.finish()
        else:
            self.mybrowsInterface = MyBrowsers(self)
            self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
            self.settingInterface = Settings(self)
            self.addSubInterface(self.settingInterface, FICO.SETTING, "Settings", NavigationItemPosition.BOTTOM)
            self.aboutInterface = About(self)
            self.addSubInterface(self.aboutInterface, FICO.INFO, "About", NavigationItemPosition.BOTTOM)
            self.show()
        self.setMicaEffectEnabled(self.settingInterface.widgetDef.optionMicaEffect.switchButton.isChecked())
        
        """ self.settingInterface.widgetDef.optionSetAsDefault.button.clicked.connect(lambda: (
            self.settingInterface.widgetDef.optionSetAsDefault.button.setEnabled(False),
            self.settingInterface.widgetDef.optionSetAsDefault.button.setVisible(False),
            self.settingInterface.widgetDef.optionSetAsDefault.iconLabel.setIcon(FICO.COMPLETED),
            self.settingInterface.widgetDef.optionSetAsDefault.titleLabel.setText("Thank you for making me your personal favorite!"),
            self.settingInterface.widgetDef.optionSetAsDefault.contentLabel.setText("SmartLinker is currently your system's default web browser.")
        )) """
        self.settingInterface.widgetDef.optionSetAsDefault.button.clicked.connect(self.settingInterface.setAsDefaultBrowser)
        self.settingInterface.widgetDef.optionMainBrowserManual.button.clicked.connect(lambda: self.settingInterface.manualSelect(self))
        self.settingInterface.optionMainBrowser.selectButton.clicked.connect(lambda: self.setFromList(self.settingInterface.optionMainBrowser.mybrowsCombo.currentText()))
        self.settingInterface.optionMainBrowser.mybrowsRefresh.clicked.connect(lambda: self.settingInterface.optionMainBrowser.refreshBrowsersCombo(self, self.settingInterface.optionMainBrowser.mybrowsCombo))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.clicked.connect(lambda: self.settingInterface.cardManualSelect(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.clicked.connect(lambda: self.settingInterface.cardSetFromList(self))
        self.settingInterface.widgetDef.optionMainBrowserCard.removeMainButton.clicked.connect(lambda: self.settingInterface.cardRemove(self))
        self.settingInterface.widgetDef.optionTheme.buttonGroup.buttonClicked.connect(lambda button: self.toggleTheme(button))
        self.settingInterface.optionAccentColor.accentCombo.currentTextChanged.connect(lambda text: self.settingInterface.optionAccentColor.selectButton.setEnabled(bool(text == "Custom accent color")))
        self.settingInterface.widgetDef.optionMicaEffect.switchButton.checkedChanged.connect(lambda checked: self.setMicaEffectEnabled(checked))
        self.settingInterface.widgetDef.optionShowCommandBar.switchButton.checkedChanged.connect(lambda checked: (
            self.mybrowsInterface.myBrowsCommandBar.setVisible(checked),
            self.mybrowsInterface.actionCaption.setVisible(checked),
            self.mybrowsInterface.actionTable.setVisible(checked),
            self.mybrowsInterface.mybrowsAddCard.setHidden(checked),
            self.mybrowsInterface.mybrowsRefreshCard.setHidden(checked),
            self.mybrowsInterface.mybrowsLoadLinkCard.setHidden(checked),
            self.mybrowsInterface.myBrowsClearCard.setHidden(checked)
        ))
        self.settingInterface.debugDelRegKeys.button.clicked.connect(self.confirmRemoveKeys)
        self.settingInterface.debugRestart.button.clicked.connect(self.confirmRestart)
        self.settingInterface.debugStop.button.clicked.connect(self.confirmStop)
        self.aboutInterface.aboutResources.pyQtBtn.clicked.connect(lambda: smartOpenURL("https://www.pythonguis.com/pyqt6/"))
        self.aboutInterface.aboutResources.pyQtBtn2.clicked.connect(lambda: smartOpenURL("https://doc.qt.io/qtforpython-6/"))
        self.aboutInterface.aboutResources.qFluentBtn.clicked.connect(lambda: smartOpenURL("https://www.qfluentwidgets.com/"))
        self.aboutInterface.aboutResources.qFluentBtn2.clicked.connect(lambda: smartOpenURL("https://github.com/zhiyiYo/PyQt-Fluent-Widgets"))
        self.aboutInterface.aboutResources.pyQtBtn.clicked.connect(lambda: smartOpenURL("https://www.flaticon.com/"))
        qconfig.themeChangedFinished.connect(lambda theme=theme(): (
            # setTheme(theme),
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smartGetRed(themeColor())}, {smartGetGreen(themeColor())}, {smartGetBlue(themeColor())}, 0.5)}}"), # type: ignore
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smartGetRed(themeColor())}, {smartGetGreen(themeColor())}, {smartGetBlue(themeColor())}, 0.5)}}"), # type: ignore
            self.aboutInterface.updateCard.setBackgroundColor(QColor(smartGetRed(themeColor()), smartGetGreen(themeColor()), smartGetBlue(themeColor()), 127)) if self.aboutInterface.updateCard else print("None"), # type: ignore
        ))
        qconfig.themeColorChanged.connect(lambda color=themeColor(): (
            self.mybrowsInterface.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smartGetRed(color)}, {smartGetGreen(color)}, {smartGetBlue(color)}, 0.5)}}"), # type: ignore
            self.settingInterface.updateSnack.setStyleSheet(f"#SSnackBase {{background-color: rgba({smartGetRed(color)}, {smartGetGreen(color)}, {smartGetBlue(color)}, 0.5)}}"), # type: ignore
            self.aboutInterface.updateCard.setBackgroundColor(QColor(smartGetRed(color), smartGetGreen(color), smartGetBlue(color), 127)) if self.aboutInterface.updateCard else None, # type: ignore
        ))

    def createSubInterfaces(self):
        loop = QEventLoop(self)
        QTimer.singleShot(cfg.get(cfg.splashDuration), loop.quit)
        loop.exec()
        self.mybrowsInterface = MyBrowsers(self)
        self.addSubInterface(self.mybrowsInterface, FICO.GLOBE, "My Browsers")
        self.settingInterface = Settings(self)
        self.addSubInterface(self.settingInterface, FICO.SETTING, "Settings", NavigationItemPosition.BOTTOM)
        self.aboutInterface = About(self)
        self.addSubInterface(self.aboutInterface, FICO.INFO, "About", NavigationItemPosition.BOTTOM)

    def centerWindow(self):
        windowGeometry = self.frameGeometry()
        screen = QApplication.primaryScreen()
        if screen:
            screenGeometry = screen.availableGeometry()
            centerPoint = screenGeometry.center()
            windowGeometry.moveCenter(centerPoint)
            self.move(windowGeometry.topLeft())
        else: self.centerWindow()

    def toggleTheme(self, button):
        if button.text() == "Use system setting":
            setTheme(Theme.AUTO)
            self.settingInterface.widgetDef.optionSetAsDefault.iconLabel.setIcon(QIcon(smartResourcePath("resources/images/icons/icon_monochrome_black.ico"))) if not isDarkModeEnabled() \
            else self.settingInterface.widgetDef.optionSetAsDefault.iconLabel.setIcon(QIcon(smartResourcePath("resources/images/icons/icon_monochrome.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.lightSheetOnDark if isDarkModeEnabled() else self.mybrowsInterface.darkSheetOnLight)
        elif button.text() == "Dark":
            setTheme(Theme.DARK)
            self.settingInterface.widgetDef.optionSetAsDefault.iconLabel.setIcon(QIcon(smartResourcePath("resources/images/icons/icon_monochrome.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.lightSheetOnDark)
        else:
            setTheme(Theme.LIGHT)
            self.settingInterface.widgetDef.optionSetAsDefault.iconLabel.setIcon(QIcon(smartResourcePath("resources/images/icons/icon_monochrome_black.ico")))
            self.mybrowsInterface.mybrowsScroll.setStyleSheet(self.mybrowsInterface.darkSheetOnLight)

    def setFromList(self, text):
        if (not self.settingInterface.optionMainBrowser.mybrowsCombo.count() == 0) or self.settingInterface.optionMainBrowser.mybrowsCombo.currentText():
            self.myBrowsers = smartLoadBrowsers()
            for browser in self.myBrowsers["MyBrowsers"]:
                if browser["name"] == text:
                    cfg.set(cfg.mainBrowser, text)
                    cfg.set(cfg.mainBrowserPath, browser["path"])
                    cfg.set(cfg.mainBrowserIsManual, False)
                    break
            self.settingInterface.optionMainBrowser.selectLabel.setText(f"{text} is your current main browser")
            self.settingInterface.optionMainBrowser.selectButton.setEnabled(False)
            self.settingInterface.optionMainBrowser.selectButton.setText("Main browser set")
            self.settingInterface.widgetDef.optionMainBrowserManual.iconLabel.setIcon(FICO.APPLICATION)
            self.settingInterface.widgetDef.optionMainBrowserManual.contentLabel.setText(f"Your current main browser has been set from your SmartList ({text}).")
            self.settingInterface.widgetDef.optionMainBrowserManual.button.setText("Select from storage")

    def confirmDeleteDialog(self, name: str, parent):
        self.deleteDlg = MessageBox(
            f"Delete {name}",
            f"Do you really want to remove {name} from your SmartList?\n" \
                "This action is irreversible.",
            parent
        )
        self.deleteDlg.yesButton.setText("Delete")
        if self.deleteDlg.exec():
            print(f"Prnding operation: Removing {name} from the SmartList...")
            smartLog(f"Removing {name} from the SmartList...")
            myBrowsList = smartLoadBrowsers()
            baseCount = len(myBrowsList["MyBrowsers"])
            updatedList = {"MyBrowsers": [browser for browser in myBrowsList["MyBrowsers"] if browser["name"] != name]}
            if len(updatedList) == baseCount:
                print(f"{Fore.YELLOW}WARNING!! {name} cannot be found, failed to remove from your SmartList...{Style.RESET_ALL}")
                smartLog(f"WARNING: {name} cannot be found, unable to proceed to its removal from the SmartList...")
                smartWarningNotify(self, "Warning, be careful!", f"{name} cannot be found, failed to remove from your SmartList...")
                return
            if cfg.get(cfg.mainBrowser):
                if cfg.get(cfg.mainBrowser) == name:
                    cfg.set(cfg.mainBrowser, "")
                    cfg.set(cfg.mainBrowserPath, "")
                    cfg.set(cfg.mainBrowserIsManual, False)
                    self.settingInterface.widgetDef.optionMainBrowserCard.removeMainButton.setEnabled(False)
                    self.settingInterface.widgetDef.optionMainBrowserCard.iconWidget.setIcon(FICO.APPLICATION)
                    self.settingInterface.widgetDef.optionMainBrowserCard.titleLabel.setText("Configure your main browser")
                    self.settingInterface.widgetDef.optionMainBrowserCard.contentLabel.setText("You can either set a browser from your storage or SmartList as your main browser if no one is running.")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.removeEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.setToolTip("Select from your storage")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageButton.installEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromStorageToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.removeEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromListToolTip)
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.setToolTip("Select from your SmartList")
                    self.settingInterface.widgetDef.optionMainBrowserCard.fromListButton.installEventFilter(self.settingInterface.widgetDef.optionMainBrowserCard.fromListToolTip)
            print("Saving the updated browsers database...")
            smartLog(f"{name} has been removed. Updating the browsers database...")
            smartWriteBrowsers(updatedList)
            self.mybrowsInterface.refreshBrowsers(self)
            print(f"{Fore.GREEN}{name} has been successfully removed from your SmartList!{Style.RESET_ALL}")
            smartLog(f"SUCCESS: {name} has been successfully removed from the SmartList.")
            smartSuccessNotify(self, "Removal complete!", f"{name} has been successfully removed from your SmartList!")

    def confirmRemoveKeys(self):
        if not self.removeKeysDlg:
            self.removeKeysDlg = MessageBox(
                "Remove all registry keys",
                f"Are you sure you really want to remove every single {SmartLinkerName}-related information from Windows registry?",
                self
            )
            self.removeKeysDlg.yesButton.setText("Remove all")
            self.removeKeysDlg.cancelButton.setText("Cancel")
        if self.removeKeysDlg.exec(): self.settingInterface.removeDefaultBrowserKeys()

    def confirmRestart(self):
        restartDlg = MessageBox(
            "Restart confirmation",
            "Are you sure you really want to restart SmartLinker?",
            self
        )
        restartDlg.yesButton.setText("Restart")
        restartDlg.cancelButton.setText("Cancel")
        if restartDlg.exec():
            try: restartApp()
            except Exception as e: smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to restart SmartLinker: {e}")
    
    def confirmStop(self):
        stopDlg = MessageBox(
            "Quit confirmation",
            "Are you sure you really want to quit SmartLinker?",
            self
        )
        stopDlg.yesButton.setText("Yes, I do")
        stopDlg.cancelButton.setText("Nah, forget about it")
        if stopDlg.exec():
            try: stopApp()
            except Exception as e: smartErrorNotify(self, "Oops! Something went wrong...", f"An error occured while attempting to close SmartLinker: {e}")

# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(smartConsoleScript())
    if len(sys.argv) > 1: appWindow = SmartSelectorGUI()
    else:
        appWindow = SmartLinkerGUI()
        appWindow.show()
    sys.exit(app.exec())