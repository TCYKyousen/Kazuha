import sys
import os
import traceback
import tempfile
import subprocess
import json

# Minimal imports for fast startup and crash handling
from PySide6.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, Slot, QSize
from PySide6.QtGui import QFontDatabase, QFont, QColor, QIcon

from ppt_assistant.core.ppt_monitor import PPTMonitor
from ppt_assistant.ui.overlay import OverlayWindow
from plugins.builtins.settings.plugin import SettingsPlugin
from ppt_assistant.ui.tray import SystemTray
from ppt_assistant.core.config import cfg, SETTINGS_PATH, reload_cfg, _apply_theme_and_color

def _apply_global_font(app: QApplication):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(root_dir, "fonts", "MiSansVF.ttf")
    if not os.path.exists(font_path):
        return
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        return
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        return
    family = families[0]
    font = QFont(family)
    app.setFont(font)

def show_webview_dialog(title, text, confirm_text="确认", cancel_text="取消", is_error=False, hide_cancel=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    theme = "auto"
    accent = "#3275F5"
    try:
        from ppt_assistant.core.config import cfg, Theme, qconfig
        theme = cfg.themeMode.value.lower() if hasattr(cfg.themeMode, "value") else "auto"
        resolved_theme = theme
        if theme == "auto":
            try:
                if isinstance(qconfig.theme, Theme):
                    resolved_theme = "dark" if qconfig.theme == Theme.DARK else "light"
            except:
                resolved_theme = "light"
        accent = "#E1EBFF" if resolved_theme == "dark" else "#3275F5"
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
        "accentColor": accent
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(dialog_data, f)
        temp_path = f.name
        
    root_dir = base_dir
    main_path = os.path.join(root_dir, "main.py")
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--webview-runner", "--dialog", temp_path]
    else:
        cmd = [sys.executable, main_path, "--webview-runner", "--dialog", temp_path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    return proc

class CrashHandler:
    def __init__(self, app=None):
        self.app = app
        self.app_instance = None
        self._handling = False
        sys.excepthook = self.handle_exception
        import threading
        threading.excepthook = self.handle_thread_exception

    def set_app_instance(self, instance):
        self.app_instance = instance

    def handle_thread_exception(self, args):
        self.handle_exception(args.exc_type, args.exc_value, args.exc_traceback)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if self._handling:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self._handling = True
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"CRASH DETECTED:\n{error_msg}", file=sys.stderr)
        
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = base_dir
            main_path = os.path.join(root_dir, "main.py")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
                f.write(error_msg)
                temp_path = f.name
            
            creationflags = 0x00000008 # DETACHED_PROCESS
            if getattr(sys, "frozen", False):
                cmd = [sys.executable, "--webview-runner", "--crash-file", temp_path]
            else:
                cmd = [sys.executable, main_path, "--webview-runner", "--crash-file", temp_path]
            subprocess.Popen(cmd, creationflags=creationflags, close_fds=True)
        except Exception as e:
            print(f"Failed to launch crash dialog: {e}", file=sys.stderr)
        
        try:
            if self.app_instance is not None:
                self.app_instance.cleanup()
        except Exception as e:
            print(f"Error during crash cleanup: {e}", file=sys.stderr)
        
        import time
        time.sleep(0.5)
        os._exit(1)

def _handle_multi_instance(app: QApplication):
    try:
        import psutil
    except ImportError:
        return

    current_pid = os.getpid()
    main_path = os.path.abspath(__file__)
    pids = []
    for p in psutil.process_iter(["pid", "cmdline"]):
        if p.info.get("pid") == current_pid: continue
        cmd = p.info.get("cmdline") or []
        for part in cmd:
            try:
                if os.path.abspath(part) == main_path or os.path.basename(part).lower() == "main.py":
                    pids.append(p.info.get("pid"))
                    break
            except: continue
    
    if not pids: return
    
    proc = show_webview_dialog(
        title="检测到程序已在运行",
        text="检测到已有一个实例在运行。\n\n选择要执行的操作：",
        confirm_text="终止旧的并运行",
        cancel_text="同时退出"
    )
    
    # Wait for the process to exit and check stdout for result
    stdout, _ = proc.communicate()
    if "DIALOG_CONFIRMED" in stdout:
        for pid in pids:
            try: psutil.Process(pid).terminate()
            except: pass
        return
    
    for pid in pids:
        try: psutil.Process(pid).terminate()
        except: pass
    app.quit()
    sys.exit(0)


class PPTAssistantApp:
    def __init__(self, app: QApplication):
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)
        
        _apply_theme_and_color(cfg.themeMode.value)
        
        _apply_global_font(self.app)

        self._settings_mtime = os.path.getmtime(SETTINGS_PATH) if os.path.exists(SETTINGS_PATH) else 0
        self._settings_timer = QTimer()
        self._settings_timer.setInterval(100)
        self._settings_timer.timeout.connect(self._check_settings_changed)
        self._settings_timer.start()

        self.app.aboutToQuit.connect(self.cleanup)

        self.monitor = PPTMonitor()
        self.overlay = OverlayWindow()
        self.settings_plugin = SettingsPlugin()
        self.tray = SystemTray()
        self.overlay.set_monitor(self.monitor)

        self._connect_signals()

        self.monitor.start_monitoring()

    def _connect_signals(self):
        self.monitor.slideshow_started.connect(self.on_slideshow_start)
        self.monitor.slideshow_ended.connect(self.on_slideshow_end)

        self.overlay.request_next.connect(self.monitor.go_next)
        self.overlay.request_prev.connect(self.monitor.go_previous)
        self.overlay.request_end.connect(self.monitor.end_show)

        self.overlay.request_ptr_arrow.connect(lambda: self.monitor.set_pointer_type(1))
        self.overlay.request_ptr_pen.connect(lambda: self.monitor.set_pointer_type(2))
        self.overlay.request_ptr_eraser.connect(lambda: self.monitor.set_pointer_type(5))
        self.overlay.request_pen_color.connect(self.monitor.set_pen_color)

        self.tray.show_settings.connect(self.settings_plugin.execute)
        self.tray.restart_app.connect(self.restart)
        self.tray.exit_app.connect(self.app.quit)

        self.monitor.slide_changed.connect(self.overlay.update_page_info)

    @Slot()
    def on_slideshow_start(self):
        if cfg.autoShowOverlay.value:
            self.overlay.showFullScreen()
            self.overlay.raise_()
            self.tray.show_message("PPT Assistant", "Slideshow detected. Overlay active.")

    @Slot()
    def on_slideshow_end(self):
        self.overlay.hide()

    def _check_settings_changed(self):
        if not os.path.exists(SETTINGS_PATH):
            return
        mtime = os.path.getmtime(SETTINGS_PATH)
        if mtime != self._settings_mtime:
            self._settings_mtime = mtime
            
            old_theme = cfg.themeMode.value
            reload_cfg()
            if cfg.themeMode.value != old_theme:
                if hasattr(self, 'tray'):
                    self.tray._update_icon()

    def restart(self):
        self.cleanup()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def cleanup(self):
        """Cleanup app resources and terminate subprocesses."""
        if hasattr(self, 'monitor'):
            self.monitor.stop_monitoring()
        if hasattr(self, 'settings_plugin'):
            self.settings_plugin.terminate()
        if hasattr(self, 'overlay'):
            self.overlay.cleanup()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    if "--webview-runner" in sys.argv:
        idx = sys.argv.index("--webview-runner")
        import plugins.webview_runner as _wv
        sys.argv = ["webview_runner.py"] + sys.argv[idx + 1 :]
        _wv.main()
        sys.exit(0)

    app = QApplication(sys.argv)
    crash_handler = CrashHandler(app)
    _handle_multi_instance(app)
    
    app_instance = PPTAssistantApp(app)
    crash_handler.set_app_instance(app_instance)
    app_instance.run()

