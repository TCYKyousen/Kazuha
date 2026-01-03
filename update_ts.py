import xml.etree.ElementTree as ET
import os
import re

def update_ts_file(ts_path, all_strings, language_code):
    if not os.path.exists(ts_path):
        root = ET.Element('TS', version="2.1", language=language_code)
    else:
        tree = ET.parse(ts_path)
        root = tree.getroot()

    existing_data = {}
    for context in root.findall('context'):
        name = context.find('name').text
        existing_data[name] = {}
        for message in context.findall('message'):
            source = message.find('source').text
            translation = message.find('translation')
            existing_data[name][source] = translation

    for context_name, strings in all_strings.items():
        context_elem = None
        for c in root.findall('context'):
            if c.find('name').text == context_name:
                context_elem = c
                break
        
        if context_elem is None:
            context_elem = ET.SubElement(root, 'context')
            ET.SubElement(context_elem, 'name').text = context_name
        
        for s in strings:
            if context_name in existing_data and s in existing_data[context_name]:
                continue
            
            message_elem = ET.SubElement(context_elem, 'message')
            ET.SubElement(message_elem, 'source').text = s
            trans_elem = ET.SubElement(message_elem, 'translation')
            if language_code == 'zh_CN':
                trans_elem.text = s

    for context in root.findall('context'):
        messages = context.findall('message')
        messages.sort(key=lambda m: m.find('source').text or "")
        for m in messages:
            context.remove(m)
        for m in messages:
            context.append(m)

    def indent(elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(root)
    tree = ET.ElementTree(root)
    with open(ts_path, 'wb') as f:
        f.write(b"<?xml version='1.0' encoding='utf-8'?>\n")
        tree.write(f, encoding='utf-8', xml_declaration=False)

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
    if not os.path.exists(file_path): return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'tr\((["\'])(.*?)\1\)', content)
    return [m[1] for m in matches]

all_strings = {}
for file_rel_path, context in contexts.items():
    strings = extract_strings(file_rel_path)
    if context not in all_strings:
        all_strings[context] = set()
    for s in strings:
        all_strings[context].add(s)

ts_files = {
    "en": "translations/kazuha_en.ts",
    "ja": "translations/kazuha_ja.ts",
    "zh_TW": "translations/kazuha_zh_TW.ts",
    "bo": "translations/kazuha_bo.ts",
    "zh_CN": "translations/kazuha_zh_CN.ts",
}

for lang, path in ts_files.items():
    print(f"Updating {path}...")
    update_ts_file(path, all_strings, lang)
