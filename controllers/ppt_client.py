import win32com.client
import pythoncom
import win32api
import win32gui
import win32con
import os
from datetime import datetime

def log(msg):
    try:
        log_dir = os.path.join(os.getenv("APPDATA"), "SeiraiPPTAssistant")
        log_path = os.path.join(log_dir, "debug.log")
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()}: [PPTClient] {msg}\n")
    except:
        pass

class PPTClient:
    def __init__(self):
        self.app = None
        self.app_type = None # 'office' or 'wps'

    def connect(self):
        """尝试连接到 PowerPoint 或 WPS"""
        self.app = None
        self.app_type = None
        
        try:
            pythoncom.CoInitialize()
        except:
            pass

        # 尝试连接 Office PowerPoint
        try:
            self.app = win32com.client.GetActiveObject("PowerPoint.Application")
            self.app_type = 'office'
            log("Connected to PowerPoint.Application")
            return True
        except Exception as e:
            # log(f"Failed to connect to PowerPoint: {e}")
            pass

        # 尝试连接 WPS Presentation
        # WPS 有多种 ProgID: Kwpp.Application, Wpp.Application
        wps_prog_ids = ["Kwpp.Application", "Wpp.Application"]
        for prog_id in wps_prog_ids:
            try:
                self.app = win32com.client.GetActiveObject(prog_id)
                self.app_type = 'wps'
                log(f"Connected to {prog_id}")
                return True
            except Exception as e:
                # log(f"Failed to connect to {prog_id}: {e}")
                continue
        
        log("Failed to connect to any PPT application")
        return False

    def get_slideshow_window_hwnd(self):
        if not self.app:
            if not self.connect():
                return 0

        try:
            # 优先尝试获取活动演示文稿的放映窗口
            try:
                if self.app.ActivePresentation and self.app.ActivePresentation.SlideShowWindow:
                    hwnd = int(self.app.ActivePresentation.SlideShowWindow.HWND)
                    if hwnd > 0 and win32gui.IsWindow(hwnd):
                        return hwnd
            except:
                pass
            
            # 遍历查找第一个有效的放映窗口
            count = int(self.app.SlideShowWindows.Count)
            for i in range(1, count + 1):
                try:
                    win = self.app.SlideShowWindows(i)
                    hwnd = int(win.HWND)
                    if hwnd > 0 and win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                        return hwnd
                except:
                    continue
        except Exception:
            self.app = None # Reset connection on error
            pass

        return 0

    def activate_window(self):
        hwnd = self.get_slideshow_window_hwnd()
        if hwnd:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
            except:
                pass
        return False

    def get_active_view(self):
        """获取当前放映视图"""
        if not self.app:
            if not self.connect():
                return None

        try:
            # 优先尝试活动演示文稿
            try:
                if self.app.ActivePresentation and self.app.ActivePresentation.SlideShowWindow:
                    view = self.app.ActivePresentation.SlideShowWindow.View
                    if view:
                        return view
            except:
                pass

            # 遍历查找
            if self.app.SlideShowWindows.Count > 0:
                for i in range(1, self.app.SlideShowWindows.Count + 1):
                    try:
                        view = self.app.SlideShowWindows(i).View
                        if view:
                            return view
                    except:
                        continue
        except Exception:
            # 连接可能已断开，尝试重新连接
            if self.connect():
                try:
                    if self.app.SlideShowWindows.Count > 0:
                        return self.app.SlideShowWindows(1).View
                except Exception:
                    pass
        return None

    def get_office_fullscreen_view(self):
        # 现在的逻辑简化为：只要能获取到有效的放映视图，就认为是全屏/放映状态
        # 之前的复杂几何计算被移除，因为它可能导致误判
        return self.get_active_view()

    def get_slide_count(self):
        try:
            if self.app and self.app.ActivePresentation:
                return self.app.ActivePresentation.Slides.Count
        except:
            pass
        return 0

    def get_current_slide_index(self):
        view = self.get_active_view()
        if view:
            try:
                return view.Slide.SlideIndex
            except:
                pass
        return 0

    def next_slide(self):
        view = self.get_active_view()
        if view:
            try:
                view.Next()
                return True
            except:
                pass
        return False

    def prev_slide(self):
        view = self.get_active_view()
        if view:
            try:
                view.Previous()
                return True
            except:
                pass
        return False

    def goto_slide(self, index):
        view = self.get_active_view()
        if view:
            try:
                view.GotoSlide(index)
                return True
            except:
                pass
        return False
        
    def get_pointer_type(self):
        view = self.get_active_view()
        if view:
            try:
                return view.PointerType
            except:
                pass
        return 0

    def set_pointer_type(self, type_id):
        view = self.get_active_view()
        if view:
            try:
                view.PointerType = type_id
                self.activate_window()
                return True
            except:
                pass
        return False

    def set_pen_color(self, rgb_color):
        view = self.get_active_view()
        if view:
            try:
                # Ensure pen mode is active
                view.PointerType = 2 
                view.PointerColor.RGB = rgb_color
                self.activate_window()
                return True
            except:
                pass
        return False

    def erase_ink(self):
        view = self.get_active_view()
        if view:
            try:
                view.EraseDrawing()
                return True
            except:
                pass
        return False

    def exit_show(self):
        view = self.get_active_view()
        if view:
            try:
                view.Exit()
                return True
            except:
                pass
        return False

    def has_ink(self):
        try:
            view = self.get_active_view()
            if not view:
                return False
            slide = view.Slide
            if slide.Shapes.Count == 0:
                return False
            for shape in slide.Shapes:
                if shape.Type == 22: # msoInk
                    return True
            return False
        except:
            return True # Fail safe
