import sys
import os
import tempfile
import json
import subprocess

def show_webview_dialog(title, text, confirm_text="确认", cancel_text="取消", is_error=False, hide_cancel=False):
    """Helper to launch a webview-based dialog in a separate process."""
    # Find the project root by looking for main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while project_root and not os.path.exists(os.path.join(project_root, "main.py")):
        parent = os.path.dirname(project_root)
        if parent == project_root: break
        project_root = parent
    
    runner_path = os.path.join(project_root, "plugins", "webview_runner.py")
    
    # Try to load theme/accent
    theme = "auto"
    accent = "#3275F5"
    try:
        from ppt_assistant.core.config import cfg
        theme = cfg.themeMode.value.lower() if hasattr(cfg.themeMode, 'value') else "auto"
        accent = cfg.themeColor.value if hasattr(cfg.themeColor, 'value') else "#3275F5"
    except:
        pass

    dialog_data = {
        "title": title,
        "text": text,
        "confirmText": confirm_text,
        "cancelText": cancel_text,
        "isError": is_error,
        "hideCancel": hide_cancel,
        "theme": theme,
        "accentColor": accent[:7] if accent.startswith("#") else "#3275F5"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(dialog_data, f)
        temp_path = f.name
        
    proc = subprocess.Popen([sys.executable, runner_path, "--dialog", temp_path], stdout=subprocess.PIPE, text=True)
    return proc

class CustomDialog:
    """Wrapper class for compatibility with existing code."""
    def __init__(self, title, text, icon_path=None, parent=None, is_error=False):
        self.title = title
        self.text = text
        self.is_error = is_error
        self.btn_confirm_text = "确定"
        self.btn_cancel_text = "取消"

    def exec(self):
        proc = show_webview_dialog(
            self.title, self.text, 
            confirm_text=self.btn_confirm_text, 
            cancel_text=self.btn_cancel_text,
            is_error=self.is_error
        )
        stdout, _ = proc.communicate()
        from PySide6.QtWidgets import QDialog
        return QDialog.Accepted if "DIALOG_CONFIRMED" in stdout else QDialog.Rejected

    @property
    def btn_confirm(self):
        class BtnWrapper:
            def __init__(self, outer): self.outer = outer
            def setText(self, t): self.outer.btn_confirm_text = t
        return BtnWrapper(self)

    @property
    def btn_cancel(self):
        class BtnWrapper:
            def __init__(self, outer): self.outer = outer
            def setText(self, t): self.outer.btn_cancel_text = t
        return BtnWrapper(self)
