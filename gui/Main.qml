import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Window
import "components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    title: "Sistema de Mapa GIS - Python & Qt6"
    
    // Cores do tema (similar ao QGIS)
    palette {
        window: AppTheme.windowBg
        windowText: AppTheme.windowText
        base: AppTheme.baseBg
        alternateBase: AppTheme.alternateBase
        text: AppTheme.text
        button: AppTheme.button
        buttonText: AppTheme.buttonText
        brightText: AppTheme.brightText
        highlight: AppTheme.highlight
        highlightedText: AppTheme.highlightedText
    }
    
    // Menu Bar
    menuBar: AppMenuBar {
        id: appMenuBar
        
        onToolChanged: (tool) => {
            appToolBar.setActiveTool(tool)
            appStatusBar.showMessage("Ferramenta: " + tool)
        }
        
        onStatusMessageChanged: (msg) => {
            appStatusBar.showMessage(msg)
        }
        
        onZoomFullExtent: {
            if (typeof mapBackend !== 'undefined') {
                mapBackend.zoom_to_full_extent()
            }
        }
        
        onMapRefreshed: {
            appStatusBar.showMessage("Mapa atualizado")
        }
    }
    
    // Toolbar
    header: AppToolBar {
        id: appToolBar
        
        onToolChanged: (tool) => {
            appStatusBar.message = "Ferramenta: " + tool
        }
        
        onLayerAdded: (filePath, layerType) => {
            if (filePath && layerType) {
                if (layerType === "vector") {
                    var success = mapBackend.add_vector_layer(filePath)
                    if (success) {
                        var fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                        fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                        // Adicionar à lista de camadas
                        sidePanel.layersPanel.layerListModel.append({
                            layerName: fileName,
                            layerType: "vector",
                            visible: true
                        })
                        sidePanel.tabBar.currentIndex = 0
                        sidePanel.collapsed = false
                    }
                } else if (layerType === "raster") {
                    success = mapBackend.add_raster_layer(filePath)
                    if (success) {
                        fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                        fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                        // Adicionar à lista de camadas
                        sidePanel.layersPanel.layerListModel.append({
                            layerName: fileName,
                            layerType: "raster",
                            visible: true
                        })
                        sidePanel.tabBar.currentIndex = 0
                        sidePanel.collapsed = false
                    }
                }
            }
        }
    }
    
    // Área principal
    SplitView {
        anchors.fill: parent
        anchors.topMargin: 5
        anchors.bottomMargin: 5
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        orientation: Qt.Horizontal
        
        // Remover o handle de resize visual (invisível e sem interação)
        handle: Rectangle {
            implicitWidth: 0
            implicitHeight: 0
            color: "transparent"
            visible: false
            
            // Remove a área de interação do handle
            containmentMask: Item {
                width: 0
                height: 0
            }
        }
        
        // Container para o painel lateral com margem
        Item {
            SplitView.fillHeight: true
            SplitView.preferredWidth: sidePanel.collapsed ? 55 : 285
            SplitView.maximumWidth: sidePanel.collapsed ? 55 : 285
            SplitView.minimumWidth: sidePanel.collapsed ? 55 : 285  // Mesmo tamanho, não permite resize
            
            // Painel lateral
            SidePanel {
                id: sidePanel
                anchors.fill: parent
                anchors.rightMargin: 5
            
            // Conectar sinais das camadas
            Connections {
                target: sidePanel
                
                function onLayerRemoved(layerName) {
                    if (typeof mapBackend !== 'undefined') {
                        mapBackend.remove_layer(layerName)
                    }
                    appStatusBar.showMessage("Camada removida: " + layerName)
                }
                
                function onLayerVisibilityChanged(layerName, visible) {
                    if (typeof mapBackend !== 'undefined') {
                        mapBackend.set_layer_visibility(layerName, visible)
                        mapBackend.render_map()
                    }
                    appStatusBar.showMessage(layerName + " " + (visible ? "visível" : "oculto"))
                }
            }
            }
        }
        
        // Canvas do mapa (centro)
        MapCanvas {
            id: mapCanvas
            SplitView.fillWidth: true
            SplitView.fillHeight: true
        }
        
        // Painel de informações (direita)
        InfoPanel {
            id: infoPanel
            SplitView.fillHeight: true
            SplitView.preferredWidth: 300
            SplitView.minimumWidth: 200
        }
    }
    
    // Status Bar
    footer: AppStatusBar {
        id: appStatusBar
    }
    
    // Diálogo Sobre
    Dialog {
        id: aboutDialog
        title: "Sobre"
        modal: true
        anchors.centerIn: parent
        
        contentItem: ColumnLayout {
            spacing: 10
            
            Label {
                text: "Sistema de Mapa GIS"
                font.bold: true
                font.pixelSize: 18
            }
            
            Label {
                text: "Versão 1.0.0"
            }
            
            Label {
                text: "Sistema de informações geográficas\ndesenvolvido com Qt 6 e Python"
                wrapMode: Text.WordWrap
            }
            
            Label {
                text: "Similar ao QGIS com Map Tools"
            }
            
            Label {
                text: "© 2025 - Desenvolvido com ❤️"
            }
        }
        
        standardButtons: Dialog.Ok
    }
    
    // Atalhos de teclado
    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: Qt.quit()
    }
    
    Shortcut {
        sequence: "P"
        onActivated: {
            appToolBar.setActiveTool("pan")
            appStatusBar.showMessage("Ferramenta: Pan")
        }
    }
    
    Shortcut {
        sequence: "I"
        onActivated: {
            appToolBar.setActiveTool("identify")
            appStatusBar.showMessage("Ferramenta: Identificar")
        }
    }
    
    Shortcut {
        sequence: "Escape"
        onActivated: {
            appToolBar.setActiveTool("pan")
            appStatusBar.showMessage("Ferramenta Pan ativada (ESC)")
        }
    }
    
    Component.onCompleted: {
        appStatusBar.showMessage("Sistema iniciado - Ferramenta: Pan")
    }
}
