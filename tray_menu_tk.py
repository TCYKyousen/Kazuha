import tkinter as tk
from tkinter import ttk
import datetime
import os
import sys

# Try to handle High DPI
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, width, height, radius=20, bg_color="#2C2C2C", border_color="#444444", **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.rect_id = None
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        
        # Draw rounded rect
        # Tkinter create_polygon with smooth=True is tricky for exact rounded rects.
        # Using arcs and lines is better.
        
        # Background
        self._round_rect(2, 2, w-3, h-3, r, fill=self.bg_color, outline=self.border_color, width=1)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, smooth=True, **kwargs)

class HoverButton(tk.Frame):
    def __init__(self, parent, text, icon_name=None, is_exit=False, is_first=False, is_last=False, command=None):
        super().__init__(parent, bg="#2C2C2C", height=38, cursor="hand2")
        self.pack_propagate(False)
        self.text = text
        self.command = command
        self.is_exit = is_exit
        
        # Colors
        self.default_bg = "#2C2C2C"
        self.hover_bg = "#FF453A" if is_exit else "#3A3A3A" # Red for exit, lighter grey for others
        self.text_color = "white"
        
        # Icon (Placeholder since we can't easily load SVG)
        self.icon_lbl = tk.Label(self, text="●", bg=self.default_bg, fg="#888888", font=("Arial", 10))
        self.icon_lbl.place(x=12, y=9)
        
        # Text
        self.lbl = tk.Label(self, text=text, bg=self.default_bg, fg=self.text_color, font=("Microsoft YaHei UI", 10))
        self.lbl.place(x=40, y=8)
        
        # Events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.lbl.bind("<Button-1>", self._on_click)
        self.icon_lbl.bind("<Button-1>", self._on_click)
        
        # Separator
        if not is_last:
            sep = tk.Frame(self, bg="#3A3A3A", height=1)
            sep.place(x=12, y=37, relwidth=1.0, width=-24)

    def _on_enter(self, event):
        bg = self.hover_bg
        self.configure(bg=bg)
        self.lbl.configure(bg=bg)
        self.icon_lbl.configure(bg=bg)

    def _on_leave(self, event):
        bg = self.default_bg
        self.configure(bg=bg)
        self.lbl.configure(bg=bg)
        self.icon_lbl.configure(bg=bg)

    def _on_click(self, event):
        if self.command:
            self.command()

class TrayMenuTk(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.overrideredirect(True) # Frameless
        self.geometry("220x260")
        self.config(bg="#000001") # Key color for transparency
        self.attributes("-transparentcolor", "#000001")
        self.attributes("-topmost", True)
        
        # Main Container (Simulating the rounded shadow/border look)
        # Tkinter canvas for rounded background
        self.canvas = RoundedFrame(self, 220, 260, radius=20, bg_color="#2C2C2C", border_color="#555555")
        self.canvas.pack(fill="both", expand=True)
        
        # Content Frame (placed on top of canvas)
        self.content = tk.Frame(self, bg="#2C2C2C")
        self.content.place(x=10, y=10, width=200, height=240)
        
        # Header
        self.header = tk.Frame(self.content, bg="#2C2C2C", height=30)
        self.header.pack(fill="x", pady=(5, 5))
        
        self.time_lbl = tk.Label(self.header, text="00:00", bg="#2C2C2C", fg="#CCCCCC", font=("Microsoft YaHei UI", 11))
        self.time_lbl.pack(side="left", padx=5)
        
        self.logo_lbl = tk.Label(self.header, text="K", bg="#2C2C2C", fg="#3275F5", font=("Arial", 12, "bold"))
        self.logo_lbl.pack(side="right", padx=5)
        
        # Group 1
        self.group1 = tk.Frame(self.content, bg="#2C2C2C", highlightbackground="#444444", highlightthickness=1)
        self.group1.pack(fill="x", pady=5)
        
        self.btn_settings = HoverButton(self.group1, "设置", is_first=True, command=lambda: print("Settings"))
        self.btn_settings.pack(fill="x")
        
        self.btn_timer = HoverButton(self.group1, "Timer 插件", is_last=True, command=lambda: print("Timer"))
        self.btn_timer.pack(fill="x")
        
        # Spacer
        tk.Frame(self.content, bg="#2C2C2C", height=10).pack()
        
        # Group 2
        self.group2 = tk.Frame(self.content, bg="#2C2C2C", highlightbackground="#444444", highlightthickness=1)
        self.group2.pack(fill="x", pady=5)
        
        self.btn_restart = HoverButton(self.group2, "重新启动程序", is_first=True, command=lambda: print("Restart"))
        self.btn_restart.pack(fill="x")
        
        self.btn_exit = HoverButton(self.group2, "退出程序", is_exit=True, is_last=True, command=self.quit)
        self.btn_exit.pack(fill="x")
        
        self._update_time()
        
        # Drag to move
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<ButtonRelease-1>", self.stop_move)
        self.header.bind("<B1-Motion>", self.do_move)

    def _update_time(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.time_lbl.config(text=now)
        self.after(1000, self._update_time)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = TrayMenuTk()
    # Center on screen
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    w = 220
    h = 260
    x = (sw - w) // 2
    y = (sh - h) // 2
    app.geometry(f"{w}x{h}+{x}+{y}")
    app.mainloop()
