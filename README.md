# Apex Browser 🌐

Welcome to **Apex Browser**, a modern and lightweight web browser built with Python and PyQt5. Designed for an elite browsing experience, it features a sleek UI, ad blocking, incognito mode, and customizable light/dark themes. While voice search is currently disabled due to dependency issues, future updates aim to enhance and re-enable this functionality.

🔗 **Project Repository:** [ApexBrowser](https://github.com/PraveenNPatil07/ApexBrowser)

## Features ✨

- **Tab Management:** Open, close, and switch between tabs with a custom tab bar.
- **Custom UI:** Frameless window with light/dark themes and a modern navigation bar.
- **Incognito Mode:** Browse privately with no saved history or cookies.
- **Ad Blocker:** Removes annoying ads for a cleaner experience.
- **Bookmark Manager:** Save and organize your favorite websites.
- **Download Manager:** Track and manage your downloads.
- **Voice Search:** (Temporarily disabled)
- **History Manager:** View and clear your browsing history.
- **Extension Support:** Basic extension loading and toggling.
- **Customizable Settings:** Adjust zoom, toggle themes, manage privacy, and more.

## ScreenShot

![Apex Browser](https://github.com/user-attachments/assets/a96a02a5-9cdf-4689-8f9d-609b74ff5884)

## Built With 🛠️

- **Core:** Python (PyQt5)
- **Web Engine:** QtWebEngine (Chromium-based)
- **Styling:** QSS (Qt Stylesheets)



## Setup Instructions ⚙️

**1. Clone the repository** 

```bash
git clone https://github.com/PraveenNPatil07/ApexBrowser.git
cd ApexBrowser 
```
**2.Create and activate a virtual environment** 

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
**3. Install dependencies** 

```bash
pip install -r requirements.txt
```

**4. Run the browser**

```bash
python main.py
```
## Usage Instructions 📖
**Navigation:** Use back, forward, reload, and home buttons.

**Tabs:** Ctrl+T to open, Ctrl+W to close, Ctrl+Shift+T to reopen tabs.

**Zoom:** Ctrl++ to zoom in, Ctrl+- to zoom out, Ctrl+0 to reset.

**Fullscreen:** Press F11 to toggle.

**Settings Menu:** Click the ⋮ icon for downloads, themes, history, and more.

**History/Downloads:** Access via the settings menu.

**Extensions:** Manage basic extensions in the Extensions menu.

## File Structure 📂
```bash
ApexBrowser/
│
├── assets/              # Icons, stylesheets, themes
├── cache/               # Browser cache
├── downloads/           # Downloaded files
├── logs/                # Logging
├── profiles/            # Persistent profile storage
├── main.py              # Main launcher
├── browser.py           # Browser logic and features
├── ui.py                # User interface layout
├── voice_search.py      # Voice search (currently disabled)
├── ad_blocker.py        # Ad-blocking system
├── bookmark_manager.py  # Bookmark handling
├── download_manager.py  # Download logic
├── history_manager.py   # History tracking
├── incognito.py         # Incognito mode logic
├── ai_assistant.py      # AI assistant features
├── extension_handler.py # Extension system
├── security_manager.py  # Web security features
├── requirements.txt     # Required Python packages
└── .gitignore           # Git config exclusions
```
## Current Limitations and Future Plans 🚀

**Limitations:**
- Voice search is currently disabled due to a dependency issue with speech_recognition (requires Python 3.11 or earlier).
  
**Future Plans:**
- Re-enable voice search by updating the speech_recognition library or replacing it with a modern alternative like vosk or whisper.
- Add support for user-created extensions and themes.
- Implement advanced AI assistant features for summarizing web pages.
