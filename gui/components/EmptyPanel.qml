import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"

Rectangle {
    id: emptyPanel
    
    property string title: "Painel Vazio"
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        
        Label {
            text: emptyPanel.title
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 12
        }
        
        Label {
            text: "Esta aba está vazia. Configure conforme necessário."
            color: AppTheme.textMuted
            font.pixelSize: 11
        }
        
        Item {
            Layout.fillHeight: true
        }
    }
}

