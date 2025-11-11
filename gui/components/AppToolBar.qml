import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"

ToolBar {
    id: toolbar
    
    property string activeTool: "pan"
    
    signal toolChanged(string tool)
    signal layerAdded(string filePath, string layerType)
    signal statusMessageChanged(string message)
    
    function setActiveTool(tool) {
        activeTool = tool
        if (typeof mapBackend !== 'undefined') {
            mapBackend.set_tool(tool)
        }
        toolbar.toolChanged(tool)
    }
    
    background: Rectangle {
        color: "#3e3e42"
    }
    
    RowLayout {
        anchors.fill: parent
        spacing: 5
        
        // Grupo: Arquivos
        Label {
            text: "Arquivos:"
            color: AppTheme.textSecondary
            leftPadding: 10
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionAddOgrLayer.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            onClicked: {
                if (typeof mapBackend !== 'undefined') {
                    var filePath = mapBackend.open_vector_dialog()
                    toolbar.layerAdded(filePath, "vector")
                }
            }
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar camada vetorial"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionAddRasterLayer.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            onClicked: {
                if (typeof mapBackend !== 'undefined') {
                    var filePath = mapBackend.open_raster_dialog()
                    toolbar.layerAdded(filePath, "raster")
                }
            }
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar camada raster"
        }
        
        ToolSeparator {}
        
        // Grupo: Navegação
        Label {
            text: "Navegação:"
            color: AppTheme.textSecondary
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionPan.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "pan"
            onClicked: toolbar.setActiveTool("pan")
            ToolTip.visible: hovered
            ToolTip.text: "Pan - Arrastar mapa (Atalho: P)"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionZoomIn.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "zoomIn"
            onClicked: toolbar.setActiveTool("zoomIn")
            ToolTip.visible: hovered
            ToolTip.text: "Zoom In - Clique para aproximar"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionZoomOut.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "zoomOut"
            onClicked: toolbar.setActiveTool("zoomOut")
            ToolTip.visible: hovered
            ToolTip.text: "Zoom Out - Clique para afastar"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionZoomFullExtent.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            onClicked: {
                if (typeof mapBackend !== 'undefined') {
                    mapBackend.zoom_to_full_extent()
                }
            }
            ToolTip.visible: hovered
            ToolTip.text: "Zoom para extensão total"
        }
        
        ToolSeparator {}
        
        // Grupo: Ferramentas
        Label {
            text: "Ferramentas:"
            color: AppTheme.textSecondary
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionIdentify.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "identify"
            onClicked: toolbar.setActiveTool("identify")
            ToolTip.visible: hovered
            ToolTip.text: "Identificar feições"
        }
        
        ToolSeparator {}
        
        // Grupo: Desenho
        Label {
            text: "Desenho:"
            color: AppTheme.textSecondary
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionCapturePoint.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "addPoint"
            onClicked: toolbar.setActiveTool("addPoint")
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar ponto"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionCaptureLine.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "addLine"
            onClicked: toolbar.setActiveTool("addLine")
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar linha (Direito finaliza)"
        }
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionCapturePolygon.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            checkable: true
            checked: toolbar.activeTool === "addPolygon"
            onClicked: toolbar.setActiveTool("addPolygon")
            ToolTip.visible: hovered
            ToolTip.text: "Adicionar polígono (Direito fecha)"
        }
        
        ToolSeparator {}
        
        ToolButton {
            icon.source: "../../images/themes/default/mActionRefresh.svg"
            icon.color: "transparent"
            icon.width: 24
            icon.height: 24
            display: AbstractButton.IconOnly
            ToolTip.visible: hovered
            ToolTip.text: "Atualizar mapa"
        }
        
        Item {
            Layout.fillWidth: true
        }
    }
}

