import os
import sys
from PySide6.QtCore import Signal, QObject
from plugins.interface import AssistantPlugin
from .spotlight_window import SpotlightWindow

class SpotlightPlugin(AssistantPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = None

    def get_name(self):
        return "聚光灯"

    def get_icon(self):
        return "spotlight.svg"

    def execute(self):
        if self.window and self.window.isVisible():
            self.window.activateWindow()
            self.window.raise_()
            if sys.platform == "win32":
                try:
                    import ctypes
                    from ctypes import wintypes
                    hwnd = int(self.window.winId())
                    if hwnd:
                        class FLASHWINFO(ctypes.Structure):
                            _fields_ = [
                                ("cbSize", wintypes.UINT),
                                ("hwnd", wintypes.HWND),
                                ("dwFlags", wintypes.DWORD),
                                ("uCount", wintypes.UINT),
                                ("dwTimeout", wintypes.DWORD),
                            ]
                        info = FLASHWINFO(
                            ctypes.sizeof(FLASHWINFO),
                            wintypes.HWND(hwnd),
                            3,
                            3,
                            0,
                        )
                        ctypes.windll.user32.FlashWindowEx(ctypes.byref(info))
                except Exception:
                    pass
            return

        self.window = SpotlightWindow()
        self.window.show()

    def terminate(self):
        if self.window:
            self.window.close()
            self.window = None
