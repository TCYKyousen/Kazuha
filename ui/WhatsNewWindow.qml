import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentWindow {
    id: root
    width: 800
    height: 650
    minimumWidth: 600
    minimumHeight: 500
    title: "What's New (〃'▽'〃)"
    visible: false
    isRinUIWindow: true

    // External properties for dynamic customization
    property var newsData: [
        {
            title: "示例功能标题",
            description: "这是一个示例描述。WhatsNewWindow 现在支持自适应布局，无论窗口缩放到多大都能正常显示。你可以通过调试菜单自定义这里的文本和图片。",
            linkText: "了解更多",
            image: "file:///" + Bridge.baseDir + "/resources/icons/banner.png",
            color: Theme.currentTheme.colors.primaryColor
        }
    ]

    function showWithData(customData) {
        if (customData) {
            newsData = customData
        }
        // Force enable backdrop for Mica/Acrylic if supported
        Utils.backdropEnabled = true
        root.show()
        root.raise()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Top Area: Visuals (Image Carousel) - Adaptive Height
        Rectangle {
            id: visualArea
            Layout.fillWidth: true
            Layout.preferredHeight: parent.height * 0.55
            color: "transparent" // Remove dark background to show Mica
            clip: true
            
            SwipeView {
                id: swipeView
                anchors.fill: parent
                clip: true
                interactive: true

                Repeater {
                    model: newsData
                    Item {
                        RowLayout {
                            anchors.centerIn: parent
                            width: parent.width
                            spacing: parent.width * 0.05
                            
                            // Left Image (Small Preview)
                            Rectangle {
                                Layout.preferredWidth: parent.width * 0.2
                                Layout.preferredHeight: Layout.preferredWidth * 0.6
                                radius: 12
                                color: "#1f2937"
                                opacity: 0.3
                                border.color: "#374151"
                                clip: true
                                visible: root.width > 700
                                Image {
                                    anchors.fill: parent
                                    source: index > 0 ? newsData[index-1].image : ""
                                    fillMode: Image.PreserveAspectCrop
                                }
                            }

                            // Center Image (Main Display)
                            Rectangle {
                                Layout.preferredWidth: root.width > 700 ? parent.width * 0.45 : parent.width * 0.85
                                Layout.preferredHeight: Layout.preferredWidth * 0.55
                                radius: 16
                                color: "#1f2937"
                                border.color: modelData.color
                                border.width: 2
                                clip: true
                                
                                Image {
                                    anchors.fill: parent
                                    source: modelData.image
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    onStatusChanged: if (status == Image.Error) source = "file:///" + Bridge.baseDir + "/resources/icons/banner.png"
                                }

                                Rectangle {
                                    anchors.fill: parent
                                    radius: 16
                                    color: "transparent"
                                    border.color: modelData.color
                                    opacity: 0.2
                                    scale: 1.02
                                }
                            }

                            // Right Image (Small Preview)
                            Rectangle {
                                Layout.preferredWidth: parent.width * 0.2
                                Layout.preferredHeight: Layout.preferredWidth * 0.6
                                radius: 12
                                color: "#1f2937"
                                opacity: 0.3
                                border.color: "#374151"
                                clip: true
                                visible: root.width > 700
                                Image {
                                    anchors.fill: parent
                                    source: index < newsData.length - 1 ? newsData[index+1].image : ""
                                    fillMode: Image.PreserveAspectCrop
                                }
                            }
                        }
                    }
                }
            }

            // Progress Badge
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 20
                anchors.horizontalCenter: parent.horizontalCenter
                width: 80; height: 40
                radius: 20
                color: Qt.rgba(0.17, 0.22, 0.28, 0.8) // Semi-transparent for Mica feel
                Text {
                    anchors.centerIn: parent
                    text: Math.round((swipeView.currentIndex + 1) / newsData.length * 100) + "%"
                    color: "white"
                    font.pixelSize: 16
                    font.bold: true
                }
            }
        }

        // Bottom Area: Content (Text & Controls)
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent" // Show Mica through background

            ScrollView {
                anchors.fill: parent
                contentWidth: availableWidth
                clip: true

                ColumnLayout {
                    width: parent.width
                    anchors.margins: 30
                    spacing: 15

                    // Pagination Info
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 8
                        Icon {
                            name: "ic_fluent_alert_16_regular"
                            size: 16
                            color: Theme.currentTheme.colors.textSecondaryColor
                        }
                        Text {
                            text: (swipeView.currentIndex + 1) + " / " + newsData.length
                            typography: Typography.Caption
                            color: Theme.currentTheme.colors.textSecondaryColor
                        }
                    }

                    // Title
                    Text {
                        Layout.fillWidth: true
                        text: newsData[swipeView.currentIndex] ? newsData[swipeView.currentIndex].title : ""
                        typography: Typography.Subtitle
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        font.bold: true
                        color: Theme.currentTheme.colors.textColor
                    }

                    // Description
                    Text {
                        Layout.fillWidth: true
                        text: newsData[swipeView.currentIndex] ? newsData[swipeView.currentIndex].description : ""
                        typography: Typography.Body
                        color: Theme.currentTheme.colors.textSecondaryColor
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        lineHeight: 1.2
                    }

                    // Action Link
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "→ " + (newsData[swipeView.currentIndex] ? newsData[swipeView.currentIndex].linkText : "")
                        typography: Typography.Body
                        color: Theme.currentTheme.colors.primaryColor
                        font.underline: true
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: console.log("Link clicked")
                        }
                    }

                    Item { Layout.preferredHeight: 20 }

                    // Navigation Buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 15
                        
                        Item { Layout.fillWidth: true }

                        Button {
                            icon.name: "ic_fluent_chevron_left_20_regular"
                            enabled: swipeView.currentIndex > 0
                            onClicked: swipeView.currentIndex--
                        }

                        Button {
                            text: swipeView.currentIndex < newsData.length - 1 ? "下一页" : "关闭"
                            highlighted: true
                            onClicked: {
                                if (swipeView.currentIndex < newsData.length - 1) {
                                    swipeView.currentIndex++
                                } else {
                                    root.close()
                                }
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                }
            }
        }
    }
}
