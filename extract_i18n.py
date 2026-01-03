import re
import os

contexts = {
    "main.py": "Main",
    "crash_handler.py": "CrashHandler",
    "watchdog.py": "CrashHandler",
    "ui/widgets.py": "Widgets",
    "ui/visual_settings.py": "ClockSettings",
    "ui/custom_settings.py": "CustomSettings",
    "ui/settings_window.py": "SettingsWindow",
    "ui/crash_dialog.py": "CrashDialog",
    "controllers/version_manager.py": "VersionManager",
    "controllers/business_logic.py": "BusinessLogic",
}

def extract_strings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'tr\((["\'])(.*?)\1\)', content)
    return [m[1] for m in matches]

all_strings = {}
for file_rel_path, context in contexts.items():
    file_path = os.path.join(os.getcwd(), file_rel_path)
    if os.path.exists(file_path):
        strings = extract_strings(file_path)
        if context not in all_strings:
            all_strings[context] = set()
        for s in strings:
            all_strings[context].add(s)

for context, strings in all_strings.items():
    print(f"Context: {context}")
    for s in sorted(strings):
        print(f"  - {s}")
