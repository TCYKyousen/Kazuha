import os
import sys
import subprocess
from PySide6.QtWidgets import QWidget, QApplication
from plugins.interface import AssistantPlugin
from ppt_assistant.core.config import SETTINGS_PATH

class OnboardingPlugin(AssistantPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None

    def get_name(self):
        return "引导"

    def get_icon(self):
        return "settings.svg"

    def execute(self, preview=False):
        if self.process and self.process.poll() is None:
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "onboarding.html")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))
        main_path = os.path.join(root_dir, "main.py")
        width = str(960)
        height = str(640)
        env = os.environ.copy()
        env["SETTINGS_PATH"] = SETTINGS_PATH
        env["ONBOARDING_PREVIEW"] = "true" if preview else "false"
        if getattr(sys, "frozen", False):
            cmd = [
                sys.executable,
                "--webview-runner",
                html_path,
                "Onboarding",
                width,
                height,
                "false",
            ]
        else:
            cmd = [
                sys.executable,
                main_path,
                "--webview-runner",
                html_path,
                "Onboarding",
                width,
                height,
                "false",
            ]
        self.process = subprocess.Popen(cmd, env=env)

    def terminate(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
