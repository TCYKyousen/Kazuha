import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "更新"
    
    property var updateDialogRef

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 24

        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            Icon {
                name: "ic_fluent_checkmark_circle_20_regular"
                size: 48
                color: Theme.currentTheme.colors.primaryColor
            }

            ColumnLayout {
                Text {
                    text: Bridge.updateStatusTitle
                    typography: Typography.Subtitle
                }
                Text {
                    text: Bridge.updateLastCheckText
                    typography: Typography.Caption
                    color: Theme.currentTheme.colors.textSecondaryColor
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "检查更新"
                highlighted: true
                onClicked: {
                    Bridge.checkUpdate()
                    if (updateDialogRef) updateDialogRef.open()
                }
            }
        }

        SettingExpander {
            Layout.fillWidth: true
            icon.name: "ic_fluent_document_text_20_regular"
            title: "更新日志"
            description: "查看当前版本的更新内容"
            expanded: true

            content: ColumnLayout {
                width: parent.width
                Layout.margins: 16
                
                Text {
                    Layout.fillWidth: true
                    text: Bridge.updateLogs
                    textFormat: Text.MarkdownText
                    wrapMode: Text.WordWrap
                    typography: Typography.Body
                }
            }
        }
    }
}
