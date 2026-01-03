from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont, QRegion, QPainterPath
from qfluentwidgets import (SettingCard, Theme, isDarkTheme, ComboBox, SwitchButton, 
                            PushButton)

class ClockPreviewWidget(QWidget):
    # Copy of ClockWidget logic but simplified for preview (no window flags)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        inner_layout = QHBoxLayout(self.container)
        inner_layout.setContentsMargins(16, 6, 16, 6)
        inner_layout.setSpacing(12)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
        self.lbl_date = QLabel()
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_date.setStyleSheet("font-size: 14px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
        self.lbl_lunar = QLabel()
        self.lbl_lunar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_lunar.setStyleSheet("font-size: 12px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
        
        inner_layout.addWidget(self.lbl_time)
        inner_layout.addWidget(self.lbl_date)
        inner_layout.addWidget(self.lbl_lunar)
        
        layout.addWidget(self.container)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Default settings
        self.show_seconds = False
        self.show_date = False
        self.show_lunar = False
        self.font_weight = "Bold"
        
        self.update_time()
        self.update_style()
        QTimer.singleShot(0, self._update_radius)

    def update_settings(self, seconds, date, lunar, weight):
        self.show_seconds = seconds
        self.show_date = date
        self.show_lunar = lunar
        self.font_weight = weight
        self.update_style()
        self.update_time()
        QTimer.singleShot(0, self._update_radius)

    def _update_radius(self):
        # Preview use same pill logic
        h = self.container.height()
        if h <= 0:
            h = self.container.sizeHint().height()
        
        # In preview, container height might be fixed or dynamic?
        # self.container.setFixedSize(160, 80) in __init__
        # So h is 80. radius = 40.
        
        radius = int(h / 2)
        
        style = self.container.styleSheet()
        import re
        new_style = re.sub(r"border-radius: .*?;", f"border-radius: {radius}px;", style)
        self.container.setStyleSheet(new_style)

        rect = self.container.rect()
        if rect.width() > 0 and rect.height() > 0:
            r = min(radius, int(rect.height() / 2))
            path = QPainterPath()
            from PyQt6.QtCore import QRectF
            path.addRoundedRect(QRectF(rect), float(r), float(r))
            self.container.setMask(QRegion(path.toFillPolygon().toPolygon()))
        else:
            self.container.clearMask()

    def update_style(self):
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        
        if theme == Theme.LIGHT:
            bg_color = "rgba(255, 255, 255, 240)"
            border_color = "rgba(0, 0, 0, 0.1)"
            text_color = "black"
        else:
            bg_color = "rgba(30, 30, 30, 240)"
            border_color = "rgba(255, 255, 255, 0.1)"
            text_color = "white"
            
        self.container.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 20px;
            }}
        """)
        
        # Update text colors for native labels
        for lbl in [self.lbl_time, self.lbl_date, self.lbl_lunar]:
            style = lbl.styleSheet()
            import re
            style = re.sub(r'color\s*:\s*[^;]+;', '', style)
            lbl.setStyleSheet(style + f" color: {text_color};")

        # Update text colors
        for lbl in [self.lbl_time, self.lbl_date, self.lbl_lunar]:
            style = lbl.styleSheet()
            import re
            style = re.sub(r'color\s*:\s*[^;]+;', '', style)
            lbl.setStyleSheet(style + f" color: {text_color};")

    def update_time(self):
        now = QDateTime.currentDateTime()
        hour = now.time().hour()
        minute = now.time().minute()
        period = "上午" if hour < 12 else "下午"
        time_str = f"{period} {hour:02d}:{minute:02d}"
        
        if self.show_seconds:
             time_str += f":{now.time().second():02d}"
             
        self.lbl_time.setText(time_str)
        
        if self.show_date:
            date_str = f"{now.date().year()}年{now.date().month()}月{now.date().day()}日"
            self.lbl_date.setText(date_str)
            self.lbl_date.setVisible(True)
        else:
            self.lbl_date.setVisible(False)
            
        if self.show_lunar:
            self.lbl_lunar.setText("农历(演示)")
            self.lbl_lunar.setVisible(True)
        else:
            self.lbl_lunar.setVisible(False)


class ClockSettingCard(SettingCard):
    def __init__(self, icon, title, content, parent=None):
        super().__init__(icon, title, content, parent)
        
        # Create a dedicated button to open the configuration flyout
        self.configBtn = PushButton("配置时钟", self)
        self.configBtn.setFixedWidth(120)
        self.configBtn.clicked.connect(self._show_config_flyout)
        
        # Add button to card
        self.hBoxLayout.addWidget(self.configBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        
    def _show_config_flyout(self):
        self._show_overlay_menu()

    def _show_overlay_menu(self):
        from qfluentwidgets import MessageBoxBase
        
        class ClockConfigDialog(MessageBoxBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.titleLabel = QLabel("时钟配置", self)
                self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
                self.viewLayout.addWidget(self.titleLabel)
                
                # Preview
                self.preview = ClockPreviewWidget()
                self.viewLayout.addWidget(self.preview)
                
                # Controls
                self.controlsWidget = QWidget()
                self.controlsLayout = QVBoxLayout(self.controlsWidget)
                self.controlsLayout.setSpacing(10)
                
                # Font Weight
                row_weight = QHBoxLayout()
                label_weight = QLabel("字重")
                label_weight.setStyleSheet("font-size: 14px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
                row_weight.addWidget(label_weight)
                self.weightCombo = ComboBox()
                self.weightCombo.addItems(["Light", "Normal", "DemiBold", "Bold"])
                self.weightCombo.setFixedWidth(120)
                row_weight.addWidget(self.weightCombo)
                self.controlsLayout.addLayout(row_weight)
                
                # Switches
                self.secSwitch = SwitchButton()
                self.secSwitch.setOnText("显示秒")
                self.secSwitch.setOffText("显示秒")
                
                self.dateSwitch = SwitchButton()
                self.dateSwitch.setOnText("显示日期")
                self.dateSwitch.setOffText("显示日期")
                
                self.lunarSwitch = SwitchButton()
                self.lunarSwitch.setOnText("显示农历")
                self.lunarSwitch.setOffText("显示农历")
                
                row1 = QHBoxLayout()
                label_sec = QLabel("秒针显示")
                label_sec.setStyleSheet("font-size: 14px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
                row1.addWidget(label_sec)
                row1.addWidget(self.secSwitch)
                
                row2 = QHBoxLayout()
                label_date = QLabel("公历日期")
                label_date.setStyleSheet("font-size: 14px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
                row2.addWidget(label_date)
                row2.addWidget(self.dateSwitch)
                
                row3 = QHBoxLayout()
                label_lunar = QLabel("农历日期")
                label_lunar.setStyleSheet("font-size: 14px; font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei';")
                row3.addWidget(label_lunar)
                row3.addWidget(self.lunarSwitch)
                
                self.controlsLayout.addLayout(row1)
                self.controlsLayout.addLayout(row2)
                self.controlsLayout.addLayout(row3)
                
                self.viewLayout.addWidget(self.controlsWidget)
                
                # Init values
                from controllers.business_logic import cfg
                self.weightCombo.setCurrentText(cfg.clockFontWeight.value)
                self.secSwitch.setChecked(cfg.clockShowSeconds.value)
                self.dateSwitch.setChecked(cfg.clockShowDate.value)
                self.lunarSwitch.setChecked(cfg.clockShowLunar.value)
                
                # Sync Preview
                self.update_preview()
                
                # Connect
                self.weightCombo.currentTextChanged.connect(self.update_cfg)
                self.secSwitch.checkedChanged.connect(self.update_cfg)
                self.dateSwitch.checkedChanged.connect(self.update_cfg)
                self.lunarSwitch.checkedChanged.connect(self.update_cfg)
                
                # Hide cancel button
                self.cancelButton.hide()
                self.yesButton.setText("完成")
                
                # Update text colors based on theme
                from qfluentwidgets import isDarkTheme
                text_color = "white" if isDarkTheme() else "black"
                for lbl in (self.titleLabel, label_weight, label_sec, label_date, label_lunar):
                    style = lbl.styleSheet()
                    import re
                    style = re.sub(r'color\s*:\s*[^;]+;', '', style)
                    lbl.setStyleSheet(style + f" color: {text_color};")

            def update_cfg(self):
                from controllers.business_logic import cfg
                cfg.clockFontWeight.value = self.weightCombo.currentText()
                cfg.clockShowSeconds.value = self.secSwitch.isChecked()
                cfg.clockShowDate.value = self.dateSwitch.isChecked()
                cfg.clockShowLunar.value = self.lunarSwitch.isChecked()
                self.update_preview()

            def update_preview(self):
                self.preview.update_settings(
                    self.secSwitch.isChecked(),
                    self.dateSwitch.isChecked(),
                    self.lunarSwitch.isChecked(),
                    self.weightCombo.currentText()
                )
                
        w = ClockConfigDialog(self.window())
        w.exec()
