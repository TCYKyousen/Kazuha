from PyQt6.QtCore import Qt, pyqtSignal, QSize, QUrl, QCoreApplication, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtGui import QFont, QDesktopServices

from qfluentwidgets import (
    ScrollArea, ExpandLayout, SettingCardGroup, SwitchSettingCard, OptionsSettingCard,
    PushSettingCard, PrimaryPushSettingCard, HyperlinkCard, FluentIcon as FIF,
    LargeTitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel, IndeterminateProgressRing,
    ProgressBar, InfoBar, InfoBarPosition, SettingCard
)

from ui.custom_settings import SchematicOptionsSettingCard, ScreenPaddingSettingCard
from ui.visual_settings import ClockSettingCard
from controllers.business_logic import cfg, get_app_base_dir
from ui.crash_dialog import CrashDialog, trigger_crash
import subprocess
import datetime
import json

def tr(context, text):
    return QCoreApplication.translate(context, text)

class BaseSettingsPage(ScrollArea):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewport().setStyleSheet("background-color: transparent;")
        self.setStyleSheet("background-color: transparent; border: none;")
        
        self.contentWidget = QWidget()
        self.contentWidget.setObjectName("contentWidget")
        self.contentWidget.setStyleSheet("background-color: transparent;")
        self.setWidget(self.contentWidget)
        
        self.expandLayout = ExpandLayout(self.contentWidget)
        self.expandLayout.setContentsMargins(36, 10, 36, 36)
        self.expandLayout.setSpacing(28)
        
        self.titleLabel = LargeTitleLabel(title, self.contentWidget)
        self.titleLabel.setObjectName("titleLabel")
        self.expandLayout.addWidget(self.titleLabel)

class GeneralInterface(BaseSettingsPage):
    def __init__(self, parent=None):
        super().__init__(tr("GeneralInterface", "常规"), parent)
        self.setObjectName("GeneralInterface")
        
        self.appGroup = SettingCardGroup(tr("GeneralInterface", "应用行为"), self.contentWidget)
        
        self.startupCard = SwitchSettingCard(
            FIF.INFO,
            tr("GeneralInterface", "开机自启动"),
            tr("GeneralInterface", "在 Windows 登录时自动启动应用"),
            configItem=cfg.enableStartUp,
            parent=self.appGroup
        )
        self.notificationCard = SwitchSettingCard(
            FIF.FEEDBACK,
            tr("GeneralInterface", "系统通知"),
            tr("GeneralInterface", "允许应用向系统发送状态通知"),
            configItem=cfg.enableSystemNotification,
            parent=self.appGroup
        )
        self.soundCard = SwitchSettingCard(
            FIF.MUSIC,
            tr("GeneralInterface", "全局音效"),
            tr("GeneralInterface", "在操作时播放交互音效"),
            configItem=cfg.enableGlobalSound,
            parent=self.appGroup
        )
        self.animationCard = SwitchSettingCard(
            FIF.MOVE,
            tr("GeneralInterface", "全局动画"),
            tr("GeneralInterface", "启用界面过渡和状态切换动画"),
            configItem=cfg.enableGlobalAnimation,
            parent=self.appGroup
        )
        self.languageCard = OptionsSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            tr("GeneralInterface", "界面语言"),
            tr("GeneralInterface", "设置应用界面的显示语言（需要重启）"),
            texts=[tr("GeneralInterface", "简体中文"), tr("GeneralInterface", "繁體中文"), tr("GeneralInterface", "English"), tr("GeneralInterface", "日本語"), tr("GeneralInterface", "Bod-yig")],
            parent=self.appGroup
        )
        
        self.appGroup.addSettingCard(self.startupCard)
        self.appGroup.addSettingCard(self.notificationCard)
        self.appGroup.addSettingCard(self.soundCard)
        self.appGroup.addSettingCard(self.animationCard)
        self.appGroup.addSettingCard(self.languageCard)
        
        self.expandLayout.addWidget(self.appGroup)

class PersonalizationInterface(BaseSettingsPage):
    def __init__(self, parent=None):
        super().__init__(tr("PersonalizationInterface", "个性化"), parent)
        self.setObjectName("PersonalizationInterface")
        
        self.styleGroup = SettingCardGroup(tr("PersonalizationInterface", "外观样式"), self.contentWidget)
        
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            tr("PersonalizationInterface", "应用主题"),
            tr("PersonalizationInterface", "切换应用的主题颜色模式"),
            texts=[tr("PersonalizationInterface", "浅色"), tr("PersonalizationInterface", "深色"), tr("PersonalizationInterface", "跟随系统")],
            parent=self.styleGroup
        )
        self.navPosCard = OptionsSettingCard(
            cfg.navPosition,
            FIF.MENU,
            tr("PersonalizationInterface", "导航栏位置"),
            tr("PersonalizationInterface", "调整侧边栏导航项目的显示位置"),
            texts=[tr("PersonalizationInterface", "底部两侧"), tr("PersonalizationInterface", "居中两侧")],
            parent=self.styleGroup
        )
        self.paddingCard = SchematicOptionsSettingCard(
            cfg.screenPadding,
            FIF.LAYOUT,
            tr("PersonalizationInterface", "屏幕边距"),
            tr("PersonalizationInterface", "调整应用窗口与屏幕边缘的间距"),
            texts=[tr("PersonalizationInterface", "较窄"), tr("PersonalizationInterface", "标准"), tr("PersonalizationInterface", "较宽")],
            parent=self.styleGroup
        )
        
        self.styleGroup.addSettingCard(self.themeCard)
        self.styleGroup.addSettingCard(self.navPosCard)
        self.styleGroup.addSettingCard(self.paddingCard)
        
        self.expandLayout.addWidget(self.styleGroup)

class ClockInterface(BaseSettingsPage):
    def __init__(self, parent=None):
        super().__init__(tr("ClockInterface", "时钟组件"), parent)
        self.setObjectName("ClockInterface")
        
        self.clockGroup = SettingCardGroup(tr("ClockInterface", "显示内容与样式"), self.contentWidget)
        
        self.clockEnableCard = SwitchSettingCard(
            FIF.DATE_TIME,
            tr("ClockInterface", "显示悬浮时钟"),
            tr("ClockInterface", "在屏幕上显示一个可自定义的悬浮时钟窗口"),
            configItem=cfg.enableClock,
            parent=self.clockGroup
        )
        
        self.clockPosCard = OptionsSettingCard(
            cfg.clockPosition,
            FIF.HISTORY,
            tr("ClockInterface", "时钟位置"),
            tr("ClockInterface", "调整桌面悬浮时钟在屏幕四角的显示位置"),
            texts=[tr("ClockInterface", "左上角"), tr("ClockInterface", "右上角"), tr("ClockInterface", "左下角"), tr("ClockInterface", "右下角")],
            parent=self.clockGroup
        )
        
        self.clockSettingCard = ClockSettingCard(
            FIF.DATE_TIME,
            tr("ClockInterface", "时钟样式"),
            tr("ClockInterface", "自定义悬浮时钟显示的内容、字体和粗细等外观"),
            parent=self.clockGroup
        )
        
        self.clockGroup.addSettingCard(self.clockEnableCard)
        self.clockGroup.addSettingCard(self.clockPosCard)
        self.clockGroup.addSettingCard(self.clockSettingCard)
        
        self.expandLayout.addWidget(self.clockGroup)
        
        self.clockConflictInfoBar = None
        self._update_clock_settings_for_cicw()
        
    def _update_clock_settings_for_cicw(self):
        running = False
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output('tasklist', startupinfo=startupinfo).decode('gbk', errors='ignore').lower()
            running = ('classisland' in output) or ('classwidgets' in output)
        except Exception:
            running = False
        
        widgets = [self.clockEnableCard, self.clockPosCard, self.clockSettingCard]
        for w in widgets:
            if w is not None:
                w.setEnabled(not running)
        
        if running:
            if not self.clockConflictInfoBar:
                bar = InfoBar.warning(
                    title=tr("ClockInterface", "检测到 ClassIsland/Class Widgets 正在运行"),
                    content=tr("ClockInterface", "ClassIsland/Class Widgets 的部分功能与本应用的时钟组件存在重叠，且另一部分功能甚至可以超出时钟组件所能做到的范围。\n为避免冲突，当前时钟组件已被临时禁用。"),
                    orient=Qt.Orientation.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.BOTTOM,
                    duration=-1,
                    parent=self
                )
                for label in bar.findChildren(QLabel):
                    label.setWordWrap(True)
                self.clockConflictInfoBar = bar
                bar.show()
            else:
                self.clockConflictInfoBar.show()
        else:
            if self.clockConflictInfoBar:
                self.clockConflictInfoBar.hide()

class DebugInterface(BaseSettingsPage):
    def __init__(self, parent=None):
        super().__init__(tr("DebugInterface", "调试"), parent)
        self.setObjectName("DebugInterface")
        
        self.debugGroup = SettingCardGroup(tr("DebugInterface", "危险功能（仅限测试）"), self.contentWidget)
        
        self.crashCard = PushSettingCard(
            tr("DebugInterface", "触发"),
            FIF.DELETE,
            tr("DebugInterface", "崩溃测试"),
            tr("DebugInterface", "仅用于开发调试环境，请勿在正式课堂或演示时点击"),
            parent=self.debugGroup
        )
        self.crashCard.clicked.connect(self.show_crash_dialog)
        
        self.debugGroup.addSettingCard(self.crashCard)
        self.expandLayout.addWidget(self.debugGroup)
        
    def show_crash_dialog(self):
        w = CrashDialog(self.window())
        if w.exec():
            settings = w.get_settings()
            if settings['countdown']:
                QTimer.singleShot(3000, lambda: trigger_crash(settings))
            else:
                trigger_crash(settings)

class UpdateInterface(BaseSettingsPage):
    checkUpdateClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(tr("UpdateInterface", "更新"), parent)
        self.setObjectName("UpdateInterface")
        
        self.updateGroup = SettingCardGroup(tr("UpdateInterface", "软件更新"), self.contentWidget)
        
        self.statusCard = PrimaryPushSettingCard(
            tr("UpdateInterface", "检查更新"),
            FIF.SYNC,
            tr("UpdateInterface", "当前版本"),
            tr("UpdateInterface", "未知"),
            self.updateGroup
        )
        self.statusCard.button.clicked.connect(self._on_check_update_clicked)
        
        self.logCard = SettingCard(
            FIF.INFO,
            tr("UpdateInterface", "更新日志"),
            tr("UpdateInterface", "暂无更新日志信息"),
            self.updateGroup
        )
        
        self.updateGroup.addSettingCard(self.statusCard)
        self.updateGroup.addSettingCard(self.logCard)
        
        self.expandLayout.addWidget(self.updateGroup)
        
        self.progressGroup = SettingCardGroup(tr("UpdateInterface", "下载进度"), self.contentWidget)
        self.progressGroup.setVisible(False)
        
        self.progressCard = SettingCard(FIF.DOWNLOAD, tr("UpdateInterface", "正在下载"), "", self.progressGroup)
        self.progressBar = ProgressBar(self.progressCard)
        self.progressBar.setFixedWidth(200)
        self.progressCard.hBoxLayout.addWidget(self.progressBar)
        self.progressCard.hBoxLayout.addSpacing(16)
        
        self.progressGroup.addSettingCard(self.progressCard)
        self.expandLayout.addWidget(self.progressGroup)
        
        self.currentVersion = "Unknown"
        self._init_version()
        
    def _init_version(self):
        version = "Unknown"
        try:
            base_dir = get_app_base_dir()
            v_path = base_dir / "config" / "version.json"
            with open(v_path, "r", encoding="utf-8") as f:
                info = json.load(f)
                version = info.get("versionName", "Unknown")
        except:
            pass
        self.currentVersion = version
        self.statusCard.setContent(f"v{version}")

    def set_update_info(self, latest_version, latest_log):
        v = latest_version or tr("UpdateInterface", "未知")
        
        if latest_version and self.currentVersion and latest_version != self.currentVersion:
             self.statusCard.setTitle(tr("UpdateInterface", "有可用更新: {version}").format(version=v))
             self.statusCard.setIcon(FIF.SYNC)
             self.statusCard.button.setText(tr("UpdateInterface", "立即下载"))
             self.statusCard.button.setProperty("is_update_ready", True)
        else:
             self.statusCard.setTitle(tr("UpdateInterface", "你使用的是最新版本"))
             self.statusCard.setIcon(FIF.COMPLETED)
             self.statusCard.button.setText(tr("UpdateInterface", "检查更新"))
             self.statusCard.button.setProperty("is_update_ready", False)

        text = latest_log.strip() if latest_log else tr("UpdateInterface", "无更新日志")
        if self.currentVersion and latest_version and self.currentVersion == latest_version:
             self.logCard.setContent(tr("UpdateInterface", "当前版本更新日志：\n{text}").format(text=text))
        else:
             self.logCard.setContent(tr("UpdateInterface", "最新 Release 版本更新日志：\n{text}").format(text=text))

    def _on_check_update_clicked(self):
        if self.statusCard.button.property("is_update_ready"):
            self._start_update_download()
        else:
            self.statusCard.button.setText(tr("UpdateInterface", "正在检查..."))
            self.checkUpdateClicked.emit()
            
    def _start_update_download(self):
        try:
            from PyQt6.QtWidgets import QApplication
            from controllers.business_logic import BusinessLogicController
            app = QApplication.instance()
            controller = None
            if app:
                for w in app.topLevelWidgets():
                    if isinstance(w, BusinessLogicController):
                        controller = w
                        break
            
            if controller:
                info = controller.version_manager.latest_release_info
                if info:
                    asset_url = None
                    for asset in info.get('assets', []):
                        if asset['name'].endswith('.exe'):
                            asset_url = asset['browser_download_url']
                            break
                    
                    if asset_url:
                        self.statusCard.button.setEnabled(False)
                        self.progressGroup.setVisible(True)
                        self.progressCard.setTitle(tr("UpdateInterface", "准备下载..."))
                        
                        controller.version_manager.update_progress.connect(self._on_update_progress)
                        controller.version_manager.update_error.connect(self._on_update_error)
                        controller.version_manager.update_complete.connect(self._on_update_complete)
                        
                        controller.start_download_update(asset_url)
        except Exception:
            pass

    def _on_update_progress(self, val):
        self.progressBar.setValue(val)
        self.progressCard.setTitle(tr("UpdateInterface", "正在下载: {0}%").format(val))
        
    def _on_update_error(self, err):
        self.progressCard.setTitle(tr("UpdateInterface", "更新失败: {0}").format(err))
        self.statusCard.button.setEnabled(True)
        
    def _on_update_complete(self):
        self.progressCard.setTitle(tr("UpdateInterface", "下载完成，准备安装..."))

    def stop_update_loading(self):
        if not self.statusCard.button.property("is_update_ready"):
             self.statusCard.button.setText(tr("UpdateInterface", "检查更新"))
