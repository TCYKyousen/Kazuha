import sys
import os
from crash_handler import CrashHandler, CrashAwareApplication
from PySide6.QtWidgets import QApplication

def crash():
    print("Crashing now!")
    raise RuntimeError("This is a test crash for reproduction with QFW.")

if __name__ == "__main__":
    handler = CrashHandler()
    handler.install()
    
    app = CrashAwareApplication(sys.argv, handler)
    app.setQuitOnLastWindowClosed(False)
    
    print("Triggering crash directly...")
    from PySide6.QtCore import QTimer
    QTimer.singleShot(1000, crash)
    
    sys.exit(app.exec())
