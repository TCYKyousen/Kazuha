import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "功能"

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_location_20_regular"
        title: "计时器位置"
        description: "调整计时器在屏幕上的显示位置"

        ComboBox {
            model: ["居中", "左上角", "右上角", "左下角", "右下角"]
            currentIndex: Bridge.timerPositionIndex
            onActivated: Bridge.timerPositionIndex = index
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_layout_row_two_20_regular"
        title: "翻页组件位置"
        description: "调整翻页按钮在屏幕上的显示位置"

        ComboBox {
            model: ["底部两侧", "中部两侧"]
            currentIndex: Bridge.navPositionIndex
            onActivated: Bridge.navPositionIndex = index
        }
    }

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_clock_20_regular"
        title: "悬浮时钟"
        description: "在屏幕上显示一个可自定义的悬浮时钟窗口"

        Switch {
            checked: Bridge.enableClock
            onToggled: Bridge.enableClock = checked
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0

            SettingItem {
                title: "时钟位置"
                description: "调整桌面悬浮时钟在屏幕四角的显示位置"
                ComboBox {
                    model: ["左上角", "右上角", "左下角", "右下角"]
                    currentIndex: Bridge.clockPositionIndex
                    onActivated: Bridge.clockPositionIndex = index
                }
            }

            SettingItem {
                title: "字体粗细"
                description: "调整时钟数字的字体显示粗细"
                ComboBox {
                    model: ["细体", "常规", "中粗", "粗体"]
                    currentIndex: Bridge.clockFontWeightIndex
                    onActivated: Bridge.clockFontWeightIndex = index
                }
            }

            SettingItem {
                title: "显示秒数"
                description: "在时钟中显示秒数"
                Switch {
                    checked: Bridge.clockShowSeconds
                    onToggled: Bridge.clockShowSeconds = checked
                }
            }

            SettingItem {
                title: "显示日期"
                description: "在时钟下方显示当前日期"
                Switch {
                    checked: Bridge.clockShowDate
                    onToggled: Bridge.clockShowDate = checked
                }
            }

            SettingItem {
                title: "显示农历"
                description: "在时钟下方显示农历日期"
                Switch {
                    checked: Bridge.clockShowLunar
                    onToggled: Bridge.clockShowLunar = checked
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.margins: 16
                height: 150
                radius: 12
                color: "#1a1a1a"
                clip: true

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 4
                    Text {
                        text: "12:34" + (Bridge.clockShowSeconds ? ":56" : "")
                        font.pixelSize: 48
                        font.weight: [Font.Light, Font.Normal, Font.DemiBold, Font.Bold][Bridge.clockFontWeightIndex]
                        color: "white"
                    }
                    Text {
                        visible: Bridge.clockShowDate
                        text: "2026年1月1日 星期四"
                        font.pixelSize: 14
                        color: "#cccccc"
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        visible: Bridge.clockShowLunar
                        text: "农历冬月十三"
                        font.pixelSize: 12
                        color: "#999999"
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }
        }
    }
}
