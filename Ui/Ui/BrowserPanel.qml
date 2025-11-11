import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: browserPanel
    
    // Sinais
    signal fileSelected(string filePath, string fileType)
    signal statusMessage(string message)
    
    color: AppTheme.baseBg
    
    property string currentPath: ""
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8
        
        Label {
            text: "Navegador de Arquivos"
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 14
        }
        
        // Barra de caminho
        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            
            Button {
                text: "Home"
                Layout.preferredWidth: 60
                ToolTip.visible: hovered
                ToolTip.text: "Pasta Home"
                
                onClicked: {
                    browserPanel.statusMessage("Navegando para Home")
                }
                
                background: Rectangle {
                    color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
                
                contentItem: Label {
                    text: parent.text
                    color: AppTheme.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            Button {
                text: "Parent"
                Layout.preferredWidth: 60
                ToolTip.visible: hovered
                ToolTip.text: "Pasta Pai"
                
                onClicked: {
                    browserPanel.statusMessage("Navegando para pasta pai")
                }
                
                background: Rectangle {
                    color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
                
                contentItem: Label {
                    text: parent.text
                    color: AppTheme.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TextField {
                id: pathField
                Layout.fillWidth: true
                placeholderText: "/caminho/para/arquivo"
                text: browserPanel.currentPath
                readOnly: true
                selectByMouse: true
                color: AppTheme.text
                font.pixelSize: 10
                
                background: Rectangle {
                    color: "#2d2d30"
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
            }
        }
        
        // Filtros de arquivo
        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            
            Label {
                text: "Filtro:"
                color: AppTheme.text
                font.pixelSize: 10
                Layout.preferredWidth: 50
            }
            
            ComboBox {
                id: filterCombo
                Layout.fillWidth: true
                model: ["Todos", "Shapefiles (*.shp)", "GeoJSON (*.geojson)", "GeoTIFF (*.tif)"]
                currentIndex: 0
                
                background: Rectangle {
                    color: "#2d2d30"
                    border.color: AppTheme.border
                    border.width: 1
                    radius: 3
                }
                
                contentItem: Label {
                    text: filterCombo.displayText
                    color: AppTheme.text
                    font.pixelSize: 10
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 8
                }
            }
        }
        
        // Lista de arquivos simplificada
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#2d2d30"
            border.color: AppTheme.border
            border.width: 1
            radius: 4
            
            ListView {
                id: fileListView
                anchors.fill: parent
                anchors.margins: 5
                clip: true
                
                model: ListModel {
                    id: fileListModel
                    
                    ListElement {
                        fileName: "shapefile.shp"
                        fileIcon: "M"
                        fileSize: "2048"
                        isDir: false
                    }
                    ListElement {
                        fileName: "geojson.geojson"
                        fileIcon: "J"
                        fileSize: "1024"
                        isDir: false
                    }
                    ListElement {
                        fileName: "raster.tif"
                        fileIcon: "R"
                        fileSize: "5120"
                        isDir: false
                    }
                    ListElement {
                        fileName: "documents"
                        fileIcon: "F"
                        fileSize: ""
                        isDir: true
                    }
                }
                
                delegate: ItemDelegate {
                    width: fileListView.width
                    height: 32
                    
                    background: Rectangle {
                        color: parent.hovered ? "#3e3e42" : "transparent"
                        border.color: "transparent"
                    }
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 4
                        spacing: 8
                        
                        Label {
                            text: "[" + model.fileIcon + "]"
                            font.pixelSize: 12
                            color: AppTheme.accentColor
                            font.bold: true
                            Layout.preferredWidth: 40
                        }
                        
                        Label {
                            text: model.fileName
                            color: AppTheme.text
                            font.pixelSize: 10
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        
                        Label {
                            text: model.fileSize ? (model.fileSize + " B") : ""
                            color: AppTheme.textMuted
                            font.pixelSize: 9
                            Layout.preferredWidth: 80
                            horizontalAlignment: Text.AlignRight
                            visible: model.fileSize !== ""
                        }
                    }
                    
                    onDoubleClicked: {
                        if (!model.isDir) {
                            var fileType = ""
                            var fname = model.fileName.toLowerCase()
                            
                            if (fname.endsWith(".shp")) {
                                fileType = "vector"
                            } else if (fname.endsWith(".geojson") || fname.endsWith(".json")) {
                                fileType = "vector"
                            } else if (fname.endsWith(".tif") || fname.endsWith(".tiff")) {
                                fileType = "raster"
                            }
                            
                            if (fileType) {
                                browserPanel.fileSelected(pathField.text + "/" + model.fileName, fileType)
                                browserPanel.statusMessage("Carregando: " + model.fileName)
                            } else {
                                browserPanel.statusMessage("Formato nao suportado")
                            }
                        }
                    }
                }
                
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
            }
        }
        
        // Botoes de acao
        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            
            Button {
                text: "Adicionar ao Mapa"
                Layout.fillWidth: true
                
                onClicked: {
                    browserPanel.statusMessage("Arquivo selecionado para carregamento")
                }
                
                background: Rectangle {
                    color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "#2d2d30")
                    border.color: AppTheme.accentColor
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
        
        // Informacoes
        Rectangle {
            Layout.fillWidth: true
            height: 70
            color: "#1e1e1e"
            border.color: AppTheme.border
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
                    text: "Clique duplo para carregar\nFormatos: .shp, .geojson, .tif"
                    color: AppTheme.textMuted
                    font.pixelSize: 9
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
    }
}
