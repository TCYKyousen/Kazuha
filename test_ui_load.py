import sys
import os
from PyQt6.QtWidgets import QApplication

# Mocking config and other dependencies if necessary
# Assuming the project structure allows direct import
sys.path.append(os.getcwd())

try:
    from ui.settings_window import SettingsWindow
    print("Successfully imported SettingsWindow")
except Exception as e:
    print(f"Failed to import SettingsWindow: {e}")
    sys.exit(1)

def test_init():
    app = QApplication(sys.argv)
    try:
        window = SettingsWindow()
        print("Successfully initialized SettingsWindow")
        # Trigger update interface creation check
        if hasattr(window, 'logPage') and hasattr(window, 'settingsPage'):
            print("Update interface pages created")
        else:
            print("Update interface pages missing")
    except Exception as e:
        print(f"Failed to initialize SettingsWindow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_init()
