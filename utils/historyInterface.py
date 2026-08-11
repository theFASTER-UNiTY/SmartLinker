from utils.SmartUtils import *

# =================================================================================================

myHistory = smart.loadHistory()

class HistoryInterface(QWidget):
    """ Main class for the "History" interface """
    itemSelected = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setObjectName("My-History")
        self.historyCards: list[TimestampHistoryCard] = []
        self.selectedItems: list = []
        self.loadInBrowserDlg = None
        self.myBrowsList = smart.loadBrowsers()

        self.opacityEffect = QGraphicsOpacityEffect()
        self.opacityEffect.setOpacity(0.5)

        mainHistLayout = QVBoxLayout(self)
        mainHistLayout.setContentsMargins(0, 20, 0, 0)
        mainHistLayout.setSpacing(20)

        mainTitleLine = QHBoxLayout()
        mainTitleLine.setContentsMargins(40, 0, 40, 0)
        mainTitleLine.setSpacing(15)
        mainHistLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("My History", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.refreshBtn = ToolButton(segFont.fromName("Refresh"))
        self.refreshBtn.setToolTip("Refresh history")
        self.refreshBtn.installEventFilter(ToolTipFilter(self.refreshBtn))
        self.searchBar = SearchLineEdit(self)
        self.searchBar.setPlaceholderText("Search from your history")
        self.searchBar.setEnabled(bool(myHistory["MyHistory"]))
        mainTitleLine.addWidget(self.title)
        mainTitleLine.addStretch(1)
        mainTitleLine.addWidget(self.refreshBtn)
        mainTitleLine.addWidget(self.searchBar, 1)

        mainActionsLine = QHBoxLayout()
        mainActionsLine.setContentsMargins(40, 0, 40, 0)
        mainActionsLine.setSpacing(15)
        mainActionsLine.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        mainActionsGrid = QGridLayout()
        mainActionsGrid.setContentsMargins(40, 0, 40, 0)
        mainActionsGrid.setSpacing(10)
        mainActionsGrid.setColumnStretch(0, 1)
        mainActionsGrid.setColumnStretch(1, 1)
        mainActionsGrid.setColumnStretch(2, 1)
        mainActionsGrid.setColumnStretch(3, 1)
        mainHistLayout.addLayout(mainActionsGrid)
        self.loadMenu = RoundMenu("Load link", self)
        self.loadMenu.addAction(Action(FICO.GLOBE, "Load in registered browser", triggered=lambda: self.loadSelectedLink(self.selectedItems[0], False, parent)))
        self.loadMenu.addAction(Action(FICO.APPLICATION, "Load in custom browser...", triggered=lambda: self.loadSelectedLink(self.selectedItems[0], True, parent)))
        self.loadLinkBtn = PrimaryDropDownPushButton(FICO.LINK, "Load...", self)
        self.loadLinkBtn.setMenu(self.loadMenu)
        self.loadLinkBtn.setEnabled(False)
        self.copyBtn = PushButton(FICO.COPY, "Copy", self)
        self.copyBtn.setEnabled(False)
        self.bookmarkBtn = PushButton(segFont.fromName("FavoriteStar"), "Add to SmartCuts", self)
        self.bookmarkBtn.setEnabled(False)
        self.moreResultsBtn = PushButton(FICO.SEARCH, "More results", self)
        self.moreResultsBtn.setEnabled(False)
        self.deleteBtn = PrimaryPushButton(FICO.DELETE, "Delete", self) # "Delete ({n})" pour n = nbre de liens sélectionnés
        self.deleteBtn.setEnabled(False)
        self.selectAllBtn = PushButton(segFont.fromName("SelectAll"), "Select all", self)
        self.selectAllBtn.setEnabled(bool(myHistory["MyHistory"]))
        self.deselectAllBtn = PushButton(FICO.CLEAR_SELECTION, "Deselect all", self)
        self.deselectAllBtn.setEnabled(False)
        self.clearBtn = PushButton(
            segFont.fromName("ClearAllInk").colored(
                QColor("red"), QColor("#F44336")
            ),
            "Clear history",
            self
        )
        self.clearBtn.setEnabled(bool(myHistory["MyHistory"]))
        mainActionsGrid.addWidget(self.loadLinkBtn, 0, 0)
        mainActionsGrid.addWidget(self.copyBtn, 0, 1)
        mainActionsGrid.addWidget(self.bookmarkBtn, 0, 2)
        mainActionsGrid.addWidget(self.moreResultsBtn, 0, 3)
        mainActionsGrid.addWidget(self.selectAllBtn, 1, 0)
        mainActionsGrid.addWidget(self.deselectAllBtn, 1, 1)
        mainActionsGrid.addWidget(self.deleteBtn, 1, 2)
        mainActionsGrid.addWidget(self.clearBtn, 1, 3)

        self.refreshBtn.clicked.connect(self.refreshHistory)

        mainHistScroll = SingleDirectionScrollArea(self)
        mainHistLayout.addWidget(mainHistScroll)
        mainHistScroll.setWidgetResizable(True)
        mainHistScroll.setContentsMargins(0, 0, 40, 0)
        mainHistScroll.enableTransparentBackground()
        mainHistScrollContent = QWidget()
        mainHistScroll.setWidget(mainHistScrollContent)
        mainHistScrollContent.setContentsMargins(40, 0, 40, 0)
        mainHistScrollContent.setStyleSheet("background: transparent")

        self.mainLayout = QVBoxLayout(mainHistScrollContent)
        self.mainLayout.setContentsMargins(0, 0, 0, 10)
        self.mainLayout.setSpacing(10)

        self.emptyState = QWidget()
        self.emptyState.setContentsMargins(0, 0, 0, 0)
        self.emptyState.setGraphicsEffect(self.opacityEffect)
        self.emptyState.setVisible(not myHistory["MyHistory"])
        self.emptyStateBox = QVBoxLayout(self.emptyState)
        self.emptyStateBox.setContentsMargins(0, 0, 0, 0)
        self.emptyStateBox.setSpacing(15)
        self.emptyStateIcon = IconWidget(FICO.HISTORY, self)
        self.emptyStateIcon.setFixedSize(128, 128)
        self.emptyStateTitle = TitleLabel("No history entries yet", self)
        self.emptyStateContent = CaptionLabel(
            "Every link you will load into a browser from your SmartList or " \
            "through the Smart Selector will be saved here.",
            self
        )

        self.searchBar.textChanged.connect(self.onSearchBarTextChanged)
        self.copyBtn.clicked.connect(lambda: self.copySelectedLinks(parent))
        self.moreResultsBtn.clicked.connect(lambda: self.moreResultsSelectedLink(parent))
        self.selectAllBtn.clicked.connect(self.selectAllItems)
        self.deselectAllBtn.clicked.connect(self.deselectAllItems)
        self.deleteBtn.clicked.connect(lambda: self.deleteSelectedItems(parent))
        self.clearBtn.clicked.connect(lambda: self.clearHistory(parent))

        self.emptyStateBox.addWidget(self.emptyStateIcon, 0, Qt.AlignmentFlag.AlignCenter)
        self.emptyStateBox.addWidget(self.emptyStateTitle, 0, Qt.AlignmentFlag.AlignCenter)
        self.emptyStateBox.addWidget(self.emptyStateContent, 0, Qt.AlignmentFlag.AlignCenter)

        if not myHistory["MyHistory"]:
            self.mainLayout.addStretch()
            self.mainLayout.addWidget(self.emptyState)
        else:
            self.loadHistoryCards(self.historyCards)

        self.mainLayout.addStretch()

        self.updateSnack = UpdateSnack("HSnackBase", self)
        self.updateSnack.setStyleSheet(f"#HSnackBase {{background-color: rgba({smart.convertToRGB(themeColor())}, 0.25)}}")
        mainHistLayout.addWidget(self.updateSnack)

    def loadHistoryCards(self, cards: list["TimestampHistoryCard"], history: dict[str, list[dict[str, typing.Any]]] | None = None):
        cards.clear()
        if history is None:
            history = myHistory["MyHistory"]

        for dateKey, entries in sorted(history.items(), reverse=True):
            dateObj = datetime.datetime.strptime(dateKey, "%Y-%m-%d").date()
            d = dateObj.fromisoformat(dateKey)
            histCard = TimestampHistoryCard(
                d.strftime("%A, %d %B %Y"),
                entries,
                self
            )
            cards.append(histCard)
            histCard.historyTable.itemSelectionChanged.connect(
                lambda table=histCard.historyTable: self.onHistoryTableSelectionChanged()
            )
            self.mainLayout.addWidget(histCard)

    def refreshHistory(self):
        smart.emptyLayout(self.mainLayout, True)
        self.historyCards.clear()
        myHistory = smart.loadHistory()

        if not myHistory["MyHistory"]:
            self.emptyState.setVisible(True)
            self.mainLayout.addStretch()
            self.mainLayout.addWidget(self.emptyState)
        else:
            self.emptyState.setVisible(False)
            self.loadHistoryCards(self.historyCards)

    def updateUiAtSelection(self, items: list):
        # print(f"Items ({len(items)}): {items}")
        self.loadLinkBtn.setEnabled(len(items) == 1)
        self.copyBtn.setEnabled(bool(items))
        self.bookmarkBtn.setEnabled(bool(items))
        self.moreResultsBtn.setEnabled(len(items) == 1)
        self.selectAllBtn.setEnabled(bool(self.getTotalItemsCount()) and len(items) < self.getTotalItemsCount())
        self.deselectAllBtn.setEnabled(bool(items))
        self.deleteBtn.setEnabled(bool(items))

    def onHistoryTableSelectionChanged(self):
        self.selectedItems = self.getSelectedItemsFromAllTables()
        self.updateUiAtSelection(self.selectedItems)

    def getSelectedItemsFromAllTables(self) -> list:
        selectedItems = []
        for card in self.historyCards:
            for modelIndex in card.historyTable.selectionModel().selectedRows(): # type: ignore
                row = modelIndex.row()
                rowItems = [card.historyTable.item(row, col) for col in range(card.historyTable.columnCount())]
                selectedItems.append((card, rowItems))
        return selectedItems

    def getTotalSelectionCount(self) -> int:
        selectedCount = 0
        for card in self.historyCards:
            selectedCount += len(card.historyTable.selectionModel().selectedRows()) # type: ignore
        return selectedCount

    def getTotalItemsCount(self) -> int:
        totalCount = 0
        for card in self.historyCards:
            totalCount += card.historyTable.rowCount()
        return totalCount

    def getFilteredHistory(self, text: str) -> dict[str, list[dict[str, typing.Any]]]:
        if not text:
            return myHistory["MyHistory"]

        needle = text.strip().lower()
        filtered: dict[str, list[dict[str, typing.Any]]] = {}

        for dateKey, entries in myHistory["MyHistory"].items():
            matchingEntries = []
            for entry in entries:
                browser = str(entry.get("browser", "")).lower()
                address = str(entry.get("address", "")).lower()

                if needle in browser or needle in address:
                    matchingEntries.append(entry)

            if matchingEntries:
                filtered[dateKey] = matchingEntries

        return filtered

    def onSearchBarTextChanged(self, text: str):
        self.refreshBtn.setEnabled(not text)
        self.deselectAllItems()
        smart.emptyLayout(self.mainLayout, True)
        self.historyCards.clear()

        filteredHistory = self.getFilteredHistory(text)
        if not filteredHistory:
            self.mainLayout.addStretch()
            self.mainLayout.addWidget(self.emptyState)
            self.emptyState.setVisible(True)
        else:
            self.emptyState.setVisible(False)
            self.loadHistoryCards(self.historyCards, filteredHistory)
        self.mainLayout.addStretch()
        
        for card in self.historyCards:
            for row in range(card.historyTable.rowCount()):
                matchFound = False
                for col in range(card.historyTable.columnCount()):
                    item = card.historyTable.item(row, col)
                    if item and text.lower() in item.text().lower():
                        matchFound = True
                        break
                card.historyTable.setRowHidden(row, not matchFound)

    def loadSelectedLink(self, item: tuple["TimestampHistoryCard", list[QTableWidgetItem]], customBrowser: bool, parent):
        from utils.aboutInterface import BrowserSelectDialog

        link = item[1][2].text() if item[1][2] else ""

        if customBrowser:
            self.myBrowsList = smart.loadBrowsers()
            if self.loadInBrowserDlg:
                self.loadInBrowserDlg = None
            self.loadInBrowserDlg = BrowserSelectDialog(
                "Load selected link with...",
                FICO.GLOBE, False, parent
            )
            self.loadInBrowserDlg.yesButton.setText("Load link")

            if self.loadInBrowserDlg.exec():
                failedAttempts = 0
                if not self.loadInBrowserDlg.browserCombo.currentText() == "Other browser":
                    RichCLI.log(f"[blue][b u]OPERATION[/b u]: Opening the link [i]'{link}'[/i] into {self.loadInBrowserDlg.browserCombo.currentText()}...[/]")
                    smart.managerLog(f"Opening the link '{link}' into {self.loadInBrowserDlg.browserCombo.currentText()}...")
                    for browser in self.myBrowsList["MyBrowsers"]:
                        if browser["name"] == self.loadInBrowserDlg.browserCombo.currentText():
                            if browser["path"]:
                                try:
                                    subprocess.Popen([browser["path"], link])
                                    RichCLI.log(f"[green][b u]SUCCESS[/b u]: The link [i]'{link}'[/i] has been successfully loaded into {browser["name"]}![/]")
                                    smart.managerLog(f"SUCCESS: The link '{link}' has been successfully loaded into {browser["name"]}.")
                                except Exception as e:
                                    smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to open the link [i]'{link}'[/i] into {browser["name"]}:\n{e}", parent)
                                    RichCLI.log(f"[red][b u]ERROR[/b u]: Failed while opening the link [i]'{link}'[/i] into {browser["name"]}:\n\t[i]{e}[/]")
                                break
                            else:
                                smart.warningNotify("Warning, be careful!", f"The path to {browser["name"]} as registered in your SmartList is empty...", parent)
                                RichCLI.log(f"[yellow][b u]WARNING[/b u]: The path to [b]{browser["name"]}[/b] as registered in your SmartList is empty...[/]")
                                smart.managerLog(f"WARNING: The path to {browser["name"]} as registered in the SmartList is empty...")
                                break

                        elif cfg.get(cfg.mainBrowserPath) and cfg.get(cfg.mainBrowserIsManual):
                            if os.path.basename(cfg.get(cfg.mainBrowserPath)) == self.loadInBrowserDlg.browserCombo.currentText():
                                try:
                                    subprocess.Popen([cfg.get(cfg.mainBrowserPath), link])
                                    RichCLI.log(f"[green][b u]SUCCESS[/b u]: The link [i]'{link}'[/i] has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}![/]")
                                    smart.managerLog(f"SUCCESS: The link '{link}' has been successfully loaded into {cfg.get(cfg.mainBrowserPath)}.")
                                except Exception as e:
                                    smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to open the link [i]'{link}'[/i] into {os.path.basename(cfg.get(cfg.mainBrowserPath))}:\n{e}", parent)
                                    RichCLI.log(f"[red][b u]ERROR[/b u]: Failed while opening the link [i]'{link}'[/i] into {cfg.get(cfg.mainBrowserPath)}:\n\t[i]{e}[/]")
                                    smart.managerLog(f"ERROR: Failed while opening the link '{link}' into {cfg.get(cfg.mainBrowserPath)}: {e}")
                                break

                        else:
                            failedAttempts += 1
                            if failedAttempts == self.loadInBrowserDlg.browserCombo.count():
                                smart.warningNotify("Warning, be careful!", f"The name '{self.loadInBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.loadInBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...", parent)
                                RichCLI.log(f"[yellow][b u]WARNING[/b u]: The name '{self.loadInBrowserDlg.browserCombo.currentText()}' is not registered into your SmartList, or {self.loadInBrowserDlg.browserCombo.currentText()} cannot be found in your SmartList...[/]")
                                smart.managerLog(f"WARNING: The name '{self.loadInBrowserDlg.browserCombo.currentText()}' is not registered into the SmartList, or {self.loadInBrowserDlg.browserCombo.currentText()} cannot be found in the SmartList...")

                else:
                    RichCLI.log(f"[blue][b u]OPERATION[/b u]: Opening the link [i]'{link}'[/i] into {os.path.basename(self.loadInBrowserDlg.otherBrowsEdit.text())}...[/]")
                    smart.managerLog(f"Opening the link '{link}' into {os.path.basename(self.loadInBrowserDlg.otherBrowsEdit.text())}...")
                    try:
                        subprocess.Popen([self.loadInBrowserDlg.otherBrowsEdit.text(), link])
                        RichCLI.log(f"[green][b u]SUCCESS[/b u]: The link [i]'{link}'[/i] has been successfully loaded into another browser: '{self.loadInBrowserDlg.otherBrowsEdit.text()}'[/]")
                        smart.managerLog(f"SUCCESS: The link '{link}' has been successfully loaded into other browser '{self.loadInBrowserDlg.otherBrowsEdit.text()}'")
                    except Exception as e:
                        smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to open the link [i]'{link}'[/i] into {os.path.basename(self.loadInBrowserDlg.otherBrowsEdit.text())}:\n{e}", parent)
                        RichCLI.log(f"[red][b u]ERROR[/b u]: An error occured while attempting to open the link [i]'{link}'[/i] into '{os.path.basename(self.loadInBrowserDlg.otherBrowsEdit.text())}':\n\t[i]{e}[/]")
                        smart.managerLog(f"ERROR: Failed to open the link '{link}' into browser at path '{self.loadInBrowserDlg.otherBrowsEdit.text()}': {e}")

        else:
            regBrowser = item[1][1].text()

            RichCLI.log(f"[blue][b u]OPERATION[/b u]: Opening the link [i]'{link}'[/i] into [b]{regBrowser}[/b]...[/]")
            smart.managerLog(f"Opening the link '{link}' into [b]{regBrowser}[/b]...")
            try:
                for browser in self.myBrowsList["MyBrowsers"]:
                    if browser["name"] == regBrowser:
                        if browser["path"]:
                            subprocess.Popen([browser["path"], link])
                            RichCLI.log(f"[green][b u]SUCCESS[/b u]: The link [i]'{link}'[/i] has been successfully loaded into [b]{regBrowser}[/b]![/]")
                            smart.managerLog(f"SUCCESS: The link '{link}' has been successfully loaded into {regBrowser}.")
                        else:
                            smart.warningNotify("Warning, be careful!", f"The path to {regBrowser} as registered in your SmartList is empty...", parent)
                            RichCLI.log(f"[yellow][b u]WARNING[/b u]: The path to [b]{regBrowser}[/b] as registered in your SmartList is empty...[/]")
                            smart.managerLog(f"WARNING: The path to {regBrowser} as registered in the SmartList is empty...")
                        break
            except Exception as e:
                smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to open the link [i]'{link}'[/i] into {regBrowser}:\n{e}", parent)
                RichCLI.log(f"[red][b u]ERROR[/b u]: An error occured while attempting to open the link [i]'{link}'[/i] into '[b]{regBrowser}[/b]':\n\t[i]{e}[/]")
                smart.managerLog(f"ERROR: Failed to open the link '{link}' into registered browser at path '{regBrowser}': {e}")

    def copySelectedLinks(self, parent):
        if not self.selectedItems:
            RichCLI.log("[yellow][b u]WARNING[/b u]: There is no selected link to copy... Make a selection first.[/]")
            smart.warningNotify("Warning, be careful!", "There is no selected link to copy... Make a selection first.", parent)
            return

        linksToCopy = []
        for card, rowItems in self.selectedItems:
            link = rowItems[2].text() if rowItems[2] else ""
            if link:
                linksToCopy.append(link)

        if linksToCopy:
            smart.copyToClipboard("\n".join(linksToCopy))
            RichCLI.log(
                f"[blue][b u]INFO[/b u]: The following link{'s' if len(linksToCopy) > 1 else ''} {"have" if len(linksToCopy) > 1 else "has"} been copied to the clipboard:\n\t-> {"\n\t-> ".join(linksToCopy)}[/]"
            )
            smart.infoNotify("", f"The selected link{'s' if len(linksToCopy) > 1 else ''} {'have' if len(linksToCopy) > 1 else 'has'} been copied to the clipboard.", parent)

    # def bookmarkSelectedLinks(self): ... To build beforehand: the SmartCuts feature

    def moreResultsSelectedLink(self, parent):
        if len(self.selectedItems) != 1:
            RichCLI.log("[yellow][b u]WARNING[/b u]: You can only search for more results of one link at a time...[/]")
            smart.warningNotify("Warning, be careful!", "You can only search for more results of one link at a time...", parent)
            return

        link = self.selectedItems[0][1][2].text() if self.selectedItems[0][1][2] else ""
        if link:
            self.searchBar.setText(link)

    def selectAllItems(self):
        for card in self.historyCards:
            card.historyTable.selectAll()
        self.selectedItems = self.getSelectedItemsFromAllTables()

    def deselectAllItems(self):
        for card in self.historyCards:
            card.historyTable.clearSelection()
        self.selectedItems.clear()

    def deleteSelectedItems(self, parent): # to check
        selectLen = len(self.selectedItems)
        deleteDlg = None
        deleteDlg = MessageBox(
            f"Delete {selectLen} history entr{'y' if selectLen == 1 else 'ies'}",
            f"Do you reealy want to remove the {"" if selectLen == 1 else f"{selectLen} "}"
            f"selected entr{'y' if selectLen == 1 else 'ies'} from your history? This action is irreversible.",
            parent
        )
        deleteDlg.yesButton.setText(f"Delete {selectLen} entr{'y' if selectLen == 1 else 'ies'}")

        if deleteDlg.exec():
            try:
                for card, rowItems in self.selectedItems:
                    row = card.historyTable.row(rowItems[0])
                    card.historyTable.removeRow(row)
                    dateKey = datetime.datetime.strptime(card.dateLabel.text(), "%A, %d %B %Y").date().isoformat()
                    if dateKey in myHistory["MyHistory"]:
                        del myHistory["MyHistory"][dateKey][row]
                        if not myHistory["MyHistory"][dateKey]:
                            del myHistory["MyHistory"][dateKey]
                smart.saveHistory(myHistory)
                self.selectedItems.clear()
                self.updateUiAtSelection(self.selectedItems)
                self.refreshHistory()
                smart.successNotify(
                    "Deletion complete!",
                    f"The {"" if selectLen == 1 else f"{selectLen} "}"
                    f"selected entr{'y has' if selectLen == 1 else 'ies have'} been successfully deleted!",
                    parent
                )
                RichCLI.log(f"[green][b u]SUCCESS[/b u]: The {"" if selectLen == 1 else f"{selectLen} "}selected entr{'y has' if selectLen == 1 else 'ies have'} been successfully deleted![/]")
                smart.managerLog(f"SUCCESS: The {"" if selectLen == 1 else f"{selectLen} "}selected entr{'y has' if selectLen == 1 else 'ies have'} been successfully deleted.")
            except Exception as e:
                smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to delete the selected entr{'y' if selectLen == 1 else 'ies'}:\n{e}", parent)
                RichCLI.log(f"[red][b u]ERROR[/b u]: Failed while deleting the selected entr{'y' if selectLen == 1 else 'ies'}:\n\t[i]{e}[/]")

    def clearHistory(self, parent):
        clearHistoryDlg = None
        clearHistoryDlg = MessageBox(
            "Clear your requests history",
            "Please note that this operation is irreversible, so if you clear your history now, " \
           f"all your visited links and addresses will be definitely deleted from {SmartLinkerName}.\n\n" \
            "Do you really want to proceed?",
            parent
        )
        clearHistoryDlg.yesButton.setText("Clear my history")

        if clearHistoryDlg.exec():
            try:
                self.historyCards.clear()
                smart.emptyLayout(self.mainLayout, True)
                myHistory["MyHistory"] = {}
                smart.saveHistory(myHistory)
                self.mainLayout.addStretch()
                self.mainLayout.addWidget(self.emptyState)
                self.emptyState.setVisible(True)
                smart.successNotify("Clear complete!", "Your history has been successfully cleared!", parent)
                RichCLI.log(f"[green][b u]SUCCESS[/b u]: The requests history has been successfully cleared![/]")
                smart.managerLog(f"SUCCESS: The requests history has been successfully cleared.")
            except Exception as e:
                smart.errorNotify(traceback.format_exc(), "Oops! Something went wrong...", f"An error occured while attempting to clear your history:\n{e}", parent)
                RichCLI.log(f"[red][b u]ERROR[/b u]: Failed while clearing the requests history:\n\t[i]{e}[/]")

class TimestampHistoryCard(SimpleCardWidget):
    """ Class for history listing in cards per timestamp """

    def __init__(self, date: str, dateHistory: list[dict[str, typing.Any]], parent=None):
        super().__init__(parent)
        self.date = date
        self.dateHistory = dateHistory
        self.vBoxLayout = QVBoxLayout(self)
        self.dateLabel = SubtitleLabel(date, self)
        self.historyTable = TableWidget(self)

        self.historyTable.setBorderVisible(False)
        self.historyTable.setWordWrap(False)
        self.historyTable.setColumnCount(3)
        self.historyTable.setRowCount(len(self.dateHistory))
        for row, historyItem in enumerate(self.dateHistory):
            historyKeys = [k for k, v in historyItem.items()]
            for col in range(3):
                self.historyTable.setItem(
                    row, col,
                    QTableWidgetItem(
                        smart.renderTimeFromSecInt(
                            historyItem[historyKeys[col]]
                        ) if col == 0
                        else historyItem[historyKeys[col]]
                    )
                )
        self.historyTable.setHorizontalHeaderLabels(["Time", "Browser", "Address"])
        # self.historyTable.resizeColumnsToContents()
        self.historyTable.resizeRowsToContents()

        totalHeight = self.historyTable.horizontalHeader().height() # type: ignore
        for row in range(self.historyTable.rowCount()):
            totalHeight += self.historyTable.rowHeight(row)
        totalHeight += 2 * self.historyTable.frameWidth()

        self.historyTable.setMinimumHeight(totalHeight)
        self.historyTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # type: ignore
        self.historyTable.setColumnWidth(0, 100)
        if self.historyTable.verticalHeader():
            self.historyTable.verticalHeader().setHidden(True) # type: ignore

        self.vBoxLayout.setContentsMargins(20, 11, 20, 11)
        self.vBoxLayout.setSpacing(15)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.dateLabel)
        self.vBoxLayout.addWidget(self.historyTable)
