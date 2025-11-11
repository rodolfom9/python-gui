import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: attributeTablePanel
    
    property string layerName: ""
    property int featureCount: 0
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8
        
        // Cabecalho
        RowLayout {
            Layout.fillWidth: true
            
            Label {
                text: "Tabela de Atributos"
                font.bold: true
                color: AppTheme.text
                font.pixelSize: 14
                Layout.fillWidth: true
            }
            
            Button {
                text: "X"
                Layout.preferredWidth: 30
                Layout.preferredHeight: 30
                ToolTip.visible: hovered
                ToolTip.text: "Fechar"
                
                onClicked: {
                    attributeTablePanel.visible = false
                }
                
                background: Rectangle {
                    color: parent.down ? "#8b0000" : (parent.hovered ? "#a52a2a" : "transparent")
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
                
                contentItem: Label {
                    text: parent.text
                    color: AppTheme.text
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        Label {
            text: layerName
            color: AppTheme.textMuted
            font.pixelSize: 10
            font.italic: true
        }
        
        // Barra de ferramentas mini
        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            
            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "Buscar..."
                color: AppTheme.text
                font.pixelSize: 10
                
                background: Rectangle {
                    color: "#2d2d30"
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
            }
            
            Button {
                text: "Exportar"
                Layout.preferredWidth: 70
                Layout.preferredHeight: 28
                ToolTip.visible: hovered
                ToolTip.text: "Exportar dados"
                
                background: Rectangle {
                    color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
                
                contentItem: Label {
                    text: parent.text
                    color: AppTheme.text
                    font.pixelSize: 10
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        // Tabela simplificada
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#2d2d30"
            border.color: AppTheme.border
            border.width: 1
            radius: 4
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 1
                spacing: 0
                
                // Cabecalho da tabela
                Rectangle {
                    Layout.fillWidth: true
                    height: 30
                    color: "#1e1e1e"
                    
                    RowLayout {
                        anchors.fill: parent
                        spacing: 1
                        
                        Rectangle {
                            Layout.preferredWidth: 60
                            Layout.fillHeight: true
                            color: "#1e1e1e"
                            border.color: AppTheme.border
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: "ID"
                                color: AppTheme.text
                                font.pixelSize: 10
                                font.bold: true
                            }
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#1e1e1e"
                            border.color: AppTheme.border
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: "Nome"
                                color: AppTheme.text
                                font.pixelSize: 10
                                font.bold: true
                            }
                        }
                        
                        Rectangle {
                            Layout.preferredWidth: 100
                            Layout.fillHeight: true
                            color: "#1e1e1e"
                            border.color: AppTheme.border
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: "Tipo"
                                color: AppTheme.text
                                font.pixelSize: 10
                                font.bold: true
                            }
                        }
                    }
                }
                
                // Linhas da tabela
                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    model: ListModel {
                        id: attributeListModel
                        
                        ListElement {
                            featureId: 1
                            featureName: "Feature 1"
                            featureType: "Ponto"
                        }
                        ListElement {
                            featureId: 2
                            featureName: "Feature 2"
                            featureType: "Linha"
                        }
                        ListElement {
                            featureId: 3
                            featureName: "Feature 3"
                            featureType: "Poligono"
                        }
                    }
                    
                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 30
                        color: index % 2 == 0 ? "#2d2d30" : "#252526"
                        
                        RowLayout {
                            anchors.fill: parent
                            spacing: 1
                            
                            Label {
                                Layout.preferredWidth: 60
                                text: model.featureId
                                color: AppTheme.text
                                font.pixelSize: 10
                                horizontalAlignment: Text.AlignHCenter
                            }
                            
                            Label {
                                Layout.fillWidth: true
                                text: model.featureName
                                color: AppTheme.text
                                font.pixelSize: 10
                                leftPadding: 10
                                elide: Text.ElideRight
                            }
                            
                            Label {
                                Layout.preferredWidth: 100
                                text: model.featureType
                                color: AppTheme.textMuted
                                font.pixelSize: 10
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onEntered: {
                                parent.color = AppTheme.accentDark
                            }
                            
                            onExited: {
                                parent.color = index % 2 == 0 ? "#2d2d30" : "#252526"
                            }
                            
                            onClicked: {
                                // Seleciona feature
                            }
                        }
                    }
                    
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }
        }
        
        // Status
        Label {
            text: featureCount + " features no total"
            color: AppTheme.textMuted
            font.pixelSize: 9
            Layout.alignment: Qt.AlignRight
        }
    }
}
