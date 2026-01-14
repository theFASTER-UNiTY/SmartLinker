# Release 2.0.0

## ✍️ Changes

- Added integrated updates downloader for an easier and quicker updating process
    
    > ***NOTE**: You still have the possibility to check out the GitHub repository if you want, this new feature is optional.*

- Added command-line interaction support, allowing users, especially terminal/command prompt lovers to manage their SmartLinker configuration only with their keyboard and a command-line window.

    > ***NOTE**: The complete list of supported arguments and their description can be found [here](CLI-ARGUMENTS.md). Make sure to check this list before using the command-line part of the software.*

    > [!Warning]
    > For compatibility reasons, the executable is bundled with a terminal window. This helps make sure that SmartLinker handles every command-line argument correctly.

## 🔧 Fixes

- Fixed a crash bug when clicking the "Download now" button on update banners

<br>

# Release 1.1.0

## ✍️ Changes

- Added sound effect when launching the Smart Selector<br>
- Added browser selection dialogs in the **About** section for loading the different resources links<br>
- Added browser selection dialog when downloading updates
- Added a quick button to refresh the main browser card in the **Settings**<br>
- Removed acrylic sidebar feature<br>

## 🔧 Fixes

- Fixed a crash bug when displaying the success notification bar<br>
- Fixed a crash bug when displaying the warning notification bar after adding a new browser with the same executable name as an existing one<br>

<br>

# First release

## 🏷️ Features

💠 Automatic URL redirection to the software for a full user-controlled management through a well-designed "Smart Selector"<br>
💠 Intelligent browser selection for loading web links of local files.<br>
💠 Persistent browser list (SmartList) for easier accessibility.<br>
💠 Personalization: from visual theme to sound effects.<br>
💠 Modern Fluent-style user interface (based on [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)).