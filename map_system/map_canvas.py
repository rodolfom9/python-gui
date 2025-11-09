"""
Módulo MapCanvas - Widget principal para exibição de mapas com zoom e pan
"""

import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from typing import Optional, Tuple, List
import numpy as np

from .layer_manager import LayerManager
from .renderer import RenderContext, SimpleRenderer
from .coordinate_transform import CoordinateTransform


class MapCanvas:
    """
    Canvas de mapa - widget principal para exibição de camadas.
    Similar ao QgsMapCanvas do QGIS.
    
    Funcionalidades:
    - Renderiza múltiplas camadas
    - Zoom com mouse wheel
    - Pan com drag do mouse
    - Controle de extensão
    """
    
    def __init__(self, master, width: int = 800, height: int = 600):
        """
        Inicializa o MapCanvas.
        
        Args:
            master: Widget pai do tkinter
            width: Largura do canvas em pixels
            height: Altura do canvas em pixels
        """
        self.master = master
        self.width = width
        self.height = height
        
        # Canvas tkinter
        self.canvas = Canvas(master, width=width, height=height, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Gerenciador de camadas
        self.layer_manager = LayerManager()
        
        # Extensão atual (minx, miny, maxx, maxy)
        self._extent = None
        
        # Renderizador padrão
        self._renderer = SimpleRenderer()
        
        # Imagem renderizada atual
        self._current_image = None
        self._tk_image = None
        
        # Cache de renderização por camada
        self._layer_cache = {}  # {layer_name: (extent, image)}
        self._cache_enabled = True
        
        # Estado do mouse para pan
        self._pan_start = None
        self._pan_active = False
        
        # Configuração de zoom
        self._zoom_factor = 1.2  # Fator de zoom por scroll
        self._min_extent_size = 1e-6  # Tamanho mínimo da extensão
        
        # Bind eventos do mouse
        self._setup_mouse_events()
        
        print(f"MapCanvas criado: {width}x{height}")
    
    def _setup_mouse_events(self):
        """Configura os eventos do mouse para interação"""
        # Zoom com wheel
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux scroll down
        
        # Pan com drag
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        
        # Redimensionamento
        self.canvas.bind("<Configure>", self._on_resize)
    
    def set_renderer(self, renderer):
        """
        Define um renderizador customizado.
        
        Args:
            renderer: Objeto Renderer
        """
        self._renderer = renderer
        print(f"Renderizador alterado para: {type(renderer).__name__}")
    
    def add_layer(self, layer, position: Optional[int] = None) -> bool:
        """
        Adiciona uma camada ao canvas.
        
        Args:
            layer: Camada a ser adicionada
            position: Posição onde inserir (None = no topo)
            
        Returns:
            True se adicionado com sucesso
        """
        success = self.layer_manager.add_layer(layer, position)
        if success:
            # Limpa cache ao adicionar camada
            self._clear_cache()
            # Se é a primeira camada, ajusta a extensão
            if self.layer_manager.layer_count() == 1 and layer.extent:
                self.zoom_to_extent(layer.extent)
            self.refresh()
        return success
    
    def remove_layer(self, layer_name: str) -> bool:
        """
        Remove uma camada do canvas.
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            True se removido com sucesso
        """
        success = self.layer_manager.remove_layer(layer_name)
        if success:
            # Remove do cache
            if layer_name in self._layer_cache:
                del self._layer_cache[layer_name]
            self.refresh()
        return success
    
    def get_extent(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Retorna a extensão atual do canvas.
        
        Returns:
            Tupla (minx, miny, maxx, maxy) ou None
        """
        return self._extent
    
    def set_extent(self, extent: Tuple[float, float, float, float]):
        """
        Define a extensão do canvas.
        
        Args:
            extent: Tupla (minx, miny, maxx, maxy)
        """
        self._extent = extent
        self.refresh()
    
    def zoom_to_full_extent(self):
        """Ajusta o zoom para mostrar todas as camadas"""
        combined_extent = self.layer_manager.get_combined_extent()
        if combined_extent:
            self.zoom_to_extent(combined_extent)
    
    def zoom_to_extent(self, extent: Tuple[float, float, float, float]):
        """
        Ajusta o zoom para uma extensão específica.
        
        Args:
            extent: Tupla (minx, miny, maxx, maxy)
        """
        minx, miny, maxx, maxy = extent
        
        # Adiciona margem de 5%
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
        """
        Aumenta o zoom (aproxima).
        
        Args:
            center: Centro do zoom em coordenadas do mapa (None = centro atual)
        """
        self._zoom(1.0 / self._zoom_factor, center)
    
    def zoom_out(self, center: Optional[Tuple[float, float]] = None):
        """
        Diminui o zoom (afasta).
        
        Args:
            center: Centro do zoom em coordenadas do mapa (None = centro atual)
        """
        self._zoom(self._zoom_factor, center)
    
    def _zoom(self, factor: float, center: Optional[Tuple[float, float]] = None):
        """
        Aplica zoom com fator especificado.
        
        Args:
            factor: Fator de zoom (>1 = zoom out, <1 = zoom in)
            center: Centro do zoom em coordenadas do mapa
        """
        if not self._extent:
            return
        
        minx, miny, maxx, maxy = self._extent
        
        # Se não especificou centro, usa o centro da extensão atual
        if center is None:
            cx = (minx + maxx) / 2
            cy = (miny + maxy) / 2
        else:
            cx, cy = center
        
        # Calcula nova extensão
        width = (maxx - minx) * factor
        height = (maxy - miny) * factor
        
        # Verifica tamanho mínimo
        if width < self._min_extent_size or height < self._min_extent_size:
            return
        
        new_extent = (
            cx - width / 2,
            cy - height / 2,
            cx + width / 2,
            cy + height / 2
        )
        
        self._extent = new_extent
        self.refresh()
    
    def pan(self, dx: float, dy: float):
        """
        Move o mapa (pan).
        
        Args:
            dx: Deslocamento X em coordenadas do mapa
            dy: Deslocamento Y em coordenadas do mapa
        """
        if not self._extent:
            return
        
        minx, miny, maxx, maxy = self._extent
        self._extent = (minx + dx, miny + dy, maxx + dx, maxy + dy)
        self.refresh()
    
    def pixel_to_world(self, px: int, py: int) -> Optional[Tuple[float, float]]:
        """
        Converte coordenadas de pixel para coordenadas do mapa.
        
        Args:
            px: Coordenada X em pixels
            py: Coordenada Y em pixels
            
        Returns:
            Tupla (x, y) em coordenadas do mapa ou None
        """
        if not self._extent:
            return None
        
        minx, miny, maxx, maxy = self._extent
        
        x = minx + (px / self.width) * (maxx - minx)
        y = maxy - (py / self.height) * (maxy - miny)  # Inverte Y
        
        return x, y
    
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """
        Converte coordenadas do mapa para coordenadas de pixel.
        
        Args:
            x: Coordenada X do mapa
            y: Coordenada Y do mapa
            
        Returns:
            Tupla (px, py) em pixels
        """
        if not self._extent:
            return 0, 0
        
        minx, miny, maxx, maxy = self._extent
        
        px = int((x - minx) / (maxx - minx) * self.width)
        py = int((maxy - y) / (maxy - miny) * self.height)  # Inverte Y
        
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
        """Redesenha o canvas"""
        if not self._extent:
            print("Extensão não definida, pulando refresh")
            return
        
        # Cria contexto de renderização
        context = RenderContext(self.width, self.height, self._extent)
        
        # Cria imagem base branca
        base_image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
        
        # Renderiza cada camada visível
        visible_layers = self.layer_manager.get_visible_layers()
        
        for layer in visible_layers:
            if not layer.is_valid:
                continue
            
            # Obtém imagem da camada (do cache ou renderiza)
            layer_image = self._get_cached_layer_image(layer, context)
            
            if layer_image:
                # Aplica opacidade
                if layer.opacity < 1.0:
                    alpha = layer_image.split()[3]  # Canal alpha
                    alpha = alpha.point(lambda x: int(x * layer.opacity))
                    layer_image.putalpha(alpha)
                
                # Compõe sobre a imagem base
                base_image = Image.alpha_composite(base_image, layer_image)
        
        # Atualiza canvas
        self._current_image = base_image
        self._tk_image = ImageTk.PhotoImage(base_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self._tk_image, anchor=tk.NW)
        
        print(f"Canvas atualizado: {len(visible_layers)} camadas visíveis")
    
    def _on_mouse_wheel(self, event):
        """Handler para zoom com mouse wheel"""
        if not self._extent:
            return
        
        # Obtém posição do mouse em coordenadas do mapa
        mouse_pos = self.pixel_to_world(event.x, event.y)
        if not mouse_pos:
            return
        
        # Determina direção do zoom
        if event.num == 4 or event.delta > 0:
            # Zoom in
            self._zoom(1.0 / self._zoom_factor, mouse_pos)
        elif event.num == 5 or event.delta < 0:
            # Zoom out
            self._zoom(self._zoom_factor, mouse_pos)
    
    def _on_mouse_press(self, event):
        """Handler para início do drag (pan)"""
        self._pan_start = (event.x, event.y)
        self._pan_active = True
        self.canvas.config(cursor="fleur")  # Cursor de movimento
    
    def _on_mouse_drag(self, event):
        """Handler para movimento do mouse durante drag"""
        if not self._pan_active or not self._pan_start or not self._extent:
            return
        
        # Calcula deslocamento em pixels
        dx_pixels = event.x - self._pan_start[0]
        dy_pixels = event.y - self._pan_start[1]
        
        # Converte para deslocamento em coordenadas do mapa
        minx, miny, maxx, maxy = self._extent
        world_width = maxx - minx
        world_height = maxy - miny
        
        dx_world = -(dx_pixels / self.width) * world_width
        dy_world = (dy_pixels / self.height) * world_height  # Inverte Y
        
        # Aplica pan
        self.pan(dx_world, dy_world)
        
        # Atualiza ponto inicial para o próximo movimento
        self._pan_start = (event.x, event.y)
    
    def _on_mouse_release(self, event):
        """Handler para fim do drag"""
        self._pan_active = False
        self._pan_start = None
        self.canvas.config(cursor="")  # Cursor padrão
    
    def _on_resize(self, event):
        """Handler para redimensionamento do canvas"""
        new_width = event.width
        new_height = event.height
        
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            print(f"Canvas redimensionado: {self.width}x{self.height}")
            self.refresh()
    
    def save_image(self, filename: str):
        """
        Salva a imagem atual do canvas em arquivo.
        
        Args:
            filename: Nome do arquivo (ex: "mapa.png")
        """
        if self._current_image:
            self._current_image.save(filename)
            print(f"Imagem salva: {filename}")
        else:
            print("Nenhuma imagem para salvar")
    
    def get_layer_manager(self) -> LayerManager:
        """
        Retorna o gerenciador de camadas.
        
        Returns:
            Objeto LayerManager
        """
        return self.layer_manager


