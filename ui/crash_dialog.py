from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QCheckBox, QLineEdit, QButtonGroup
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PushButton, RadioButton
from PyQt6.QtCore import Qt, QTimer

class CrashDialog(MessageBoxBase):
    """ Crash Test Configuration Dialog """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("崩溃测试配置", self)

        self.viewLayout.addWidget(self.titleLabel)
        
        # Crash Type Radio Buttons
        self.radioGroup = QButtonGroup(self)
        self.rbNormal = RadioButton("常规崩溃 (Raise Exception)", self)
        self.rbStack = RadioButton("堆栈溢出 (Stack Overflow)", self)
        
        self.radioGroup.addButton(self.rbNormal, 0)
        self.radioGroup.addButton(self.rbStack, 1)
        self.rbNormal.setChecked(True)
        
        self.viewLayout.addWidget(self.rbNormal)
        self.viewLayout.addWidget(self.rbStack)
        
        # Custom Text
        self.textEdit = LineEdit(self)
        self.textEdit.setPlaceholderText("自定义崩溃文本 (仅常规崩溃有效)")
        self.viewLayout.addWidget(self.textEdit)
        
        # Countdown Checkbox
        self.cbCountdown = QCheckBox("倒数 3 秒", self)
        self.cbCountdown.setChecked(True) # Default checked as requested "Selectable"
        self.viewLayout.addWidget(self.cbCountdown)
        
        # Buttons are handled by MessageBoxBase (Yes/Cancel)
        self.yesButton.setText("触发崩溃")
        self.cancelButton.setText("取消")
        
        self.widget.setMinimumWidth(350)
        
    def get_settings(self):
        return {
            'type': 'stack' if self.rbStack.isChecked() else 'normal',
            'text': self.textEdit.text() or "Manual Crash Test",
            'countdown': self.cbCountdown.isChecked()
        }

def trigger_crash(settings):
    """ Helper to execute crash based on settings """
    crash_type = settings['type']
    text = settings['text']
    
    if crash_type == 'normal':
        raise Exception(text)
    elif crash_type == 'stack':
        def infinite_recursion(n):
            infinite_recursion(n+1)
        infinite_recursion(0)
