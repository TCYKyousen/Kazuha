from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class AssistantPlugin(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context = None
        self.manifest = {}

    def get_name(self) -> str:
        raise NotImplementedError

    def get_icon(self) -> str:
        raise NotImplementedError

    def get_widget(self) -> QWidget:
        return None

    def execute(self):
        pass

    def terminate(self):
        """Terminate the plugin process if it's running."""
        pass

    def set_context(self, context):
        self.context = context

    def get_type(self) -> str:
        if isinstance(self.manifest, dict):
            return self.manifest.get("type", "toolbar")
        return "toolbar"
