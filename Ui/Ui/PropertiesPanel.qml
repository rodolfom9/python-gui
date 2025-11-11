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
        spacing: 10
        
        Label {
            text: "Propriedades da Camada"
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 14
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ColumnLayout {
                width: propertiesPanel.width - 30
                spacing: 10
                
                // Informações Gerais
                GroupBox {
                    Layout.fillWidth: true
                    title: "Informações Gerais"
                    visible: currentLayerIndex >= 0 && layerModel
                    
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
                        spacing: 8
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "Nome:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 80
                            }
                            Label {
                text: currentLayerIndex >= 0 && layerModel ? 
                                    layerModel.get(currentLayerIndex).layerName : "-"
                                color: AppTheme.text
                                font.pixelSize: 10
                                font.bold: true
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "Tipo:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 80
                            }
                            Label {
                                text: {
                                    if (currentLayerIndex >= 0 && layerModel) {
                                        var type = layerModel.get(currentLayerIndex).layerType
                                        return type === "vector" ? "📐 Vetorial" : "🖼 Raster"
                                    }
                                    return "-"
                                }
                                color: AppTheme.text
                                font.pixelSize: 10
                                Layout.fillWidth: true
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "Visível:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 80
                            }
                            Label {
                                text: {
                                    if (currentLayerIndex >= 0 && layerModel) {
                                        return layerModel.get(currentLayerIndex).visible ? "✓ Sim" : "✗ Não"
                                    }
                                    return "-"
                                }
                                color: AppTheme.text
                                font.pixelSize: 10
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
                
                // Sistema de Coordenadas (CRS)
                GroupBox {
                    Layout.fillWidth: true
                    title: "Sistema de Coordenadas (CRS)"
                    visible: currentLayerIndex >= 0 && layerModel
                    
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
                        spacing: 8
                        
                        Label {
                            text: "EPSG:4326 (WGS 84)"
                            color: AppTheme.text
                            font.pixelSize: 10
                            font.family: "Consolas"
                            Layout.fillWidth: true
                        }
                        
                        Label {
                            text: "Sistema de coordenadas geográficas"
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }
                
                // Extensão (Extent)
                GroupBox {
                    Layout.fillWidth: true
                    title: "Extensão (Extent)"
                    visible: currentLayerIndex >= 0 && layerModel
                    
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
                    
                    GridLayout {
                        anchors.fill: parent
                        columns: 2
                        rowSpacing: 6
                        columnSpacing: 10
                        
                        Label {
                            text: "Min X:"
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                        }
                        Label {
                            text: "-45.123456"
                            color: AppTheme.text
                            font.pixelSize: 9
                            font.family: "Consolas"
                        }
                        
                        Label {
                            text: "Max X:"
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                        }
                        Label {
                            text: "-44.987654"
                            color: AppTheme.text
                            font.pixelSize: 9
                            font.family: "Consolas"
                        }
                        
                        Label {
                            text: "Min Y:"
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                        }
                        Label {
                            text: "-23.456789"
                            color: AppTheme.text
                            font.pixelSize: 9
                            font.family: "Consolas"
                        }
                        
                        Label {
                            text: "Max Y:"
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                        }
                        Label {
                            text: "-22.123456"
                            color: AppTheme.text
                            font.pixelSize: 9
                            font.family: "Consolas"
                        }
                    }
                }
                
                // Estatísticas
                GroupBox {
                    Layout.fillWidth: true
                    title: "Estatísticas"
                    visible: currentLayerIndex >= 0 && layerModel
                
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
                        spacing: 8
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "Features:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 100
                            }
                            Label {
                                text: "0"
                                color: AppTheme.text
                                font.pixelSize: 10
                                font.bold: true
                                Layout.fillWidth: true
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            visible: currentLayerIndex >= 0 && layerModel && 
                                    layerModel.get(currentLayerIndex).layerType === "vector"
                            Label {
                                text: "Tipo Geom.:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 100
                            }
                            Label {
                                text: "Ponto/Linha/Polígono"
                                color: AppTheme.text
                                font.pixelSize: 10
                                Layout.fillWidth: true
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            visible: currentLayerIndex >= 0 && layerModel && 
                                    layerModel.get(currentLayerIndex).layerType === "raster"
                            Label {
                                text: "Dimensões:"
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                Layout.preferredWidth: 100
                            }
                            Label {
                                text: "1024 x 768 pixels"
                                color: AppTheme.text
                                font.pixelSize: 10
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
                
                // Botão para abrir tabela de atributos
                Button {
                    Layout.fillWidth: true
                    text: "Abrir Tabela de Atributos"
                    visible: currentLayerIndex >= 0 && layerModel && 
                            layerModel.get(currentLayerIndex).layerType === "vector"
                    
                    onClicked: {
                        // TODO: Abrir janela de tabela de atributos
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                        border.color: AppTheme.accentColor
                        border.width: 1
                        radius: 4
                    }
                    
                    contentItem: Label {
                        text: parent.text
                        color: AppTheme.text
                        font.pixelSize: 10
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                // Mensagem quando nenhuma camada selecionada
                Label {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: currentLayerIndex < 0 || !layerModel
                    text: "Selecione uma camada no painel de Camadas para visualizar suas propriedades"
                    color: AppTheme.textMuted
                    font.pixelSize: 11
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}

