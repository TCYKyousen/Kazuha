from plugins.interface import AssistantPlugin
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTimeEdit
from PySide6.QtCore import QTimer, Qt, QTime
from qfluentwidgets import FluentWindow, SubtitleLabel, DisplayLabel, PrimaryPushButton, SegmentedWidget, FluentIcon as FIF


class TimerPlugin(AssistantPlugin):
    def get_name(self):
        return "Timer"

    def get_icon(self):
        return "timer.svg"

    def execute(self):
        if not hasattr(self, "window"):
            self.window = TimerWindow()

        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()
            self.window.activateWindow()


class TimerWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timer Tool")
        self.resize(300, 240)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.navigationInterface.hide()

        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 30, 10, 10)

        self.tabs = SegmentedWidget(self)
        self.tabs.addItem("Clock", "Clock")
        self.tabs.addItem("Stopwatch", "Stopwatch")
        self.tabs.addItem("Countdown", "Countdown")
        self.tabs.currentItemChanged.connect(self.on_tab_changed)

        self.display_lbl = DisplayLabel("00:00:00", self)
        self.display_lbl.setAlignment(Qt.AlignCenter)

        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(0, 5, 0))
        self.time_edit.hide()

        self.control_layout = QHBoxLayout()
        self.btn_start = PrimaryPushButton("Start", self)
        self.btn_reset = PrimaryPushButton("Reset", self)
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_reset.clicked.connect(self.reset_timer)
        self.control_layout.addWidget(self.btn_start)
        self.control_layout.addWidget(self.btn_reset)

        self.layout.addWidget(self.tabs, 0, Qt.AlignHCenter)
        self.layout.addStretch(1)
        self.layout.addWidget(self.display_lbl, 0, Qt.AlignHCenter)
        self.layout.addWidget(self.time_edit, 0, Qt.AlignHCenter)
        self.layout.addStretch(1)
        self.layout.addLayout(self.control_layout)

        self.stackedWidget.addWidget(self.central_widget)
        self.stackedWidget.setCurrentWidget(self.central_widget)

        self.mode = "Clock"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(100)

        self.elapsed_ms = 0
        self.countdown_ms = 0
        self.running = False

        self.tabs.setCurrentItem("Clock")

    def on_tab_changed(self, item):
        if not item:
            return
        key = item if isinstance(item, str) else item.text()
        self.mode = key
        self.running = False
        self.elapsed_ms = 0
        self.btn_start.setText("Start")
        self.time_edit.hide()
        self.display_lbl.show()

        if key == "Clock":
            self.btn_start.hide()
            self.btn_reset.hide()
        elif key == "Stopwatch":
            self.btn_start.show()
            self.btn_reset.show()
            self.display_lbl.setText("00:00:00")
        elif key == "Countdown":
            self.btn_start.show()
            self.btn_reset.show()
            self.display_lbl.hide()
            self.time_edit.show()

    def update_time(self):
        if self.mode == "Clock":
            self.display_lbl.setText(QTime.currentTime().toString("HH:mm:ss"))
        elif self.mode == "Stopwatch":
            if self.running:
                self.elapsed_ms += 100
                total_sec = self.elapsed_ms // 1000
                hrs = total_sec // 3600
                mins = (total_sec % 3600) // 60
                secs = total_sec % 60
                self.display_lbl.setText(f"{hrs:02}:{mins:02}:{secs:02}")
        elif self.mode == "Countdown":
            if self.running:
                self.countdown_ms -= 100
                if self.countdown_ms <= 0:
                    self.countdown_ms = 0
                    self.running = False
                    self.btn_start.setText("Start")

                total_sec = self.countdown_ms // 1000
                hrs = total_sec // 3600
                mins = (total_sec % 3600) // 60
                secs = total_sec % 60
                self.display_lbl.setText(f"{hrs:02}:{mins:02}:{secs:02}")

    def toggle_timer(self):
        if self.mode == "Countdown" and not self.running and self.btn_start.text() == "Start":
            t = self.time_edit.time()
            self.countdown_ms = (t.hour() * 3600 + t.minute() * 60 + t.second()) * 1000
            self.time_edit.hide()
            self.display_lbl.setText(t.toString("HH:mm:ss"))
            self.display_lbl.show()

        self.running = not self.running
        self.btn_start.setText("Pause" if self.running else "Start")

    def reset_timer(self):
        self.running = False
        self.elapsed_ms = 0
        self.display_lbl.setText("00:00:00")
        self.btn_start.setText("Start")
        if self.mode == "Countdown":
            self.display_lbl.hide()
            self.time_edit.show()
