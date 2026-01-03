import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Property, Signal, Slot
import RinUI
from RinUI import RinUIWindow, ThemeManager

class Bridge(QObject):
    themeModeChanged = Signal()
    themeModeIndexChanged = Signal()
    navPositionIndexChanged = Signal()
    screenPaddingIndexChanged = Signal()
    timerPositionIndexChanged = Signal()
    enableStartUpChanged = Signal()
    enableSystemNotificationChanged = Signal()
    enableGlobalSoundChanged = Signal()
    enableGlobalAnimationChanged = Signal()
    enableClockChanged = Signal()
    clockPositionIndexChanged = Signal()
    clockFontWeightIndexChanged = Signal()
    clockShowSecondsChanged = Signal()
    clockShowDateChanged = Signal()
    clockShowLunarChanged = Signal()
    checkUpdateOnStartChanged = Signal()
    updateStatusTitleChanged = Signal()
    updateLastCheckTextChanged = Signal()
    updateLogsChanged = Signal()
    updateLogChanged = Signal()
    versionChanged = Signal()
    versionTextChanged = Signal()
    iconPathChanged = Signal()
    baseDirChanged = Signal()
    currentPageIndexChanged = Signal()
    isUpdatingChanged = Signal()
    updateProgressChanged = Signal()
    crashTestClicked = Signal()
    checkUpdateClicked = Signal()
    startUpdateClicked = Signal()

    def __init__(self):
        super().__init__()
    @Property(str, notify=versionTextChanged)
    def versionText(self): return "1.0.0"
    @Property(str, notify=themeModeChanged)
    def themeMode(self): return "Auto"
    @Property(int, notify=themeModeIndexChanged)
    def themeModeIndex(self): return 0
    @Property(bool, notify=isUpdatingChanged)
    def isUpdating(self): return False
    @Property(str, notify=updateStatusTitleChanged)
    def updateStatusTitle(self): return "Title"
    @Property(str, notify=updateLastCheckTextChanged)
    def updateLastCheckText(self): return "Text"
    @Property(str, notify=updateLogsChanged)
    def updateLogs(self): return "Logs"
    @Property(str, notify=baseDirChanged)
    def baseDir(self): return "."
    @Property(float, notify=updateProgressChanged)
    def updateProgress(self): return 0.0
    @Property(int, notify=screenPaddingIndexChanged)
    def screenPaddingIndex(self): return 0
    @Property(int, notify=timerPositionIndexChanged)
    def timerPositionIndex(self): return 0
    @Property(int, notify=navPositionIndexChanged)
    def navPositionIndex(self): return 0
    @Property(bool, notify=enableStartUpChanged)
    def enableStartUp(self): return False
    @Property(bool, notify=enableSystemNotificationChanged)
    def enableSystemNotification(self): return False
    @Property(bool, notify=checkUpdateOnStartChanged)
    def checkUpdateOnStart(self): return False
    @Property(bool, notify=enableClockChanged)
    def enableClock(self): return False
    @Property(int, notify=clockPositionIndexChanged)
    def clockPositionIndex(self): return 0
    @Property(bool, notify=clockShowSecondsChanged)
    def clockShowSeconds(self): return False
    @Property(bool, notify=clockShowDateChanged)
    def clockShowDate(self): return False
    @Property(int, notify=clockFontWeightIndexChanged)
    def clockFontWeightIndex(self): return 0
    @Slot()
    def checkUpdate(self): pass

app = QApplication(sys.argv)
ui = RinUIWindow()
rin_ui_path = os.path.dirname(os.path.dirname(RinUI.__file__))
ui.engine.addImportPath(rin_ui_path)
ui.engine.addImportPath(str(Path("h:/Dev/Kazuha/ui")))
bridge = Bridge()
ui.engine.rootContext().setContextProperty("Bridge", bridge)
ui.engine.rootContext().setContextProperty("ThemeManager", ThemeManager)

try:
    ThemeManager.set_theme(bridge.themeMode)
except:
    pass

qml_path = "h:/Dev/Kazuha/ui/Settings.qml"
print("Loading QML...")
try:
    ui.load(qml_path)
    if not ui.engine.rootObjects():
        print("Failed to load root object")
        for w in ui.engine.warnings(): print(w.toString())
        sys.exit(1)
    else:
        print("Success!")
except Exception as e:
    print(f"Error: {e}")
    for w in ui.engine.warnings(): print(w.toString())
    sys.exit(1)

sys.exit(0)
