import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

Dialog {
    id: root
    width: 680
    height: 520
    title: "What's New (〃'▽'〃)"
    standardButtons: Dialog.NoButton // We use custom buttons

    property var newsData: [
        {
            title: "Comprehensive Notification System Upgrade",
            description: "A completely rebuilt notification system that supports in-app notification toggles, intelligent ringtone configuration, and customizable notification providers. Bringing users a more flexible and intelligent notification exp...",
            linkText: "Configure Notifications on Settings",
            image: "ic_fluent_alert_24_regular",
            color: "#00c4b4"
        },
        {
            title: "Enhanced Performance & Stability",
            description: "We've optimized the core engine to reduce memory usage by 30% and improved start-up speed. The application now runs smoother even on lower-end hardware.",
            linkText: "View Performance Logs",
            image: "ic_fluent_flash_24_regular",
            color: "#4a90e2"
        },
        {
            title: "New UI Themes & Customization",
            description: "Explore a variety of new themes including Acrylic and Mica effects. Customize your workspace with new accent colors and layout options to match your workflow.",
            linkText: "Change Theme in Settings",
            image: "ic_fluent_paint_brush_24_regular",
            color: "#f5a623"
        }
    ]

    contentItem: Item {
        clip: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // Top Area: Visuals
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 280
                color: "#0d1117"
                
                // Background Glow
                Rectangle {
                    anchors.centerIn: parent
                    width: 400; height: 400
                    radius: 200
                    color: newsData[swipeView.currentIndex].color
                    opacity: 0.15
                    layer.enabled: true
                    // layer.effect: GaussianBlur { radius: 100 } // Not available in all Qt versions, skipping for safety
                }

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
                                spacing: 20
                                
                                // Left Card (Small)
                                Rectangle {
                                    width: 120; height: 80
                                    radius: 12
                                    color: "#1f2937"
                                    opacity: 0.5
                                    border.color: "#374151"
                                    Icon {
                                        anchors.centerIn: parent
                                        name: modelData.image
                                        color: "white"
                                        size: 24
                                    }
                                }

                                // Center Card (Main)
                                Rectangle {
                                    width: 280; height: 140
                                    radius: 16
                                    color: "#1f2937"
                                    border.color: modelData.color
                                    border.width: 2
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 20
                                        spacing: 12
                                        
                                        RowLayout {
                                            spacing: 10
                                            Icon { name: modelData.image; color: "white"; size: 24 }
                                            Rectangle { width: 80; height: 8; radius: 4; color: "#374151" }
                                        }
                                        
                                        Rectangle { Layout.fillWidth: true; height: 8; radius: 4; color: "#374151" }
                                        Rectangle { width: 120; height: 8; radius: 4; color: "#374151" }
                                    }

                                    // Inner Glow Effect
                                    Rectangle {
                                        anchors.fill: parent
                                        radius: 16
                                        color: "transparent"
                                        border.color: modelData.color
                                        opacity: 0.3
                                        scale: 1.05
                                    }
                                }

                                // Right Card (Small)
                                Rectangle {
                                    width: 120; height: 80
                                    radius: 12
                                    color: "#1f2937"
                                    opacity: 0.5
                                    border.color: "#374151"
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 60; height: 8; radius: 4; color: "#374151"
                                    }
                                }
                            }
                        }
                    }
                }

                // Progress Badge (e.g., "80%")
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 20
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 80; height: 44
                    radius: 22
                    color: "#2d3748"
                    Text {
                        anchors.centerIn: parent
                        text: Math.round((swipeView.currentIndex + 1) / newsData.length * 100) + "%"
                        color: "white"
                        font.pixelSize: 18
                        font.bold: true
                    }
                }
            }

            // Bottom Area: Content
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.currentTheme.colors.backgroundColor

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 32
                    spacing: 16

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
                        text: newsData[swipeView.currentIndex].title
                        typography: Typography.Subtitle
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        font.bold: true
                    }

                    // Description
                    Text {
                        Layout.fillWidth: true
                        text: newsData[swipeView.currentIndex].description
                        typography: Typography.Body
                        color: Theme.currentTheme.colors.textSecondaryColor
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        maximumLineCount: 3
                        elide: Text.ElideRight
                    }

                    // Link
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "→ " + newsData[swipeView.currentIndex].linkText
                        typography: Typography.Body
                        color: Theme.currentTheme.colors.primaryColor
                        font.underline: true
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: console.log("Link clicked")
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // Navigation Buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Item { Layout.fillWidth: true }

                        Button {
                            id: prevBtn
                            icon.name: "ic_fluent_chevron_left_20_regular"
                            enabled: swipeView.currentIndex > 0
                            onClicked: swipeView.currentIndex--
                        }

                        Button {
                            id: nextBtn
                            icon.name: "ic_fluent_chevron_right_20_regular"
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
