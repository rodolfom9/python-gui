
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: toolsPanel
    
    // Sinais para comunicação com o MapCanvas
    signal toolSelected(string toolName)
    signal statusMessage(string message)
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        Label {
            text: "Ferramentas de Edição"
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 14
        }
        
        // Seção: Ferramentas de Seleção
        GroupBox {
            Layout.fillWidth: true
            title: "Seleção"
            
            background: Rectangle {
                color: "#2d2d30"
                border.color: AppTheme.border
                border.width: 1
                radius: 4
            }
            
            label: Label {
                text: parent.title
                color: AppTheme.text
                font.pixelSize: 11
                font.bold: true
                padding: 5
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                Button {
                    Layout.fillWidth: true
                    text: "Selecionar Feature"
                    icon.source: "../../images/themes/default/mActionSelect.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("select")
                        toolsPanel.statusMessage("Ferramenta: Selecionar Feature")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionSelect.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Selecionar Feature"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Selecao em Caixa"
                    
                    onClicked: {
                        toolsPanel.toolSelected("boxSelect")
                        toolsPanel.statusMessage("Ferramenta: Seleção em Caixa (arrastar)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Label {
                            text: "⬜"
                            color: AppTheme.text
                            font.pixelSize: 16
                            Layout.preferredWidth: 20
                        }
                        Label {
                            text: "Seleção em Caixa"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Limpar Selecao"
                    
                    onClicked: {
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.clear_selection()
                        }
                        toolsPanel.statusMessage("Seleção limpa")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Label {
                            text: "🧹"
                            color: AppTheme.text
                            font.pixelSize: 16
                            Layout.preferredWidth: 20
                        }
                        Label {
                            text: "Limpar Seleção"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
        
        // Seção: Ferramentas de Desenho
        GroupBox {
            Layout.fillWidth: true
            title: "Desenho"
            
            background: Rectangle {
                color: "#2d2d30"
                border.color: AppTheme.border
                border.width: 1
                radius: 4
            }
            
            label: Label {
                text: parent.title
                color: AppTheme.text
                font.pixelSize: 11
                font.bold: true
                padding: 5
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                Button {
                    Layout.fillWidth: true
                    text: "Adicionar Ponto"
                    icon.source: "../../images/themes/default/mActionCapturePoint.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("addPoint")
                        toolsPanel.statusMessage("Ferramenta: Adicionar Ponto (clique no mapa)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionCapturePoint.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Adicionar Ponto"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Adicionar Linha"
                    icon.source: "../../images/themes/default/mActionCaptureLine.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("addLine")
                        toolsPanel.statusMessage("Ferramenta: Adicionar Linha (clique para vértices)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionCaptureLine.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Adicionar Linha"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Adicionar Poligono"
                    icon.source: "../../images/themes/default/mActionCapturePolygon.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("addPolygon")
                        toolsPanel.statusMessage("Ferramenta: Adicionar Polígono (clique para vértices)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionCapturePolygon.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Adicionar Polígono"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
        
        // Seção: Ferramentas de Edição
        GroupBox {
            Layout.fillWidth: true
            title: "Edição"
            
            background: Rectangle {
                color: "#2d2d30"
                border.color: AppTheme.border
                border.width: 1
                radius: 4
            }
            
            label: Label {
                text: parent.title
                color: AppTheme.text
                font.pixelSize: 11
                font.bold: true
                padding: 5
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                Button {
                    Layout.fillWidth: true
                    text: "Editar Vertices"
                    icon.source: "../../images/themes/default/mActionVertexTool.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("editVertices")
                        toolsPanel.statusMessage("Ferramenta: Editar Vértices (selecione feature)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionVertexTool.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Editar Vértices"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Deletar Feature"
                    icon.source: "../../images/themes/default/mActionDeleteSelected.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        if (typeof mapBackend !== 'undefined') {
                            mapBackend.delete_selected_features()
                        }
                        toolsPanel.statusMessage("Features selecionadas deletadas")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? "#8b0000" : (parent.hovered ? "#a52a2a" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionDeleteSelected.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Deletar Feature"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Mover Feature"
                    icon.source: "../../images/themes/default/mActionMoveFeature.svg"
                    icon.color: "transparent"
                    
                    onClicked: {
                        toolsPanel.toolSelected("moveFeature")
                        toolsPanel.statusMessage("Ferramenta: Mover Feature (arraste)")
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: RowLayout {
                        spacing: 8
                        Image {
                            source: "../../images/themes/default/mActionMoveFeature.svg"
                            sourceSize.width: 20
                            sourceSize.height: 20
                            Layout.preferredWidth: 20
                            Layout.preferredHeight: 20
                        }
                        Label {
                            text: "Mover Feature"
                            color: AppTheme.text
                            font.pixelSize: 11
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
        
        Item {
            Layout.fillHeight: true
        }
        
        // Informacao sobre a ferramenta ativa
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: "#1e1e1e"
            border.color: AppTheme.accentColor
            border.width: 1
            radius: 4
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 4
                
                Label {
                    text: "Dica:"
                    font.bold: true
                    color: AppTheme.accentColor
                    font.pixelSize: 10
                }
                
                Label {
                    text: "ESC para cancelar\nBotao direito para finalizar"
                    color: AppTheme.textMuted
                    font.pixelSize: 9
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
    }
}

