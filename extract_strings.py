import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

TRANSLATIONS = {
    "常规设置": {
        "zh_TW": "常規設置",
        "en": "General Settings",
        "ja": "一般設定",
        "bo": "རྒྱུན་ལྡན་སྒྲིག་བཀོད།"
    },
    "界面语言": {
        "zh_TW": "介面語言",
        "en": "Interface Language",
        "ja": "インターフェース言語",
        "bo": "ངོས་ཀྱི་སྐད་ཡིག"
    },
    "简体中文": {
        "zh_TW": "簡體中文",
        "en": "Simplified Chinese",
        "ja": "簡体中国語",
        "bo": "རྒྱ་ཡིག་དཀྱུས་མ།"
    },
    "繁體中文": {
        "zh_TW": "繁體中文",
        "en": "Traditional Chinese",
        "ja": "繁体中国語",
        "bo": "རྒྱ་ཡིག་རྙིང་མ།"
    },
    "英语": {
        "zh_TW": "英語",
        "en": "English",
        "ja": "英語",
        "bo": "དབྱིན་ཡིག"
    },
    "日语": {
        "zh_TW": "日語",
        "en": "Japanese",
        "ja": "日本語",
        "bo": "ཉི་ཧོང་སྐད་ཡིག"
    },
    "藏语": {
        "zh_TW": "藏語",
        "en": "Tibetan",
        "ja": "チベット語",
        "bo": "བོད་ཡིག"
    },
    "退出": {
        "zh_TW": "退出",
        "en": "Exit",
        "ja": "終了",
        "bo": "ཕྱིར་འཐེན།"
    },
    "关于": {
        "zh_TW": "關於",
        "en": "About",
        "ja": "バージョン情報",
        "bo": "སྐོར།"
    },
    "确定": {
        "zh_TW": "確定",
        "en": "OK",
        "ja": "OK",
        "bo": "གཏན་འཁེལ།"
    },
    "取消": {
        "zh_TW": "取消",
        "en": "Cancel",
        "ja": "キャンセル",
        "bo": "རྩིས་མེད་གཏོང་བ།"
    },
    "更新": {
        "zh_TW": "更新",
        "en": "Update",
        "ja": "更新",
        "bo": "གསར་སྒྱུར།"
    },
    "检查更新": {
        "zh_TW": "檢查更新",
        "en": "Check for Updates",
        "ja": "更新を確認",
        "bo": "གསར་སྒྱུར་བཤེར་བ།"
    },
    "时钟组件": {
        "zh_TW": "時鐘組件",
        "en": "Clock Widget",
        "ja": "時計ウィジェット",
        "bo": "ཆུ་ཚོད་ཆ་ཤས།"
    },
    "计时器": {
        "zh_TW": "計時器",
        "en": "Timer",
        "ja": "タイマー",
        "bo": "དུས་ཚོད་འཇལ་ཆས།"
    },
    "画笔": {
        "zh_TW": "畫筆",
        "en": "Pen",
        "ja": "ペン",
        "bo": "སྨྱུ་གུ།"
    },
    "橡皮擦": {
        "zh_TW": "橡皮擦",
        "en": "Eraser",
        "ja": "消しゴム",
        "bo": "ས་སྨྱུག་འཕྱིད་བྱེད།"
    },
    "清除墨迹": {
        "zh_TW": "清除墨跡",
        "en": "Clear Ink",
        "ja": "インクを消去",
        "bo": "སྣག་ཚ་གཙང་སེལ།"
    },
    "上一页": {
        "zh_TW": "上一頁",
        "en": "Previous Slide",
        "ja": "前のスライド",
        "bo": "ཤོག་ངོས་གོང་མ།"
    },
    "下一页": {
        "zh_TW": "下一頁",
        "en": "Next Slide",
        "ja": "次のスライド",
        "bo": "ཤོག་ངོས་འོག་མ།"
    },
    "Kazuha 崩溃啦！": {
        "zh_TW": "Kazuha 崩潰啦！",
        "en": "Kazuha Crashed!",
        "ja": "Kazuha がクラッシュしました！",
        "bo": "Kazuha མར་བརྡིབས་སོང།"
    },
    "程序异常退出，错误代码：{}": {
        "zh_TW": "程式異常退出，錯誤代碼：{}",
        "en": "Program exited unexpectedly, error code: {}",
        "ja": "プログラムが異常終了しました。エラーコード：{}",
        "bo": "བྱ་རིམ་རྒྱུན་ལྡན་མིན་པར་ཕྱིར་འཐེན་བྱས་སོང། ནོར་འཁྲུལ་ཨང་རྟགས། {}"
    },
    "复制错误日志": {
        "zh_TW": "複製錯誤日誌",
        "en": "Copy Error Log",
        "ja": "エラーログをコピー",
        "bo": "ནོར་འཁྲུལ་ཉིན་ཐོ་འདྲ་བཤུས།"
    },
    "重启程序": {
        "zh_TW": "重啟程式",
        "en": "Restart Program",
        "ja": "プログラムを再起動",
        "bo": "བྱ་རིམ་བསྐྱར་དུ་སྤར་བ།"
    },
    "退出程序": {
        "zh_TW": "退出程式",
        "en": "Exit Program",
        "ja": "プログラムを終了",
        "bo": "བྱ་རིམ་ཕྱིར་འཐེན།"
    }
}

def extract_strings_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    context_match = re.search(r'QCoreApplication\.translate\("([^"]+)", text\)', content)
    context = context_match.group(1) if context_match else None
    
    strings = []
    pattern = r'\btr\((["\'])(.*?)(?<!\\)\1\)'
    matches = re.finditer(pattern, content)
    for m in matches:
        strings.append((context, m.group(2)))
        
    pattern_direct = r'QCoreApplication\.translate\((["\'])(.*?)\1,\s*(["\'])(.*?)\3\)'
    matches_direct = re.finditer(pattern_direct, content)
    for m in matches_direct:
        strings.append((m.group(2), m.group(4)))
        
    return strings

def update_ts_file(ts_path, all_strings):
    lang = ts_path.stem.split('_')[1] if '_' in ts_path.stem else 'en'
    if lang == 'bo': lang_key = 'bo'
    elif lang == 'ja': lang_key = 'ja'
    elif lang == 'en': lang_key = 'en'
    elif lang == 'zh_TW': lang_key = 'zh_TW'
    elif lang == 'zh_CN': lang_key = 'zh_CN'
    else: lang_key = 'en'

    if not os.path.exists(ts_path):
        root = ET.Element('TS', version='2.1', language=lang)
    else:
        tree = ET.parse(ts_path)
        root = tree.getroot()

    context_map = {}
    for context, text in all_strings:
        if not context: continue
        if context not in context_map:
            context_map[context] = set()
        context_map[context].add(text)

    for context_name, texts in context_map.items():
        context_elem = None
        for c in root.findall('context'):
            if c.find('name').text == context_name:
                context_elem = c
                break
        
        if context_elem is None:
            context_elem = ET.SubElement(root, 'context')
            ET.SubElement(context_elem, 'name').text = context_name
        
        existing_sources = {m.find('source').text: m for m in context_elem.findall('message')}
        
        for text in texts:
            if text not in existing_sources:
                message_elem = ET.SubElement(context_elem, 'message')
                ET.SubElement(message_elem, 'source').text = text
                translation_elem = ET.SubElement(message_elem, 'translation')
                
                if lang_key == 'zh_CN':
                    translation_elem.text = text
                elif text in TRANSLATIONS and lang_key in TRANSLATIONS[text]:
                    translation_elem.text = TRANSLATIONS[text][lang_key]
                else:
                    translation_elem.text = "" 
            else:
                message_elem = existing_sources[text]
                translation_elem = message_elem.find('translation')
                if lang_key == 'zh_CN':
                    if translation_elem is None:
                        translation_elem = ET.SubElement(message_elem, 'translation')
                    if not translation_elem.text or not translation_elem.text.strip():
                        translation_elem.text = text
                elif translation_elem is not None:
                    if not translation_elem.text or not translation_elem.text.strip():
                        if text in TRANSLATIONS and lang_key in TRANSLATIONS[text]:
                            translation_elem.text = TRANSLATIONS[text][lang_key]

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
    tree.write(ts_path, encoding='utf-8', xml_declaration=True)

def main():
    root_dir = Path(".")
    py_files = list(root_dir.glob("**/*.py"))
    
    all_extracted = []
    for py_file in py_files:
        if "venv" in str(py_file) or "site-packages" in str(py_file):
            continue
        try:
            extracted = extract_strings_from_file(py_file)
            if extracted:
                all_extracted.extend(extracted)
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    translations_dir = root_dir / "translations"
    ts_files = list(translations_dir.glob("*.ts"))
    
    for ts_file in ts_files:
        update_ts_file(ts_file, all_extracted)
        print(f"Updated {ts_file}")

if __name__ == "__main__":
    main()
