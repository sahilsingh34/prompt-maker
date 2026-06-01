# ⚡ PromptEnhancer

A lightweight, modern Windows desktop utility that runs silently in your system tray and instantly enhances any selected text into a highly structured, professional AI prompt using a simple keyboard shortcut (**`Ctrl+Shift+E`**). Works globally across all Windows applications (browsers, editors, IDEs, etc.).

Powered by the **Groq API** with automatic support for state-of-the-art models like `llama-3.3-70b-versatile` and `deepseek-r1-distill-llama-70b`.

---

## ✨ Key Features

* **Global Hotkey Integration (`Ctrl+Shift+E`):** Highlight text in any application, press the shortcut, and watch it automatically replace with an optimized AI prompt in seconds.
* **🧠 Adaptive Category-Aware Prompt Architect:** Automatically detects what you are typing and structures the enhanced prompt specifically for that context:
  * 💻 **Coding & Debugging:** Adds objectives, stack specifics, edge cases, best practices, and formatted code blocks.
  * 📋 **PRD (Product Requirements Document):** Adds Executive Summaries, detailed User Stories, prioritized features (MoSCoW), and KPIs.
  * ⚙️ **Feature Implementation Plan:** Generates technical plans categorized by database, API, UI, and testing steps.
  * 🎨 **Image Generation (Midjourney/DALL-E):** Expands simple concepts into rich sensory details (subject, art style, framing, lighting, and parameters).
  * 🌐 **General Use:** Assigns senior expert personas, formats data in markdown tables, and structures constraints.
* **🔒 Encrypted Security:** Stored API keys are encrypted at rest using industry-standard **Fernet symmetric encryption** (saved locally under `%APPDATA%/PromptEnhancer/`).
* **🎨 Modern Settings UI:** Modern dark/light-mode UI built with **CustomTkinter** featuring:
  * Encrypted API Key manager with connection testing.
  * Adaptive **Hotkey Recorder** to bind your custom shortcut.
  * Radio selections for 4 distinct styles: **Standard**, **Detailed**, **Concise**, and **Creative**.
  * Dynamic Windows Startup toggle.
* **📋 Enhancement History:** Scrollable history panel allowing you to review, search, and quickly re-copy your last 50 prompt enhancements.
* **🚀 Silent System Tray Execution:** Minimizes to the notification area with full control right-click menus.
* **📦 Professional Packaging:** Automated scripts to compile into a single executable (`PromptEnhancer.exe`) or package into a professional native Windows setup installer (`PromptEnhancerSetup.exe`).

---

## 🛠️ Tech Stack

* **Core Language:** Python 3.10+
* **GUI Engine:** CustomTkinter (Modern styling wrapper for Tkinter)
* **API Client:** Requests (utilizing Groq's high-speed endpoint)
* **Global Hooks:** `keyboard` & `pystray` (for hotkey capture and tray integration)
* **Clipboard Engine:** `win32clipboard` (native Windows integration preserving complex multi-format clipboards)
* **Security:** Cryptography (Fernet symmetric encryption)
* **Installer:** Inno Setup 6

---

## 🚀 Getting Started (Developers)

### Prerequisites
* **Windows 10 / 11 (64-bit)**
* **Python 3.10+** (Ensure **"Add Python to PATH"** is checked during installation)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/prompt-maker.git
   cd prompt-maker
   ```
2. Set up a virtual environment and install dependencies:
   ```batch
   python -m venv venv
   venv\Scripts\pip.exe install -r requirements.txt
   ```
3. Generate the application icon:
   ```batch
   venv\Scripts\python.exe -c "from src.generate_icon import create_icon; create_icon('assets/icon.ico')"
   ```
4. Run the application:
   ```batch
   venv\Scripts\python.exe run.py
   ```

---

## 📦 Compiling to Standalone EXE & Installer

We have provided two simple scripts to compile and package the app for easy distribution:

### 1. Build the Standalone EXE (`PromptEnhancer.exe`)
Run the automated pipeline batch script:
```batch
setup_all.bat
```
* **What it does:** Verifies Python, builds your virtual environment, installs packages, generates the app icon, and compiles everything using PyInstaller.
* **Output:** `dist\PromptEnhancer.exe` (~27 MB, completely portable with no Python dependency).

### 2. Package into a Native Windows Installer (`PromptEnhancerSetup.exe`)
1. Download and install **[Inno Setup 6](https://jrsoftware.org/isdl.php)**.
2. Run the installer batch script:
   ```batch
   create_installer.bat
   ```
* **Output:** `dist\PromptEnhancerSetup.exe`. Run this setup file to install the application directly onto your system, create desktop and Start Menu shortcuts, and enable Run at Startup registry integration automatically.

---

## 🔒 Security & Data Privacy

* **Zero Telemetry:** The app never collects, logs, or transmits your usage data.
* **Direct Connections:** All API requests are sent directly from your machine to Groq's secure endpoint (`https://api.groq.com`).
* **Local Encryption:** Your API key is encrypted on your machine using a unique machine-generated secret key.

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
