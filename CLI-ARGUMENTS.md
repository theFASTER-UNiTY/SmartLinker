# SmartLinker: Command-Line Arguments

Since the version `2.0.0`, SmartLinker can be completely managed through a command-line interface, like **Command Prompt** or **PowerShell**.

The following list mentions all the different arguments handled by the software.

## Categories

The different arguments of SmartLinker are organized into **two main categories**:

- `load`: the category responsible of the URL requests management
- `core`: the category focused on SmartLinker configuration and other related information

## -I- `load` or *"Don't really need the Smart Selector"*

*A bit catchy, you might think (and you're right)* 😅

As mentioned before, the category `load` is used as the command-line alternative of the Smart Selector. There's not a lot to say about this, since its usage is as simple:

```powershell
SmartLinker.exe load <request_URL>
```

For example:
```powershell
SmartLinker.exe load "https://github.com/theFASTER-UNiTY/SmartLinker"
```

And that's it.

Well... Not really, because this simple method ***still*** uses the Smart Selector. But, if you **really** don't want to use it, then good news! A couple of arguments have been implemented in order for you to load a URL even more easily.

- `--smart-list` (shortly `-sl`) can be used to load a URL into a browser from your actual SmartList.

    Here's the correct way to use it:
    ```powershell
    SmartLinker.exe load <request_URL> --smart-list <browser_name>
    ```

    For example:
    ```powershell
    SmartLinker.exe load "https://github.com/theFASTER-UNiTY/SmartLinker" --smart-list "Vivaldi"
    ```

    This way, instead of opening the Smart Selector, SmartLinker will **directly** load the URL into the browser whose name has been specified.

    > [!Warning]
    > You must enter the name of a browser **exactly as specified in the SmartList**! Otherwise, SmartLinker won't be able to find it. Plus, that browser **must be installed in your computer**, or else SmartLinker won't be able to redirect the link and the whole operation will fail.
    
    <br>

- `--external-browser` (shortly `-eb`) can be used to load a URL into any browser from your computer storage.

    Here's the correct way to use it:
    ```powershell
    SmartLinker.exe load <request_URL> --external-browser <absolute_path_to_browser>
    ```

    For example:
    ```powershell
    SmartLinker.exe load "https://github.com/theFASTER-UNiTY/SmartLinker" --external-browser "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    ```

    This way, instead of opening the Smart Selector, SmartLinker will **directly** load the URL into the browser whose path has been specified.

    > [!Warning]
    > You must enter the **absolute path** (*the path should start with a drive letter, like `C:\`*) to the browser you would want to load a URL into. Otherwise, SmartLinker will look into **its own directory** and won't find it. Also, the command does not support shortcuts yet, but it is already planned for the future updates.

## -II- `core` or *"Configure SmartLinker like a pro"*

*Another catchy statement, yeah (but let's be honest, it does feel like it)* 😎

This time, `core` is the configuration-focused category that allows you to manage various settings of SmartLinker, without even opening the software. And for that purpose, a lot of commands are available, to let you experience SmartLinker in a whole different way.

> Yeah... Okay, but... Why `core` though?

> *It's because keywords like `config`, `manage` or `settings` are just too common, in our opinion, and we wanted to use something that would feel **unique**, maybe unusual, but still different from anything else... And, why not?*

So, a whole bunch of commands have been implemented for you to manage your own SmartLinker configuration by using just a terminal window.

- `add-browser` is one of the different browser-related commands. As you might have guessed, it allows you to add a new browser installed on your computer into your SmartList. It includes two options:

    - `--name` (shortly `-n`) for the name of the browser
    - `--path` (shortly `-p`) for the path to the browser

    For example:
    ```powershell
    SmartLinker.exe core add-browser --name "Ablaze Floorp" --path "C:\Program Files\Floorp\app\floorp.exe"
    ```
    With this command, a new browser named `Ablaze Floorp` at path `"C:\Program Files\Floorp\app\floorp.exe"` will be added into your SmartList. The new browser will be instantly available for use.

    > [!Warning]
    > The path to the new browser must be **absolute**. Otherwise, SmartLinker will look into **its own directory** and will not find it...

    <br>

- `clear-browsers` is the browser-related command that helps you remove every single browser from your SmartList (if you would want to start all over again, for some reason). It can be coupled with the option `--noconfirm` (shortly `-ncf`), which tells SmartLinker to validate the operation without prompting you for confirmation.

    For example:
    ```powershell
    SmartLinker.exe core clear-browsers
    ```
    
    or
    ```powershell
    SmartLinker.exe core clear-browsers --noconfirm
    ```

    Please make sure before using the command that you know what you're doing. We are not responsible for any mistake of yours.

    > [!Warning]
    > This operation is irreversible, meaning that if you would want to revert back to your previous SmartList configuration, just forget about it, it's gone...

    <br>

- `edit-browser` is another browser-related one, whose purpose is to help you apply changes to an existing SmartList browser. This command includes three options:

    - `--name` (shortly `-n`) for the name of the target browser, as mentioned in the SmartList
    - `--new-name` (shortly `-new`) for the new name you would want to assign to the specified browser
    - `--path` (shortly `-p`) for the new path you would want to assign to the specified browser

    For example:
    ```powershell
    SmartLinker.exe core edit-browser --name "Google Chrome" --new-name "Chromium" --path "C:\Program Files\Chromium\chrome.exe"
    ```
    Here, the browser labeled as `Google Chrome` will get a new name `Chromium` and will be assigned a new path `"C:\Program Files\Chromium\chrome.exe"`. As the changes will be immediately applied, you will need therefore to refer to that browser as its new name.

    > ***NOTE**: You can also modify one of the properties without changing the other. For the name, you can use `core edit-browser --name <current_name> --new-name <new_name>`, leaving the path as is. And for path only, `core edit-browser --name <current_name> --path <new_absolute_path>`, without changing its actual name.*

    <br>

- `list-browsers` is the command that displays all the browsers saved into your SmartList. It has been implemented with two options (three in the coming updates):
    
    - `--json` (shortly `-j`) to output the list in JSON format into the path specified
    - `--name-only` to display **only the names** of your SmartList browsers

    For example:
    - ```powershell
      SmartLinker.exe core list-browsers
      ```
      just lists all the different browsers (*name and path*) as registered in your SmartList;

    - ```powershell
      SmartLinker.exe core list-browsers --name-only
      ```
      will only list your SmartList browsers' names, not their complete information;

    - ```powershell
      SmartLinker.exe core list-browsers --json "C:\Users\Windows\Documents\SmartListBrowsers.json"
      ```
      will export the list into a JSON file whose path is `"C:\Users\Windows\Documents\SmartListBrowsers.json"`.
      > ***NOTE:** For the `--json` argument, if only the file name is specified (eg. `core list-browsers --json SmartListBrowsers.json`), it will be created into SmartLinker's installation directory.*
    
    The last option is a ***secret***, you will discover it once a new update is available.

    <br>

- `main-browser` is the command you can use to manage your main browser configuration. If you don't get it yet, the main browser is directly inspired from the system's default browser setting, meaning that if set, every URL request will be redirected to that main browser, if no browser from your SmartList is running at the same time. There are three different ways of using this command, considering that it handles two options, resembling the ones from `load`:

    - If no option is used, the command will just display your current main browser if set, or else a message like `No browser has been set as your main browser...`
    - `--smart-list` (shortly `-sl`) for setting one of your SmartList browsers as your main browser
    - `--external-browser` (shortly `-eb`) for setting a browser from your storage as your main browser

    For example:
    
    - ```powershell
      SmartLinker.exe core main-browser
      ```
      will display your current main browser configuration;

    - ```powershell
      SmartLinker.exe core main-browser --smart-list "Zen"
      ```
      will set the browser from your SmartList named `Zen` as your main browser; if no known browser is running, every URL request will be automatically redirected to that specific browser, without even going through the Smart Selector;

    - ```powershell
      SmartLinker.exe core main-browser --external-browser "C:\Program Files\Waterfox\waterfox.exe"
      ```
      will set the browser located at path `"C:\Program Files\Waterfox\waterfox.exe"` as your main browser; if no known browser is running, every URL request will be automatically redirected to that specific browser, without even going through the Smart Selector.
    
    <br>

- `remove-browser` is the last browser-focused command whose purpose is to help you remove a browser from your actual SmartList. Its usage is pretty simple, so you just need one option to make it work its magic: `--name` (shortly `-n`) for the name of the browser you would want to remove.

    For example:
    ```powershell
    SmartLinker.exe core remove-browser --name "Microsoft Edge"
    ```
    will remove the browser named `Microsoft Edge` from your SmartList.

    <br>

- `sfx`, as it already suggests, is the command you can use to manage SmartLinker's sound effects, may it be globally or individually. Just like the previous ones, the sound management command is coupled with several options (*four, to be accurate*), in specified ways:

    - If no option is specified, the command shows the current state of the global sound effects setting
    - `--enable` (shortly `-on`) for enabling the global sound effects setting
    - `--disable` (shortly `-off`) for disabling the global sound effects setting
    - `--type` (shortly `-t`) for specifying the sound effect to configure
    - `--file` (shortly `-f`) for specifying the path to the audio file to assign to the sound effect whose type has been specified

    For the different sound effects you can specify with the `--type` option, please refer to the following table:
    
    | `--type` argument | Description               |
    |-------------------|---------------------------|
    | `startup`         | SmartLinker startup       |
    | `success`         | Success notification      |
    | `info`            | Informative notification  |
    | `warning`         | Warning notification      |
    | `error`           | Error notification        |
    | `question`        | Confirmation dialog       |
    | `selector`        | Smart Selector launch     |

    For example:
    - ```powershell
      SmartLinker.exe core sfx --enable
      ```
      or
      ```powershell
      SmartLinker.exe core sfx --disable
      ```
      will enable/disable the global sound effects;
    
    - ```powershell
      SmartLinker.exe core sfx --type warning --file "C:\Users\Windows\Music\uh-oh-sound-effect.mp3"
      ```
      will apply the `"uh-oh-sound-effect.mp3"` sound file located at the specified path to the warning sound effect.

  ### Use scenarios
    1. `--enable` and `--disable` can only be used for the global setting

    2. If `--type` is used without `--file`, you will get the specified sound effect's state (either **disabled** or **enabled** (*with path to audio file*))

    3. `--file` cannot be used without `--type` (obviously, since the file you select will be applied to a specified sound effect)

    4. If you want to disable a specific sound effect, you can set `None` as the `--file` argument, like this:
        ```powershell
        SmartLinker.exe core sfx --type <TYPE> --file None
        ```
        This way, the specified sound effect will be disabled.

    <br>
  
- `splash` is the command handling the splash screen configuration (only for the SmartLinker Manager). To configure this part of SmartLinker, four options are included in this command-line parameter:

  - `--enable` (shortly `-on`) for enabling the splash screen
  - `--disable` (shortly `-off`) for disabling the splash screen
  - `--state` (shortly `-s`) for displaying the current state of the splash screen configuration
  - `--duration` (shortly `-d`) for setting the duration of the splash screen (in milliseconds)
  
  For example:
  - ```powershell
    SmartLinker.exe core splash --state
    ```
    will display the current state of the splash screen configuration;
  
  - ```powershell
    SmartLinker.exe core splash --duration 3000
    ```
    will set the splash duration to **3000 milliseconds** (3 seconds).

  ### Use scenarios
    1. `--enable` must be used along with `--duration` for a quicker and easier configuration. If `--duration` is not specified, SmartLinker will prompt you to specify the duration you would want the splash screen to be displayed for.

    2. If you use `--duration` along with `--disable` or `--state`, the duration parameter will be ignored.

    <br>

- `temp-clean` is the command allowing the user to easily delete all the temporary files generated by SmartLinker, after an update, for example. It has been implemented with just one option, for it to be even simpler: `--noconfirm` (shortly `-ncf`) to validate the operation without prompting.

  For example:
  ```powershell
  SmartLinker.exe core temp-clean --noconfirm
  ```
  will delete every single temporary file generated by SmartLinker, without needing you to confirm the operation.

  > [!Warning]
  > Be cautious, and be sure that you know what you're doing, because this operation is irreversible. If you have stored any other file into SmartLinker's temporary folder, they will also be deleted.

    <br>

- `update` is one of the most important commands of SmartLinker, as it allows the user to manage the software's update configuration, and also (if available) update it directly through the command-line interface. For it to complete its mission, four options can be used with this command:

  - `--auto-check-enable` (shortly `-ace`) for enabling the automatic check for updates at SmartLinker startup
  - `--auto-check-disable` (shortly `-acd`) for disabling the automatic check for updates at SmartLinker startup
  - `--check` (shortly `-c`) for checking for the latest update available
  - `--install` (shortly `-i`) for installing the latest update if already downloaded, or else downloading it before installing

  For example:
  - ```powershell
    SmartLinker.exe core update --auto-check-enable
    ```
    or
    ```powershell
    SmartLinker.exe core update --auto-check-disable
    ```
    will enable/disable the automatic check for updates at SmartLinker startup;
  
  - ```powershell
    SmartLinker.exe core update --check
    ```
    will check for the latest update available on the official GitHub repository;
  
  - ```powershell
    SmartLinker.exe core update --install
    ```
    will install the latest update if already downloaded, or else download it before installing.

  **NOTE**: *No need to remind you that for `--check` and `--install` to work properly, it is recommended to have your computer connected to the Internet.*

    <br>

- `update-banners` is another update-related command, this one managing the update banners displayed in the SmartLinker Manager whenever a new update is available. It has been implemented with three options:

  - `--enable` (shortly `-on`) for enabling the update banners
  - `--disable` (shortly `-off`) for disabling the update banners
  - `--state` (shortly `-s`) for displaying the current state of the update banners configuration

  For example:
  - ```powershell
    SmartLinker.exe core update-banners --state
    ```
    will display the current state of the update banners configuration;
  
  - ```powershell
    SmartLinker.exe core update-banners --enable
    ```
    or
    ```powershell
    SmartLinker.exe core update-banners --disable
    ```
    will enable/disable the update banners display.

    <br>

- `version` is the last implemented command, functioning the same way as the `ver` command in Command Prompt. It just displays the current version of SmartLinker.

  ```powershell
  SmartLinker.exe core version
  ```
  will simply display the current version of SmartLinker installed on your computer.

  <br>

# Finished!
So, that's it for the command-line arguments section of SmartLinker. With future updates, new arguments will be implemented and available for you to use.

Thank you for using SmartLinker!

### ***\#theF∆STER™ CODE&BU!LD™***