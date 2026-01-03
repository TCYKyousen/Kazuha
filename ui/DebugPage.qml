import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI 1.0

FluentPage {
    title: "调试"
    
    property var whatsNewWindowRef

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_bug_20_regular"
        title: "组件测试"
        description: "测试应用内的新增组件和交互"
        
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0
            
            SettingItem {
                title: "更新日志窗口"
                description: "展示复刻版的 Whats New 独立窗口 (支持自定义)"
                
                RowLayout {
                    spacing: 8
                    Button {
                        text: "默认展示"
                        onClicked: if (whatsNewWindowRef) whatsNewWindowRef.showWithData()
                    }
                    Button {
                        text: "自定义测试"
                        highlighted: true
                        onClicked: {
                            if (whatsNewWindowRef) {
                                whatsNewWindowRef.showWithData([
                                    {
                                        title: "调试：自定义功能标题",
                                        description: "这是通过调试菜单动态传入的描述文本。现在窗口支持自适应布局，图片也会根据窗口大小自动缩放，长文本会自动启用滚动条。",
                                        linkText: "点击跳转",
                                        image: "file:///" + Bridge.baseDir + "/resources/icons/banner.png",
                                        color: "#ff4757"
                                    }
                                ])
                            }
                        }
                    }
                }
            }
        }
    }
}
