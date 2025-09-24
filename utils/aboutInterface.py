# import os
# import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    FluentIcon as FICO, TitleLabel, SingleDirectionScrollArea, IconWidget, CaptionLabel, PrimaryPushSettingCard, SwitchSettingCard,
    HyperlinkCard, SimpleExpandGroupSettingCard, BodyLabel, ExpandGroupSettingCard, ToolButton, ToolTipFilter, themeColor,
    ToolTipPosition, CardWidget, PrimaryPushButton, SubtitleLabel
)
from utils.SmartUtils import *

class AboutInterface(QWidget):
    """ Main class for the 'About' interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("About-SmartLinker")
        self.latestVersion = smartGetLatestVersionTag()
        self.updateAvailable = False
        self.lastChecked = f"Last checked: {cfg.get(cfg.lastCheckedDate)}" if cfg.get(cfg.lastCheckedDate) else "Click on the following button to check for the latest updates."
        self.updateCard = None

        if bool(cfg.get(cfg.checkUpdatesOnStart)):
            autoCheckTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if not self.latestVersion:
                self.updateAvailable = False
                self.lastChecked = f"Last checked: {autoCheckTime} (Failed to check for updates)"
                cfg.set(cfg.lastCheckedDate, autoCheckTime)
            elif Version(self.latestVersion) > Version(SmartLinkerVersion):
                self.updateAvailable = True
                self.lastChecked = f"Last checked: {autoCheckTime} (Latest version: {smartGetLatestVersionTag()})"
                cfg.set(cfg.lastCheckedDate, autoCheckTime)
                self.updateCard = UpdateAvailableCard("A new update is available for download!", f"You can now download the latest version of {SmartLinkerName} from the official GitHub repository.")
            else:
                self.updateAvailable = False
                self.lastChecked = f"Last checked: {autoCheckTime}"
                cfg.set(cfg.lastCheckedDate, autoCheckTime)
        elif bool(cfg.get(cfg.updateAvailable)): self.updateCard = UpdateAvailableCard("A new update is available for download!", f"You can now download the latest version of {SmartLinkerName} from the official GitHub repository.")

        mainAboutLayout = QVBoxLayout(self)
        ### mainAboutLayout.setContentsMargins(0, 60, 0, 0) # for split fluent window
        mainAboutLayout.setContentsMargins(0, 20, 0, 0) # for fluent window
        mainTitleLine = QHBoxLayout()
        ### mainTitleLine.setContentsMargins(80, 0, 0, 0) # for split fluent window
        mainTitleLine.setContentsMargins(40, 0, 0, 0) # for split fluent window
        mainAboutLayout.addLayout(mainTitleLine)
        self.title = TitleLabel("About", self)
        # self.title.setFont(smartSegoeTitle())
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainTitleLine.addWidget(self.title)
        mainAboutScroll = SingleDirectionScrollArea(self, Qt.Orientation.Vertical)
        mainAboutLayout.addWidget(mainAboutScroll)
        mainAboutScroll.setWidgetResizable(True)
        mainAboutScroll.enableTransparentBackground()
        mainAboutScrollContent = QWidget()
        mainAboutScroll.setWidget(mainAboutScrollContent)
        mainAboutScroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainAboutScroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid #FFFFFF")
        ### mainAboutScrollContent.setContentsMargins(80, 0, 80, 0) # for split fluent window
        mainAboutScrollContent.setContentsMargins(40, 0, 40, 0) # for split fluent window
        layout = QVBoxLayout(mainAboutScrollContent)
        layout.setSpacing(5)

        aboutMainLine = QHBoxLayout()
        layout.addLayout(aboutMainLine)
        aboutLogo = IconWidget(QIcon(smartResourcePath("resources/images/icons/icon_splash.ico")))
        aboutLogo.setFixedSize(64, 64)
        aboutMainLine.addWidget(aboutLogo)
        aboutTextBox = QVBoxLayout()
        aboutTextBox.setContentsMargins(10, 20, 0, 20)
        aboutMainLine.addLayout(aboutTextBox)
        aboutTitle = TitleLabel("SmartLinker - Mastering URL Handling")
        aboutSubtitle = CaptionLabel(f"© 2025 {SmartLinkerAuthor}")
        aboutSubtitle.setStyleSheet("color: gray")
        aboutTextBox.addWidget(aboutTitle)
        aboutTextBox.addWidget(aboutSubtitle)
        if (self.updateAvailable and self.updateCard) or bool(cfg.get(cfg.updateAvailable)):
            layout.addWidget(self.updateCard)
        self.aboutVersion = PrimaryPushSettingCard(
            "Check for updates",
            FICO.INFO,
            "Current version: " + SmartLinkerVersion,
            self.lastChecked
        )
        layout.addWidget(self.aboutVersion)
        self.aboutCheckUpdates = SwitchSettingCard(
            FICO.UPDATE,
            "Check for updates when the software starts",
            "You will get automatically notified when a new, better and more featured version will be released.",
            cfg.checkUpdatesOnStart
        )
        self.aboutCheckUpdates.switchButton.setOnText("Enabled")
        self.aboutCheckUpdates.switchButton.setOffText("Disabled")
        self.aboutCheckUpdates.switchButton.checkedChanged.connect(lambda checked: (
            self.aboutCheckUpdates.switchButton.setOnText("Enabled"),
            self.aboutCheckUpdates.switchButton.setOffText("Disabled"),
        ))
        layout.addWidget(self.aboutCheckUpdates)
        self.aboutFeedback = HyperlinkCard(
            "about:blank",
            "Provide feedback",
            FICO.FEEDBACK,
            "Tell us what you think",
            "You can help us improve the overall experience by providing feedback."
        )
        layout.addWidget(self.aboutFeedback)
        self.aboutInformation = AboutAppGroup()
        layout.addWidget(self.aboutInformation)
        self.aboutResources = ResourcesGroup()
        layout.addWidget(self.aboutResources)

        layout.addStretch(1)

class AboutAppGroup(SimpleExpandGroupSettingCard):
    """ Class for the informative text about SmartLinker in the About section """

    def __init__(self, parent=None):
        super().__init__(
            FICO.QUESTION,
            "What exactly is SmartLinker?",
            "If you ever want to know about SmartLinker itself, just check out our little resume."
        )

        # Information
        self.aboutInfo = BodyLabel(
            "SmartLinker - Mastering URL Handling is an easy-to-use URL handler that allows you to manage conveniently and customize the way documents and web links are opened in web browsers. " \
            "Its main purpose is to help those who have many (a lot of) browsers installed on their computers and not enough hardware resources to manage them all at once.\n \n" \
            "For example, let's assume that there are five (5) browsers installed on your computer and some of them are already running. If your system's default one isn't at the same time, Windows will try to open a link you would want to visit (or maybe a local file of almost any type) with that known-as-default web browser, which would be useless since others can do the same job, and would overload your PC for nothing.\n \n" \
            "We already know how much RAM and CPU web browsers nowadays need and use to run a lot of integrated stuff like extensions, and to manage open tabs that many people are used to open in number. " \
            "Our little software is also meant to avoid that risk of overloading your system and overheating your piece of hardware unnecessarily.\n \n" \
            "So, to be simple, SmartLinker helps you redirect any browsing-based requests to any browser you have already running, and opens a new process of your preferred one for you if no one is. That way, you have full control on how your browsing experience is handled by your system."
        )
        self.aboutInfo.setWordWrap(True)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add_group(self.aboutInfo)

    def add_group(self, label):
        """ Add informative text to the group. """
        wid = QWidget()
        wid.setFixedHeight(self.aboutInfo.sizeHint().height())
        widLayout = QHBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(label)

        self.addGroupWidget(wid)

class ResourcesGroup(ExpandGroupSettingCard):
    """ Class made for the Resources group in the About section """
    
    def __init__(self, parent=None):
        super().__init__(
            FICO.LIBRARY,
            "Resources"
        )
        self.creditsLabel = BodyLabel("For this software to work correctly, the following resources have been used:")
        self.creditsLabel.setContentsMargins(0, 0, 0, 10)

        # List of resources
        self.pyQtLine = QHBoxLayout()
        self.pyQtLine.setSpacing(10)
        self.pyQtLabel = BodyLabel("PyQt6 - The official Qt library for Python")
        self.pyQtLabel.setWordWrap(True)
        # self.pyQtLabel.setStyleSheet(f"color: {themeColor().name()}")
        self.pyQtBtn = ToolButton(QIcon(smartResourcePath("resources/images/icons/pyqt6_icon.ico")))
        self.pyQtBtn.setToolTip("Python GUIs website")
        self.pyQtBtn.installEventFilter(ToolTipFilter(self.pyQtBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.pyQtBtn2 = ToolButton(QIcon(smartResourcePath("resources/images/icons/qtforpython_icon.ico")))
        self.pyQtBtn2.setToolTip("Qt Documentation website")
        self.pyQtBtn2.installEventFilter(ToolTipFilter(self.pyQtBtn2, showDelay=300, position=ToolTipPosition.TOP))
        self.pyQtLine.addWidget(self.pyQtLabel)
        # self.pyQtLine.addStretch(0)
        self.pyQtLine.addWidget(self.pyQtBtn)
        self.pyQtLine.addWidget(self.pyQtBtn2)
        self.qFluentLine = QHBoxLayout()
        self.qFluentLine.setSpacing(10)
        self.qFluentLabel = BodyLabel("zhiyiYo/QFluentWidgets - A Qt-based GUI library for Python inspired by Windows 11's Fluent Design")
        self.qFluentLabel.setWordWrap(True)
        # self.qFluentLabel.setStyleSheet(f"color: {themeColor().name()}")
        self.qFluentBtn = ToolButton(QIcon(smartResourcePath("resources/images/icons/qfluentwidgets_icon.ico")))
        self.qFluentBtn.setToolTip("QFluentWidgets website")
        self.qFluentBtn.installEventFilter(ToolTipFilter(self.qFluentBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.qFluentBtn2 = ToolButton(FICO.GITHUB)
        self.qFluentBtn2.setToolTip("QFluentWidgets GitHub repository")
        self.qFluentBtn2.installEventFilter(ToolTipFilter(self.qFluentBtn2, showDelay=300, position=ToolTipPosition.TOP))
        self.qFluentLine.addWidget(self.qFluentLabel)
        # self.qFluentLine.addStretch(1)
        self.qFluentLine.addWidget(self.qFluentBtn)
        self.qFluentLine.addWidget(self.qFluentBtn2)
        self.flaticonLine = QHBoxLayout()
        self.flaticonLine.setSpacing(10)
        self.flaticonLabel = BodyLabel("Flaticon - The largest database of free icons available in multiple formats (credits to Freepik for the SmartLinker icon)")
        self.flaticonLabel.setWordWrap(True)
        # self.flaticonLabel.setStyleSheet(f"color: {themeColor().name()}")
        self.flaticonBtn = ToolButton(QIcon(smartResourcePath("resources/images/icons/flaticon_icon.ico")))
        self.flaticonBtn.setToolTip("Flaticon website")
        self.flaticonBtn.installEventFilter(ToolTipFilter(self.flaticonBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.flaticonLine.addWidget(self.flaticonLabel)
        # self.flaticonLine.addStretch(1)
        self.flaticonLine.addWidget(self.flaticonBtn)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.add_group()

    def add_group(self):
        """ Add resources elements to the group. """
        wid = QWidget()
        # wid.setFixedHeight(60)
        widLayout = QVBoxLayout(wid)
        widLayout.setContentsMargins(48, 12, 48, 12)

        widLayout.addWidget(self.creditsLabel)
        widLayout.addLayout(self.pyQtLine)
        widLayout.addLayout(self.qFluentLine)
        widLayout.addLayout(self.flaticonLine)

        self.addGroupWidget(wid)

# HTML icon attribution - <a href="https://www.flaticon.com/free-icons/development" title="development icons">Development icons created by Bharat Icons - Flaticon</a>
# SmartLinker icon attribution - <a href="https://www.flaticon.com/free-icons/link" title="link icons">Link icons created by Freepik - Flaticon</a>

class UpdateAvailableCard(CardWidget):

    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(FICO.IOT)
        self.titleLabel = SubtitleLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.downloadButton = PrimaryPushButton('Download now', self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(80)
        self.setBackgroundColor(QColor(smartGetRed(themeColor()), smartGetGreen(themeColor()), smartGetBlue(themeColor()), 127)) # type: ignore
        self.iconWidget.setFixedSize(40, 40)
        self.contentLabel.setTextColor(QColor("#606060"), QColor("#d2d2d2"))
        # self.downloadButton.setFixedWidth(120)

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
        self.hBoxLayout.addWidget(self.downloadButton, 0, Qt.AlignmentFlag.AlignRight)
