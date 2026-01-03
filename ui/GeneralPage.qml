import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "常规"

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_power_20_regular"
        title: "开机自启"
        description: "在系统启动时自动运行 Kazuha"

        Switch {
            checked: Bridge.enableStartUp
            onToggled: Bridge.enableStartUp = checked
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_alert_20_regular"
        title: "系统通知"
        description: "允许 Kazuha 发送系统通知消息"

        Switch {
            checked: Bridge.enableSystemNotification
            onToggled: Bridge.enableSystemNotification = checked
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_arrow_sync_20_regular"
        title: "自动检查更新"
        description: "在启动时自动检查新版本"

        Switch {
            checked: Bridge.checkUpdateOnStart
            onToggled: Bridge.checkUpdateOnStart = checked
        }
    }
}
