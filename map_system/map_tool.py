"""
Sistema de Ferramentas de Mapa (Map Tools)
Similar ao sistema QgsMapTool do QGIS - permite diferentes modos de interação
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple, List
from dataclasses import dataclass


class MapToolType(Enum):
    """Tipos de ferramentas de mapa"""
    PAN = "pan"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    IDENTIFY = "identify"
    ADD_POINT = "add_point"
    ADD_LINE = "add_line"
    ADD_POLYGON = "add_polygon"
    MEASURE = "measure"


@dataclass
class MouseEvent:
    """Evento de mouse"""
    x: int
    y: int
    button: int  # 1=left, 2=middle, 3=right
    modifiers: int = 0


@dataclass
class Geometry:
    """Geometria simples"""
    type: str  # "Point", "LineString", "Polygon"
    coordinates: List[Tuple[float, float]]
    properties: dict = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class MapTool(ABC):
    """
    Classe base para ferramentas de mapa.
    Similar ao QgsMapTool do QGIS.
    """
    
    def __init__(self, canvas):
        """
        Inicializa a ferramenta.
        
        Args:
            canvas: MapCanvas associado
        """
        self.canvas = canvas
        self._active = False
        self._cursor = "default"
    
    @property
    def active(self) -> bool:
        """Retorna se a ferramenta está ativa"""
        return self._active
    
    @property
    def cursor(self) -> str:
        """Retorna o cursor da ferramenta"""
        return self._cursor
    
    def activate(self):
        """Ativa a ferramenta"""
        self._active = True
        print(f"Ferramenta {self.__class__.__name__} ativada")
    
    def deactivate(self):
        """Desativa a ferramenta"""
        self._active = False
        print(f"Ferramenta {self.__class__.__name__} desativada")
    
    @abstractmethod
    def mouse_press(self, event: MouseEvent):
        """Handler para botão do mouse pressionado"""
        pass
    
    @abstractmethod
    def mouse_move(self, event: MouseEvent):
        """Handler para movimento do mouse"""
        pass
    
    @abstractmethod
    def mouse_release(self, event: MouseEvent):
        """Handler para botão do mouse solto"""
        pass
    
    def mouse_wheel(self, event: MouseEvent, delta: int):
        """Handler para scroll do mouse"""
        pass
    
    def key_press(self, key: str):
        """Handler para tecla pressionada"""
        pass
    
    def draw_overlay(self, painter):
        """
        Desenha overlay sobre o mapa (rubber bands, etc).
        
        Args:
            painter: Objeto para desenho
        """
        pass


class PanTool(MapTool):
    """Ferramenta de Pan - arrasta o mapa"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "move"
        self._dragging = False
        self._last_pos = None
    
    def mouse_press(self, event: MouseEvent):
        """Inicia o pan"""
        if event.button == 1:  # Botão esquerdo
            self._dragging = True
            self._last_pos = (event.x, event.y)
    
    def mouse_move(self, event: MouseEvent):
        """Move o mapa durante pan"""
        if self._dragging and self._last_pos:
            dx = event.x - self._last_pos[0]
            dy = event.y - self._last_pos[1]
            
            # Chama o pan do canvas
            if hasattr(self.canvas, 'pan'):
                self.canvas.pan(dx, dy)
            
            self._last_pos = (event.x, event.y)
    
    def mouse_release(self, event: MouseEvent):
        """Finaliza o pan"""
        self._dragging = False
        self._last_pos = None


class ZoomInTool(MapTool):
    """Ferramenta de Zoom In - clique para aproximar"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "zoom_in"
    
    def mouse_press(self, event: MouseEvent):
        """Aplica zoom centrado no clique"""
        if event.button == 1:
            # Converte posição do mouse para coordenadas do mapa
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos and hasattr(self.canvas, 'zoom_in'):
                    self.canvas.zoom_in(world_pos)
    
    def mouse_move(self, event: MouseEvent):
        """Não faz nada no move"""
        pass
    
    def mouse_release(self, event: MouseEvent):
        """Não faz nada no release"""
        pass


class ZoomOutTool(MapTool):
    """Ferramenta de Zoom Out - clique para afastar"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "zoom_out"
    
    def mouse_press(self, event: MouseEvent):
        """Aplica zoom out centrado no clique"""
        if event.button == 1:
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos and hasattr(self.canvas, 'zoom_out'):
                    self.canvas.zoom_out(world_pos)
    
    def mouse_move(self, event: MouseEvent):
        pass
    
    def mouse_release(self, event: MouseEvent):
        pass


class IdentifyTool(MapTool):
    """Ferramenta de Identificação - clique para identificar features"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "crosshair"
    
    def mouse_press(self, event: MouseEvent):
        """Identifica features no ponto clicado"""
        if event.button == 1:
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos:
                    print(f"Identificando features em: {world_pos}")
                    # TODO: Implementar identificação de features
    
    def mouse_move(self, event: MouseEvent):
        pass
    
    def mouse_release(self, event: MouseEvent):
        pass


class AddPointTool(MapTool):
    """Ferramenta para adicionar pontos"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "crosshair"
        self.points = []
    
    def mouse_press(self, event: MouseEvent):
        """Adiciona ponto no clique"""
        if event.button == 1:
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos:
                    self.points.append(world_pos)
                    print(f"Ponto adicionado: {world_pos}")
                    
                    # Cria geometria
                    geom = Geometry(
                        type="Point",
                        coordinates=[world_pos],
                        properties={"id": len(self.points)}
                    )
                    
                    # Emite sinal (se canvas tiver suporte)
                    if hasattr(self.canvas, 'geometry_added'):
                        self.canvas.geometry_added.emit(geom)
    
    def mouse_move(self, event: MouseEvent):
        pass
    
    def mouse_release(self, event: MouseEvent):
        pass
    
    def draw_overlay(self, painter):
        """Desenha pontos temporários"""
        # TODO: Implementar desenho de overlay
        pass


class AddLineTool(MapTool):
    """Ferramenta para adicionar linhas"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "crosshair"
        self.vertices = []
        self._active_line = False
    
    def activate(self):
        super().activate()
        self.vertices = []
        self._active_line = False
    
    def mouse_press(self, event: MouseEvent):
        """Adiciona vértice à linha"""
        if event.button == 1:  # Botão esquerdo - adiciona vértice
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos:
                    self.vertices.append(world_pos)
                    self._active_line = True
                    print(f"Vértice {len(self.vertices)}: {world_pos}")
        
        elif event.button == 3:  # Botão direito - finaliza linha
            if len(self.vertices) >= 2:
                geom = Geometry(
                    type="LineString",
                    coordinates=self.vertices.copy(),
                    properties={}
                )
                print(f"Linha finalizada com {len(self.vertices)} vértices")
                
                if hasattr(self.canvas, 'geometry_added'):
                    self.canvas.geometry_added.emit(geom)
                
                # Reset
                self.vertices = []
                self._active_line = False
    
    def mouse_move(self, event: MouseEvent):
        """Atualiza preview da linha"""
        # TODO: Atualizar rubber band
        pass
    
    def mouse_release(self, event: MouseEvent):
        pass
    
    def key_press(self, key: str):
        """ESC cancela, Enter finaliza"""
        if key == "Escape":
            self.vertices = []
            self._active_line = False
            print("Desenho de linha cancelado")
        elif key == "Return" and len(self.vertices) >= 2:
            # Finaliza como se fosse botão direito
            geom = Geometry(
                type="LineString",
                coordinates=self.vertices.copy()
            )
            if hasattr(self.canvas, 'geometry_added'):
                self.canvas.geometry_added.emit(geom)
            self.vertices = []
            self._active_line = False


class AddPolygonTool(MapTool):
    """Ferramenta para adicionar polígonos"""
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self._cursor = "crosshair"
        self.vertices = []
        self._active_polygon = False
    
    def activate(self):
        super().activate()
        self.vertices = []
        self._active_polygon = False
    
    def mouse_press(self, event: MouseEvent):
        """Adiciona vértice ao polígono"""
        if event.button == 1:  # Botão esquerdo - adiciona vértice
            if hasattr(self.canvas, 'pixel_to_world'):
                world_pos = self.canvas.pixel_to_world(event.x, event.y)
                if world_pos:
                    self.vertices.append(world_pos)
                    self._active_polygon = True
                    print(f"Vértice {len(self.vertices)}: {world_pos}")
        
        elif event.button == 3:  # Botão direito - fecha polígono
            if len(self.vertices) >= 3:
                # Fecha o anel
                vertices = self.vertices.copy()
                if vertices[0] != vertices[-1]:
                    vertices.append(vertices[0])
                
                geom = Geometry(
                    type="Polygon",
                    coordinates=[vertices],  # Lista de anéis
                    properties={}
                )
                print(f"Polígono finalizado com {len(self.vertices)} vértices")
                
                if hasattr(self.canvas, 'geometry_added'):
                    self.canvas.geometry_added.emit(geom)
                
                # Reset
                self.vertices = []
                self._active_polygon = False
    
    def mouse_move(self, event: MouseEvent):
        """Atualiza preview do polígono"""
        # TODO: Atualizar rubber band
        pass
    
    def mouse_release(self, event: MouseEvent):
        pass
    
    def key_press(self, key: str):
        """ESC cancela, Enter finaliza"""
        if key == "Escape":
            self.vertices = []
            self._active_polygon = False
            print("Desenho de polígono cancelado")
        elif key == "Return" and len(self.vertices) >= 3:
            vertices = self.vertices.copy()
            if vertices[0] != vertices[-1]:
                vertices.append(vertices[0])
            
            geom = Geometry(
                type="Polygon",
                coordinates=[vertices]
            )
            if hasattr(self.canvas, 'geometry_added'):
                self.canvas.geometry_added.emit(geom)
            self.vertices = []
            self._active_polygon = False


class MapToolManager:
    """
    Gerenciador de ferramentas de mapa.
    Controla qual ferramenta está ativa.
    """
    
    def __init__(self, canvas):
        """
        Inicializa o gerenciador.
        
        Args:
            canvas: MapCanvas associado
        """
        self.canvas = canvas
        self._tools = {}
        self._current_tool = None
        
        # Registra ferramentas padrão
        self.register_tool(MapToolType.PAN, PanTool(canvas))
        self.register_tool(MapToolType.ZOOM_IN, ZoomInTool(canvas))
        self.register_tool(MapToolType.ZOOM_OUT, ZoomOutTool(canvas))
        self.register_tool(MapToolType.IDENTIFY, IdentifyTool(canvas))
        self.register_tool(MapToolType.ADD_POINT, AddPointTool(canvas))
        self.register_tool(MapToolType.ADD_LINE, AddLineTool(canvas))
        self.register_tool(MapToolType.ADD_POLYGON, AddPolygonTool(canvas))
        
        # Ativa Pan por padrão
        self.set_tool(MapToolType.PAN)
    
    def register_tool(self, tool_type: MapToolType, tool: MapTool):
        """Registra uma ferramenta"""
        self._tools[tool_type] = tool
    
    def set_tool(self, tool_type: MapToolType):
        """
        Ativa uma ferramenta.
        
        Args:
            tool_type: Tipo da ferramenta
        """
        if tool_type not in self._tools:
            print(f"Ferramenta {tool_type} não registrada")
            return
        
        # Desativa ferramenta atual
        if self._current_tool:
            self._current_tool.deactivate()
        
        # Ativa nova ferramenta
        self._current_tool = self._tools[tool_type]
        self._current_tool.activate()
    
    def current_tool(self) -> Optional[MapTool]:
        """Retorna a ferramenta atual"""
        return self._current_tool
    
    def handle_mouse_press(self, event: MouseEvent):
        """Repassa evento para ferramenta atual"""
        if self._current_tool:
            self._current_tool.mouse_press(event)
    
    def handle_mouse_move(self, event: MouseEvent):
        """Repassa evento para ferramenta atual"""
        if self._current_tool:
            self._current_tool.mouse_move(event)
    
    def handle_mouse_release(self, event: MouseEvent):
        """Repassa evento para ferramenta atual"""
        if self._current_tool:
            self._current_tool.mouse_release(event)
    
    def handle_mouse_wheel(self, event: MouseEvent, delta: int):
        """Repassa evento para ferramenta atual"""
        if self._current_tool:
            self._current_tool.mouse_wheel(event, delta)
    
    def handle_key_press(self, key: str):
        """Repassa evento para ferramenta atual"""
        if self._current_tool:
            self._current_tool.key_press(key)