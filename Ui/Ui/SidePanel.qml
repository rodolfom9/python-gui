import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: sidePanel
    
    // Propriedades exportadas
    property alias tabBar: tabBar
    property alias tabIndex: tabBar.currentIndex
    property bool collapsed: true  // Inicia minimizado
    property alias layersPanel: layersPanel  // Expor o painel de camadas
    
    // Sinais
    signal layerAdded(string fileName, string layerType)
    signal layerRemoved(string layerName)
    signal layerVisibilityChanged(string layerName, bool visible)
    
    // Cores
    color: AppTheme.windowBg
    border.color: AppTheme.accentColor
    border.width: 1
    radius: 8
    clip: true
    
    property int previousIndex: -1
    
    // TabBar invisível para gerenciar o índice das abas
    TabBar {
        id: tabBar
        visible: false
        
        TabButton { text: "Camadas" }
        TabButton { text: "Propriedades" }
        TabButton { text: "Processamento" }
        TabButton { text: "Ferramentas" }
        TabButton { text: "Navegador" }
        TabButton { text: "Nova Camada" }
        TabButton { text: "Raster" }
        TabButton { text: "Banco de Dados" }
    }
    
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // Painel de ícones laterais (esquerda)
        Rectangle {
            id: iconPanel
            Layout.preferredWidth: 50
            Layout.fillHeight: true
            color: AppTheme.windowBg
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 5
                clip: false
                spacing: 10
                
                // Ícone Camadas
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionLayers.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 0 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 0
                        } else {
                            tabBar.currentIndex = 0
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Camadas"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 0 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 0 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Propriedades
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionPropertiesWidget.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 1 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 1
                        } else {
                            tabBar.currentIndex = 1
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Propriedades"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 1 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 1 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Processamento
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionFilter.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 2 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 2
                        } else {
                            tabBar.currentIndex = 2
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Processamento"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 2 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 2 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Ferramentas
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionIdentify.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 3 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 3
                        } else {
                            tabBar.currentIndex = 3
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Ferramentas"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 3 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 3 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Navegador
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mIconBrowserRelations.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 4 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 4
                        } else {
                            tabBar.currentIndex = 4
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Navegador"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 4 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 4 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Nova Camada
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionNewVectorLayer.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 5 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 5
                        } else {
                            tabBar.currentIndex = 5
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Nova Camada"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 5 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 5 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Raster
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mActionAddRasterLayer.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 6 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 6
                        } else {
                            tabBar.currentIndex = 6
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Raster"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 6 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 6 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                // Ícone Banco de Dados
                ToolButton {
                    Layout.alignment: Qt.AlignHCenter
                    icon.source: "../../images/themes/default/mIconDbSchema.svg"
                    icon.color: "transparent"
                    icon.width: 24
                    icon.height: 24
                    display: AbstractButton.IconOnly
                    onClicked: {
                        if (tabBar.currentIndex === 7 && !sidePanel.collapsed) {
                            sidePanel.collapsed = true
                            sidePanel.previousIndex = 7
                        } else {
                            tabBar.currentIndex = 7
                            sidePanel.collapsed = false
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Banco de Dados"
                    
                    background: Rectangle {
                        color: tabBar.currentIndex === 7 ? "#3e3e42" : "transparent"
                        border.color: tabBar.currentIndex === 7 ? AppTheme.accentColor : "transparent"
                        border.width: 2
                        radius: 4
                    }
                }
                
                Item { Layout.fillHeight: true }
            }
        }
        
        // Conteúdo das abas (direita)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !sidePanel.collapsed
            
            StackLayout {
                anchors.fill: parent
                currentIndex: tabBar.currentIndex
                
                // Aba 1: Camadas
                LayersPanel {
                    id: layersPanel
                    onLayerAdded: sidePanel.layerAdded(fileName, layerType)
                    onLayerRemoved: sidePanel.layerRemoved(layerName)
                    onLayerVisibilityChanged: sidePanel.layerVisibilityChanged(layerName, visible)
                }
                
                // Aba 2: Propriedades
                PropertiesPanel {
                    layerModel: layersPanel.layerListModel
                    currentLayerIndex: layersPanel.layerList.currentIndex
                }
                
                // Aba 3: Processamento
                ProcessingPanel {}
                
                // Aba 4: Ferramentas
                EmptyPanel { title: "Ferramentas" }
                
                // Aba 5: Navegador
                EmptyPanel { title: "Navegador de Arquivos" }
                
                // Aba 6: Nova Camada
                EmptyPanel { title: "Criar Nova Camada" }
                
                // Aba 7: Raster
                EmptyPanel { title: "Gerenciar Rasters" }
                
                // Aba 8: Banco de Dados
                EmptyPanel { title: "Conexões de Banco de Dados" }
            }
        }
    }
}

