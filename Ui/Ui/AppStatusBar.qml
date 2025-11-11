import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

ToolBar {
    id: statusBar
    
    property string message: "Pronto"
    property string activeTool: "pan"
    
    height: 20
    
    function showMessage(msg) {
        message = msg
    }
    
    background: Rectangle {
        color: AppTheme.statusOk
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 2
        spacing: 10
        
        Label {
            text: statusBar.message
            color: AppTheme.brightText
            font.pixelSize: 10
            Layout.fillWidth: true
        }
        
        Label {
            text: "Ferramenta: " + statusBar.activeTool
            color: AppTheme.brightText
            font.pixelSize: 10
        }
    }
}

