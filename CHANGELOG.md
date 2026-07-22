# Release 3.0.0 (codename `Great Leap`)

## ✍️ Changes

- Added a search feature in **My Browsers** interface of the Manager, in order to facilitate the SmartList management;

- Implemented new Markdown managing tools to SmartLinker: 
    * *A **Markdown Viewer** directly integrated to the Manager, which allows users to visualize Markdown files rendered into the appropriate formatting system;*
    * *A **Markdown editor** (called **"Smart DownMarker"**) in a separate window which provides, besides of the Viewer's features, a complete Markdown editor with syntax highlighting, custom theming, and a customizable, embedded live preview panel.*

- Added a dynamic "Link Preview" feature to the **Smart Selector**, giving users some information about the link they are about to open (*works only for web links*);

- Added a preview option for the **Smart Selector**, accessible through its Settings section, which allows users to see what the Smart Selector looks like based on their current configuration, without always having to provide a link to open;

- Added the option to add a new browser directly from the Smart Selector, accessible through the dedicated card in its SmartList (*the option can be toggled in the Manager's settings*).

## 🔧 Fixes

- Fixed the dynamic theme switching when the theme option is set to follow the system configuration;

- Fixed the browser cards in the Smart Selector that worked only through the "Load link" button, now they can redirect the given to the selected browser when directly clicked;

- Fixed a Smart Selector misbehavior, when it would never close after loading a link into an external browser while the option `Close window on browser selection` is enabled.

- Fixed a Smart Selector misbehavior, when it would generate log files where a local file was opened with SmartLinker, now the Selector log files are only generated inside the root directory of SmartLinker.

<br>

# Release 2.0.0

## ✍️ Changes

- Added integrated updates downloader for an easier and quicker updating process;
    
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

- Added sound effect when launching the Smart Selector;
- Added browser selection dialogs in the **About** section for loading the different resources links;
- Added browser selection dialog when downloading updates;
- Added a quick button to refresh the main browser card in the **Settings**;
- Removed acrylic sidebar feature.

## 🔧 Fixes

- Fixed a crash bug when displaying the success notification bar;
- Fixed a crash bug when displaying the warning notification bar after adding a new browser with the same executable name as an existing one.

<br>

# First release

## 🏷️ Features

💠 Automatic URL redirection to the software for a full user-controlled management through a well-designed "Smart Selector";<br>
💠 Intelligent browser selection for loading web links of local files;<br>
💠 Persistent browser list (SmartList) for easier accessibility;<br>
💠 Personalization: from visual theme to sound effects;<br>
💠 Modern Fluent-style user interface (based on [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)).