import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    title: "Sistema de Mapa GIS - Python & Qt6"
    
    // Cores do tema (similar ao QGIS)
    palette {
        window: "#2d2d30"
        windowText: "#f1f1f1"
        base: "#1e1e1e"
        alternateBase: "#2d2d30"
        text: "#f1f1f1"
        button: "#3e3e42"
        buttonText: "#f1f1f1"
        brightText: "#ffffff"
        highlight: "#094771"
        highlightedText: "#ffffff"
    }
    
    // Menu Bar (estilo QGIS)
    menuBar: MenuBar {
        id: mainMenuBar
        
        background: Rectangle {
            color: "#3e3e42"
        }
        
        // Menu Arquivo
        Menu {
            title: "Arquivo"
            
            Menu {
                title: "Projeto"
                
                MenuItem {
                    text: "Novo Projeto"
                    icon.name: "document-new"
                    onTriggered: statusBar.showMessage("Novo Projeto")
                }
                
                MenuItem {
                    text: "Abrir Projeto..."
                    icon.name: "document-open"
                    onTriggered: statusBar.showMessage("Abrir Projeto")
                }
                
                MenuItem {
                    text: "Salvar Projeto"
                    icon.name: "document-save"
                    onTriggered: statusBar.showMessage("Salvar Projeto")
                }
                
                MenuSeparator {}
                
                MenuItem {
                    text: "Fechar Projeto"
                    onTriggered: statusBar.showMessage("Fechar Projeto")
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Adicionar Camada Vetor..."
                icon.name: "insert-object"
                onTriggered: {
                    if (typeof mapBackend !== 'undefined') {
                        var filePath = mapBackend.open_vector_dialog()
                        if (filePath) {
                            var success = mapBackend.add_vector_layer(filePath)
                            if (success) {
                                var fileName = filePath.substring(filePath.lastIndexOf('/') + 1)
                                fileName = filePath.substring(filePath.lastIndexOf('\\') + 1)
                                fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                                layerListModel.append({
                                    layerName: fileName,
                                    layerType: "vector",
                                    visible: true
                                })
                            }
                        }
                    }
                }
            }
            
            MenuItem {
                text: "Adicionar Camada Raster..."
                icon.name: "insert-image"
                onTriggered: {
                    if (typeof mapBackend !== 'undefined') {
                        var filePath = mapBackend.open_raster_dialog()
                        if (filePath) {
                            var success = mapBackend.add_raster_layer(filePath)
                            if (success) {
                                var fileName = filePath.substring(filePath.lastIndexOf('/') + 1)
                                fileName = filePath.substring(filePath.lastIndexOf('\\') + 1)
                                fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                                layerListModel.append({
                                    layerName: fileName,
                                    layerType: "raster",
                                    visible: true
                                })
                            }
                        }
                    }
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Salvar Imagem..."
                icon.name: "document-save-as"
                onTriggered: statusBar.showMessage("Salvar Imagem")
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
                onTriggered: statusBar.showMessage("Desfazer")
            }
            
            MenuItem {
                text: "Refazer"
                icon.name: "edit-redo"
                enabled: false
                onTriggered: statusBar.showMessage("Refazer")
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Copiar"
                icon.name: "edit-copy"
                onTriggered: statusBar.showMessage("Copiar")
            }
            
            MenuItem {
                text: "Colar"
                icon.name: "edit-paste"
                onTriggered: statusBar.showMessage("Colar")
            }
        }
        
        // Menu Visualização
        Menu {
            title: "Visualização"
            
            MenuItem {
                text: "Pan (Arrastar)"
                icon.name: "transform-move"
                checkable: true
                checked: toolbar.activeTool === "pan"
                onTriggered: {
                    toolbar.setActiveTool("pan")
                    statusBar.showMessage("Ferramenta: Pan (Arrastar mapa)")
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Zoom In"
                icon.name: "zoom-in"
                checkable: true
                checked: toolbar.activeTool === "zoomIn"
                onTriggered: {
                    toolbar.setActiveTool("zoomIn")
                    statusBar.showMessage("Ferramenta: Zoom In (Clique para aproximar)")
                }
            }
            
            MenuItem {
                text: "Zoom Out"
                icon.name: "zoom-out"
                checkable: true
                checked: toolbar.activeTool === "zoomOut"
                onTriggered: {
                    toolbar.setActiveTool("zoomOut")
                    statusBar.showMessage("Ferramenta: Zoom Out (Clique para afastar)")
                }
            }
            
            MenuItem {
                text: "Zoom Total"
                icon.name: "zoom-fit-best"
                onTriggered: {
                    statusBar.showMessage("Zoom Total")
                    if (typeof mapBackend !== 'undefined') {
                        mapBackend.zoom_to_full_extent()
                    }
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Atualizar Mapa"
                icon.name: "view-refresh"
                onTriggered: {
                    mapCanvas.update()
                    statusBar.showMessage("Mapa atualizado")
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Painéis"
                enabled: false
            }
            
            MenuItem {
                text: "Barras de Ferramentas"
                enabled: false
            }
        }
        
        
        // Menu Ferramentas
        Menu {
            title: "Ferramentas"
            
            MenuItem {
                text: "Identificar Feição"
                icon.name: "help-about"
                checkable: true
                checked: toolbar.activeTool === "identify"
                onTriggered: {
                    toolbar.setActiveTool("identify")
                    statusBar.showMessage("Ferramenta: Identificar (Clique em features)")
                }
            }
            
            MenuSeparator {}
            
            Menu {
                title: "Desenho"
                
                MenuItem {
                    text: "Adicionar Ponto"
                    checkable: true
                    checked: toolbar.activeTool === "addPoint"
                    onTriggered: {
                        toolbar.setActiveTool("addPoint")
                        statusBar.showMessage("Ferramenta: Adicionar Ponto")
                    }
                }
                
                MenuItem {
                    text: "Adicionar Linha"
                    checkable: true
                    checked: toolbar.activeTool === "addLine"
                    onTriggered: {
                        toolbar.setActiveTool("addLine")
                        statusBar.showMessage("Ferramenta: Adicionar Linha (Direito finaliza)")
                    }
                }
                
                MenuItem {
                    text: "Adicionar Polígono"
                    checkable: true
                    checked: toolbar.activeTool === "addPolygon"
                    onTriggered: {
                        toolbar.setActiveTool("addPolygon")
                        statusBar.showMessage("Ferramenta: Adicionar Polígono (Direito fecha)")
                    }
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Medida"
                enabled: false
            }
            
            MenuItem {
                text: "Seleção"
                enabled: false
            }
        }
        
        // Menu Ajuda
        Menu {
            title: "Ajuda"
            
            MenuItem {
                text: "Sobre"
                icon.name: "help-about"
                onTriggered: aboutDialog.open()
            }
            
            MenuItem {
                text: "Documentação"
                icon.name: "help-contents"
                onTriggered: statusBar.showMessage("Documentação em desenvolvimento")
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Verificar Atualizações"
                onTriggered: statusBar.showMessage("Versão atual: 1.0.0")
            }
        }
    }
    
    // Toolbar principal (estilo QGIS)
    header: ToolBar {
        id: toolbar
        
        property string activeTool: "pan"
        
        function setActiveTool(tool) {
            activeTool = tool
            if (typeof mapBackend !== 'undefined') {
                mapBackend.set_tool(tool)
            }
        }
        
        background: Rectangle {
            color: "#3e3e42"
        }
        
        RowLayout {
            anchors.fill: parent
            spacing: 5
            
            // Grupo: Arquivos
            Label {
                text: "Arquivos:"
                color: "#cccccc"
                leftPadding: 10
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionAddOgrLayer.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                onClicked: {
                    if (typeof mapBackend !== 'undefined') {
                        var filePath = mapBackend.open_vector_dialog()
                        if (filePath) {
                            var success = mapBackend.add_vector_layer(filePath)
                            if (success) {
                                var fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                                fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                                layerListModel.append({
                                    layerName: fileName,
                                    layerType: "vector",
                                    visible: true
                                })
                            }
                        }
                    }
                }
                ToolTip.visible: hovered
                ToolTip.text: "Adicionar camada vetorial"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionAddRasterLayer.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                onClicked: {
                    if (typeof mapBackend !== 'undefined') {
                        var filePath = mapBackend.open_raster_dialog()
                        if (filePath) {
                            var success = mapBackend.add_raster_layer(filePath)
                            if (success) {
                                var fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                                fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                                layerListModel.append({
                                    layerName: fileName,
                                    layerType: "raster",
                                    visible: true
                                })
                            }
                        }
                    }
                }
                ToolTip.visible: hovered
                ToolTip.text: "Adicionar camada raster"
            }
            
            ToolSeparator {}
            
            // Grupo: Navegação
            Label {
                text: "Navegação:"
                color: "#cccccc"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionPan.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "pan"
                onClicked: {
                    toolbar.setActiveTool("pan")
                    statusBar.showMessage("Ferramenta: Pan (Arrastar mapa)")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Pan - Arrastar mapa (Atalho: P)"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionZoomIn.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "zoomIn"
                onClicked: {
                    toolbar.setActiveTool("zoomIn")
                    statusBar.showMessage("Ferramenta: Zoom In")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Zoom In - Clique para aproximar"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionZoomOut.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "zoomOut"
                onClicked: {
                    toolbar.setActiveTool("zoomOut")
                    statusBar.showMessage("Ferramenta: Zoom Out")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Zoom Out - Clique para afastar"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionZoomFullExtent.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                onClicked: {
                    statusBar.showMessage("Zoom Total")
                    if (typeof mapBackend !== 'undefined') {
                        mapBackend.zoom_to_full_extent()
                    }
                }
                ToolTip.visible: hovered
                ToolTip.text: "Zoom para extensão total"
            }
            
            ToolSeparator {}
            
            // Grupo: Ferramentas
            Label {
                text: "Ferramentas:"
                color: "#cccccc"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionIdentify.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "identify"
                onClicked: {
                    toolbar.setActiveTool("identify")
                    statusBar.showMessage("Ferramenta: Identificar")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Identificar feições"
            }
            
            ToolSeparator {}
            
            // Grupo: Desenho
            Label {
                text: "Desenho:"
                color: "#cccccc"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionCapturePoint.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "addPoint"
                onClicked: {
                    toolbar.setActiveTool("addPoint")
                    statusBar.showMessage("Ferramenta: Adicionar Ponto")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Adicionar ponto"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionCaptureLine.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "addLine"
                onClicked: {
                    toolbar.setActiveTool("addLine")
                    statusBar.showMessage("Ferramenta: Adicionar Linha")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Adicionar linha (Direito finaliza)"
            }
            
            ToolButton {
                icon.source: "images/themes/default/mActionCapturePolygon.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                checkable: true
                checked: toolbar.activeTool === "addPolygon"
                onClicked: {
                    toolbar.setActiveTool("addPolygon")
                    statusBar.showMessage("Ferramenta: Adicionar Polígono")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Adicionar polígono (Direito fecha)"
            }
            
            ToolSeparator {}
            
            ToolButton {
                icon.source: "images/themes/default/mActionRefresh.svg"
                icon.color: "transparent"
                icon.width: 24
                icon.height: 24
                display: AbstractButton.IconOnly
                onClicked: {
                    mapCanvas.update()
                    statusBar.showMessage("Mapa atualizado")
                }
                ToolTip.visible: hovered
                ToolTip.text: "Atualizar mapa"
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
    }
    
    // Área principal
    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal
        
        // Painel com Abas (esquerda) - Menu Sanduíche
        Rectangle {
            id: tabbedPanel
            property bool collapsed: false
            property int previousIndex: -1  // Rastreia a aba anterior para toggle
            SplitView.preferredWidth: collapsed ? 50 : 280
            SplitView.minimumWidth: collapsed ? 50 : 200
            color: "#2d2d30"
            
            // TabBar invisível para gerenciar o índice das abas
            TabBar {
                id: tabBar
                visible: false
                
                TabButton { text: "Camadas" }
                TabButton { text: "Propriedades" }
                TabButton { text: "Processamento" }
                TabButton { text: "Vazio1" }
                TabButton { text: "Vazio2" }
            }
            
            RowLayout {
                anchors.fill: parent
                spacing: 0
                
                // Painel de ícones laterais (esquerda)
                Rectangle {
                    id: iconPanel
                    Layout.preferredWidth: 50
                    Layout.fillHeight: true
                    color: "#2d2d30"
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 10
                        
                        // Ícone Camadas
                        ToolButton {
                            Layout.alignment: Qt.AlignHCenter
                            icon.source: "images/themes/default/mActionLayers.svg"
                            icon.color: "transparent"
                            icon.width: 24
                            icon.height: 24
                            display: AbstractButton.IconOnly
                            onClicked: {
                                if (tabBar.currentIndex === 0 && !tabbedPanel.collapsed) {
                                    // Se já está nessa aba e expandido, minimiza
                                    tabbedPanel.collapsed = true
                                    tabbedPanel.previousIndex = 0
                                } else {
                                    // Se é outra aba ou está minimizado, seleciona e expande
                                    tabBar.currentIndex = 0
                                    tabbedPanel.collapsed = false
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: "Camadas"
                            
                            background: Rectangle {
                                color: tabBar.currentIndex === 0 ? "#3e3e42" : "transparent"
                                border.color: tabBar.currentIndex === 0 ? "#007acc" : "transparent"
                                border.width: 2
                                radius: 4
                            }
                        }
                        
                        // Ícone Propriedades
                        ToolButton {
                            Layout.alignment: Qt.AlignHCenter
                            icon.source: "images/themes/default/mActionProperties.svg"
                            icon.color: "transparent"
                            icon.width: 24
                            icon.height: 24
                            display: AbstractButton.IconOnly
                            onClicked: {
                                if (tabBar.currentIndex === 1 && !tabbedPanel.collapsed) {
                                    tabbedPanel.collapsed = true
                                    tabbedPanel.previousIndex = 1
                                } else {
                                    tabBar.currentIndex = 1
                                    tabbedPanel.collapsed = false
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: "Propriedades"
                            
                            background: Rectangle {
                                color: tabBar.currentIndex === 1 ? "#3e3e42" : "transparent"
                                border.color: tabBar.currentIndex === 1 ? "#007acc" : "transparent"
                                border.width: 2
                                radius: 4
                            }
                        }
                        
                        // Ícone Processamento
                        ToolButton {
                            Layout.alignment: Qt.AlignHCenter
                            icon.source: "images/themes/default/mActionFilter.svg"
                            icon.color: "transparent"
                            icon.width: 24
                            icon.height: 24
                            display: AbstractButton.IconOnly
                            onClicked: {
                                if (tabBar.currentIndex === 2 && !tabbedPanel.collapsed) {
                                    tabbedPanel.collapsed = true
                                    tabbedPanel.previousIndex = 2
                                } else {
                                    tabBar.currentIndex = 2
                                    tabbedPanel.collapsed = false
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: "Processamento"
                            
                            background: Rectangle {
                                color: tabBar.currentIndex === 2 ? "#3e3e42" : "transparent"
                                border.color: tabBar.currentIndex === 2 ? "#007acc" : "transparent"
                                border.width: 2
                                radius: 4
                            }
                        }
                        
                        // Ícone Vazio1
                        ToolButton {
                            Layout.alignment: Qt.AlignHCenter
                            icon.source: "images/themes/default/mActionIdentify.svg"
                            icon.color: "transparent"
                            icon.width: 24
                            icon.height: 24
                            display: AbstractButton.IconOnly
                            onClicked: {
                                if (tabBar.currentIndex === 3 && !tabbedPanel.collapsed) {
                                    tabbedPanel.collapsed = true
                                    tabbedPanel.previousIndex = 3
                                } else {
                                    tabBar.currentIndex = 3
                                    tabbedPanel.collapsed = false
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: "Vazio1"
                            
                            background: Rectangle {
                                color: tabBar.currentIndex === 3 ? "#3e3e42" : "transparent"
                                border.color: tabBar.currentIndex === 3 ? "#007acc" : "transparent"
                                border.width: 2
                                radius: 4
                            }
                        }
                        
                        // Ícone Vazio2
                        ToolButton {
                            Layout.alignment: Qt.AlignHCenter
                            icon.source: "images/themes/default/mActionMapTips.svg"
                            icon.color: "transparent"
                            icon.width: 24
                            icon.height: 24
                            display: AbstractButton.IconOnly
                            onClicked: {
                                if (tabBar.currentIndex === 4 && !tabbedPanel.collapsed) {
                                    tabbedPanel.collapsed = true
                                    tabbedPanel.previousIndex = 4
                                } else {
                                    tabBar.currentIndex = 4
                                    tabbedPanel.collapsed = false
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: "Vazio2"
                            
                            background: Rectangle {
                                color: tabBar.currentIndex === 4 ? "#3e3e42" : "transparent"
                                border.color: tabBar.currentIndex === 4 ? "#007acc" : "transparent"
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
                    
                    StackLayout {
                        id: contentStack
                        anchors.fill: parent
                        currentIndex: tabBar.currentIndex
                    
                    // Aba 1: Camadas
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 5
                        
                        ListView {
                            id: layerList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            
                            model: ListModel {
                                id: layerListModel
                                
                                ListElement {
                                    layerName: "Exemplo Pontos"
                                    layerType: "vector"
                                    visible: true
                                }
                                ListElement {
                                    layerName: "Camada Vetorial"
                                    layerType: "vector"
                                    visible: true
                                }
                                ListElement {
                                    layerName: "Camada Raster"
                                    layerType: "raster"
                                    visible: false
                                }
                            }
                            
                            delegate: ItemDelegate {
                                width: layerList.width
                                height: 40
                                
                                background: Rectangle {
                                    color: layerList.currentIndex === index ? "#094771" : "#3e3e42"
                                    border.color: "#555555"
                                    border.width: 1
                                }
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 5
                                    spacing: 8
                                    
                                    CheckBox {
                                        checked: model.visible
                                        onToggled: {
                                            layerListModel.setProperty(index, "visible", checked)
                                            statusBar.showMessage(model.layerName + " " + (checked ? "visível" : "oculto"))
                                        }
                                    }
                                    
                                    Label {
                                        text: model.layerType === "vector" ? "📐" : "🖼"
                                        font.pixelSize: 14
                                    }
                                    
                                    Label {
                                        text: model.layerName
                                        color: "#f1f1f1"
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                        font.pixelSize: 11
                                    }
                                }
                                
                                onClicked: {
                                    layerList.currentIndex = index
                                    statusBar.showMessage("Selecionado: " + model.layerName)
                                }
                            }
                            
                            ScrollBar.vertical: ScrollBar {
                                policy: ScrollBar.AsNeeded
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 5
                            
                            Button {
                                icon.source: "images/themes/default/mActionAddLayer.svg"
                                icon.color: "transparent"
                                icon.width: 16
                                icon.height: 16
                                display: AbstractButton.IconOnly
                                Layout.fillWidth: true
                                onClicked: {
                                    if (typeof mapBackend !== 'undefined') {
                                        var filePath = mapBackend.open_vector_dialog()
                                        if (filePath) {
                                            var success = mapBackend.add_vector_layer(filePath)
                                            if (success) {
                                                var fileName = filePath.substring(Math.max(filePath.lastIndexOf('/'), filePath.lastIndexOf('\\')) + 1)
                                                fileName = fileName.substring(0, fileName.lastIndexOf('.'))
                                                layerListModel.append({
                                                    layerName: fileName,
                                                    layerType: "vector",
                                                    visible: true
                                                })
                                            }
                                        }
                                    }
                                }
                                ToolTip.visible: hovered
                                ToolTip.text: "Adicionar camada"
                            }
                            
                            Button {
                                icon.source: "images/themes/default/mActionRemoveLayer.svg"
                                icon.color: "transparent"
                                icon.width: 16
                                icon.height: 16
                                display: AbstractButton.IconOnly
                                Layout.fillWidth: true
                                enabled: layerList.currentIndex >= 0
                                onClicked: {
                                    if (layerList.currentIndex >= 0) {
                                        var layerName = layerListModel.get(layerList.currentIndex).layerName
                                        if (typeof mapBackend !== 'undefined') {
                                            mapBackend.remove_layer(layerName)
                                        }
                                        layerListModel.remove(layerList.currentIndex)
                                        statusBar.showMessage("Removido: " + layerName)
                                    }
                                }
                                ToolTip.visible: hovered
                                ToolTip.text: "Remover camada selecionada"
                            }
                        }
                    }
                    
                    // Aba 2: Propriedades
                    Rectangle {
                        color: "#1e1e1e"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Propriedades da Camada Selecionada"
                                font.bold: true
                                color: "#f1f1f1"
                                font.pixelSize: 12
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                TextArea {
                                    readOnly: true
                                    wrapMode: TextArea.Wrap
                                    color: "#cccccc"
                                    text: layerList.currentIndex >= 0 ? 
                                        "Nome: " + layerListModel.get(layerList.currentIndex).layerName + "\n" +
                                        "Tipo: " + layerListModel.get(layerList.currentIndex).layerType + "\n" +
                                        "Visível: " + layerListModel.get(layerList.currentIndex).visible
                                        : "Selecione uma camada"
                                    
                                    background: Rectangle {
                                        color: "#2d2d30"
                                        border.color: "#555555"
                                        border.width: 1
                                    }
                                }
                            }
                        }
                    }
                    
                    // Aba 3: Processamento
                    Rectangle {
                        color: "#1e1e1e"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Ferramentas de Processamento"
                                font.bold: true
                                color: "#f1f1f1"
                                font.pixelSize: 12
                            }
                            
                            Label {
                                text: "Funcionalidades de processamento em desenvolvimento"
                                color: "#999999"
                                font.pixelSize: 11
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                            
                            Item {
                                Layout.fillHeight: true
                            }
                        }
                    }
                    
                    // Aba 4: Vazio1
                    Rectangle {
                        color: "#1e1e1e"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Vazio 1"
                                font.bold: true
                                color: "#f1f1f1"
                                font.pixelSize: 12
                            }
                            
                            Label {
                                text: "Esta aba está vazia. Configure conforme necessário."
                                color: "#999999"
                                font.pixelSize: 11
                            }
                            
                            Item {
                                Layout.fillHeight: true
                            }
                        }
                    }
                    
                    // Aba 5: Vazio2
                    Rectangle {
                        color: "#1e1e1e"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Vazio 2"
                                font.bold: true
                                color: "#f1f1f1"
                                font.pixelSize: 12
                            }
                            
                            Label {
                                text: "Esta aba está vazia. Configure conforme necessário."
                                color: "#999999"
                                font.pixelSize: 11
                            }
                            
                            Item {
                                Layout.fillHeight: true
                            }
                        }
                    }
                    }
                }
            }
        }
        
        // Canvas do mapa (centro)
        Rectangle {
            SplitView.fillWidth: true
            color: "#1e1e1e"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 5
                
                Label {
                    text: "Mapa Interativo com Map Tools"
                    font.bold: true
                    font.pixelSize: 14
                    color: "#f1f1f1"
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Rectangle {
                    id: mapCanvas
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#ffffff"
                    border.color: "#555555"
                    border.width: 2
                    
                    // Imagem do mapa renderizado
                    Image {
                        id: mapImage
                        anchors.fill: parent
                        fillMode: Image.Stretch
                        cache: false
                        
                        // Usa o ImageProvider do Python
                        source: "image://mapimage/map?" + (typeof mapBackend !== 'undefined' ? mapBackend.update_counter : 0)
                        
                        // Mensagem quando não há mapa
                        Label {
                            anchors.centerIn: parent
                            text: "Adicione uma camada vetorial ou raster\npara visualizar o mapa"
                            horizontalAlignment: Text.AlignHCenter
                            color: "#999999"
                            font.pixelSize: 14
                            visible: mapImage.status !== Image.Ready
                        }
                    }
                    
                    // MouseArea para interação
                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        hoverEnabled: true
                        
                        property point lastPos
                        
                        onPressed: (mouse) => {
                            lastPos = Qt.point(mouse.x, mouse.y)
                            statusBar.showMessage("Mouse: " + mouse.x + ", " + mouse.y + " - Ferramenta: " + toolbar.activeTool)
                        }
                        
                        onPositionChanged: (mouse) => {
                            coordLabel.text = "Coordenadas: " + mouse.x + ", " + mouse.y
                        }
                        
                        onReleased: (mouse) => {
                            statusBar.showMessage("Mouse released at: " + mouse.x + ", " + mouse.y)
                        }
                        
                        onWheel: (wheel) => {
                            // Implementar zoom com scroll
                            if (wheel.angleDelta.y > 0) {
                                if (typeof mapBackend !== 'undefined') {
                                    mapBackend.zoom_in()
                                }
                            } else {
                                if (typeof mapBackend !== 'undefined') {
                                    mapBackend.zoom_out()
                                }
                            }
                        }
                    }
                    
                    // Notifica mudança de tamanho
                    onWidthChanged: {
                        if (typeof mapBackend !== 'undefined' && width > 0 && height > 0) {
                            mapBackend.set_canvas_size(Math.floor(width), Math.floor(height))
                        }
                    }
                    
                    onHeightChanged: {
                        if (typeof mapBackend !== 'undefined' && width > 0 && height > 0) {
                            mapBackend.set_canvas_size(Math.floor(width), Math.floor(height))
                        }
                    }
                }
                
                Label {
                    id: coordLabel
                    text: "Coordenadas: 0, 0"
                    color: "#cccccc"
                    font.pixelSize: 10
                }
            }
        }
        
        // Painel de informações (direita)
        Rectangle {
            SplitView.preferredWidth: 300
            SplitView.minimumWidth: 200
            color: "#2d2d30"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 5
                
                Label {
                    text: "Informações"
                    font.bold: true
                    font.pixelSize: 14
                    color: "#f1f1f1"
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    TextArea {
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        color: "#f1f1f1"
                        selectByMouse: true
                        
                        text: "FERRAMENTAS DE MAPA\n\n" +
                              "🖱️ NAVEGAÇÃO:\n" +
                              "• Pan: Arrastar mapa\n" +
                              "• Zoom In: Clique para aproximar\n" +
                              "• Zoom Out: Clique para afastar\n" +
                              "• Wheel: Zoom no cursor\n\n" +
                              "ℹ️ CONSULTA:\n" +
                              "• Identificar: Clique em features\n\n" +
                              "✏️ DESENHO:\n" +
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
                            color: "#1e1e1e"
                            border.color: "#555555"
                            border.width: 1
                        }
                    }
                }
            }
        }
    }
    
    // Barra de status (rodapé)
    footer: ToolBar {
        id: statusBar
        height: 40
        
        property string message: "Pronto"
        
        function showMessage(msg) {
            message = msg
        }
        
        background: Rectangle {
            color: "#007acc"
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 6
            spacing: 10
            
            Label {
                text: statusBar.message
                color: "#ffffff"
                font.pixelSize: 13
                Layout.fillWidth: true
            }
            
            Label {
                text: "Ferramenta: " + toolbar.activeTool
                color: "#ffffff"
                font.pixelSize: 13
            }
        }
    }
    
    // Diálogo Sobre
    Dialog {
        id: aboutDialog
        title: "Sobre"
        modal: true
        anchors.centerIn: parent
        
        contentItem: ColumnLayout {
            spacing: 10
            
            Label {
                text: "Sistema de Mapa GIS"
                font.bold: true
                font.pixelSize: 18
            }
            
            Label {
                text: "Versão 1.0.0"
            }
            
            Label {
                text: "Sistema de informações geográficas\ndesenvolvido com Qt 6 e Python"
                wrapMode: Text.WordWrap
            }
            
            Label {
                text: "Similar ao QGIS com Map Tools"
            }
            
            Label {
                text: "© 2025 - Desenvolvido com ❤️"
            }
        }
        
        standardButtons: Dialog.Ok
    }
    
    // Atalhos de teclado
    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: Qt.quit()
    }
    
    Shortcut {
        sequence: "P"
        onActivated: {
            toolbar.setActiveTool("pan")
            statusBar.showMessage("Ferramenta: Pan")
        }
    }
    
    Shortcut {
        sequence: "I"
        onActivated: {
            toolbar.setActiveTool("identify")
            statusBar.showMessage("Ferramenta: Identificar")
        }
    }
    
    Shortcut {
        sequence: "Escape"
        onActivated: {
            toolbar.setActiveTool("pan")
            statusBar.showMessage("Ferramenta Pan ativada (ESC)")
        }
    }
    
    Component.onCompleted: {
        statusBar.showMessage("Sistema iniciado - Ferramenta: Pan")
    }
}
