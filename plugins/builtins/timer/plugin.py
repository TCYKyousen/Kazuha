import os
import sys
import subprocess
import threading
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Signal
from plugins.interface import AssistantPlugin
from ppt_assistant.core.config import SETTINGS_PATH
from ppt_assistant.core.timer_manager import TimerManager

class TimerPlugin(AssistantPlugin):
    start_requested = Signal(int)
    pause_requested = Signal()
    resume_requested = Signal()
    stop_requested = Signal()
    finish_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self._timer_manager = TimerManager()
        self.start_requested.connect(self._timer_manager.start)
        self.pause_requested.connect(self._timer_manager.pause)
        self.resume_requested.connect(self._timer_manager.resume)
        self.stop_requested.connect(self._timer_manager.stop)
        self.finish_requested.connect(self._timer_manager.finish)

    def get_name(self):
        return "计时器"

    def get_icon(self):
        return "timer.svg"

    def execute(self):
        if self.process and self.process.poll() is None:
            if sys.platform == "win32":
                try:
                    import ctypes
                    # Find window by title "Kazuha Timer Plugin"
                    hwnd = ctypes.windll.user32.FindWindowW(None, "Kazuha Timer Plugin")
                    if hwnd:
                        # SW_RESTORE = 9
                        ctypes.windll.user32.ShowWindow(hwnd, 9)
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                except:
                    pass
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "timer.html")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))
        main_path = os.path.join(root_dir, "main.py")
        assets_path = os.path.join(base_dir, "assets", "timer_ring.ogg")
        
        screen = QApplication.primaryScreen()
        screen_geo = screen.geometry() if screen else QWidget().screen().geometry()
        width = str(int(min(max(600, screen_geo.width() * 0.35), screen_geo.width() * 0.5)))
        height = str(int(min(max(500, screen_geo.height() * 0.45), screen_geo.height() * 0.6)))

        env = os.environ.copy()
        env["SETTINGS_PATH"] = SETTINGS_PATH
        env["ASSETS_PATH"] = assets_path
        env["TIMER_REMAINING"] = str(self._timer_manager.remaining_seconds)
        env["TIMER_IS_RUNNING"] = "true" if self._timer_manager.is_running else "false"

        if getattr(sys, "frozen", False):
            cmd = [
                sys.executable,
                "--webview-runner",
                html_path,
                "Kazuha Timer Plugin",
                width,
                height,
                "true",
            ]
        else:
            cmd = [
                sys.executable,
                main_path,
                "--webview-runner",
                html_path,
                "Kazuha Timer Plugin",
                width,
                height,
                "true",
            ]

        self.process = subprocess.Popen(
            cmd, 
            env=env, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # Start a thread to read stdout and sync with TimerManager
        threading.Thread(target=self._read_stdout, args=(self.process,), daemon=True).start()

    def _read_stdout(self, process):
        while process.poll() is None:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("TIMER_START:"):
                try:
                    seconds = int(line.split(":")[1])
                    self.start_requested.emit(seconds)
                except:
                    pass
            elif line == "TIMER_PAUSE":
                self.pause_requested.emit()
            elif line == "TIMER_RESUME":
                self.resume_requested.emit()
            elif line == "TIMER_STOP":
                self.stop_requested.emit()
            elif line == "TIMER_FINISH":
                self.finish_requested.emit()
        
        # When process exits, we no longer stop the timer logic here 
        # as per user request to keep timer running even if window is closed.
        pass

    def terminate(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
