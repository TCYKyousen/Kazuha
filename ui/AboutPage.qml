import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "关于"
    
    property var developerDialogRef

    Rectangle {
        Layout.fillWidth: true
        height: 180
        radius: 8
        clip: true
        
        Image {
            anchors.fill: parent
            source: "file:///" + Bridge.baseDir + "/resources/icons/banner.png"
            fillMode: Image.PreserveAspectCrop
        }
        
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "transparent" }
                GradientStop { position: 1.0; color: "#aa000000" }
            }
        }
        
        ColumnLayout {
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.margins: 20
            spacing: 4
            
            Text {
                text: "Kazuha"
                color: "white"
                typography: Typography.Title
            }
            Text {
                text: "Version " + Bridge.versionText
                color: "#eeeeee"
                typography: Typography.Body
            }
        }
    }

    Text {
        Layout.fillWidth: true
        text: "一个基于 Python 和 PySide6 开发的幻灯片演示增强工具。\n\n" +
              "旨在提供更流畅、更美观的演示辅助体验。"
        typography: Typography.Body
        wrapMode: Text.WordWrap
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_person_20_regular"
        title: "开发者"
        description: "了解背后的开发团队"
        
        Button {
            text: "查看详情"
            onClicked: if (developerDialogRef) developerDialogRef.open()
        }
    }

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_book_20_regular"
        title: "开源许可"
        description: "本软件使用的第三方开源组件"
        
        content: ColumnLayout {
            width: parent.width
            Layout.margins: 16
            Text { text: "PySide6 (LGPL v3)"; typography: Typography.Body }
            Text { text: "RinUI (MIT)"; typography: Typography.Body }
            Text { text: "QFluentWidgets (GPL v3)"; typography: Typography.Body }
        }
    }
}
