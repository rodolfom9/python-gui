"""
MapCanvas Interativo com suporte a Map Tools
Versão avançada do MapCanvas com sistema de ferramentas similar ao QGIS
"""

import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw
from typing import Optional, Tuple
from PyQt6.QtCore import pyqtSignal

from .layer_manager import LayerManager
from .renderer import RenderContext, SimpleRenderer
from .map_tool import MapToolManager, MouseEvent, MapToolType


class MapCanvasInteractive:
    """
    Canvas de mapa interativo com sistema de ferramentas.
    Similar ao QgsMapCanvas do QGIS com Map Tools.
    """
    
    def __init__(self, master, width: int = 800, height: int = 600):
        """
        Inicializa o MapCanvas interativo.
        
        Args:
            master: Widget pai do tkinter
            width: Largura do canvas
            height: Altura do canvas
        """
        self.master = master
        self.width = width
        self.height = height
        
        # Canvas tkinter
        self.canvas = Canvas(master, width=width, height=height, bg='#1a1a1a')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Gerenciador de camadas
        self.layer_manager = LayerManager()
        
        # Gerenciador de ferramentas
        self.tool_manager = MapToolManager(self)
        
        # Extensão atual
        self._extent = None
        
        # Renderizador
        self._renderer = SimpleRenderer()
        
        # Imagem renderizada
        self._current_image = None
        self._tk_image = None
        
        # Cache de renderização por camada
        self._layer_cache = {}  # {layer_name: (extent, image)}
        self._cache_enabled = True
        
        # Overlay para desenhos temporários
        self._overlay_image = None
        
        # Zoom config
        self._zoom_factor = 1.2
        self._min_extent_size = 1e-6
        
        # Bind eventos
        self._setup_events()
        
        print(f"MapCanvas Interativo criado: {width}x{height}")
        print("Ferramentas disponíveis: Pan, Zoom In/Out, Identificar, Adicionar Ponto/Linha/Polígono")
    
    def _setup_events(self):
        """Configura eventos do mouse e teclado"""
        # Mouse
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<ButtonPress-2>", self._on_mouse_press)
        self.canvas.bind("<ButtonPress-3>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_motion)
        self.canvas.bind("<B2-Motion>", self._on_mouse_motion)
        self.canvas.bind("<B3-Motion>", self._on_mouse_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<ButtonRelease-2>", self._on_mouse_release)
        self.canvas.bind("<ButtonRelease-3>", self._on_mouse_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        
        # Wheel
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)
        
        # Teclado
        self.canvas.bind("<KeyPress>", self._on_key_press)
        self.canvas.focus_set()
        
        # Redimensionamento
        self.canvas.bind("<Configure>", self._on_resize)
    
    def _on_mouse_press(self, event):
        """Handler para botão do mouse pressionado"""
        mouse_event = MouseEvent(
            x=event.x,
            y=event.y,
            button=event.num,
            modifiers=0
        )
        self.tool_manager.handle_mouse_press(mouse_event)
    
    def _on_mouse_motion(self, event):
        """Handler para movimento com botão pressionado"""
        mouse_event = MouseEvent(
            x=event.x,
            y=event.y,
            button=event.num,
            modifiers=0
        )
        self.tool_manager.handle_mouse_move(mouse_event)
    
    def _on_mouse_move(self, event):
        """Handler para movimento do mouse (sem botão)"""
        mouse_event = MouseEvent(
            x=event.x,
            y=event.y,
            button=0,
            modifiers=0
        )
        self.tool_manager.handle_mouse_move(mouse_event)
    
    def _on_mouse_release(self, event):
        """Handler para botão do mouse solto"""
        mouse_event = MouseEvent(
            x=event.x,
            y=event.y,
            button=event.num,
            modifiers=0
        )
        self.tool_manager.handle_mouse_release(mouse_event)
    
    def _on_mouse_wheel(self, event):
        """Handler para scroll do mouse"""
        delta = event.delta if hasattr(event, 'delta') else (-120 if event.num == 5 else 120)
        mouse_event = MouseEvent(
            x=event.x,
            y=event.y,
            button=0,
            modifiers=0
        )
        
        # Zoom com wheel
        if not self._extent:
            return
        
        world_pos = self.pixel_to_world(event.x, event.y)
        if world_pos:
            if delta > 0:
                self.zoom_in(world_pos)
            else:
                self.zoom_out(world_pos)
    
    def _on_key_press(self, event):
        """Handler para tecla pressionada"""
        self.tool_manager.handle_key_press(event.keysym)
    
    def _on_resize(self, event):
        """Handler para redimensionamento"""
        if event.width != self.width or event.height != self.height:
            self.width = event.width
            self.height = event.height
            self.refresh()
    
    # ========== Métodos de ferramenta ==========
    
    def set_tool(self, tool_type: MapToolType):
        """
        Define a ferramenta ativa.
        
        Args:
            tool_type: Tipo da ferramenta
        """
        self.tool_manager.set_tool(tool_type)
        
        # Atualiza cursor
        tool = self.tool_manager.current_tool()
        if tool:
            cursor_map = {
                "default": "",
                "move": "fleur",
                "crosshair": "crosshair",
                "zoom_in": "plus",
                "zoom_out": "minus"
            }
            cursor = cursor_map.get(tool.cursor, "")
            self.canvas.config(cursor=cursor)
    
    # ========== Métodos do MapCanvas original ==========
    
    def add_layer(self, layer, position: Optional[int] = None) -> bool:
        """Adiciona camada"""
        success = self.layer_manager.add_layer(layer, position)
        if success:
            # Limpa cache ao adicionar camada
            self._clear_cache()
            if self.layer_manager.layer_count() == 1 and layer.extent:
                self.zoom_to_extent(layer.extent)
            self.refresh()
        return success
    
    def remove_layer(self, layer_name: str) -> bool:
        """Remove camada"""
        success = self.layer_manager.remove_layer(layer_name)
        if success:
            # Remove do cache
            if layer_name in self._layer_cache:
                del self._layer_cache[layer_name]
            self.refresh()
        return success
    
    def get_extent(self) -> Optional[Tuple[float, float, float, float]]:
        """Retorna extensão atual"""
        return self._extent
    
    def set_extent(self, extent: Tuple[float, float, float, float]):
        """Define extensão"""
        self._extent = extent
        self.refresh()
    
    def zoom_to_full_extent(self):
        """Zoom para todas as camadas"""
        combined = self.layer_manager.get_combined_extent()
        if combined:
            self.zoom_to_extent(combined)
    
    def zoom_to_extent(self, extent: Tuple[float, float, float, float]):
        """Zoom para extensão específica"""
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
        self.refresh()
    
    def zoom_in(self, center: Optional[Tuple[float, float]] = None):
        """Zoom in"""
        self._zoom(1.0 / self._zoom_factor, center)
    
    def zoom_out(self, center: Optional[Tuple[float, float]] = None):
        """Zoom out"""
        self._zoom(self._zoom_factor, center)
    
    def _zoom(self, factor: float, center: Optional[Tuple[float, float]] = None):
        """Aplica zoom"""
        if not self._extent:
            return
        
        minx, miny, maxx, maxy = self._extent
        
        if center is None:
            cx = (minx + maxx) / 2
            cy = (miny + maxy) / 2
        else:
            cx, cy = center
        
        width = (maxx - minx) * factor
        height = (maxy - miny) * factor
        
        if width < self._min_extent_size or height < self._min_extent_size:
            return
        
        self._extent = (
            cx - width / 2,
            cy - height / 2,
            cx + width / 2,
            cy + height / 2
        )
        self.refresh()
    
    def pan(self, dx: float, dy: float):
        """Pan (movimento)"""
        if not self._extent:
            return
        
        minx, miny, maxx, maxy = self._extent
        
        # Converte pixels para coordenadas do mapa
        world_width = maxx - minx
        world_height = maxy - miny
        dx_world = -(dx / self.width) * world_width
        dy_world = (dy / self.height) * world_height
        
        self._extent = (
            minx + dx_world,
            miny + dy_world,
            maxx + dx_world,
            maxy + dy_world
        )
        self.refresh()
    
    def pixel_to_world(self, px: int, py: int) -> Optional[Tuple[float, float]]:
        """Converte pixel para coordenadas do mapa"""
        if not self._extent:
            return None
        
        minx, miny, maxx, maxy = self._extent
        x = minx + (px / self.width) * (maxx - minx)
        y = maxy - (py / self.height) * (maxy - miny)
        return x, y
    
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """Converte coordenadas do mapa para pixel"""
        if not self._extent:
            return 0, 0
        
        minx, miny, maxx, maxy = self._extent
        px = int((x - minx) / (maxx - minx) * self.width)
        py = int((maxy - y) / (maxy - miny) * self.height)
        return px, py
    
    def _clear_cache(self):
        """Limpa o cache de renderização"""
        self._layer_cache.clear()
    
    def _get_cached_layer_image(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """
        Obtém imagem da camada do cache ou renderiza se necessário.
        
        Args:
            layer: Camada a renderizar
            context: Contexto de renderização
            
        Returns:
            Imagem renderizada ou None
        """
        if not self._cache_enabled:
            return self._renderer.render(layer, context)
        
        cache_key = layer.name
        cached_data = self._layer_cache.get(cache_key)
        
        # Verifica se o cache é válido (mesma extensão)
        if cached_data is not None:
            cached_extent, cached_image = cached_data
            if cached_extent == self._extent:
                return cached_image
        
        # Renderiza e armazena no cache
        layer_image = self._renderer.render(layer, context)
        if layer_image:
            self._layer_cache[cache_key] = (self._extent, layer_image)
        
        return layer_image
    
    def refresh(self):
        """Redesenha o mapa"""
        if not self._extent:
            return
        
        # Cria contexto de renderização
        context = RenderContext(self.width, self.height, self._extent)
        
        # Renderiza camadas
        base_image = Image.new('RGBA', (self.width, self.height), (26, 26, 26, 255))
        
        for layer in self.layer_manager.get_visible_layers():
            if not layer.is_valid:
                continue
            
            # Obtém imagem da camada (do cache ou renderiza)
            layer_image = self._get_cached_layer_image(layer, context)
            if layer_image:
                if layer.opacity < 1.0:
                    alpha = layer_image.split()[3]
                    alpha = alpha.point(lambda x: int(x * layer.opacity))
                    layer_image.putalpha(alpha)
                base_image = Image.alpha_composite(base_image, layer_image)
        
        # TODO: Desenhar overlay da ferramenta atual
        
        self._current_image = base_image
        self._tk_image = ImageTk.PhotoImage(base_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self._tk_image, anchor=tk.NW)
    
    def save_image(self, filename: str):
        """Salva imagem"""
        if self._current_image:
            self._current_image.save(filename)
    
    def get_layer_manager(self) -> LayerManager:
        """Retorna gerenciador de camadas"""
        return self.layer_manager