import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"

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
        
        Button {
            icon.source: "../../images/themes/default/mActionAddLayer.svg"
            icon.color: "transparent"
            icon.width: 16
            icon.height: 16
            display: AbstractButton.IconOnly
            Layout.fillWidth: true
            onClicked: {
                if (typeof mapBackend !== 'undefined') {
                    var filePath = mapBackend.open_vector_dialog()
                    if (filePath) {
                        var success = mapBackend.add_vector_layer(filePath)
                        if (success) {
                            var fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                            fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                            layerListModel.append({
                                layerName: fileName,
                                layerType: "vector",
                                visible: true
                            })
                            layersPanel.layerAdded(fileName, "vector")
                        }
                    }
                }
            }
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar camada"
        }
        
        Button {
            icon.source: "../../images/themes/default/mActionRemoveLayer.svg"
            icon.color: "transparent"
            icon.width: 16
            icon.height: 16
            display: AbstractButton.IconOnly
            Layout.fillWidth: true
            enabled: layerList.currentIndex >= 0
            onClicked: {
                if (layerList.currentIndex >= 0) {
                    var layerName = layerListModel.get(layerList.currentIndex).layerName
                    if (typeof mapBackend !== 'undefined') {
                        mapBackend.remove_layer(layerName)
                    }
                    layerListModel.remove(layerList.currentIndex)
                    layersPanel.layerRemoved(layerName)
                    layersPanel.statusMessage("Removido: " + layerName)
                }
            }
            ToolTip.visible: hovered
            ToolTip.text: "Remover camada selecionada"
        }
    }
}

