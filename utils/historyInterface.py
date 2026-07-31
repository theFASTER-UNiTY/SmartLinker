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
        self.loadLinkBtn = PrimaryPushButton(FICO.LINK, "Load", self)
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

        mainHistScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainHistLayout.addWidget(mainHistScroll)
        mainHistScroll.setWidgetResizable(True)
        mainHistScroll.setContentsMargins(0, 0, 40, 0)
        #mainHistScroll.enableTransparentBackground()
        mainHistScroll.setStyleSheet("border: 1px solid red")
        mainHistScrollContent = QWidget()
        mainHistScroll.setWidget(mainHistScrollContent)
        mainHistScrollContent.setContentsMargins(40, 0, 40, 0)

        self.mainLayout = QVBoxLayout(mainHistScrollContent)
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

    def loadHistoryCards(self, cards: list["TimestampHistoryCard"]):
        for dateKey, entries in myHistory["MyHistory"].items():
            dateObj = datetime.datetime.strptime(dateKey, "%Y-%m-%d").date()
            d = dateObj.fromisoformat(dateKey)
            histCard = TimestampHistoryCard(
                d.strftime("%A, %d %B %Y"),
                entries,
                self
            )
            cards.append(histCard)
            histCard.historyTable.itemSelectionChanged.connect(self.itemSelected.emit)
            self.mainLayout.addWidget(histCard)

    def refreshHistory(self):
        smart.emptyLayout(self.mainLayout, True)
        myHistory = smart.loadHistory()

        if not myHistory["MyHistory"]:
            self.emptyState.setVisible(True)
            self.mainLayout.addStretch()
            self.mainLayout.addWidget(self.emptyState)
        else:
            self.emptyState.setVisible(False)
            self.loadHistoryCards(self.historyCards)

    def updateUiAtSelection(self, table: TableWidget):
        selected = table.selectedItems()

        self.loadLinkBtn.setEnabled(len(selected) == 1)
        self.copyBtn.setEnabled(bool(selected))
        self.bookmarkBtn.setEnabled(bool(selected))
        self.moreResultsBtn.setEnabled(len(selected) == 1)
        # self.selectAllBtn.setEnabled(bool(selected))
        self.deselectAllBtn.setEnabled(bool(selected))
        self.loadLinkBtn.setEnabled(bool(selected))

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
        self.historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # type: ignore
        self.historyTable.setColumnWidth(0, 100)
        if self.historyTable.verticalHeader():
            self.historyTable.verticalHeader().setHidden(True) # type: ignore

        self.vBoxLayout.setContentsMargins(20, 11, 20, 11)
        self.vBoxLayout.setSpacing(15)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.dateLabel)
        self.vBoxLayout.addWidget(self.historyTable)
