import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0
import "."

FluentWindow {
    id: window
    width: 900
    height: 640
    title: "界面设置 - Kazuha"
    visible: true
    isRinUIWindow: true

    titleBarArea: RowLayout {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8
        
        Icon {
            name: "ic_fluent_info_16_regular"
            size: 16
            color: Theme.currentTheme.colors.textSecondaryColor
        }
        
        Text {
            text: "v" + Bridge.versionText
            typography: Typography.Caption
            color: Theme.currentTheme.colors.textSecondaryColor
        }
    }

    Component.onCompleted: {
        navigationView.push(generalPage)
        ThemeManager.toggle_theme(Bridge.themeMode)
    }

    navigationItems: [
        { title: "常规", icon: "ic_fluent_settings_20_regular", page: generalPage },
        { title: "界面", icon: "ic_fluent_paint_brush_20_regular", page: uiPage },
        { title: "功能", icon: "ic_fluent_flash_20_regular", page: featurePage },
        { title: "更新", icon: "ic_fluent_arrow_sync_20_regular", page: updatePage },
        { title: "关于", icon: "ic_fluent_info_20_regular", page: aboutPage },
        { title: "调试", icon: "ic_fluent_bug_20_regular", page: debugPage }
    ]

    Dialog {
        id: updateDialog
        title: "检查更新"
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            spacing: 12
            Layout.fillWidth: true
            Text {
                text: Bridge.isUpdating ? "正在检查并下载更新..." : "当前已是最新版本"
                typography: Typography.Body
            }
            ProgressBar {
                visible: Bridge.isUpdating
                Layout.fillWidth: true
            }
        }
    }

    Dialog {
        id: developerDialog
        title: "开发者信息"
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            spacing: 16
            Layout.fillWidth: true
            
            RowLayout {
                spacing: 16
                Rectangle {
                    width: 64; height: 64; radius: 32
                    color: Theme.currentTheme.colors.primaryColor
                    Icon {
                        anchors.centerIn: parent
                        name: "ic_fluent_person_24_filled"
                        color: "white"
                        size: 32
                    }
                }
                ColumnLayout {
                    Text { text: "Kazuha Team"; typography: Typography.Subtitle }
                    Text { text: "Main Maintainer"; typography: Typography.Caption; color: Theme.currentTheme.colors.textSecondaryColor }
                }
            }
            
            Text {
                Layout.fillWidth: true
                text: "一个热爱开源和幻灯片演示的开发团队。\n我们的目标是让演示变得更简单、更优雅。"
                typography: Typography.Body
                wrapMode: Text.WordWrap
            }
        }
    }

    WhatsNewWindow {
        id: whatsNewWindow
    }

    Component {
        id: generalPage
        GeneralPage {}
    }

    Component {
        id: uiPage
        InterfacePage {}
    }

    Component {
        id: featurePage
        FeaturesPage {}
    }

    Component {
        id: updatePage
        UpdatePage {
            updateDialogRef: window.updateDialog
        }
    }

    Component {
        id: aboutPage
        AboutPage {
            developerDialogRef: window.developerDialog
        }
    }

    Component {
        id: debugPage
        DebugPage {
            whatsNewWindowRef: window.whatsNewWindow
        }
    }
}
