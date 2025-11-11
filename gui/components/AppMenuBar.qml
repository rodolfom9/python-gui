import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import "../components"

MenuBar {
    id: mainMenuBar
    
    signal toolChanged(string tool)
    signal statusMessageChanged(string message)
    signal zoomFullExtent()
    signal mapRefreshed()
    
    background: Rectangle {
        color: "#1e1e1e"
        border.color: AppTheme.accentColor
        border.width: 1
        
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 2
            color: AppTheme.accentColor
        }
    }
    
    // Menu Arquivo
    Menu {
        title: "Arquivo"
        
        Menu {
            title: "Projeto"
            
            MenuItem {
                text: "Novo Projeto"
                icon.name: "document-new"
                onTriggered: mainMenuBar.statusMessageChanged("Novo Projeto")
            }
            
            MenuItem {
                text: "Abrir Projeto..."
                icon.name: "document-open"
                onTriggered: mainMenuBar.statusMessageChanged("Abrir Projeto")
            }
            
            MenuItem {
                text: "Salvar Projeto"
                icon.name: "document-save"
                onTriggered: mainMenuBar.statusMessageChanged("Salvar Projeto")
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Fechar Projeto"
                onTriggered: mainMenuBar.statusMessageChanged("Fechar Projeto")
            }
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Sair"
            icon.name: "application-exit"
            onTriggered: Qt.quit()
        }
    }
    
    // Menu Editar
    Menu {
        title: "Editar"
        
        MenuItem {
            text: "Desfazer"
            icon.name: "edit-undo"
            enabled: false
            onTriggered: mainMenuBar.statusMessageChanged("Desfazer")
        }
        
        MenuItem {
            text: "Refazer"
            icon.name: "edit-redo"
            enabled: false
            onTriggered: mainMenuBar.statusMessageChanged("Refazer")
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Copiar"
            icon.name: "edit-copy"
            onTriggered: mainMenuBar.statusMessageChanged("Copiar")
        }
        
        MenuItem {
            text: "Colar"
            icon.name: "edit-paste"
            onTriggered: mainMenuBar.statusMessageChanged("Colar")
        }
    }
    
    // Menu Visualização
    Menu {
        title: "Visualização"
        
        MenuItem {
            text: "Pan (Arrastar)"
            icon.name: "transform-move"
            checkable: true
            onTriggered: mainMenuBar.toolChanged("pan")
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Zoom In"
            icon.name: "zoom-in"
            checkable: true
            onTriggered: mainMenuBar.toolChanged("zoomIn")
        }
        
        MenuItem {
            text: "Zoom Out"
            icon.name: "zoom-out"
            checkable: true
            onTriggered: mainMenuBar.toolChanged("zoomOut")
        }
        
        MenuItem {
            text: "Zoom Total"
            icon.name: "zoom-fit-best"
            onTriggered: mainMenuBar.zoomFullExtent()
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Atualizar Mapa"
            icon.name: "view-refresh"
            onTriggered: mainMenuBar.mapRefreshed()
        }
    }
    
    // Menu Ferramentas
    Menu {
        title: "Ferramentas"
        
        MenuItem {
            text: "Identificar Feição"
            icon.name: "help-about"
            checkable: true
            onTriggered: mainMenuBar.toolChanged("identify")
        }
        
        MenuSeparator {}
        
        Menu {
            title: "Desenho"
            
            MenuItem {
                text: "Adicionar Ponto"
                checkable: true
                onTriggered: mainMenuBar.toolChanged("addPoint")
            }
            
            MenuItem {
                text: "Adicionar Linha"
                checkable: true
                onTriggered: mainMenuBar.toolChanged("addLine")
            }
            
            MenuItem {
                text: "Adicionar Polígono"
                checkable: true
                onTriggered: mainMenuBar.toolChanged("addPolygon")
            }
        }
    }
    
    // Menu Ajuda
    Menu {
        title: "Ajuda"
        
        MenuItem {
            text: "Sobre"
            icon.name: "help-about"
            onTriggered: mainMenuBar.statusMessageChanged("Sobre")
        }
        
        MenuItem {
            text: "Documentação"
            icon.name: "help-contents"
            onTriggered: mainMenuBar.statusMessageChanged("Documentação em desenvolvimento")
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Verificar Atualizações"
            onTriggered: mainMenuBar.statusMessageChanged("Versão atual: 1.0.0")
        }
    }
}

