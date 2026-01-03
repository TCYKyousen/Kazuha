import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.settings_window import AutoHeightTextBrowser, isDarkTheme, setTheme, Theme

def test_markdown_browser():
    app = QApplication(sys.argv)
    
    # Enable dark theme for testing
    setTheme(Theme.DARK)
    
    browser = AutoHeightTextBrowser()
    browser.setMarkdown("""
# Change Log
## Version 1.2.3
- Added **bold** text support
- Added [link](https://example.com) support
- Fixed bugs
    - Bug A
    - Bug B

This is a long paragraph to test word wrapping. This is a long paragraph to test word wrapping. This is a long paragraph to test word wrapping.
""")
    
    browser.resize(400, 100) # Initial size, should auto resize height
    browser.show()
    
    # Check if height adjusted (async)
    print("Initial height:", browser.height())
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_markdown_browser()
