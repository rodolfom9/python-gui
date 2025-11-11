import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"

Rectangle {
    id: processingPanel
    
    color: AppTheme.baseBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        
        Label {
            text: "Ferramentas de Processamento"
            font.bold: true
            color: AppTheme.text
            font.pixelSize: 12
        }
        
        Label {
            text: "Funcionalidades de processamento em desenvolvimento"
            color: AppTheme.textMuted
            font.pixelSize: 11
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        Item {
            Layout.fillHeight: true
        }
    }
}

