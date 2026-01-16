
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QTimer
import sys

app = QGuiApplication(sys.argv)

def check():
    print("Screens:")
    for screen in app.screens():
        print(f"Name: {screen.name()}")
        print(f"Model: {screen.model()}")
        print(f"Manufacturer: {screen.manufacturer()}")
        print(f"Serial: {screen.serialNumber()}")
        print(f"Geometry: {screen.geometry()}")
        print(f"DPR: {screen.devicePixelRatio()}")
        print("-" * 20)
    app.quit()

QTimer.singleShot(0, check)
app.exec()
