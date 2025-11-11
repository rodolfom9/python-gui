import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"

Rectangle {
    id: mapCanvasContainer
    
    property string activeTool: "pan"
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 5
        
        Label {
            text: "Mapa Interativo com Map Tools"
            font.bold: true
            font.pixelSize: 14
            color: AppTheme.text
            Layout.alignment: Qt.AlignHCenter
        }
        
        Rectangle {
            id: mapCanvas
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ffffff"
            border.color: AppTheme.border
            border.width: 2
            
            // Imagem do mapa renderizado
            Image {
                id: mapImage
                anchors.fill: parent
                fillMode: Image.Stretch
                cache: false
                
                // Usa o ImageProvider do Python
                source: "image://mapimage/map?" + (typeof mapBackend !== 'undefined' ? mapBackend.update_counter : 0)
                
                // Mensagem quando não há mapa
                Label {
                    anchors.centerIn: parent
                    text: "Adicione uma camada vetorial ou raster\npara visualizar o mapa"
                    horizontalAlignment: Text.AlignHCenter
                    color: AppTheme.textMuted
                    font.pixelSize: 14
                    visible: mapImage.status !== Image.Ready
                }
            }
            
            // MouseArea para interação
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                hoverEnabled: true
                
                property point lastPos
                
                onPressed: (mouse) => {
                    lastPos = Qt.point(mouse.x, mouse.y)
                }
                
                onPositionChanged: (mouse) => {
                    coordLabel.text = "Coordenadas: " + mouse.x + ", " + mouse.y
                }
                
                onReleased: (mouse) => {
                }
                
                onWheel: (wheel) => {
                    // Implementar zoom com scroll
                    if (wheel.angleDelta.y > 0) {
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.zoom_in()
                        }
                    } else {
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.zoom_out()
                        }
                    }
                }
            }
            
            // Notifica mudança de tamanho
            onWidthChanged: {
                if (typeof mapBackend !== 'undefined' && width > 0 && height > 0) {
                    mapBackend.set_canvas_size(Math.floor(width), Math.floor(height))
                }
            }
            
            onHeightChanged: {
                if (typeof mapBackend !== 'undefined' && width > 0 && height > 0) {
                    mapBackend.set_canvas_size(Math.floor(width), Math.floor(height))
                }
            }
        }
        
        Label {
            id: coordLabel
            text: "Coordenadas: 0, 0"
            color: AppTheme.textSecondary
            font.pixelSize: 10
        }
    }
}

