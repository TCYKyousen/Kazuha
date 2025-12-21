import sys
import os
import traceback
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from controllers.business_logic import BusinessLogicController
from ui.widgets import ToolBarWidget, PageNavWidget, SpotlightOverlay, ClockWidget

def setup_logging():
    try:
        log_dir = os.path.join(os.getenv("APPDATA"), "SeiraiPPTAssistant")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, "debug.log")
        
        # Reset log file
        with open(log_path, "w") as f:
            f.write(f"Session started at {datetime.now()}\n")
            
        return log_path
    except:
        return None

def log_message(msg):
    log_dir = os.path.join(os.getenv("APPDATA"), "SeiraiPPTAssistant")
    log_path = os.path.join(log_dir, "debug.log")
    try:
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except:
        pass

def main():
    log_path = setup_logging()
    
    # Enable high DPI scaling
    from PyQt6.QtCore import Qt
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        log_message("Initializing Controller...")
        controller = BusinessLogicController()
        controller.set_font("Bahnschrift")
        
        # Initialize UI components
        log_message("Initializing UI...")
        controller.toolbar = ToolBarWidget()
        controller.nav_left = PageNavWidget(is_right=False)
        controller.nav_right = PageNavWidget(is_right=True)
        controller.clock_widget = ClockWidget()
        controller.spotlight = SpotlightOverlay()
        
        # Setup connections between UI and business logic
        log_message("Setting up connections...")
        controller.setup_connections()
        controller.setup_tray()
        
        # Show the application
        log_message("Showing Controller...")
        controller.show()
        
        log_message("Entering Event Loop...")
        sys.exit(app.exec())
    except Exception as e:
        log_message(f"CRITICAL ERROR: {str(e)}\n{traceback.format_exc()}")
        # Show error message box if possible
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Error", f"Application failed to start:\n{str(e)}")
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    main()
