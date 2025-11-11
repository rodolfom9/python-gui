"""
Sistema de Mapa Interativo - Main
Interface QML com menus do Tkinter
Integra renderizador Qt, GDAL e interface QML
"""

import sys
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

# IMPORTANTE: Inicializa GDAL ANTES de importar Qt
from osgeo import gdal, ogr
# Configura GDAL para evitar conflitos com Qt
gdal.SetConfigOption('GDAL_PAM_ENABLED', 'NO')
gdal.SetConfigOption('CPL_DEBUG', 'OFF')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot, pyqtProperty, QThread
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtQuick import QQuickImageProvider

# Importa componentes
from map_system import VectorLayer, RasterLayer
from map_system.layer_manager import LayerManager
from map_system.qml_renderer import QtSimpleRenderer, RenderContext


class MapImageProvider(QQuickImageProvider):
    """Provedor de imagem do mapa para QML"""
    
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self.current_image = None
    
    def requestImage(self, id, size):
        """Retorna a imagem do mapa"""
        from PyQt6.QtCore import QSize
        
        try:
            if self.current_image is not None and not self.current_image.isNull():
                # Retorna a imagem e seu tamanho
                print(f"[DEBUG] ImageProvider retornando imagem: {self.current_image.width()}x{self.current_image.height()}")
                return self.current_image, self.current_image.size()
            
            # Retorna imagem vazia se não houver mapa
            print(f"[DEBUG] ImageProvider retornando imagem vazia")
            img = QImage(800, 600, QImage.Format.Format_RGB32)
            img.fill(0xFFFFFF)
            return img, QSize(800, 600)
            
        except Exception as e:
            print(f"[ERRO] Erro no ImageProvider.requestImage: {str(e)}")
            import traceback
            traceback.print_exc()
            # Retorna imagem de fallback
            img = QImage(800, 600, QImage.Format.Format_RGB32)
            img.fill(0xFFFFFF)
            return img, QSize(800, 600)
    
    def set_image(self, image):
        """Define a imagem atual"""
        self.current_image = image


class MapBridgeMain(QObject):
    """Bridge entre QML e sistema de mapas Python - versao main"""
    
    # Signals
    layer_count_changed = pyqtSignal()
    status_message = pyqtSignal(str)
    map_updated = pyqtSignal()
    image_updated = pyqtSignal()
    
    def __init__(self, image_provider):
        super().__init__()
        
        self.layer_manager = LayerManager()
        self.renderer = QtSimpleRenderer()
        self.image_provider = image_provider
        self._extent = None
        self._width = 1200
        self._height = 800
        self._update_counter = 0
        
        print("MapBridge inicializado com Qt Renderer")
    
    @pyqtSlot(str, result=bool)
    def add_vector_layer(self, file_path: str) -> bool:
        """Adiciona camada vetorial"""
        try:
            file_path = file_path.replace("file:///", "").replace("file://", "")
            
            print(f"[DEBUG] Carregando camada vetorial: {file_path}")
            
            name = Path(file_path).stem
            layer = VectorLayer(name, file_path)
            
            print(f"[DEBUG] Chamando layer.load()...")
            if not layer.load():
                print(f"[ERRO] Não foi possível carregar: {file_path}")
                return False
            
            print(f"[DEBUG] Camada carregada, adicionando ao layer_manager...")
            self.layer_manager.add_layer(layer)
            
            print(f"[DEBUG] Verificando extent: {layer.extent}")
            if self.layer_manager.layer_count() == 1 and layer.extent:
                print(f"[DEBUG] Primeira camada, ajustando zoom para extent: {layer.extent}")
                self._zoom_to_extent(layer.extent)
                print(f"[DEBUG] Novo extent após zoom: {self._extent}")
            
            print(f"[DEBUG] Emitindo sinais...")
            self.layer_count_changed.emit()
            self.map_updated.emit()
            
            print(f"[OK] Camada adicionada: {name} ({layer.get_feature_count()} features)")
            self.status_message.emit(f"Camada adicionada: {name}")
            
            # Renderiza o mapa
            print(f"[DEBUG] Chamando render_map()...")
            self.render_map()
            print(f"[DEBUG] render_map() concluído")
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Exceção em add_vector_layer: {str(e)}")
            self.status_message.emit(f"Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @pyqtSlot(result=str)
    def open_vector_dialog(self) -> str:
        """Abre dialog para selecionar arquivo vetorial usando Tkinter"""
        try:
            # Cria janela Tkinter invisível
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # Abre dialog
            file_path = filedialog.askopenfilename(
                title="Selecione arquivo vetorial",
                filetypes=[
                    ("Shapefiles", "*.shp"),
                    ("GeoJSON", "*.geojson *.json"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            root.destroy()
            return file_path if file_path else ""
        except Exception as e:
            print(f"[ERRO] Erro ao abrir dialog: {str(e)}")
            return ""
    
    @pyqtSlot(result=str)
    def open_raster_dialog(self) -> str:
        """Abre dialog para selecionar arquivo raster usando Tkinter"""
        try:
            # Cria janela Tkinter invisível
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # Abre dialog
            file_path = filedialog.askopenfilename(
                title="Selecione arquivo raster",
                filetypes=[
                    ("GeoTIFF", "*.tif *.tiff"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            root.destroy()
            return file_path if file_path else ""
        except Exception as e:
            print(f"[ERRO] Erro ao abrir dialog: {str(e)}")
            return ""
    
    @pyqtSlot(str, result=bool)
    def add_raster_layer(self, file_path: str) -> bool:
        """Adiciona camada raster"""
        try:
            file_path = file_path.replace("file:///", "").replace("file://", "")
            
            print(f"Carregando camada raster: {file_path}")
            
            name = Path(file_path).stem
            layer = RasterLayer(name, file_path)
            
            if not layer.load():
                print(f"Erro ao carregar: {file_path}")
                return False
            
            self.layer_manager.add_layer(layer)
            
            if self.layer_manager.layer_count() == 1 and layer.extent:
                self._zoom_to_extent(layer.extent)
            
            self.layer_count_changed.emit()
            self.map_updated.emit()
            
            print(f"[OK] Raster adicionado: {name}")
            self.status_message.emit(f"Raster adicionado: {name}")
            
            return True
            
        except Exception as e:
            print(f"Erro: {str(e)}")
            self.status_message.emit(f"Erro: {str(e)}")
            return False
    
    @pyqtSlot(str, result=bool)
    def remove_layer(self, layer_name: str) -> bool:
        """Remove camada"""
        success = self.layer_manager.remove_layer(layer_name)
        if success:
            self.layer_count_changed.emit()
            self.map_updated.emit()
            self.status_message.emit(f"Camada removida: {layer_name}")
            # Renderiza o mapa novamente após remover a camada
            self.render_map()
        return success
    
    @pyqtSlot(str, bool)
    def set_layer_visibility(self, layer_name: str, visible: bool) -> None:
        """Define visibilidade da camada"""
        success = self.layer_manager.set_layer_visibility(layer_name, visible)
        if success:
            self.status_message.emit(f"Camada '{layer_name}' " + ("visível" if visible else "oculta"))
    
    @pyqtSlot()
    def zoom_in(self):
        """Zoom in"""
        if self._extent:
            self._zoom(1.0 / 1.2)
            self.render_map()
            self.map_updated.emit()
            self.status_message.emit("Zoom In")
    
    @pyqtSlot()
    def zoom_out(self):
        """Zoom out"""
        if self._extent:
            self._zoom(1.2)
            self.render_map()
            self.map_updated.emit()
            self.status_message.emit("Zoom Out")
    
    @pyqtSlot()
    def zoom_to_full_extent(self):
        """Zoom total"""
        combined_extent = self.layer_manager.get_combined_extent()
        if combined_extent:
            self._zoom_to_extent(combined_extent)
            self.render_map()
            self.map_updated.emit()
            self.status_message.emit("Zoom Total")
    
    @pyqtSlot(str)
    def set_tool(self, tool_name: str):
        """Define ferramenta ativa"""
        self.status_message.emit(f"Ferramenta: {tool_name}")
    
    @pyqtSlot(int, int)
    def set_canvas_size(self, width: int, height: int):
        """Define tamanho do canvas"""
        self._width = width
        self._height = height
        if self._extent:
            self.render_map()
    
    @pyqtSlot()
    def render_map(self):
        """Renderiza o mapa"""
        print(f"[DEBUG] render_map chamado - extent: {self._extent}, layers: {self.layer_manager.layer_count()}")
        
        if not self._extent or self.layer_manager.layer_count() == 0:
            print("[DEBUG] Sem extent ou camadas, pulando renderização")
            return
        
        if self._width <= 0 or self._height <= 0:
            print(f"[DEBUG] Dimensões inválidas: {self._width}x{self._height}")
            return
        
        try:
            print(f"[DEBUG] Criando QImage base: {self._width}x{self._height}")
            # Cria QImage base branca
            base_image = QImage(self._width, self._height, QImage.Format.Format_RGB32)
            base_image.fill(0xFFFFFF)  # Branco
            
            print(f"[DEBUG] Criando RenderContext")
            # Cria contexto de renderização
            context = RenderContext(
                width=self._width,
                height=self._height,
                extent=self._extent
            )
            
            # Cria QPainter para compor as camadas
            from PyQt6.QtGui import QPainter
            painter = QPainter(base_image)
            
            print(f"[DEBUG] Renderizando {self.layer_manager.layer_count()} camadas")
            # Renderiza todas as camadas
            layer_count = 0
            for layer in self.layer_manager.get_all_layers():
                if layer.visible:
                    print(f"[DEBUG] Renderizando camada: {layer.name}")
                    try:
                        # Renderer retorna uma QImage
                        layer_image = self.renderer.render(layer, context)
                        if layer_image:
                            # Desenha a imagem da camada na imagem base
                            painter.drawImage(0, 0, layer_image)
                            layer_count += 1
                    except Exception as layer_error:
                        print(f"[ERRO] Falha ao renderizar camada {layer.name}: {str(layer_error)}")
                        import traceback
                        traceback.print_exc()
            
            painter.end()
            print(f"[DEBUG] {layer_count} camadas renderizadas com sucesso")
            
            # Atualiza o image provider
            print(f"[DEBUG] Atualizando image provider")
            self.image_provider.set_image(base_image)
            
            # Incrementa contador e emite sinal
            self._update_counter += 1
            print(f"[DEBUG] Emitindo image_updated (counter: {self._update_counter})")
            self.image_updated.emit()
            
            print(f"[OK] Mapa renderizado: {self._width}x{self._height}")
            
        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro ao renderizar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @pyqtProperty(int, notify=image_updated)
    def update_counter(self):
        """Contador de atualizações para forçar refresh da imagem"""
        return self._update_counter
    
    def _zoom(self, factor):
        """Aplica zoom"""
        if not self._extent:
            return
        
        minx, miny, maxx, maxy = self._extent
        
        cx = (minx + maxx) / 2
        cy = (miny + maxy) / 2
        
        width = (maxx - minx) * factor
        height = (maxy - miny) * factor
        
        self._extent = (
            cx - width / 2,
            cy - height / 2,
            cx + width / 2,
            cy + height / 2
        )
    
    def _zoom_to_extent(self, extent):
        """Ajusta zoom para extensao"""
        minx, miny, maxx, maxy = extent
        
        width = maxx - minx
        height = maxy - miny
        margin_x = width * 0.05
        margin_y = height * 0.05
        
        self._extent = (
            minx - margin_x,
            miny - margin_y,
            maxx + margin_x,
            maxy + margin_y
        )
    
    @property
    def layer_count(self):
        """Retorna numero de camadas"""
        return self.layer_manager.layer_count()


def main():
    """Funcao principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Mapa Interativo - Map Tools")
    app.setApplicationVersion("1.0")
    
    print("=" * 70)
    print("Sistema de Mapa Interativo - Map Tools")
    print("=" * 70)
    print("[OK] Renderizador: QtSimpleRenderer (QPainter native)")
    print("[OK] Interface: Qt QML com Menus")
    print("[OK] Backend: Python + GDAL/OGR")
    print("=" * 70)
    
    # Cria engine
    engine = QQmlApplicationEngine()
    
    # Define o diretório base para recursos (onde está o QML)
    base_dir = Path(__file__).parent
    ui_dir = base_dir / "Ui"
    engine.setBaseUrl(QUrl.fromLocalFile(str(ui_dir)))
    
    # Adiciona caminhos para componentes e módulos
    engine.addImportPath(str(ui_dir / "Ui"))  # Para componentes como AppMenuBar, etc
    engine.addImportPath(str(ui_dir))  # Para módulo "Ui"
    
    # Cria image provider
    image_provider = MapImageProvider()
    engine.addImageProvider("mapimage", image_provider)
    
    # Cria bridge com image provider
    map_bridge = MapBridgeMain(image_provider)
    
    # Registra bridge no QML
    engine.rootContext().setContextProperty("mapBackend", map_bridge)
    
    # Carrega QML
    qml_file = ui_dir / "UiContent" / "App.qml"
    print(f"Carregando QML: {qml_file}")
    print(f"Diretório base: {ui_dir}")
    
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("Erro: Nao foi possivel carregar QML")
        sys.exit(-1)
    
    print("[OK] Interface QML carregada com sucesso!")
    print("[OK] Menus do Tkinter integrados no QML")
    print("[OK] Janela exibida")
    print("=" * 70)
    print("Use os menus: Arquivo, Ferramentas, Camadas, Ajuda")
    print("Pressione Ctrl+C para sair\n")
    
    # Force a exibicao da janela
    root = engine.rootObjects()[0]
    if root:
        root.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

    def set_layer_visibility(self, layer_name: str, visible: bool) -> None:
        """Define visibilidade da camada"""
        success = self.layer_manager.set_layer_visibility(layer_name, visible)
        if success:
            self.status_message.emit(f"Camada '{layer_name}' " + ("visível" if visible else "oculta"))
    
    @pyqtSlot()

    def zoom_in(self):

        """Zoom in"""

        if self._extent:

            self._zoom(1.0 / 1.2)

            self.render_map()

            self.map_updated.emit()

            self.status_message.emit("Zoom In")

    

    @pyqtSlot()

    def zoom_out(self):

        """Zoom out"""

        if self._extent:

            self._zoom(1.2)

            self.render_map()

            self.map_updated.emit()

            self.status_message.emit("Zoom Out")

    

    @pyqtSlot()

    def zoom_to_full_extent(self):

        """Zoom total"""

        combined_extent = self.layer_manager.get_combined_extent()

        if combined_extent:

            self._zoom_to_extent(combined_extent)

            self.render_map()

            self.map_updated.emit()

            self.status_message.emit("Zoom Total")

    

    @pyqtSlot(str)

    def set_tool(self, tool_name: str):

        """Define ferramenta ativa"""

        self.status_message.emit(f"Ferramenta: {tool_name}")

    

    @pyqtSlot(int, int)

    def set_canvas_size(self, width: int, height: int):

        """Define tamanho do canvas"""

        self._width = width

        self._height = height

        if self._extent:

            self.render_map()

    

    @pyqtSlot()

    def render_map(self):

        """Renderiza o mapa"""

        print(f"[DEBUG] render_map chamado - extent: {self._extent}, layers: {self.layer_manager.layer_count()}")

        

        if not self._extent or self.layer_manager.layer_count() == 0:

            print("[DEBUG] Sem extent ou camadas, pulando renderização")

            return

        

        if self._width <= 0 or self._height <= 0:

            print(f"[DEBUG] Dimensões inválidas: {self._width}x{self._height}")

            return

        

        try:

            print(f"[DEBUG] Criando QImage base: {self._width}x{self._height}")

            # Cria QImage base branca

            base_image = QImage(self._width, self._height, QImage.Format.Format_RGB32)

            base_image.fill(0xFFFFFF)  # Branco

            

            print(f"[DEBUG] Criando RenderContext")

            # Cria contexto de renderização

            context = RenderContext(

                width=self._width,

                height=self._height,

                extent=self._extent

            )

            

            # Cria QPainter para compor as camadas

            from PyQt6.QtGui import QPainter

            painter = QPainter(base_image)

            

            print(f"[DEBUG] Renderizando {self.layer_manager.layer_count()} camadas")

            # Renderiza todas as camadas

            layer_count = 0

            for layer in self.layer_manager.get_all_layers():

                if layer.visible:

                    print(f"[DEBUG] Renderizando camada: {layer.name}")

                    try:

                        # Renderer retorna uma QImage

                        layer_image = self.renderer.render(layer, context)

                        if layer_image:

                            # Desenha a imagem da camada na imagem base

                            painter.drawImage(0, 0, layer_image)

                            layer_count += 1

                    except Exception as layer_error:

                        print(f"[ERRO] Falha ao renderizar camada {layer.name}: {str(layer_error)}")

                        import traceback

                        traceback.print_exc()

            

            painter.end()

            print(f"[DEBUG] {layer_count} camadas renderizadas com sucesso")

            

            # Atualiza o image provider

            print(f"[DEBUG] Atualizando image provider")

            self.image_provider.set_image(base_image)

            

            # Incrementa contador e emite sinal

            self._update_counter += 1

            print(f"[DEBUG] Emitindo image_updated (counter: {self._update_counter})")

            self.image_updated.emit()

            

            print(f"[OK] Mapa renderizado: {self._width}x{self._height}")

            

        except Exception as e:

            print(f"[ERRO CRÍTICO] Erro ao renderizar: {str(e)}")

            import traceback

            traceback.print_exc()

    

    @pyqtProperty(int, notify=image_updated)

    def update_counter(self):

        """Contador de atualizações para forçar refresh da imagem"""

        return self._update_counter

    

    def _zoom(self, factor):

        """Aplica zoom"""

        if not self._extent:

            return

        

        minx, miny, maxx, maxy = self._extent

        

        cx = (minx + maxx) / 2

        cy = (miny + maxy) / 2

        

        width = (maxx - minx) * factor

        height = (maxy - miny) * factor

        

        self._extent = (

            cx - width / 2,

            cy - height / 2,

            cx + width / 2,

            cy + height / 2

        )

    

    def _zoom_to_extent(self, extent):

        """Ajusta zoom para extensao"""

        minx, miny, maxx, maxy = extent

        

        width = maxx - minx

        height = maxy - miny

        margin_x = width * 0.05

        margin_y = height * 0.05

        

        self._extent = (

            minx - margin_x,

            miny - margin_y,

            maxx + margin_x,

            maxy + margin_y

        )

    

    @property

    def layer_count(self):

        """Retorna numero de camadas"""

        return self.layer_manager.layer_count()





def main():

    """Funcao principal"""

    app = QApplication(sys.argv)

    app.setApplicationName("Sistema de Mapa Interativo - Map Tools")

    app.setApplicationVersion("1.0")

    

    print("=" * 70)

    print("Sistema de Mapa Interativo - Map Tools")

    print("=" * 70)

    print("[OK] Renderizador: QtSimpleRenderer (QPainter native)")

    print("[OK] Interface: Qt QML com Menus")

    print("[OK] Backend: Python + GDAL/OGR")

    print("=" * 70)

    

    # Cria engine

    engine = QQmlApplicationEngine()

    
    # Define o diretório base para recursos (onde está o QML)
    base_dir = Path(__file__).parent
    gui_dir = base_dir / "gui"
    engine.setBaseUrl(QUrl.fromLocalFile(str(gui_dir)))
    
    # Adiciona caminho para componentes
    engine.addImportPath(str(gui_dir / "components"))
    

    # Cria image provider

    image_provider = MapImageProvider()

    engine.addImageProvider("mapimage", image_provider)

    

    # Cria bridge com image provider

    map_bridge = MapBridgeMain(image_provider)

    

    # Registra bridge no QML

    engine.rootContext().setContextProperty("mapBackend", map_bridge)

    

    # Carrega QML

    qml_file = gui_dir / "UiContent" / "App.qml"
    print(f"Carregando QML: {qml_file}")

    print(f"Diretório base: {gui_dir}")
    

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    

    if not engine.rootObjects():

        print("Erro: Nao foi possivel carregar QML")

        sys.exit(-1)

    

    print("[OK] Interface QML carregada com sucesso!")

    print("[OK] Menus do Tkinter integrados no QML")

    print("[OK] Janela exibida")

    print("=" * 70)

    print("Use os menus: Arquivo, Ferramentas, Camadas, Ajuda")

    print("Pressione Ctrl+C para sair\n")

    

    # Force a exibicao da janela

    root = engine.rootObjects()[0]

    if root:

        root.show()

    

    sys.exit(app.exec())





if __name__ == "__main__":

    main()


