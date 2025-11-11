import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: propertiesPanel
    
    property var layerModel
    property int currentLayerIndex: -1
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        
        Label {
            text: "Propriedades da Camada Selecionada"
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 12
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            TextArea {
                readOnly: true
                wrapMode: TextArea.Wrap
                color: AppTheme.textSecondary
                text: currentLayerIndex >= 0 && layerModel ? 
                    "Nome: " + layerModel.get(currentLayerIndex).layerName + "\n" +
                    "Tipo: " + layerModel.get(currentLayerIndex).layerType + "\n" +
                    "Visível: " + layerModel.get(currentLayerIndex).visible
                    : "Selecione uma camada"
                
                background: Rectangle {
                    color: "#2d2d30"
                    border.color: AppTheme.border
                    border.width: 1
                }
            }
        }
    }
}

