from plugins.interface import AssistantPlugin


class StatusBarPlugin(AssistantPlugin):
    def get_name(self):
        if isinstance(self.manifest, dict) and "name" in self.manifest:
            return self.manifest["name"]
        return "Status Bar"

    def get_icon(self):
        if isinstance(self.manifest, dict) and "icon" in self.manifest:
            return self.manifest["icon"]
        return ""

