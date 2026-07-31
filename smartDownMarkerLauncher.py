from utils.SmartUtils import *
from utils.smartDownMarker import SmartDownMarkerGUI as DownMarker, TITLE as SDMTitle


def openErrorDialog(title, content):
    dlg = Dialog(title, content)
    dlg.setTitleBarVisible(False)
    dlg.yesButton.setEnabled(False)
    dlg.yesButton.setVisible(False)
    dlg.cancelButton.setText("Understood")
    if not dlg.exec():
        sys.exit()

def launchDownMarker():
    qapp = QApplication(sys.argv)
    qapp.setApplicationName(f"{SDMTitle} for {SmartLinkerName}")
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    setTheme(Theme.AUTO)

    if Path.exists(ROOT_PATH / "_internal" / "bin"):
        setThemeColor(getSystemAccentColor())
        parent = FramelessWindow()
        parent.setWindowIcon(QIcon(smart.resourcePath("resources/icons/ico/icon.ico")))
        parent.resize(960, 540)
        smart.centerWindow(parent)
        parent.show()
        migrationDlg = MigrationDialog(parent)
        if migrationDlg.exec():
            if migrationDlg.isSuccess:
                smart.restartApp(True)
            else:
                smart.stopApp()
            return
    
    else:
        if path:
            pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')

            if pattern.match(path):
                openErrorDialog(
                    "URL/URI not allowed",
                    "Smart DownMarker cannot handle files from web links "
                    "or content providers. You must use a local file path.\n\n"
                    f"Specified link: {path}"
                )
            elif not os.path.exists(path):
                openErrorDialog(
                    "Provided file inaccessible",
                    "The file you attempt to open from the specified path "
                    "cannot be found or does not exist...\n\n"
                    f"Specified file path: {path}"
                )
            else:
                if not (path.endswith(".md") or path.endswith(".markdown")):
                    openErrorDialog(
                        "Incompatible file type",
                        "The file you attempt to open from the specified path "
                        "cannot be identified as a Markdown file. "
                        "Only Markdown files are allowed.\n\n"
                        f"Specified file path: {path}"
                    )
                else:
                    if not smart.getFileMimeType(path).startswith("text"):
                        openErrorDialog(
                            "Unsupported file format",
                            "Despite having a Markdown extension, the file you attempt "
                            "to open from the specified path cannot be recognized as a valid "
                            "Markdown file.\n\n"
                            f"Specified file path: {path}"
                        )
                    else:
                        appWindow = DownMarker(path)
                        appWindow.show()
                        sys.exit(qapp.exec())

        else:
            appWindow = DownMarker("")
            appWindow.show()
            sys.exit(qapp.exec())


if __name__ == "__main__":
    launchDownMarker()
