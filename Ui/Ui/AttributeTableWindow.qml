import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Window
import "."

Window {
    id: attributeTableWindow
    
    property string layerName: ""
    property var attributeModel: ListModel {}
    
    width: 900
    height: 600
    minimumWidth: 600
    minimumHeight: 400
    
    title: "Tabela de Atributos - " + layerName
    
    color: AppTheme.windowBg
    
    // Sinais
    signal attributeChanged(int featureId, string fieldName, var newValue)
    signal featuresDeleted(var featureIds)
    signal selectionChanged(var selectedIds)
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8
        
        // Barra de ferramentas
        ToolBar {
            Layout.fillWidth: true
            
            background: Rectangle {
                color: "#2d2d30"
                border.color: AppTheme.border
                border.width: 1
                radius: 4
            }
            
            RowLayout {
                anchors.fill: parent
                spacing: 5
                
                Button {
                    text: "Editar"
                    Layout.preferredHeight: 32
                    checkable: true
                    
                    onClicked: {
                        // Ativar/Desativar edicao
                    }
                    
                    background: Rectangle {
                        color: parent.checked ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "transparent")
                        border.color: parent.checked ? AppTheme.accentColor : "transparent"
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
                
                Button {
                    text: "Nova"
                    Layout.preferredHeight: 32
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "transparent")
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
                
                Button {
                    text: "Deletar"
                    Layout.preferredHeight: 32
                    
                    onClicked: {
                        // Deletar selecionados
                    }
                    
                    background: Rectangle {
                        color: parent.down ? "#8b0000" : (parent.hovered ? "#a52a2a" : "transparent")
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
                
                Button {
                    text: "Selecionar Tudo"
                    Layout.preferredHeight: 32
                    
                    onClicked: {
                        for (var i = 0; i < attributeModel.count; i++) {
                            attributeModel.setProperty(i, "selected", true)
                        }
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "transparent")
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
                
                Button {
                    text: "Limpar Selecao"
                    Layout.preferredHeight: 32
                    
                    onClicked: {
                        for (var i = 0; i < attributeModel.count; i++) {
                            attributeModel.setProperty(i, "selected", false)
                        }
                    }
                    
                    background: Rectangle {
                        color: parent.down ? AppTheme.accentDark : (parent.hovered ? "#3e3e42" : "transparent")
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
                
                TextField {
                    id: searchField
                    Layout.preferredWidth: 200
                    placeholderText: "Buscar..."
                    color: AppTheme.text
                    font.pixelSize: 10
                    
                    background: Rectangle {
                        color: "#1e1e1e"
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                Label {
                    text: attributeModel.count + " features"
                    color: AppTheme.textMuted
                    font.pixelSize: 10
                }
            }
        }
        
        // Tabela de atributos
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#2d2d30"
            border.color: AppTheme.border
            border.width: 1
            radius: 4
            
            ListView {
                id: tableView
                anchors.fill: parent
                anchors.margins: 5
                clip: true
                spacing: 1
                
                model: attributeModel
                
                delegate: Rectangle {
                    width: tableView.width - 20
                    height: 30
                    color: index % 2 == 0 ? "#2d2d30" : "#252526"
                    border.color: AppTheme.border
                    border.width: 0.5
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 10
                        
                        Rectangle {
                            Layout.preferredWidth: 60
                            height: 20
                            color: model.selected ? AppTheme.accentColor : "transparent"
                            border.color: AppTheme.border
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: model.featureId ? model.featureId : index + 1
                                color: AppTheme.text
                                font.pixelSize: 9
                            }
                        }
                        
                        Label {
                            text: model.display ? model.display : "Feature"
                            color: AppTheme.text
                            font.pixelSize: 10
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            model.selected = !model.selected
                        }
                    }
                }
                
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
            }
        }
        
        // Barra de status
        Rectangle {
            Layout.fillWidth: true
            height: 30
            color: "#1e1e1e"
            border.color: AppTheme.border
            border.width: 1
            radius: 4
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 10
                
                Label {
                    text: {
                        var count = 0
                        for (var i = 0; i < attributeModel.count; i++) {
                            if (attributeModel.get(i).selected) count++
                        }
                        return count > 0 ? count + " selecionadas" : "Nenhuma selecao"
                    }
                    color: AppTheme.textMuted
                    font.pixelSize: 9
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Exportar"
                    Layout.preferredHeight: 24
                    
                    onClicked: {
                        // Implementar exportacao
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
                        font.pixelSize: 9
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                Button {
                    text: "Salvar"
                    Layout.preferredHeight: 24
                    
                    onClicked: {
                        attributeTableWindow.close()
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
                        font.pixelSize: 9
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                Button {
                    text: "Fechar"
                    Layout.preferredHeight: 24
                    
                    onClicked: {
                        attributeTableWindow.close()
                    }
                    
                    background: Rectangle {
                        color: parent.down ? "#8b0000" : (parent.hovered ? "#a52a2a" : "#2d2d30")
                        border.color: AppTheme.border
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: Label {
                        text: parent.text
                        color: AppTheme.text
                        font.pixelSize: 9
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }
}
