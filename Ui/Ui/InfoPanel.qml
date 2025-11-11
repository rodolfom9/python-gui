import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "."

Rectangle {
    id: infoPanel
    
    color: AppTheme.windowBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 5
        
        Label {
            text: "Informações"
            font.bold: true
            font.pixelSize: 14
            color: AppTheme.text
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            TextArea {
                readOnly: true
                wrapMode: TextArea.Wrap
                color: AppTheme.text
                selectByMouse: true
                
                text: "FERRAMENTAS DE MAPA\n\n" +
                      "🖱️ NAVEGAÇÃO:\n" +
                      "• Pan: Arrastar mapa\n" +
                      "• Zoom In: Clique para aproximar\n" +
                      "• Zoom Out: Clique para afastar\n" +
                      "• Wheel: Zoom no cursor\n\n" +
                      "ℹ️ CONSULTA:\n" +
                      "• Identificar: Clique em features\n\n" +
                      "DESENHO:\n" +
                      "• Ponto: Clique para adicionar\n" +
                      "• Linha: Cliques para vértices\n" +
                      "  Botão direito: Finalizar\n" +
                      "• Polígono: Cliques para vértices\n" +
                      "  Botão direito: Fechar\n\n" +
                      "⌨️ ATALHOS:\n" +
                      "• ESC: Cancelar desenho\n" +
                      "• Enter: Finalizar desenho\n" +
                      "• P: Ferramenta Pan\n" +
                      "• I: Ferramenta Identificar\n\n" +
                      "Similar ao QGIS com Map Tools!\n\n" +
                      "Desenvolvido com Qt 6 + Python"
                
                background: Rectangle {
                    color: AppTheme.baseBg
                    border.color: AppTheme.border
                    border.width: 1
                }
            }
        }
    }
}

