import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "界面"

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_paint_brush_20_regular"
        title: "应用主题"
        description: "调整应用的外观颜色模式"
        
        ComboBox {
            model: ["浅色", "深色", "跟随系统"]
            currentIndex: Bridge.themeModeIndex
            onActivated: {
                Bridge.themeModeIndex = index
                ThemeManager.toggle_theme(Bridge.themeMode)
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0

            SettingItem {
                title: "主题预览"
                description: "当前主题颜色的实时预览"
                
                Rectangle {
                    width: 300
                    height: 80
                    radius: 8
                    color: Theme.currentTheme.colors.backgroundAcrylicColor
                    border.color: Theme.currentTheme.colors.controlBorderColor
                    
                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 20
                        
                        Rectangle {
                            width: 40; height: 40; radius: 20
                            color: Theme.currentTheme.colors.primaryColor
                        }
                        ColumnLayout {
                            Text { text: "预览文本"; color: Theme.currentTheme.colors.textColor; typography: Typography.Body }
                            Text { text: "次要信息"; color: Theme.currentTheme.colors.textSecondaryColor; typography: Typography.Caption }
                        }
                    }
                }
            }
        }
    }

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_flash_20_regular"
        title: "界面反馈"
        description: "管理应用的视觉动画和声音反馈"
        
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0
            
            SettingItem {
                title: "全局音效"
                description: "开启或关闭应用内的所有音效"
                Switch {
                    checked: Bridge.enableGlobalSound
                    onToggled: Bridge.enableGlobalSound = checked
                }
            }
            
            SettingItem {
                title: "全局动画"
                description: "开启或关闭界面过渡动画"
                Switch {
                    checked: Bridge.enableGlobalAnimation
                    onToggled: Bridge.enableGlobalAnimation = checked
                }
            }
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_full_screen_zoom_20_regular"
        title: "屏幕边距"
        description: "调整所有组件距离屏幕边缘的距离"

        ComboBox {
            model: ["较小", "正常", "较大"]
            currentIndex: Bridge.screenPaddingIndex
            onActivated: Bridge.screenPaddingIndex = index
        }
    }
}
