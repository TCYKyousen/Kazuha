import sys
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QToolButton, QSlider, QGraphicsDropShadowEffect,
    QStyleOption, QStyle
)
from PySide6.QtCore import (
    Qt, QRect, QPoint, QSize, Signal, Property, 
    QEasingCurve, QPropertyAnimation
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QScreen, 
    QPixmap, QCursor, QPainterPath, QRegion
)
from qfluentwidgets import (
    Slider, setTheme, Theme, qconfig, FluentIcon as FIF
)
import os

class SpotlightToolButton(QFrame):
    clicked = Signal()

    def __init__(self, icon, tooltip, parent=None, is_active=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.icon = icon
        self.is_active = is_active
        
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setFixedSize(38, 38)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        self._update_icon()
        self.update_style()

    def _update_icon(self):
        color = QColor("#3275F5") if self.is_active else QColor("#FFFFFF")
        # 使用 FluentIcon 的 icon() 方法生成带颜色的图标并转为 pixmap
        pixmap = self.icon.icon(color=color).pixmap(20, 20)
        self.icon_label.setPixmap(pixmap)

    def set_active(self, active):
        if self.is_active != active:
            self.is_active = active
            self._update_icon()
            self.update_style()

    def update_style(self):
        bg = "rgba(255, 255, 255, 0.1)" if self.is_active else "transparent"
        self.setStyleSheet(f"""
            SpotlightToolButton {{
                background-color: {bg};
                border-radius: 19px;
            }}
            SpotlightToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class SpotlightControlPanel(QFrame):
    """聚光灯控制面板 - 像素级还原顶层工具栏风格"""
    mode_changed = Signal(str)
    lights_off_toggled = Signal(bool)
    opacity_changed = Signal(int)
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SpotlightControlPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)
        self.layout.setSpacing(4)
        self.layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        
        # 模式切换
        # 只保留放大镜按钮，点击切换 放大/高亮
        self.btn_magnify = SpotlightToolButton(FIF.ZOOM_IN, "放大镜模式", self)
        self.btn_magnify.clicked.connect(self._on_magnify_click)
        self.layout.addWidget(self.btn_magnify)

        # 分割线
        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFixedWidth(1)
        self.line1.setFixedHeight(24)
        self.line1.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); border: none; margin: 0 4px;")
        self.layout.addWidget(self.line1)

        # 关灯模式
        self.btn_lights = SpotlightToolButton(FIF.BRIGHTNESS, "关灯模式", self)
        self.btn_lights.clicked.connect(self._toggle_lights)
        self.layout.addWidget(self.btn_lights)

        # 暗度调节
        self.opacity_slider = Slider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(180)
        self.opacity_slider.setFixedWidth(80)
        self.opacity_slider.valueChanged.connect(self.opacity_changed)
        self.layout.addWidget(self.opacity_slider)

        # 关闭
        self.btn_close = SpotlightToolButton(FIF.CLOSE, "关闭", self)
        self.btn_close.clicked.connect(self.close_requested)
        self.layout.addWidget(self.btn_close)

        # 整体样式
        self.setStyleSheet("""
            #SpotlightControlPanel {
                background-color: #202020;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 27px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def _on_magnify_click(self):
        # 切换放大镜状态
        is_magnify = not self.btn_magnify.is_active
        self.btn_magnify.set_active(is_magnify)
        self.mode_changed.emit('magnify' if is_magnify else 'highlight')

    def _toggle_lights(self):
        active = not self.btn_lights.is_active
        self.btn_lights.set_active(active)
        # 关灯时禁用滑块，开灯时启用
        self.opacity_slider.setEnabled(not active)
        self.lights_off_toggled.emit(active)

class SpotlightWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化状态
        self.selection_rect = QRect()
        self.start_point = QPoint()
        self.is_selecting = False
        self.mode = 'highlight' # 'highlight', 'magnify'
        self.lights_off = False
        self.dim_opacity = 180
        self.magnification = 2.0
        self.original_selection_rect = None
        
        # 屏幕截图（用于放大镜）
        self.full_screen_pixmap = None
        
        # 控制面板
        self.control_panel = SpotlightControlPanel()
        self.control_panel.mode_changed.connect(self.set_mode)
        self.control_panel.lights_off_toggled.connect(self.set_lights_off)
        self.control_panel.opacity_changed.connect(self.set_opacity)
        self.control_panel.close_requested.connect(self.close)
        
        # 全屏覆盖
        self.update_geometry()
        self.capture_screen()

    def update_geometry(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def capture_screen(self):
        # 抓取所有屏幕的组合
        desktop = QApplication.primaryScreen()
        screens = QApplication.screens()
        
        # 计算总范围
        total_rect = QRect()
        for s in screens:
            total_rect = total_rect.united(s.geometry())
        
        self.setGeometry(total_rect)
        
        # 抓取整个桌面
        self.full_screen_pixmap = QPixmap(total_rect.size())
        painter = QPainter(self.full_screen_pixmap)
        for s in screens:
            painter.drawPixmap(s.geometry().topLeft() - total_rect.topLeft(), s.grabWindow(0))
        painter.end()

    def set_mode(self, mode):
        if mode == 'magnify' and self.mode == 'highlight' and not self.selection_rect.isEmpty():
            # 记录原始选区，并按比例放大选区本身
            self.original_selection_rect = QRect(self.selection_rect)
            
            center = self.selection_rect.center()
            new_w = self.selection_rect.width() * self.magnification
            new_h = self.selection_rect.height() * self.magnification
            
            self.selection_rect = QRect(
                int(center.x() - new_w / 2),
                int(center.y() - new_h / 2),
                int(new_w),
                int(new_h)
            )
            # 边界检查
            self.selection_rect = self.selection_rect.intersected(self.rect())
            self._update_panel_position()
        elif mode == 'highlight' and self.mode == 'magnify' and self.original_selection_rect:
            # 恢复原始选区
            self.selection_rect = QRect(self.original_selection_rect)
            self.original_selection_rect = None
            self._update_panel_position()

        self.mode = mode
        self.update()

    def _update_panel_position(self):
        # 显示控制面板在选区正下方
        if not self.selection_rect.isEmpty():
            # 确保布局已计算
            self.control_panel.adjustSize()
            panel_width = self.control_panel.width()
            panel_height = self.control_panel.height()
            
            # 计算选区在全局屏幕中的位置
            selection_global_rect = QRect(
                self.mapToGlobal(self.selection_rect.topLeft()),
                self.selection_rect.size()
            )
            
            panel_x = selection_global_rect.center().x() - panel_width / 2
            panel_y = selection_global_rect.bottom() + 12 # 距离选区底部 12px
            
            panel_pos = QPoint(int(panel_x), int(panel_y))
            
            # 获取当前鼠标所在的屏幕
            current_screen = QApplication.screenAt(QCursor.pos())
            if not current_screen:
                current_screen = QApplication.primaryScreen()
            screen_geo = current_screen.geometry()
            
            # 边界检查
            if panel_pos.x() < screen_geo.left() + 10:
                panel_pos.setX(screen_geo.left() + 10)
            if panel_pos.x() + panel_width > screen_geo.right() - 10:
                panel_pos.setX(screen_geo.right() - panel_width - 10)
            
            # 如果下方放不下，或者超出了当前屏幕底部
            if panel_pos.y() + panel_height > screen_geo.bottom() - 10:
                panel_pos.setY(selection_global_rect.top() - panel_height - 12)
            
            self.control_panel.move(panel_pos)
            self.control_panel.show()
            # 确保在顶层
            self.control_panel.raise_()

    def set_lights_off(self, enabled):
        self.lights_off = enabled
        self.update()

    def set_opacity(self, value):
        self.dim_opacity = value
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.selection_rect = QRect(self.start_point, QSize())
            self.original_selection_rect = None
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_rect = QRect(self.start_point, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            self._update_panel_position()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. 绘制背景阴影
        overlay_color = QColor(0, 0, 0, 255 if self.lights_off else self.dim_opacity)
        
        path = QPainterPath()
        path.addRect(self.rect())
        
        if not self.selection_rect.isEmpty():
            # 镂空选区
            selection_path = QPainterPath()
            selection_path.addRoundedRect(self.selection_rect, 4, 4)
            path = path.subtracted(selection_path)
            
        painter.fillPath(path, QBrush(overlay_color))

        # 2. 如果是放大模式且有选区，绘制放大内容
        if self.mode == 'magnify' and not self.selection_rect.isEmpty() and self.full_screen_pixmap:
            if self.original_selection_rect:
                # 如果有记录原始选区，则将原始选区内容拉伸绘制到当前选区
                source_rect = self.original_selection_rect
            else:
                # 如果没有原始选区（例如直接在放大模式下绘制），则按比例缩放中心区域
                w = self.selection_rect.width() / self.magnification
                h = self.selection_rect.height() / self.magnification
                center = self.selection_rect.center()
                source_rect = QRect(
                    int(center.x() - w/2), 
                    int(center.y() - h/2), 
                    int(w), 
                    int(h)
                )
            
            painter.drawPixmap(self.selection_rect, self.full_screen_pixmap, source_rect)

        # 3. 绘制边框
        if not self.selection_rect.isEmpty():
            pen = QPen(QColor(50, 117, 245), 2) # Kazuha blue
            painter.setPen(pen)
            painter.drawRoundedRect(self.selection_rect, 4, 4)

    def showEvent(self, event):
        super().showEvent(event)
        # 每次显示时重新抓取屏幕，确保放大镜内容是最新的
        self.capture_screen()

    def closeEvent(self, event):
        self.control_panel.close()
        super().closeEvent(event)
