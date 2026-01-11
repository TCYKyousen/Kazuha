from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QApplication, QLabel, QGraphicsDropShadowEffect, QPushButton, QSwipeGesture, QGestureEvent
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QEvent, QTimer, QTime
from PySide6.QtGui import QColor, QIcon, QPainter, QBrush, QPen, QPixmap, QGuiApplication
from PySide6.QtSvg import QSvgRenderer
import os
import importlib.util
import sys
import tempfile
import json
import subprocess
from ppt_assistant.core.config import cfg
from qfluentwidgets import FluentWidget, FluentIcon as FIF, BodyLabel, IconWidget, themeColor

try:
    import psutil
except ImportError:
    psutil = None

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons")
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plugins", "builtins")


class StatusBarWidget(QFrame):
    is_light_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(26)
        self._is_light = False
        self._monitor = None
        self._network_kind = "offline"
        self._volume_supported = False
        self._build_ui()
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_time)
        self._clock_timer.start(1000)
        self._color_timer = QTimer(self)
        self._color_timer.timeout.connect(self._update_color_from_screen)
        self._color_timer.start(2000)
        self._video_timer = QTimer(self)
        self._video_timer.timeout.connect(self._update_video)
        self._video_timer.start(500)
        self._network_timer = QTimer(self)
        self._network_timer.timeout.connect(self._update_network)
        self._network_timer.start(5000)
        self._volume_timer = QTimer(self)
        self._volume_timer.timeout.connect(self._update_volume)
        self._volume_timer.start(1000)
        self._update_time()
        self._update_palette()
        self._update_volume()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        self.time_label = BodyLabel("", self)
        layout.addWidget(self.time_label)

        self.center_widget = QWidget(self)
        center_layout = QHBoxLayout(self.center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(6)
        self.progress_value = BodyLabel("", self.center_widget)
        self.progress_caption = BodyLabel("媒体时长", self.center_widget)
        self.progress_caption.hide()
        self.progress_value.hide()
        center_layout.addWidget(self.progress_value)
        center_layout.addWidget(self.progress_caption, 0, Qt.AlignBottom)

        layout.addStretch(1)
        layout.addWidget(self.center_widget)
        layout.addStretch(1)

        self.net_icon = IconWidget(FIF.WIFI, self)
        self.net_icon.setFixedSize(18, 18)
        layout.addWidget(self.net_icon)

        self.volume_icon = IconWidget(FIF.VOLUME, self)
        self.volume_icon.setFixedSize(18, 18)
        layout.addWidget(self.volume_icon)

        self.time_label.setStyleSheet("font-weight: 900;")
        self.progress_value.setStyleSheet("font-weight: 900;")
        self.progress_caption.setStyleSheet("font-size: 9px;")

    def _update_time(self):
        self.time_label.setText(QTime.currentTime().toString("HH:mm"))

    def set_monitor(self, monitor):
        self._monitor = monitor

    def _update_video(self):
        if not self._monitor:
            self.progress_caption.hide()
            self.progress_value.hide()
            return
        try:
            ratio, pos, length = self._monitor.get_video_progress()
        except Exception:
            self.progress_caption.hide()
            self.progress_value.hide()
            return
        if length is None or length <= 0:
            self.progress_caption.hide()
            self.progress_value.hide()
            return
        length_sec = length or 0.0
        if length_sec > 36000:
            length_sec = length_sec / 1000.0
        total_text = self._format_seconds(length_sec)
        self.progress_value.setText(total_text)
        self.progress_caption.show()
        self.progress_value.show()

    def _format_seconds(self, value):
        secs = int(float(value))
        if secs < 0:
            secs = 0
        m = secs // 60
        s = secs % 60
        return f"{m:02}:{s:02}"

    def _update_color_from_screen(self):
        # Disabled adaptive logic as per user request for forced light theme
        pass

    def _update_network(self):
        kind = "offline"
        if psutil is not None:
            try:
                stats = psutil.net_if_stats()
                for name, st in stats.items():
                    if not st.isup:
                        continue
                    lname = name.lower()
                    if "wi-fi" in lname or "wifi" in lname or "wlan" in lname:
                        kind = "wifi"
                        break
                    if "ethernet" in lname or "eth" in lname or "lan" in lname:
                        kind = "wired"
                if kind == "offline" and any(st.isup for st in stats.values()):
                    kind = "wired"
            except Exception:
                pass
        if kind == "offline":
            try:
                out = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"],
                    encoding="utf-8",
                    errors="ignore",
                )
                if "state" in out.lower() and "connected" in out.lower():
                    kind = "wifi"
            except Exception:
                pass
        self._network_kind = kind
        if kind == "wifi":
            self.net_icon.setIcon(FIF.WIFI)
        elif kind == "wired":
            icon = getattr(FIF, "ETHERNET", FIF.WIFI)
            self.net_icon.setIcon(icon)
        else:
            self.net_icon.setIcon(FIF.WIFI)

    def _update_volume(self):
        try:
            self.volume_icon.setIcon(FIF.VOLUME)
        except Exception:
            pass

    def _update_palette(self, is_light=False):
        self._is_light = is_light
        if is_light:
            fg = "#191919"
            bg = "rgba(255, 255, 255, 0.75)"
        else:
            fg = "#FFFFFF"
            bg = "rgba(16, 16, 16, 0.75)"
        self.setStyleSheet(
            f"""
            StatusBarWidget {{
                background-color: {bg};
                border-bottom: 1px solid rgba(0, 0, 0, 0);
            }}
            QLabel {{
                color: {fg};
                font-family: 'MiSans VF','MiSans','Segoe UI';
            }}
            IconWidget {{
                color: {fg};
            }}
        """
        )

class ClickableLabel(QLabel):
    clicked = Signal(QPoint)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(event, "globalPosition"):
                pos = event.globalPosition().toPoint()
            else:
                pos = event.globalPos()
            self.clicked.emit(pos)
        super().mousePressEvent(event)

class PenColorPopup(QFrame):
    color_selected = Signal(int, int, int)

    def __init__(self, parent=None, colors=None, is_light=False):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.colors = colors or []
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        bg = "white" if is_light else "rgb(32, 32, 32)"
        border = "rgba(0, 0, 0, 0.08)" if is_light else "rgba(255, 255, 255, 0.1)"
        
        self.setStyleSheet(f"""
            PenColorPopup {{
                background-color: {bg};
                border-radius: 12px;
                border: 1px solid {border};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        for r, g, b in self.colors:
            btn = QPushButton(self)
            btn.setFixedSize(22, 22)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({r}, {g}, {b});
                    border-radius: 11px;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                }}
                QPushButton:hover {{
                    border: 1px solid rgba(0, 0, 0, 0.3);
                }}
            """)
            btn.clicked.connect(lambda _, r=r, g=g, b=b: self._on_color_clicked(r, g, b))
            layout.addWidget(btn)

    def _on_color_clicked(self, r, g, b):
        self.color_selected.emit(r, g, b)
        self.close()

class CustomToolButton(QPushButton):
    def __init__(self, icon_name, tooltip, parent=None, is_exit=False, tool_name=None):
        super().__init__(parent)
        self.is_exit = is_exit
        self.tool_name = tool_name
        self.icon_name = icon_name
        self.setFixedSize(33, 33)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style(False)
        self.set_icon_color(False) # Default to dark mode (white icons)

    def set_icon_color(self, is_light):
        icon_path = os.path.join(ICON_DIR, self.icon_name)
        if not os.path.exists(icon_path):
            return
            
        color = QColor(25, 25, 25) if is_light else QColor(255, 255, 255)
        if self.is_exit:
            color = QColor(255, 255, 255)
            
        renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(18, 18))

    def update_style(self, is_active, is_light=True, use_indicator=False):
        accent = themeColor()
        r = accent.red()
        g = accent.green()
        b = accent.blue()
        
        if self.is_exit:
            bg = "rgba(255, 69, 58, 220)"
            hover_bg = "rgba(255, 69, 58, 255)"
        elif use_indicator:
            bg = "transparent"
            hover_bg = "rgba(0, 0, 0, 0.05)" if is_light else "rgba(255, 255, 255, 0.05)"
        elif is_active:
            bg = f"rgba({r}, {g}, {b}, 0.22)"
            hover_bg = f"rgba({r}, {g}, {b}, 0.32)"
        else:
            bg = "transparent"
            hover_bg = "rgba(0, 0, 0, 0.06)" if is_light else "rgba(255, 255, 255, 0.06)"
        
        radius = self.height() // 2
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border-radius: {radius}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """)

class SlidePreviewPopup(FluentWidget):
    def __init__(self, parent=None, monitor=None, is_light=False):
        super().__init__(parent=parent)
        self.monitor = monitor
        self._is_light = is_light
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.Tool)
        self.cards = []
        self.slide_indices = []
        self.current_index = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        bg = "white" if self._is_light else "rgb(32, 32, 32)"
        border = "rgba(0, 0, 0, 0.12)" if self._is_light else "rgba(255, 255, 255, 0.18)"
        fg = "#191919" if self._is_light else "#FFFFFF"
        self.setStyleSheet(f"""
            SlidePreviewPopup {{
                background-color: {bg};
                border-radius: 10px;
                border: 1px solid {border};
            }}
            QLabel {{
                color: {fg};
                font-family: 'MiSans VF','MiSans','Segoe UI';
            }}
        """)
        self.card_container = QWidget(self)
        self.card_layout = QHBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(6)
        layout.addWidget(self.card_container)
        self.page_label = QLabel(self)
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.page_label)
        self._load_slides()
        self._update_page_label()

    def _load_slides(self):
        if not self.monitor or not hasattr(self.monitor, "get_total_slides"):
            return
        total = self.monitor.get_total_slides()
        if not total:
            return
        temp_dir = os.path.join(tempfile.gettempdir(), "kazuha_ppt_thumbs")
        os.makedirs(temp_dir, exist_ok=True)
        for slide_num in range(1, total + 1):
            path = os.path.join(temp_dir, f"slide_{slide_num}.png")
            try:
                if hasattr(self.monitor, "export_slide_thumbnail"):
                    self.monitor.export_slide_thumbnail(slide_num, path)
            except Exception:
                continue
            pix = QPixmap(path)
            if pix.isNull():
                continue
            btn = QPushButton(self.card_container)
            btn.setFlat(True)
            btn.setIcon(QIcon(pix))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { border-radius: 14px; border: 1px solid rgba(0,0,0,0.05); background-color: #F5F6F8; }"
                "QPushButton:hover { border: 1px solid rgba(50,117,245,0.5); background-color: #FFFFFF; }"
            )
            index_in_row = len(self.cards)
            btn.clicked.connect(lambda _, idx=index_in_row: self._on_card_clicked(idx))
            self.card_layout.addWidget(btn)
            self.cards.append(btn)
            self.slide_indices.append(slide_num)
        self._update_cards()

    def _update_cards(self):
        for idx, btn in enumerate(self.cards):
            w, h = 180, 110
            btn.setFixedSize(w, h)
            btn.setIconSize(QSize(w, h))

    def _update_page_label(self):
        total = len(self.cards)
        if total == 0:
            self.page_label.setText("")
        else:
            self.page_label.setText(f"{self.current_index + 1}/{total}")

    def _go_prev(self):
        if not self.cards:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._update_cards()
            self._update_page_label()

    def _go_next(self):
        if not self.cards:
            return
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1
            self._update_cards()
            self._update_page_label()

    def _activate_current(self):
        if not self.cards or not self.slide_indices:
            return
        index = self.slide_indices[self.current_index]
        if self.monitor and hasattr(self.monitor, "go_to_slide"):
            self.monitor.go_to_slide(index)
        self.close()

    def _on_card_clicked(self, idx):
        if idx < 0 or idx >= len(self.cards):
            return
        self.current_index = idx
        self._update_cards()
        self._update_page_label()
        self._activate_current()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._go_prev()
        elif delta < 0:
            self._go_next()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Left, Qt.Key_A):
            self._go_prev()
        elif key in (Qt.Key_Right, Qt.Key_D):
            self._go_next()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            self._activate_current()
        elif key == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def event(self, e):
        if e.type() == QEvent.Gesture:
            ge = e
            if isinstance(ge, QGestureEvent):
                swipe = ge.gesture(Qt.SwipeGesture)
                if isinstance(swipe, QSwipeGesture):
                    if swipe.horizontalDirection() == QSwipeGesture.Left:
                        self._go_next()
                        return True
                    if swipe.horizontalDirection() == QSwipeGesture.Right:
                        self._go_prev()
                        return True
        return super().event(e)

class OverlayWindow(QWidget):
    request_next = Signal()
    request_prev = Signal()
    request_end = Signal()
    request_ptr_arrow = Signal()
    request_ptr_pen = Signal()
    request_ptr_eraser = Signal()
    request_pen_color = Signal(int, int, int)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Add this attribute to fix UpdateLayeredWindowIndirect error on some systems
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_PaintOnScreen, False)
        self.setWindowTitle("顶层效果窗口")
        self.status_bar = None
        self.plugins = []
        self.monitor = None
        self.slide_preview = None
        self.load_plugins()
        self.init_ui()
        self.update_layout()

    def bind_monitor_signals(self):
        if self.monitor:
            return

    def set_monitor(self, monitor):
        self.monitor = monitor
        if self.status_bar:
            self.status_bar.set_monitor(monitor)
        self.bind_monitor_signals()

    def show_slide_preview(self, global_pos=None):
        if not self.monitor:
            return
        self.slide_preview = SlidePreviewPopup(self, self.monitor, getattr(self, "_is_light", True))
        self.slide_preview.adjustSize()
        if isinstance(global_pos, QPoint):
            screen = QGuiApplication.screenAt(global_pos)
            if not screen:
                screen = QGuiApplication.primaryScreen()
            geo = screen.availableGeometry()
            w = self.slide_preview.width()
            h = self.slide_preview.height()
            x = global_pos.x() - w // 2
            y = global_pos.y() - h - 12
            if x < geo.left():
                x = geo.left() + 8
            if x + w > geo.right():
                x = geo.right() - w - 8
            if y < geo.top():
                y = global_pos.y() + 12
            self.slide_preview.move(x, y)
        else:
            center = self.rect().center()
            center_global = self.mapToGlobal(center)
            x = center_global.x() - self.slide_preview.width() // 2
            y = center_global.y() - self.slide_preview.height() // 2
            self.slide_preview.move(x, y)
        self.slide_preview.show()
        self.slide_preview.raise_()
        self.slide_preview.setFocus()

    def load_plugins(self):
        if not os.path.exists(PLUGIN_DIR):
            return
        for entry in os.listdir(PLUGIN_DIR):
            plugin_dir = os.path.join(PLUGIN_DIR, entry)
            if not os.path.isdir(plugin_dir):
                continue
            manifest_path = os.path.join(plugin_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                continue
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                entry_point = manifest.get("entry")
                if not entry_point:
                    continue
                module_name, class_name = entry_point.rsplit(".", 1)
                module_path = os.path.join(plugin_dir, module_name + ".py")
                if not os.path.exists(module_path):
                    continue
                spec = importlib.util.spec_from_file_location(f"plugins.builtins.{entry}.{module_name}", module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugin_cls = getattr(module, class_name, None)
                if plugin_cls is None:
                    continue
                plugin_instance = plugin_cls()
                plugin_instance.manifest = manifest
                plugin_instance.set_context(self)
                self.plugins.append(plugin_instance)
                print(f"Loaded plugin: {plugin_instance.get_name()}")
            except Exception as e:
                print(f"Error loading plugin {entry}: {e}")

    def init_ui(self):
        self.toolbar_height = 45
        has_status_plugin = any(
            hasattr(p, "manifest")
            and isinstance(p.manifest, dict)
            and p.manifest.get("type") == "status_bar"
            for p in self.plugins
        )
        self._has_status_plugin = has_status_plugin
        if cfg.showStatusBar.value and has_status_plugin:
            self.status_bar = StatusBarWidget(self)
            self.status_bar.show()
        cfg.showStatusBar.valueChanged.connect(self._on_status_bar_visibility_changed)
        
        self.toolbar = ToolbarWidget(self, self.plugins, height=self.toolbar_height) 
        self.toolbar.prev_clicked.connect(self.request_prev.emit)
        self.toolbar.next_clicked.connect(self.request_next.emit)
        self.toolbar.end_clicked.connect(self.request_end.emit)
        
        self.toolbar.select_clicked.connect(self.request_ptr_arrow.emit)
        self.toolbar.pen_clicked.connect(self.request_ptr_pen.emit)
        self.toolbar.eraser_clicked.connect(self.request_ptr_eraser.emit)
        self.toolbar.pen_color_changed.connect(self.request_pen_color.emit)
        
        self.left_flipper = PageFlipWidget("Left", self, height=self.toolbar_height)
        self.left_flipper.clicked_prev.connect(self.request_prev.emit)
        self.left_flipper.clicked_next.connect(self.request_next.emit)
        self.left_flipper.page_clicked.connect(self.show_slide_preview)
        
        self.right_flipper = PageFlipWidget("Right", self, height=self.toolbar_height)
        self.right_flipper.clicked_prev.connect(self.request_prev.emit)
        self.right_flipper.clicked_next.connect(self.request_next.emit)
        self.right_flipper.page_clicked.connect(self.show_slide_preview)

        # Connect adaptive theme signal
        if self.status_bar:
            self.status_bar.is_light_changed.connect(self._on_theme_changed)
        
        self.left_flipper.show()
        self.right_flipper.show()
        self.toolbar.show()
        
        self._update_theme_from_cfg()
        cfg.themeMode.valueChanged.connect(self._update_theme_from_cfg)

    def _update_theme_from_cfg(self):
        theme = cfg.themeMode.value
        if theme == "Auto":
            from qfluentwidgets import isDarkTheme
            is_light = not isDarkTheme()
        else:
            is_light = (theme == "Light")
        self._on_theme_changed(is_light)

    def _on_theme_changed(self, is_light):
        self._is_light = is_light
        self.toolbar.update_style(is_light)
        self.left_flipper.update_style(is_light)
        self.right_flipper.update_style(is_light)
        if self.status_bar:
            self.status_bar._update_palette(is_light)

    def _on_status_bar_visibility_changed(self, visible: bool):
        if visible and getattr(self, "_has_status_plugin", False):
            if self.status_bar is None:
                self.status_bar = StatusBarWidget(self)
                if self.monitor:
                    self.status_bar.set_monitor(self.monitor)
            self.status_bar.show()
        else:
            if self.status_bar is not None:
                self.status_bar.hide()
        self.update_layout()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_layout()

    def cleanup(self):
        """Clean up resources and terminate plugins."""
        for plugin in self.plugins:
            try:
                plugin.terminate()
            except Exception as e:
                print(f"Error terminating plugin {plugin.get_name()}: {e}")

    def update_layout(self):
        w = self.width()
        h = self.height()
        margin = 20
        top_offset = 0
        if self.status_bar and self.status_bar.isVisible():
            self.status_bar.setFixedWidth(w)
            self.status_bar.move(0, 0)
            top_offset = self.status_bar.height() + 6
        
        if w <= 100 or h <= 100:
            return

        # Ensure the widgets have correct sizes before moving
        self.toolbar.setFixedSize(self.toolbar.sizeHint().width(), self.toolbar_height)
        self.left_flipper.setFixedSize(self.left_flipper.sizeHint().width(), self.toolbar_height)
        self.right_flipper.setFixedSize(self.right_flipper.sizeHint().width(), self.toolbar_height)

        y_pos = h - self.toolbar_height - 30 
        
        tb_w = self.toolbar.width()
        self.toolbar.move((w - tb_w) // 2, y_pos)
        
        self.left_flipper.move(margin, y_pos)
        
        self.right_flipper.move(w - self.right_flipper.width() - margin, y_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_layout()

    # paintEvent removed to ensure full transparency of the overlay container

    def update_page_info(self, current, total):
        self.left_flipper.set_page_info(current, total)
        self.right_flipper.set_page_info(current, total)
        
        # Force update to clean artifacts if any
        self.update()

class ToolbarWidget(QFrame):
    prev_clicked = Signal()
    next_clicked = Signal()
    end_clicked = Signal()
    select_clicked = Signal()
    pen_clicked = Signal()
    eraser_clicked = Signal()
    pen_color_changed = Signal(int, int, int)

    def __init__(self, parent=None, plugins=[], height=45):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.plugins = plugins
        self.h_val = height
        self.current_tool = "select"
        self.pen_popup = None
        self._is_light = True
        
        # Indicator for tool switching
        self.indicator = QFrame(self)
        self.indicator.setObjectName("Indicator")
        self.setFixedHeight(self.h_val)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        self.init_ui()
        self.update_style()

    def update_style(self, is_light=True):
        self._is_light = is_light
        accent = themeColor()
        r, g, b = accent.red(), accent.green(), accent.blue()
        
        if is_light:
            bg = "rgba(255, 255, 255, 0.85)"
            fg = "#191919"
            border = "rgba(0, 0, 0, 0.08)"
            line_color = "rgba(0, 0, 0, 0.1)"
            indicator_bg = f"rgba({r}, {g}, {b}, 0.15)"
        else:
            bg = "rgba(32, 32, 32, 0.85)"
            fg = "#FFFFFF"
            border = "rgba(255, 255, 255, 0.08)"
            line_color = "rgba(255, 255, 255, 0.14)"
            indicator_bg = f"rgba({r}, {g}, {b}, 0.25)"

        self.setStyleSheet(f"""
            ToolbarWidget {{
                background-color: {bg};
                border-radius: {self.h_val // 2}px;
                border: 1px solid {border};
            }}
            #Indicator {{
                background-color: {indicator_bg};
                border-radius: 22px;
            }}
            QLabel {{
                color: {fg};
                font-family: 'MiSans VF', 'MiSans', 'Segoe UI';
                font-weight: 500;
            }}
        """)
        
        for line in self.findChildren(QFrame):
            if line.frameShape() == QFrame.VLine:
                line.setStyleSheet(f"color: {line_color};")
                
        for btn in self.findChildren(CustomToolButton):
            btn.set_icon_color(is_light)
            is_tool = btn.tool_name in ["select", "pen", "eraser"]
            btn.update_style(btn.tool_name == self.current_tool, is_light, use_indicator=is_tool)

    def _on_undo_redo_visibility_changed(self, visible: bool):
        self.btn_undo.setVisible(visible)
        self.btn_redo.setVisible(visible)
        self.line1.setVisible(visible)
        QTimer.singleShot(10, self._update_indicator_now)

    def _update_indicator_now(self):
        target_btn = None
        if self.current_tool == "select": target_btn = self.btn_select
        elif self.current_tool == "pen": target_btn = self.btn_pen
        elif self.current_tool == "eraser": target_btn = self.btn_eraser
        
        if target_btn:
            self.indicator.setGeometry(target_btn.geometry())

    def _ensure_pen_popup(self):
        if self.pen_popup is None:
            self.pen_popup = PenColorPopup(self.window(), self._pen_colors, self._is_light)
            self.pen_popup.color_selected.connect(self._on_pen_color_selected)

    def _position_pen_popup(self):
        if not self.pen_popup:
            return
        self.pen_popup.adjustSize()
        btn_center = self.btn_pen.mapToGlobal(self.btn_pen.rect().center())
        top_left = self.window().mapToGlobal(self.window().rect().topLeft())
        x = btn_center.x() - self.pen_popup.width() // 2
        y = btn_center.y() - self.btn_pen.height() // 2 - self.pen_popup.height() - 12
        self.pen_popup.move(x, y)

    def _toggle_pen_popup(self):
        self._ensure_pen_popup()
        if self.pen_popup.isVisible():
            self.pen_popup.hide()
        else:
            self._position_pen_popup()
            self.pen_popup.show()

    def _on_pen_button_clicked(self):
        if self.current_tool == "pen":
            self._toggle_pen_popup()
        else:
            self._on_tool_changed("pen", self.pen_clicked)

    def _on_pen_color_selected(self, r, g, b):
        self.pen_color_changed.emit(r, g, b)

    def _on_tool_changed(self, tool_name, signal):
        old_tool = self.current_tool
        self.current_tool = tool_name
        
        target_btn = None
        if tool_name == "select": target_btn = self.btn_select
        elif tool_name == "pen": target_btn = self.btn_pen
        elif tool_name == "eraser": target_btn = self.btn_eraser
        
        if target_btn:
            if not self.indicator.isVisible():
                self.indicator.show()
            self.indicator.setGeometry(target_btn.geometry())

        for btn in [self.btn_select, self.btn_pen, self.btn_eraser]:
            if isinstance(btn, CustomToolButton):
                btn.update_style(btn.tool_name == self.current_tool, self._is_light, use_indicator=True)
        
        if tool_name != "pen" and self.pen_popup and self.pen_popup.isVisible():
            self.pen_popup.hide()
        if hasattr(self, "color_palette"):
            self.color_palette.setVisible(tool_name == "pen")
        if signal:
            signal.emit()
        
        # parent = self.parent()
        # if parent is not None and hasattr(parent, "update_layout"):
        #     parent.update_layout()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self.btn_select = CustomToolButton("Mouse.svg", "Select", self, tool_name="select")
        self.btn_select.clicked.connect(lambda: self._on_tool_changed("select", self.select_clicked))
        layout.addWidget(self.btn_select)

        self.btn_pen = CustomToolButton("Pen.svg", "Pen", self, tool_name="pen")
        self.btn_pen.clicked.connect(self._on_pen_button_clicked)
        layout.addWidget(self.btn_pen)

        self._pen_colors = [
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
        ]

        self.btn_eraser = CustomToolButton("Eraser.svg", "Eraser", self, tool_name="eraser")
        self.btn_eraser.clicked.connect(lambda: self._on_tool_changed("eraser", self.eraser_clicked))
        layout.addWidget(self.btn_eraser)

        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFixedHeight(18)
        layout.addWidget(self.line1)

        self.btn_undo = CustomToolButton("Previous.svg", "Undo", self)
        self.btn_undo.clicked.connect(self.prev_clicked.emit)
        layout.addWidget(self.btn_undo)

        self.btn_redo = CustomToolButton("Next.svg", "Redo", self)
        self.btn_redo.clicked.connect(self.next_clicked.emit)
        layout.addWidget(self.btn_redo)

        self.btn_undo.setVisible(cfg.showUndoRedo.value)
        self.btn_redo.setVisible(cfg.showUndoRedo.value)
        self.line1.setVisible(cfg.showUndoRedo.value)
        cfg.showUndoRedo.valueChanged.connect(self._on_undo_redo_visibility_changed)

        toolbar_plugins = []
        for plugin in self.plugins:
            plugin_type = "toolbar"
            if hasattr(plugin, "get_type"):
                plugin_type = plugin.get_type()
            if plugin_type == "toolbar":
                toolbar_plugins.append(plugin)
        if toolbar_plugins:
            self.line2 = QFrame()
            self.line2.setFrameShape(QFrame.VLine)
            self.line2.setFixedHeight(18)
            layout.addWidget(self.line2)
            for plugin in toolbar_plugins:
                btn = CustomToolButton(plugin.get_icon() or "More.svg", plugin.get_name(), self)
                btn.clicked.connect(plugin.execute)
                layout.addWidget(btn)

        self.line3 = QFrame()
        self.line3.setFrameShape(QFrame.VLine)
        self.line3.setFixedHeight(18)
        layout.addWidget(self.line3)

        self.btn_end = CustomToolButton("Minimaze.svg", "End Show", self, is_exit=True)
        self.btn_end.clicked.connect(self.end_clicked.emit)
        layout.addWidget(self.btn_end)
        
        # Ensure indicator is at the correct position initially
        QTimer.singleShot(0, self._update_indicator_now)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._update_indicator_now)

class PageFlipWidget(QFrame):
    clicked_prev = Signal()
    clicked_next = Signal()
    page_clicked = Signal(QPoint)

    def __init__(self, side="Left", parent=None, height=45):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.side = side
        self.h_val = height
        
        self.update_style()
        self.setFixedSize(180, self.h_val)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.btn_prev = self._create_icon_btn("Previous.svg")
        self.btn_prev.clicked.connect(self.clicked_prev.emit)
        
        self.lbl_page = ClickableLabel("0/0")
        self.lbl_page.setFixedWidth(64)
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.lbl_page.clicked.connect(self.page_clicked)
        
        self.btn_next = self._create_icon_btn("Next.svg")
        self.btn_next.clicked.connect(self.clicked_next.emit)
        
        self.layout.addWidget(self.btn_prev)
        self.layout.addWidget(self.lbl_page)
        self.layout.addWidget(self.btn_next)

    def update_style(self, is_light=True):
        if is_light:
            bg = "rgba(255, 255, 255, 0.85)"
            fg = "#191919"
            border = "rgba(0, 0, 0, 0.08)"
        else:
            bg = "rgba(32, 32, 32, 0.85)"
            fg = "#FFFFFF"
            border = "rgba(255, 255, 255, 0.08)"

        self.setStyleSheet(f"""
            PageFlipWidget {{
                background-color: {bg}; 
                border-radius: {self.h_val // 2}px;
                border: 1px solid {border};
            }}
            QLabel {{
                color: {fg};
                font-weight: 700;
                font-size: 14px;
                font-family: 'MiSans VF', 'MiSans', 'Segoe UI', sans-serif;
            }}
        """)
        for btn in self.findChildren(CustomToolButton):
            btn.set_icon_color(is_light)
            btn.update_style(False, is_light)

    def _create_icon_btn(self, icon_name):
        btn = CustomToolButton(icon_name, "", self)
        btn.setIconSize(QSize(20, 20))
        btn.setFixedSize(36, 36)
        return btn

    def set_page_info(self, current, total):
        self.lbl_page.setText(f"{current}/{total}")
