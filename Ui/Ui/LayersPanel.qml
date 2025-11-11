import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

ColumnLayout {
    id: layersPanel
    
    // Propriedades exportadas
    property alias layerList: layerList
    property alias layerListModel: layerListModel
    
    // Sinais
    signal layerAdded(string fileName, string layerType)
    signal layerRemoved(string layerName)
    signal layerVisibilityChanged(string layerName, bool visible)
    signal statusMessage(string message)
    
    spacing: 5
    
    ListView {
        id: layerList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        
        model: ListModel {
            id: layerListModel
        }
        
        delegate: ItemDelegate {
            width: layerList.width
            height: 40
            
            background: Rectangle {
                color: layerList.currentIndex === index ? AppTheme.accentDark : "#3e3e42"
                border.color: AppTheme.border
                border.width: 1
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 8
                
                CheckBox {
                    checked: model.visible
                    onToggled: {
                        layerListModel.setProperty(index, "visible", checked)
                        layersPanel.layerVisibilityChanged(model.layerName, checked)
                        layersPanel.statusMessage(model.layerName + " " + (checked ? "visível" : "oculto"))
                    }
                }
                
                Label {
                    text: model.layerType === "vector" ? "📐" : "🖼"
                    font.pixelSize: 14
                }
                
                Label {
                    text: model.layerName
                    color: AppTheme.text
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                    font.pixelSize: 11
                }
            }
            
            onClicked: {
                layerList.currentIndex = index
                layersPanel.statusMessage("Selecionado: " + model.layerName)
            }
        }
        
        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }
    }
    
    RowLayout {
        Layout.fillWidth: true
        spacing: 5
    }
}

