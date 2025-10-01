from utils.SmartUtils import *

myBrowsList = smart.loadBrowsers()

class MyBrowsersInterface(QWidget):
    """ Main class for the 'My Browsers' interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("My-Browsers")
        self.lightSheetOnDark: str = "SingleDirectionScrollArea {background: rgba(242, 242, 242, 0.05); border-radius: 10px; border: 1px solid rgba(242, 242, 242, 0.1)}"
        self.darkSheetOnLight: str = "SingleDirectionScrollArea {background: rgba(32, 32, 32, 0.05); border-radius: 10px; border: 1px solid rgba(32, 32, 32, 0.1)}"
        self.browsAddDlg = None
        self.browsEditDlg = None
        self.loadLinkDlg = None
        self.myBrowsCards = []

        mainBrowLayout = QVBoxLayout(self)
        mainBrowLayout.setContentsMargins(0, 20, 0, 0)
        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(40, 0, 0, 0)
        mainBrowLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("My Browsers", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainTitleLine.addWidget(self.title)
        mainBrowScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainBrowLayout.addWidget(mainBrowScroll)
        mainBrowScroll.setWidgetResizable(True)
        mainBrowScroll.setContentsMargins(0, 0, 0, 0)
        mainBrowScroll.enableTransparentBackground()
        mainBrowScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid #FFFFFF")
        mainBrowScrollContent = QWidget()
        mainBrowScroll.setWidget(mainBrowScrollContent)
        mainBrowScrollContent.setContentsMargins(40, 0, 40, 0)
        layout = QVBoxLayout(mainBrowScrollContent)
        layout.setSpacing(10)

        self.mybrowsSub = BodyLabel("The list below, named 'SmartList', contains all the web browsers installed on your system that you've been adding up to now.")
        self.mybrowsSub.setMaximumHeight(30)
        self.mybrowsSub.setWordWrap(True)
        layout.addWidget(self.mybrowsSub)
        self.mybrowsSub.setHidden(not myBrowsList["MyBrowsers"])
        self.addCommand = Action(FICO.ADD, "Add a browser", triggered=lambda: self.openNewBrowserDialog(parent))
        self.refreshCommand = Action(FICO.SYNC, "Refresh", triggered=lambda: self.refreshWrapper(parent))
        self.loadLinkCommand = Action(FICO.LINK, "Load a link", triggered=lambda: self.loadLinkDialog(parent))
        self.clearCommand = Action(FICO.DELETE.colored(QColor("red"), QColor("#F44336")), "Clear SmartList", triggered=lambda: self.confirmClearDialog(parent))
        self.clearCommand.setEnabled(bool(myBrowsList["MyBrowsers"]))
        self.myBrowsCommandBar = CommandBar()
        self.myBrowsCommandBar.setVisible(bool(cfg.get(cfg.showCommandBar)))
        self.myBrowsCommandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.myBrowsCommandBar.addAction(self.addCommand)
        self.myBrowsCommandBar.addSeparator()
        self.myBrowsCommandBar.addActions([self.refreshCommand, self.loadLinkCommand, self.clearCommand])
        self.mybrowsScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        layout.addWidget(self.mybrowsScroll)
        self.mybrowsScroll.setWidgetResizable(True)
        self.mybrowsScroll.setContentsMargins(0, 0, 0, 0)
        self.mybrowsScroll.setMaximumHeight(300)
        self.mybrowsScroll.setStyleSheet(self.lightSheetOnDark if theme() == Theme.DARK else self.darkSheetOnLight)
        mybrowsScrollContent = QWidget()
        self.mybrowsScroll.setWidget(mybrowsScrollContent)
        self.mybrowsLayout = QVBoxLayout(mybrowsScrollContent)
        self.mybrowsLayout.setSpacing(10)
        self.mybrowsEmptyMsg = BodyLabel("No web browsers have been added yet... Click on the 'Add a browser' button below to begin!")
        self.mybrowsEmptyMsg.setContentsMargins(0, 30, 0, 30)
        layout.addWidget(self.myBrowsCommandBar)
        self.mybrowsAddCard = PrimaryPushSettingCard(
            "Add a browser",
            FICO.ADD,
            "Add a browser to your SmartList",
            "For SmartLinker to really do its job, you need to add to the SmartList above the different browsers installed on your computer."
        )
        self.mybrowsAddCard.button.clicked.connect(lambda: self.openNewBrowserDialog(parent))
        layout.addWidget(self.mybrowsAddCard)
        self.mybrowsAddCard.setVisible(not cfg.get(cfg.showCommandBar))
        self.mybrowsRefreshCard = PushSettingCard(
            "Refresh",
            SegoeFontIcon.fromName("refresh"),
            "Refresh my SmartList",
            "If for any reason, you need to refresh the list of browsers above, this is the quickest way to proceed."
        )
        self.mybrowsRefreshCard.button.clicked.connect(lambda: self.refreshWrapper(parent))
        layout.addWidget(self.mybrowsRefreshCard)
        self.mybrowsRefreshCard.setVisible(not cfg.get(cfg.showCommandBar))
        self.mybrowsLoadLinkCard = PushSettingCard(
            "Load a link",
            SegoeFontIcon.fromName("link"),
            "Load a link into a browser",
            "For ease of access, you can directly load a URL into any browser of your choice from your SmartList."
        )
        self.mybrowsLoadLinkCard.button.clicked.connect(lambda: self.loadLinkDialog(parent))
        layout.addWidget(self.mybrowsLoadLinkCard)
        self.mybrowsLoadLinkCard.setVisible(bool(myBrowsList["MyBrowsers"] or (cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual))) and not cfg.get(cfg.showCommandBar))
        self.myBrowsClearCard = PushSettingCard(
            "Clear",
            FICO.DELETE.colored(QColor("red"), QColor("#F44336")),
            "Clear my SmartList",
            "If you really, really need to wipe your SmartList completely, this is the easiest way to proceed."
        )
        self.myBrowsClearCard.button.clicked.connect(lambda: self.confirmClearDialog(parent))
        layout.addWidget(self.myBrowsClearCard)
        self.myBrowsClearCard.setVisible(bool(myBrowsList["MyBrowsers"]) and not cfg.get(cfg.showCommandBar))
        self.actionCaption = BodyLabel("The following table gives you a descrption for every action in the bar above:")
        self.actionCaption.setContentsMargins(0, 20, 0, 0)
        layout.addWidget(self.actionCaption)
        self.actionCaption.setVisible(cfg.get(cfg.showCommandBar))
        self.actionListing = [
            ["Add a browser", "For SmartLinker to really do its job, you need to add to the list above the different browsers installed on your computer."],
            ["Refresh my SmartList", "If for any reason, you need to refresh the list of browsers above, this is the quickest way to proceed."],
            ["Load a link into a browser", "For ease of access, you can directly load a URL into any browser of your choice from your SmartList."],
            ["Clear my SmartList", "If you really, really need to wipe your SmartList completely, this is the easiest way to proceed."]
        ]
        self.actionTable = TableWidget()
        self.actionTable.setBorderVisible(True)
        self.actionTable.setBorderRadius(8)
        self.actionTable.setWordWrap(True)
        self.actionTable.setColumnCount(2)
        self.actionTable.setRowCount(len(self.actionListing))
        for row, actionItem in enumerate(self.actionListing):
            for col in range(2):
                self.actionTable.setItem(row, col, QTableWidgetItem(actionItem[col]))
        self.actionTable.setHorizontalHeaderLabels(["Action", "Description"])
        self.actionTable.resizeColumnsToContents()
        self.actionTable.setEnabled(False)
        self.actionTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.actionTableVH = self.actionTable.verticalHeader()
        self.actionTableVH.setHidden(True) if self.actionTableVH else None
        layout.addWidget(self.actionTable)
        self.actionTable.setVisible(cfg.get(cfg.showCommandBar))
        if myBrowsList["MyBrowsers"]: self.loadBrowsers(parent)
        else: self.mybrowsLayout.addWidget(self.mybrowsEmptyMsg, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        
        self.updateSnack = QWidget()
        self.updateSnack.setObjectName("BSnackBase")
        self.updateSnack.setStyleSheet(f"#BSnackBase {{background-color: rgba({smart.convertToRGB(themeColor().name())}, 0.25)}}")
        mainBrowLayout.addWidget(self.updateSnack)
        self.updateSnack.setVisible(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners))) 
        self.updateSnack.setEnabled(bool(cfg.get(cfg.updateAvailable) and cfg.get(cfg.showUpdateBanners))) 
        self.updateSnackLayout = QHBoxLayout(self.updateSnack)
        self.updateSnackLayout.setContentsMargins(20, 10, 20, 10)
        self.updateSnackIcon = IconWidget(FICO.IOT)
        self.updateSnackIcon.setFixedSize(32, 32)
        self.updateSnackLayout.setSpacing(20)
        self.updateSnackLayout.addWidget(self.updateSnackIcon)
        self.updateSnackLabel = StrongBodyLabel("A new update is available for download!")
        self.updateSnackLabel.setStyleSheet("background-color: transparent")
        self.updateSnackLayout.addWidget(self.updateSnackLabel)
        self.updateSnackLayout.addStretch(1)
        self.updateSnackButton = PrimaryPushButton(FICO.DOWNLOAD, "Download now")
        self.updateSnackLayout.addWidget(self.updateSnackButton)

    def loadBrowsers(self, parent):
        """ :MyBrowsersInterface: Saved browsers loader in the SmartList"""
        myBrowsList = smart.loadBrowsers()
        if myBrowsList["MyBrowsers"]:
            print("Loading browsers from database...")
            smart.managerLog("Loading browsers from database...")
            for browser in myBrowsList["MyBrowsers"]:
                bName = browser["name"]
                bPath = browser["path"]
                bCard = MyBrowsersCard(QIcon(smart.getFileIcon(bPath)), bName, bPath)
                bCard.editButton.setToolTip(f"Edit {bName}")
                bCard.editButton.installEventFilter(ToolTipFilter(bCard.editButton, showDelay=300, position=ToolTipPosition.TOP))
                bCard.deleteButton.setToolTip(f"Delete {bName} from my SmartList")
                bCard.deleteButton.installEventFilter(ToolTipFilter(bCard.deleteButton, showDelay=300, position=ToolTipPosition.TOP))
                bCard.editButton.clicked.connect(lambda checked, path=bPath, name=bName, parent=parent: self.openEditBrowserDialog(path, name, parent))
                bCard.deleteButton.clicked.connect(lambda checked, name=bName: self.confirmDeleteDialog(name, parent))
                bCard.openButton.clicked.connect(lambda checked, path=bPath, name=bName: self.launchBrowser(path, name, parent))
                self.mybrowsLayout.addWidget(bCard)
                self.myBrowsCards.append(bCard)
            print(f"{Fore.GREEN}Your browsers database has been successfully loaded!{Style.RESET_ALL}")
            smart.managerLog("SUCCESS: The browsers database has been succesfully loaded into the SmartList.")
            self.mybrowsEmptyMsg.setHidden(True)
            self.mybrowsSub.setHidden(False)
            if cfg.get(cfg.showCommandBar): self.loadLinkCommand.setEnabled(True)
            else: self.mybrowsLoadLinkCard.setHidden(False)
            if cfg.get(cfg.showCommandBar): self.clearCommand.setEnabled(True)
            else: self.myBrowsClearCard.setHidden(False)
        else:
            print(f"{Fore.YELLOW}Your browsers database is currently empty...{Style.RESET_ALL}")
            smart.managerLog("WARNING: The browsers database is currently empty...")
            self.mybrowsLayout.addWidget(self.mybrowsEmptyMsg, 0, Qt.AlignmentFlag.AlignCenter)
            self.mybrowsEmptyMsg.setHidden(False)
            self.mybrowsSub.setHidden(True)
            if cfg.get(cfg.showCommandBar): self.loadLinkCommand.setEnabled(False)
            else: self.mybrowsLoadLinkCard.setHidden(True)
            if cfg.get(cfg.showCommandBar): self.clearCommand.setEnabled(False)
            else: self.myBrowsClearCard.setHidden(True)

    def refreshBrowsers(self, parent):
        """ :MyBrowsersInterface: Refresh the SmartList without need to restart """
        print("Refreshing the SmartList...")
        smart.managerLog("Refreshing the SmartList...")
        while self.mybrowsLayout.count():
            item = self.mybrowsLayout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    self.mybrowsLayout.removeWidget(widget)
        print(f"{Fore.GREEN}All the browsers have been successfully removed!{Style.RESET_ALL}")
        smart.managerLog("SUCCESS: All the browsers have been successfully removed!")
        self.loadBrowsers(parent)
    
    def refreshWrapper(self, parent):
        self.refreshBrowsers(parent)
        smart.infoNotify("SmartList refreshed!", "Your SmartList has been successfully refreshed!", parent)

    def openNewBrowserDialog(self, parent):
        """ :MyBrowsersInterface: 'Add a new browser' dialog loader """
        if not self.browsAddDlg: self.browsAddDlg = NewBrowserDialog(parent)
        if self.browsAddDlg.exec():
            print(f"New browser name: {self.browsAddDlg.nameEdit.text()}")
            print(f"New browser path: {self.browsAddDlg.pathEdit.text()}")
            self.addNewBrowserToList(self.browsAddDlg.nameEdit.text(), self.browsAddDlg.pathEdit.text(), parent)
    
    def openEditBrowserDialog(self, path: str, name: str, parent):
        """ :MyBrowsersInterface: 'Edit a browser' dialog loader """
        if not self.browsEditDlg: self.browsEditDlg = EditBrowserDialog(path, name, parent)
        else:
            self.browsEditDlg = None
            self.browsEditDlg = EditBrowserDialog(path, name, parent)
        if self.browsEditDlg.exec():
            print(f"{Fore.GREEN}The changes have been successfully applied!{Style.RESET_ALL}\n" \
                  f"Browser name: {Fore.RED}{name}{Style.RESET_ALL} -> {Fore.GREEN}{self.browsEditDlg.nameEdit.text()}{Style.RESET_ALL}\n" \
                  f"Browser path: {Fore.RED}{path}{Style.RESET_ALL} -> {Fore.GREEN}{self.browsEditDlg.pathEdit.text()}{Style.RESET_ALL}")
            smart.managerLog("SUCCESS: Browser entry successfully updated\n" \
                     f"Browser name: {name} -> {self.browsEditDlg.nameEdit.text()}\n" \
                     f"Browser executable path: {path} -> {self.browsEditDlg.pathEdit.text()}")
            self.updateBrowserOfList(name, path, parent)

    def confirmDeleteDialog(self, name: str, parent):
        self.deleteDlg = MessageBox(
            f"Delete {name}",
            f"Do you really want to remove {name} from your SmartList?\n" \
                "This action is irreversible.",
            parent
        )
        self.deleteDlg.yesButton.setText("Delete")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if self.deleteDlg.exec():
            print(f"Prnding operation: Removing {name} from the SmartList...")
            smart.managerLog(f"Removing {name} from the SmartList...")
            myBrowsList = smart.loadBrowsers()
            baseCount = len(myBrowsList["MyBrowsers"])
            updatedList = {"MyBrowsers": [browser for browser in myBrowsList["MyBrowsers"] if browser["name"] != name]}
            # print(updatedList)
            if len(updatedList) == baseCount:
                print(f"{Fore.YELLOW}WARNING!! {name} cannot be found, failed to remove from your SmartList...{Style.RESET_ALL}")
                smart.managerLog(f"WARNING: {name} cannot be found, unable to proceed to its removal from the SmartList...")
                smart.warningNotify("Warning, be careful!", f"{name} cannot be found, failed to remove from your SmartList...", parent)
                return
            print("Saving the updated browsers database...")
            smart.managerLog(f"{name} has been removed. Updating the browsers database...")
            smart.writeBrowsers(updatedList)
            self.refreshBrowsers(parent)
            print(f"{Fore.GREEN}{name} has been successfully removed from your SmartList!{Style.RESET_ALL}")
            smart.managerLog(f"SUCCESS: {name} has been successfully removed from the SmartList.")
            smart.successNotify("Removal complete!", f"{name} has been successfully removed from your SmartList!", parent)

    def confirmClearDialog(self, parent):
        self.clearDlg = MessageBox(
            "Clear the SmartList",
            "By doing this, every single browser registered in your SmartList will be erased, " \
                "and this action is irreversible. Rest assured, these browsers will not be deleted from your storage, " \
                "and no sensitive data will be affected by this operation.\n\n" \
                "Do you really want to empty your SmartList?",
            parent
        )
        self.clearDlg.yesButton.setText("Clear my SmartList")
        if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
        if self.clearDlg.exec():
            print(f"{Fore.YELLOW}Waiting for the final confirmation to empty the SmartList...{Style.RESET_ALL}")
            smart.managerLog("WARNING: An attempt of clearing the SmartList has been initiated. Waiting for confirmation...")
            confirmClearDlg = MessageBox(
                "Confirm complete removal",
                "Before proceeding, please note that removing all your browsers from your SmartList " \
                    "is at YOUR OWN RISK, and you will have to start all over again if it is a mistake of yours.\n\n" \
                    "So continue only if you're 100% SURE and you know what you're doing!!",
                parent
            )
            confirmClearDlg.yesButton.setText("I'm 100% sure!")
            confirmClearDlg.cancelButton.setText("Nevermind...")
            if bool(cfg.get(cfg.enableSoundEffects) and cfg.get(cfg.questionSFXPath)): smart.playSound(soundStreamer, cfg.get(cfg.questionSFXPath), "confirmation dialog")
            if confirmClearDlg.exec():
                print(f"{Fore.GREEN}Confirmation granted!{Style.RESET_ALL}\nPending operation: Proceeding with complete removal...")
                smart.managerLog("WARNING: The confirmation has been granted. Proceeding with complete removal...")
                myBrowsList["MyBrowsers"] = []
                smart.writeBrowsers(myBrowsList)
                smart.successNotify("Clearing complete!", "Your SmartList has been successfully cleared!", parent)
                self.refreshBrowsers(parent)
                print(f"{Fore.GREEN}Your SmartList has been successfully cleared!{Style.RESET_ALL}")
                smart.managerLog("SUCCESS: The SmartList has been successfully cleared.")
            else:
                print(f"{Fore.BLUE}Confirmation denied! The operation has been cancelled.{Style.RESET_ALL}")
                smart.managerLog("INFO: The confirmation has been denied. The removal operation has been cancelled by the user.")

    def loadLinkDialog(self, parent):
        """ :MyBrowsersInterface: 'Load link' dialog loader """
        myBrowsList = smart.loadBrowsers()
        if not self.loadLinkDlg:
            self.loadLinkDlg = LoadLinkDialog(parent)
        if self.loadLinkDlg.exec():
            failedAttempts = 0
            if not self.loadLinkDlg.browserCombo.currentText() == "Other browser":
                print(f"Loading '{self.loadLinkDlg.linkEdit.text()}' into {self.loadLinkDlg.browserCombo.currentText()}...")
                smart.managerLog(f"Loading '{self.loadLinkDlg.linkEdit.text()}' into {self.loadLinkDlg.browserCombo.currentText()}...")
                for browser in myBrowsList["MyBrowsers"]:
                    if browser["name"] == self.loadLinkDlg.browserCombo.currentText():
                        if browser["path"]:
                            try:
                                subprocess.Popen([browser["path"], self.loadLinkDlg.linkEdit.text()])
                                print(f"{Fore.GREEN}'{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into {browser["name"]}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: '{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into {browser["name"]}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {browser["name"]}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to load {self.loadLinkDlg.linkEdit.text()} into {browser["name"]}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while loading '{self.loadLinkDlg.linkEdit.text()}' into {browser["name"]}: {e}")
                            break
                        else:
                            smart.warningNotify("Warning, be careful!", f"The path to {browser["name"]} as registered in your SmartList is empty...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The path to {browser["name"]} as registered in your SmartList is empty...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The path to {browser["name"]} as registered in the SmartList is empty...")
                            break
                    elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                        if os.path.basename(cfg.get(cfg.mainBrowserPath)) == self.loadLinkDlg.browserCombo.currentText():
                            try:
                                subprocess.Popen([cfg.get(cfg.mainBrowserPath), self.loadLinkDlg.linkEdit.text()])
                                print(f"{Fore.GREEN}'{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}!{Style.RESET_ALL}")
                                smart.managerLog(f"SUCCESS: '{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}.")
                            except Exception as e:
                                smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(cfg.get(cfg.mainBrowserPath))}: {e}", parent)
                                print(f"{Fore.RED}An error occured while attempting to load {self.loadLinkDlg.linkEdit.text()} into {cfg.get(cfg.mainBrowserPath)}: {e}{Style.RESET_ALL}")
                                smart.managerLog(f"ERROR: Failed while loading '{self.loadLinkDlg.linkEdit.text()}' into {cfg.get(cfg.mainBrowserPath)}: {e}")
                            break
                    else:
                        failedAttempts += 1
                        if failedAttempts == self.loadLinkDlg.browserCombo.count():
                            smart.warningNotify("Warning, be careful!", f"The name '{self.loadLinkDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.loadLinkDlg.browserCombo.currentText()} cannot be found in your SmartList...", parent)
                            print(f"{Fore.YELLOW}WARNING!! The name '{self.loadLinkDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.loadLinkDlg.browserCombo.currentText()} cannot be found in your SmartList...{Style.RESET_ALL}")
                            smart.managerLog(f"WARNING: The name '{self.loadLinkDlg.browserCombo.currentText()}' is not registered into the SmartList, or {self.loadLinkDlg.browserCombo.currentText()} cannot be found in the SmartList...")
            else:
                print(f"Loading '{self.loadLinkDlg.linkEdit.text()}' into {os.path.basename(self.loadLinkDlg.otherBrowsEdit.text())}...")
                smart.managerLog(f"Loading '{self.loadLinkDlg.linkEdit.text()}' into {os.path.basename(self.loadLinkDlg.otherBrowsEdit.text())}...")
                try:
                    subprocess.Popen([self.loadLinkDlg.otherBrowsEdit.text(), self.loadLinkDlg.linkEdit.text()])
                    print(f"{Fore.GREEN}'{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into another browser: '{self.loadLinkDlg.otherBrowsEdit.text()}'{Style.RESET_ALL}")
                    smart.managerLog(f"SUCCESS: '{self.loadLinkDlg.linkEdit.text()}' has been successfully loaded into other browser '{self.loadLinkDlg.otherBrowsEdit.text()}'")
                except Exception as e:
                    smart.errorNotify("Oops! Something went wrong...", f"An error occured while attempting to load your link into {os.path.basename(self.loadLinkDlg.otherBrowsEdit.text())}: {e}", parent)
                    print(f"{Fore.RED}An error occured while attempting to load {self.loadLinkDlg.linkEdit.text()} into '{os.path.basename(self.loadLinkDlg.otherBrowsEdit.text())}': {e}{Style.RESET_ALL}")
                    smart.managerLog(f"ERROR: Failed to load '{self.loadLinkDlg.linkEdit.text()}' into browser at path '{self.loadLinkDlg.otherBrowsEdit.text()}': {e}")

    def launchBrowser(self, path: str, name: str, parent):
        """ :MyBrowsersInterface: Specified browser execution handler """
        if os.path.exists(path):
            try:
                subprocess.Popen(path)
                print(f"{Fore.GREEN}Successfully launched {name} at path: '{path}'{Style.RESET_ALL}")
                smart.managerLog(f'SUCCESS: Launched {name} from path: "{path}"')
            except Exception as e:
                smart.errorNotify("Oops! Something went wrong...", f"An error occured while launching {name}:\n{e}", parent)
                print(f"{Fore.RED}An error occured while launching {name}: {e}{Style.RESET_ALL}")
                smart.managerLog(f"ERROR: Failed to launch {name}: {e}")
        else:
            smart.warningNotify("Warning, be careful!", f"The executable for {name} does not seem to exist at the known location anymore...", parent)
            print(f"{Fore.YELLOW}WARNING!! The executable for {name} cannot be found at the specified location... ({path}){Style.RESET_ALL}")
            smart.managerLog(f'WARNING: The executable for {name} cannot be found at the specified location: "{path}"')

    def addNewBrowserToList(self, name: str, path: str, parent):
        """ :MyBrowsersInterface: New browser adding function from 'Add a new browser' dialog
        Parameters
        ----------
        name: string
            The name of the provided browser
        path: string
            The complete path of the provided browser executable
        """
        print("Pending operation: Adding a new browser to the SmartList...\n" \
              f"Browser name: {name}\nBrowser complete path: {path}")
        smart.managerLog(f"Adding a new browser to the SmartList...\nBrowser name: {name}\nBrowser path: {path}")
        for browser in myBrowsList["MyBrowsers"]:
            if browser["exec"] == os.path.basename(path): smart.warningNotify(parent, "Warning, be careful!", f"The new browser has the same executable name as {browser["name"]}.\nIt is not really an issue, but it might be confusing for {SmartLinkerName}...")
        myBrowsList["MyBrowsers"].append({
            "name": name,
            "path": path,
            "exec": os.path.basename(path)
        })
        smart.writeBrowsers(myBrowsList)
        self.refreshBrowsers(parent)
        smart.successNotify("Adding complete!", f"{name} has been succesfully added to your SmartList!", parent)
        print(f"{Fore.GREEN}'{name}' has been successfully added to your SmartList!{Style.RESET_ALL}")
        smart.managerLog(f'SUCCESS: "{name}" has been successfully added to the SmartList.')

    def updateBrowserOfList(self, name: str, path: str, parent):
        """ :MyBrowsersInterface: Browser modifying function from 'Edit a browser' dialog
        Parameters
        ----------
        name: string
            The name of the provided browser
        path: string
            The complete path of the provided browser executable
        """
        if self.browsEditDlg:
            myBrowsList = smart.loadBrowsers()
            for browser in myBrowsList["MyBrowsers"]:
                if browser["name"] == name and browser["path"] == path:
                    browser["name"] = self.browsEditDlg.nameEdit.text()
                    browser["path"] = self.browsEditDlg.pathEdit.text()
                    browser["exec"] = os.path.basename(self.browsEditDlg.pathEdit.text())
                    break
            smart.writeBrowsers(myBrowsList)
            smart.successNotify("Update complete!", f"{name} has been successfully updated to {self.browsEditDlg.nameEdit.text()}!", parent)
            self.refreshBrowsers(parent)

class NewBrowserDialog(MessageBoxBase):
    """ Class for the 'Add a new browser' dialog box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = SubtitleLabel("Add a new browser", self)
        self.iconLine = QHBoxLayout()
        self.iconLine.setContentsMargins(0, 10, 0, 10)
        self.iconLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon = IconWidget(FICO.ADD_TO)
        self.icon.setFixedSize(64, 64)
        self.addBlock = False

        self.pathRow = QHBoxLayout()
        self.pathEdit = LineEdit()
        self.pathEdit.setClearButtonEnabled(True)
        self.pathEdit.setPlaceholderText("The path must end with '.exe'")
        self.pathEdit.textChanged.connect(self.pathChangeListener)
        self.browseBtn = ToolButton(FICO.FOLDER)
        self.browseBtn.setToolTip("Browse...")
        self.browseBtn.installEventFilter(ToolTipFilter(self.browseBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.browseBtn.clicked.connect(self.browseDialog)

        self.pathWarningLabel = CaptionLabel("")
        self.pathWarningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))

        self.nameEdit = LineEdit()
        self.nameEdit.setClearButtonEnabled(True)
        self.nameEdit.setPlaceholderText("Browser name")
        self.nameEdit.textChanged.connect(lambda: self.nameWarningLabel.setHidden(True))
        self.nameEdit.setEnabled(False)

        self.nameWarningLabel = CaptionLabel("")
        self.nameWarningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))

        self.viewLayout.addWidget(self.title)
        self.viewLayout.addLayout(self.iconLine)
        self.iconLine.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addLayout(self.pathRow)
        self.pathRow.addWidget(self.pathEdit)
        self.pathRow.addWidget(self.browseBtn)
        self.viewLayout.addWidget(self.pathWarningLabel)
        self.pathWarningLabel.setHidden(True)
        self.viewLayout.addWidget(self.nameEdit)
        self.viewLayout.addWidget(self.nameWarningLabel)
        self.nameWarningLabel.setHidden(True)

        self.widget.setMinimumWidth(400)
        self.yesButton.setText("Add to SmartList")

    def browseDialog(self):
        """ :NewBrowserDialog: Provide a browser executable through file picker dialog """
        self.pathEdit.setText(smart.browseFileDialog(self, "Select a browser executable", "", "Executables (*.exe)").replace("/", "\\"))

    def pathChangeListener(self, text: str):
        """ :NewBrowserDialog: Make actions whenever the path entry content is changed """
        myBrowsList = smart.loadBrowsers()
        for browser in myBrowsList["MyBrowsers"]:
            if browser["path"] == text:
                self.addBlock = True
                break
            else:
                self.addBlock = False
                self.pathWarningLabel.setHidden(True)
        self.updateIcon(text)
        self.updateBrowserName(text)

    def updateBrowserName(self, text):
        if text.lower().endswith(".exe"):
            if os.path.exists(text):
                self.nameEdit.setEnabled(True)
                """ productName = ""
                try:
                    info = win32api.GetFileVersionInfo(text, '\\')
                    # Extract ProductName from the version info dictionary
                    for block in info:
                        if isinstance(info[block], dict) and 'ProductName' in info[block]:
                            productName = info[block]['ProductName']
                            break
                    # print(productName)
                    self.nameEdit.setText(productName)
                except Exception as e: print(e) """
            else:
                self.nameEdit.setText("")
                self.nameEdit.setEnabled(False)
                self.nameWarningLabel.setHidden(True)
        else:
            self.nameEdit.setText("")
            self.nameEdit.setEnabled(False)
            self.nameWarningLabel.setHidden(True)

    def updateIcon(self, text):
        """ :NewBrowserDialog: Provide the specified executable icon """
        if text.lower().endswith(".exe"):
            if os.path.exists(text):
                self.icon.setIcon(QIcon(smart.getFileIcon(text)))
            else: self.icon.setIcon(FICO.ADD_TO)
        else: self.icon.setIcon(FICO.ADD_TO)
        
    def validate(self) -> bool:
        path = self.pathEdit.text()
        if path.lower().endswith(".exe"):
            if os.path.exists(path):
                if not self.addBlock:
                    if not self.nameEdit.text() == "":
                        return True
                    else:
                        self.nameWarningLabel.setText("The browser name cannot be empty. Try again.")
                        self.nameWarningLabel.setHidden(False)
                        return False
                else:
                    self.pathWarningLabel.setText("This browser already exists in your SmartList.")
                    self.pathWarningLabel.setHidden(False)
                    return False
            else:
                self.pathWarningLabel.setText("The current path does not exist. Try again.")
                self.pathWarningLabel.setHidden(False)
                return False
        else:
            self.pathWarningLabel.setText("The current path is not an executable. Try again.")
            self.pathWarningLabel.setHidden(False)
            return False

class EditBrowserDialog(MessageBoxBase):
    """ Class for the 'Add a new browser' dialog box """

    def __init__(self, path: str, name: str, parent=None):
        super().__init__(parent)
        self.title = SubtitleLabel(f"Edit {name}", self)
        self.iconLine = QHBoxLayout()
        self.iconLine.setContentsMargins(0, 10, 0, 10)
        self.iconLine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon = IconWidget(smart.getFileIcon(path))
        self.icon.setFixedSize(64, 64)
        self.addBlock = False
        self.addNBlock = False

        self.pathRow = QHBoxLayout()
        self.pathEdit = LineEdit()
        self.pathEdit.setText(path)
        self.pathEdit.setClearButtonEnabled(True)
        self.pathEdit.setPlaceholderText("The path must end with '.exe'")
        self.pathEdit.textChanged.connect(self.pathChangeListener)
        self.browseBtn = ToolButton(FICO.FOLDER)
        self.browseBtn.setToolTip("Browse...")
        self.browseBtn.installEventFilter(ToolTipFilter(self.browseBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.browseBtn.clicked.connect(self.browseDialog)

        self.pathWarningLabel = CaptionLabel("")
        self.pathWarningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))

        self.nameEdit = LineEdit()
        self.nameEdit.setText(name)
        self.nameEdit.setClearButtonEnabled(True)
        self.nameEdit.setPlaceholderText("Browser name")
        self.nameEdit.textChanged.connect(self.nameChangeListener)

        self.nameWarningLabel = CaptionLabel("")
        self.nameWarningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))

        self.viewLayout.addWidget(self.title)
        self.viewLayout.addLayout(self.iconLine)
        self.iconLine.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addLayout(self.pathRow)
        self.pathRow.addWidget(self.pathEdit)
        self.pathRow.addWidget(self.browseBtn)
        self.viewLayout.addWidget(self.pathWarningLabel)
        self.pathWarningLabel.setHidden(True)
        self.viewLayout.addWidget(self.nameEdit)
        self.viewLayout.addWidget(self.nameWarningLabel)
        self.nameWarningLabel.setHidden(True)

        self.widget.setMinimumWidth(400)
        self.yesButton.setText("Confirm edition")

    def browseDialog(self):
        """ :EditBrowserDialog: Provide a browser executable through file picker dialog """
        self.pathEdit.setText(smart.browseFileDialog(self, "Select a browser executable", "", "Executables (*.exe)"))

    def pathChangeListener(self, text):
        """ :EditBrowserDialog: Make actions whenever the path entry content is changed """
        myBrowsList = smart.loadBrowsers()
        for browser in myBrowsList["MyBrowsers"]:
            if browser["path"] == text:
                self.addBlock = True
                break
            else:
                self.addBlock = False
                self.pathWarningLabel.setHidden(True)
        self.updateIcon(text)
        self.updateBrowserName(text)
    
    def nameChangeListener(self, text):
        """ :EditBrowserDialog: Make actions whenever the name entry content is changed """
        myBrowsList = smart.loadBrowsers()
        for browser in myBrowsList["MyBrowsers"]:
            if browser["name"] == text:
                self.addNBlock = True
                break
            else:
                self.addNBlock = False
                self.nameWarningLabel.setHidden(True)

    def updateIcon(self, text):
        """ :EditBrowserDialog: Provide the specified executable icon """
        if text.lower().endswith(".exe"):
            if os.path.exists(text):
                self.icon.setIcon(QIcon(smart.getFileIcon(text)))
            else: self.icon.setIcon(FICO.EDIT)
        else: self.icon.setIcon(FICO.EDIT)
    
    def updateBrowserName(self, text):
        if text.lower().endswith(".exe"):
            if os.path.exists(text):
                self.nameEdit.setEnabled(True)
                """ productName = ""
                try:
                    info = win32api.GetFileVersionInfo(text, '\\')
                    # Extract ProductName from the version info dictionary
                    for block in info:
                        if isinstance(info[block], dict) and 'ProductName' in info[block]:
                            productName = info[block]['ProductName']
                            break
                    # print(productName)
                    self.nameEdit.setText(productName)
                except Exception as e: print(e) """
            else:
                self.nameEdit.setText("")
                self.nameEdit.setEnabled(False)
                self.nameWarningLabel.setHidden(True)
        else:
            self.nameEdit.setText("")
            self.nameEdit.setEnabled(False)
            self.nameWarningLabel.setHidden(True)
    
    def validate(self) -> bool:
        path = self.pathEdit.text()
        if path.lower().endswith(".exe"):
            if os.path.exists(path):
                if not self.addBlock:
                    if not self.nameEdit.text() == "":
                        if not self.addNBlock:
                            return True
                        else:
                            self.nameWarningLabel.setText("This browser name already exists in your SmartList.")
                            self.nameWarningLabel.setHidden(False)
                            return False
                    else:
                        self.nameWarningLabel.setText("The browser name cannot be empty. Try again.")
                        self.nameWarningLabel.setHidden(False)
                        return False
                else:
                    self.pathWarningLabel.setText("This browser already exists in your SmartList.")
                    self.pathWarningLabel.setHidden(False)
                    return False
            else:
                self.pathWarningLabel.setText("The current path does not exist. Try again.")
                self.pathWarningLabel.setHidden(False)
                return False
        else:
            self.pathWarningLabel.setText("The current path is not an executable. Try again.")
            self.pathWarningLabel.setHidden(False)
            return False

class MyBrowsersCard(CardWidget):
    """ Class for the SmartList's saved browsers cards """

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.openButton = PushButton(FICO.LINK, 'Launch', self)
        self.editButton = ToolButton(FICO.EDIT, self)
        self.deleteButton = ToolButton(FICO.DELETE.colored(QColor("red"), QColor("#F44336")), self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(36, 36)
        self.contentLabel.setTextColor(QColor("#606060"), QColor("#d2d2d2"))
        self.openButton.setFixedWidth(120)

        self.hBoxLayout.setContentsMargins(20, 11, 15, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addWidget(self.editButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addWidget(self.deleteButton, 0, Qt.AlignmentFlag.AlignRight)
    
class LoadLinkDialog(MessageBoxBase):
    """ Class for the 'Open with link' dialog box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("Load link into a browser", self)
        self.browsIcon = IconWidget(FICO.LINK)
        self.otherBrowsLine = QHBoxLayout()
        self.otherBrowsEdit = LineEdit()
        self.otherBrowsBrowse = ToolButton(FICO.FOLDER)
        self.linkEdit = LineEdit(self)

        self.browsIcon.setFixedSize(64, 64)
        self.browserCombo = ComboBox()
        self.browserCombo.setPlaceholderText("Select a SmartList browser")
        for browser in myBrowsList["MyBrowsers"]:
            self.browserCombo.addItem(browser["name"], smart.getFileIcon(browser["path"]))
        if cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
            self.browserCombo.addItem(os.path.basename(cfg.get(cfg.mainBrowserPath)), smart.getFileIcon(cfg.get(cfg.mainBrowserPath)))
        self.browserCombo.addItem("Other browser", FICO.APPLICATION)
        if not self.browserCombo.currentText() == "Other browser":
            for browser in myBrowsList["MyBrowsers"]:
                if browser["name"] == self.browserCombo.currentText():
                    self.browsIcon.setIcon(smart.getFileIcon(browser["path"]))
                    break
                else: self.browsIcon.setIcon(FICO.LINK)
        else: self.browsIcon.setIcon(FICO.APPLICATION)
        self.otherBrowsLine.setSpacing(10)
        self.otherBrowsEdit.setVisible(self.browserCombo.currentText() == "Other browser")
        self.otherBrowsEdit.setClearButtonEnabled(True)
        self.otherBrowsEdit.setPlaceholderText("Other browser path")
        self.otherBrowsBrowse.setVisible(self.browserCombo.currentText() == "Other browser")
        self.otherBrowsBrowse.setToolTip("Browse...")
        self.otherBrowsBrowse.installEventFilter(ToolTipFilter(self.otherBrowsBrowse))

        self.linkEdit.setPlaceholderText('Enter the URL of a file or website')
        self.linkEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor(QColor("#cf1010"), QColor(255, 28, 32))
        self.otherBrowsLine.addWidget(self.otherBrowsEdit)
        self.otherBrowsLine.addWidget(self.otherBrowsBrowse)

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.browsIcon, 0, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addWidget(self.browserCombo)
        self.viewLayout.addLayout(self.otherBrowsLine)
        self.viewLayout.addWidget(self.linkEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.setHidden(True)

        self.widget.setMinimumWidth(350)
        self.yesButton.setText("Load link")
        self.browserCombo.currentTextChanged.connect(lambda text: self.comboChangeListener(text))
        self.otherBrowsEdit.textChanged.connect(lambda text: self.otherPathChangeListener(text))
        self.otherBrowsBrowse.clicked.connect(lambda: self.otherBrowsEdit.setText(smart.browseFileDialog(parent, "Select another browser to load the link", "", "Executables (*.exe)")))
        self.linkEdit.textChanged.connect(lambda: self.warningLabel.setHidden(True))

    def comboChangeListener(self, text):
        """ :LoadLink: Make actions whenever the current text of the combo is changed """
        if self.browserCombo.count() > 0:
            if not text == "Other browser":
                self.otherBrowsEdit.setHidden(True)
                self.otherBrowsBrowse.setHidden(True)
                for browser in myBrowsList["MyBrowsers"]:
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
        """ :LoadLink: Make actions whenever the path entry content is changed """
        if self.browserCombo.currentIndex() == self.browserCombo.count() - 1:
            if text and os.path.exists(text): self.browsIcon.setIcon(smart.getFileIcon(text))
            else: self.browsIcon.setIcon(FICO.APPLICATION)

    def validate(self):
        if self.linkEdit.text():
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
        else:
            self.warningLabel.setText("You must enter a URL to a file or a website.")
            self.warningLabel.setHidden(False)
            return False
