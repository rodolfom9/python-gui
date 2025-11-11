import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: mapCanvasContainer
    
    property string activeTool: "pan"
    property bool isDrawingBox: false
    property point boxStart: Qt.point(0, 0)
    property point boxEnd: Qt.point(0, 0)
    
    signal featureSelected(int featureId)
    signal featuresSelected(var featureIds)
    signal featureHovered(int featureId, point pos)
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 5
        
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
            }
            
            // MouseArea para interação
            MouseArea {
                id: mapMouseArea
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                hoverEnabled: true
                
                property point lastPos
                property bool isPanning: false
                
                cursorShape: {
                    if (activeTool === "pan" && isPanning) return Qt.ClosedHandCursor
                    if (activeTool === "pan") return Qt.OpenHandCursor
                    if (activeTool === "select" || activeTool === "boxSelect") return Qt.CrossCursor
                    if (activeTool === "identify") return Qt.WhatsThisCursor
                    return Qt.ArrowCursor
                }
                
                onPressed: (mouse) => {
                    lastPos = Qt.point(mouse.x, mouse.y)
                    
                    if (activeTool === "pan" && mouse.button === Qt.LeftButton) {
                        isPanning = true
                    } else if (activeTool === "boxSelect" && mouse.button === Qt.LeftButton) {
                        isDrawingBox = true
                        boxStart = Qt.point(mouse.x, mouse.y)
                        boxEnd = Qt.point(mouse.x, mouse.y)
                    } else if (activeTool === "select" && mouse.button === Qt.LeftButton) {
                        // Seleciona feature no ponto clicado
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.select_feature_at(mouse.x, mouse.y)
                        }
                        mapCanvasContainer.featureSelected(-1) // -1 para indicar clique simples
                    }
                }
                
                onPositionChanged: (mouse) => {
                    // Atualiza coordenadas
                    if (typeof mapBackend !== 'undefined') {
                        var worldCoords = mapBackend.pixel_to_world(mouse.x, mouse.y)
                        if (worldCoords) {
                            coordLabel.text = "X: " + worldCoords.x.toFixed(6) + ", Y: " + worldCoords.y.toFixed(6)
                        } else {
                            coordLabel.text = "X: " + mouse.x + ", Y: " + mouse.y
                        }
                    } else {
                        coordLabel.text = "X: " + mouse.x + ", Y: " + mouse.y
                    }
                    
                    // Pan com arrastar
                    if (isPanning && activeTool === "pan") {
                        var dx = mouse.x - lastPos.x
                        var dy = mouse.y - lastPos.y
                        
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.pan(dx, dy)
                        }
                        
                        lastPos = Qt.point(mouse.x, mouse.y)
                    }
                    
                    // Atualiza box de seleção
                    if (isDrawingBox && activeTool === "boxSelect") {
                        boxEnd = Qt.point(mouse.x, mouse.y)
                    }
                    
                    // Hover sobre features
                    if (activeTool === "identify" || activeTool === "select") {
                        // Emite sinal de hover
                        mapCanvasContainer.featureHovered(-1, Qt.point(mouse.x, mouse.y))
                    }
                }
                
                onReleased: (mouse) => {
                    if (isPanning) {
                        isPanning = false
                    }
                    
                    if (isDrawingBox && activeTool === "boxSelect") {
                        isDrawingBox = false
                        
                        // Calcula retângulo de seleção
                        var minX = Math.min(boxStart.x, boxEnd.x)
                        var minY = Math.min(boxStart.y, boxEnd.y)
                        var maxX = Math.max(boxStart.x, boxEnd.x)
                        var maxY = Math.max(boxStart.y, boxEnd.y)
                        
                        // Verifica se o retângulo tem tamanho mínimo (evita cliques acidentais)
                        if (Math.abs(maxX - minX) > 5 && Math.abs(maxY - minY) > 5) {
                            if (typeof mapBackend !== 'undefined') {
                                mapBackend.select_features_in_box(minX, minY, maxX, maxY)
                            }
                            mapCanvasContainer.featuresSelected([])
                        }
                        
                        // Reseta box
                        boxStart = Qt.point(0, 0)
                        boxEnd = Qt.point(0, 0)
                    }
                }
                
                onWheel: (wheel) => {
                    // Zoom com scroll refinado
                    var zoomFactor = wheel.angleDelta.y > 0 ? 1.2 : 0.8
                    
                        if (typeof mapBackend !== 'undefined') {
                        // Zoom centrado no cursor
                        mapBackend.zoom_at_point(wheel.x, wheel.y, zoomFactor)
                        }
                }
            }
            
            // Retângulo de seleção
            Rectangle {
                id: selectionBox
                visible: isDrawingBox
                x: Math.min(boxStart.x, boxEnd.x)
                y: Math.min(boxStart.y, boxEnd.y)
                width: Math.abs(boxEnd.x - boxStart.x)
                height: Math.abs(boxEnd.y - boxStart.y)
                color: "#4080c0ff"
                border.color: "#80c0ff"
                border.width: 2
                opacity: 0.3
            }
            
            // Tooltip de hover
            Rectangle {
                id: hoverTooltip
                visible: false
                width: tooltipLabel.width + 20
                height: tooltipLabel.height + 10
                color: "#2d2d30"
                border.color: AppTheme.accentColor
                border.width: 1
                radius: 4
                z: 100
                
                Label {
                    id: tooltipLabel
                    anchors.centerIn: parent
                    text: "Feature info"
                    color: AppTheme.text
                    font.pixelSize: 10
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

