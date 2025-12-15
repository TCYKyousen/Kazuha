import sys
from PyQt6.QtWidgets import QApplication
from controllers.business_logic import BusinessLogicController
from ui.widgets import ToolBarWidget, PageNavWidget, SpotlightOverlay

def main():
    # Enable high DPI scaling
    from PyQt6.QtCore import Qt
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize business logic controller
    controller = BusinessLogicController()
    
    # Initialize UI components
    controller.toolbar = ToolBarWidget()
    controller.nav_left = PageNavWidget(is_right=False)
    controller.nav_right = PageNavWidget(is_right=True)
    controller.spotlight = SpotlightOverlay()
    
    # Setup connections between UI and business logic
    controller.setup_connections()
    controller.setup_tray()
    
    # Show the application
    controller.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()