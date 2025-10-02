<p align="center">
  <img width="25%" align="center" src="https://raw.githubusercontent.com/theFASTER-UNiTY/SmartLinker/master/resources/images/icons/png/icon_shadow_1.png" alt="logo">
</p>
<h1 align="center" style="font-size: 32px">
  SmartLinker
</h1>
<p align="center">
  A Fluent design-based URL redirection handler.
</p>

<div align="center">

[![Version](https://img.shields.io/badge/Version-1.0.0-color)]()
[![License GPLv3](https://img.shields.io/badge/License-GPLv3-8a2be2)](LICENSE)
[![Platform Win32](https://img.shields.io/badge/Platform-Windows-2196f3)]()
[![Architecture x64](https://img.shields.io/badge/Architecture-64--bit-fcaf00)]()

</div>

<br>

## ❓ What is SmartLinker?

SmartLinker - Mastering URL Handling (shortly SmartLinker) is a Windows desktop application that allows you to simply, yet intelligently manage and redirect URLs. Entirely based on PyQt6, currently the latest version of the Qt library for Python, it also provides a Fluent-inspired user interface for better visual immersion with the latest Windows system's UI language.

SmartLinker provides users flexibility and easy-to-use features to quickly open links with a target browser, manage a persistent "SmartList" of browsers, and even customize appearance and sound effects.

***These are some of the software's main features:***
- Automatic URL redirection to the software for a full user-controlled management through a well-designed "Smart Selector"
- Intelligent browser selection for loading web links of local files.
- Persistent browser list (SmartList) for easier accessibility.
- Personalization: from visual theme to sound effects.
- Modern Fluent-style user interface (based on [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)).

*(Not much, you might say, but just what you need)* 😁

## 🏃 Let's get started!

We'll guide you through the whole process to install it on your own computer.

### Prerequisites
- Windows 10 version 20H2 (build 19042) x64 or later
- Python 3.10 or later
- A fresh virtual environment (venv)
- The required Python packages listed in [requirements.txt](requirements.txt)

### Standalone installation
If you'd rather prefer getting the installer, check out the [Releases](https://github.com/theFASTER-UNiTY/SmartLinker/releases) page of the repository (you can skip the Quick start section).<br>
After installation, you will just have to set SmartLinker as your system's default web browser.

### Quick start
To get all the files required for SmartLinker right in your computer:

- If you have Git installed, just type the following command in your terminal:
```shell
git clone https://github.com/theFASTER-UNiTY/SmartLinker.git
```
- If not, click on the green **Code** button, then on **Download ZIP**. Then, extract it into a folder of your choice. Just be sure that the target location does have full write access.

Once the required files are ready, follow these instructions step-by-step:

1. In the SmartLinker directory, create a virtual environment by tapping this command:
```shell
python -m venv .venv
```
2. Then activate the freshly created environment:
```shell
.venv\Scripts\activate
```
3. Install all the needed dependencies with `pip`:
```shell
pip install -r requirements.txt
```
- **IMPORTANT**: To get QFluentWidgets properly installed, follow the instructions from the [official GitHub repository from zhiyiYo](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).
4. After that, everything should be set for the software to run on your computer. The final command to run is this simple one:
```shell
python smartLinker.py
```
* **NOTE**: If you want to load a link to a webpage or a local file into the Smart Selector, run this command instead:
```shell
python smartLinker.py "complete_file_path_or_website_url"
```

And you're all set! SmartLinker is installed into your system!

> [!Warning]
> You should keep in mind that if you choose the manual Python installation, the software will not do its job as meant to, since it has to be registered in the Windows registry to work properly. That can only be achieved with the installer.

## 🖼️ Here are some screenshots

#### Main interface

![main_interface](https://raw.githubusercontent.com/theFASTER-UNiTY/SmartLinker/master/screenshots/main_interface.png)

#### About interface

![about_interface](https://raw.githubusercontent.com/theFASTER-UNiTY/SmartLinker/master/screenshots/about_interface.png)

#### Selector window
![selector](https://raw.githubusercontent.com/theFASTER-UNiTY/SmartLinker/master/screenshots/selector.png)

## 🤝 Want to contribute?
**You might have already guessed, but this software is still in its first stages. So there are many aspects that might not be handled correctly.
So contributions in any form are greatly welcome and appreciated.**

Feel free to either create an issue from the [Issues](https://github.com/theFASTER-UNiTY/SmartLinker) section of the repository, or fork this project and create a pull request. For more details, please read the provided [CONTRIBUTING](CONTRIBUTING) document.

## 📜 License
This software is licensed under the **GPL**. See the [LICENSE](LICENSE) file for more information.

## 📬 Contact me
**Maintainer:** #theF∆STER™ CODE&BU!LD (software development section of the UN!TY group) (in case you would be wondering 😁)

**Email:** unity.thefaster@protonmail.com