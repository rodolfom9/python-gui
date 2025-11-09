"""
Módulo de Renderização - Sistema abstrato para renderizar camadas
A arquitetura permite substituir implementações Python por C++ no futuro
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, List
from PIL import Image, ImageDraw
import numpy as np

try:
    from osgeo import ogr
except ImportError:
    raise ImportError("GDAL não está instalado. Instale com: pip install gdal")


class RenderContext:
    """
    Contexto de renderização - contém informações sobre a área a ser renderizada.
    Similar ao QgsRenderContext do QGIS.
    """
    
    def __init__(self, 
                 width: int, 
                 height: int, 
                 extent: Tuple[float, float, float, float],
                 dpi: int = 96):
        """
        Inicializa o contexto de renderização.
        
        Args:
            width: Largura do canvas em pixels
            height: Altura do canvas em pixels
            extent: Extensão geográfica (minx, miny, maxx, maxy)
            dpi: Resolução em DPI
        """
        self.width = width
        self.height = height
        self.extent = extent
        self.dpi = dpi
        
        # Calcula fatores de escala
        self.minx, self.miny, self.maxx, self.maxy = extent
        self.scale_x = width / (self.maxx - self.minx)
        self.scale_y = height / (self.maxy - self.miny)
    
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """
        Converte coordenadas geográficas para coordenadas de pixel.
        
        Args:
            x: Coordenada X no sistema de referência
            y: Coordenada Y no sistema de referência
            
        Returns:
            Tupla (px, py) com coordenadas em pixels
        """
        px = int((x - self.minx) * self.scale_x)
        py = int((self.maxy - y) * self.scale_y)  # Inverte Y
        return px, py


class Renderer(ABC):
    """
    Classe base abstrata para renderizadores.
    Esta interface pode ser implementada em C++ no futuro usando ctypes ou pybind11.
    """
    
    @abstractmethod
    def render(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """
        Renderiza uma camada.
        
        Args:
            layer: Camada a ser renderizada
            context: Contexto de renderização
            
        Returns:
            Imagem PIL renderizada ou None se erro
        """
        pass
    
    @abstractmethod
    def supports_layer_type(self, layer_type: str) -> bool:
        """
        Verifica se o renderizador suporta um tipo de camada.
        
        Args:
            layer_type: Tipo da camada
            
        Returns:
            True se suportado, False caso contrário
        """
        pass


class SimpleRenderer(Renderer):
    """
    Renderizador simples - implementação básica em Python.
    Pode ser substituído por uma implementação em C++ mantendo a mesma interface.
    """
    
    def __init__(self):
        """Inicializa o renderizador simples"""
        self._default_color = (100, 100, 255, 180)  # RGBA
        self._default_outline_color = (0, 0, 0, 255)
        self._default_outline_width = 1
    
    def supports_layer_type(self, layer_type: str) -> bool:
        """Verifica se suporta o tipo de camada"""
        return layer_type in ["vector", "raster"]
    
    def render(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """
        Renderiza uma camada de forma simples.
        
        Args:
            layer: Camada a ser renderizada
            context: Contexto de renderização
            
        Returns:
            Imagem PIL renderizada ou None se erro
        """
        from .layer import LayerType
        
        if layer.get_type() == LayerType.VECTOR:
            return self._render_vector(layer, context)
        elif layer.get_type() == LayerType.RASTER:
            return self._render_raster(layer, context)
        
        return None
    
    def _render_vector(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """Renderiza uma camada vetorial"""
        # Cria imagem transparente
        img = Image.new('RGBA', (context.width, context.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Renderiza cada feature
        for feature in layer.features:
            geom = feature['geometry']
            if geom is None:
                continue
            
            self._draw_geometry(draw, geom, context)
        
        return img
    
    def _render_raster(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """Renderiza uma camada raster"""
        try:
            # Lê a primeira banda
            data = layer.read_band(1)
            if data is None:
                return None
            
            # Normaliza para 0-255
            data_min = np.nanmin(data)
            data_max = np.nanmax(data)
            if data_max > data_min:
                data_norm = ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)
            else:
                data_norm = np.zeros_like(data, dtype=np.uint8)
            
            # Cria imagem
            img = Image.fromarray(data_norm, mode='L')
            
            # Redimensiona para o tamanho do contexto se necessário
            if img.size != (context.width, context.height):
                img = img.resize((context.width, context.height), Image.BILINEAR)
            
            # Converte para RGBA
            img = img.convert('RGBA')
            
            return img
            
        except Exception as e:
            print(f"Erro ao renderizar raster: {e}")
            return None
    
    def _draw_geometry(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha uma geometria com proteção contra erros"""
        try:
            if geom is None:
                return
            
            geom_type = geom.GetGeometryType()
            
            if geom_type in [ogr.wkbPoint, ogr.wkbPoint25D]:
                self._draw_point(draw, geom, context)
            elif geom_type in [ogr.wkbLineString, ogr.wkbLineString25D]:
                self._draw_linestring(draw, geom, context)
            elif geom_type in [ogr.wkbPolygon, ogr.wkbPolygon25D]:
                self._draw_polygon(draw, geom, context)
            elif geom_type in [ogr.wkbMultiPoint, ogr.wkbMultiPoint25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_point(draw, sub_geom, context)
            elif geom_type in [ogr.wkbMultiLineString, ogr.wkbMultiLineString25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_linestring(draw, sub_geom, context)
            elif geom_type in [ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_polygon(draw, sub_geom, context)
        except Exception as e:
            # Não falha a renderização inteira por causa de uma geometria
            print(f"Aviso: Erro ao desenhar geometria: {e}")
            pass
    
    def _draw_point(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha um ponto"""
        x, y = geom.GetX(), geom.GetY()
        px, py = context.world_to_pixel(x, y)
        radius = 3
        draw.ellipse([px-radius, py-radius, px+radius, py+radius], 
                    fill=self._default_color, 
                    outline=self._default_outline_color)
    
    def _draw_linestring(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha uma linha"""
        point_count = geom.GetPointCount()
        if point_count < 2:
            return
        
        # OTIMIZAÇÃO: Pré-aloca lista e processa em lote
        points = [(0, 0)] * point_count
        for i in range(point_count):
            x, y = geom.GetX(i), geom.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points[i] = (px, py)
        
        draw.line(points, fill=self._default_outline_color, width=self._default_outline_width)
    
    def _draw_polygon(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha um polígono"""
        # Desenha o anel externo
        ring = geom.GetGeometryRef(0)
        if ring is None:
            return
        
        point_count = ring.GetPointCount()
        if point_count < 3:
            return
        
        # OTIMIZAÇÃO: Pré-aloca lista e processa em lote
        points = [(0, 0)] * point_count
        for i in range(point_count):
            x, y = ring.GetX(i), ring.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points[i] = (px, py)
        
        draw.polygon(points, fill=self._default_color, outline=self._default_outline_color)


class VectorRenderer(Renderer):
    """
    Renderizador vetorial configurável - permite definir cores, bordas, etc.
    Esta classe demonstra como estender o renderizador base.
    """
    
    def __init__(self, 
                 fill_color: Tuple[int, int, int, int] = (100, 100, 255, 180),
                 outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                 outline_width: int = 1,
                 point_size: int = 3):
        """
        Inicializa o renderizador vetorial.
        
        Args:
            fill_color: Cor de preenchimento RGBA
            outline_color: Cor da borda RGBA
            outline_width: Largura da borda em pixels
            point_size: Tamanho dos pontos em pixels
        """
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.point_size = point_size
    
    def supports_layer_type(self, layer_type: str) -> bool:
        """Verifica se suporta o tipo de camada"""
        return layer_type == "vector"
    
    def render(self, layer, context: RenderContext) -> Optional[Image.Image]:
        """Renderiza uma camada vetorial com estilos configuráveis"""
        from .layer import LayerType
        
        if layer.get_type() != LayerType.VECTOR:
            return None
        
        # Cria imagem transparente
        img = Image.new('RGBA', (context.width, context.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Renderiza cada feature
        for feature in layer.features:
            geom = feature['geometry']
            if geom is None:
                continue
            
            self._draw_geometry(draw, geom, context)
        
        return img
    
    def _draw_geometry(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha uma geometria com estilos configuráveis e proteção contra erros"""
        try:
            if geom is None:
                return
            
            geom_type = geom.GetGeometryType()
            
            if geom_type in [ogr.wkbPoint, ogr.wkbPoint25D]:
                self._draw_point(draw, geom, context)
            elif geom_type in [ogr.wkbLineString, ogr.wkbLineString25D]:
                self._draw_linestring(draw, geom, context)
            elif geom_type in [ogr.wkbPolygon, ogr.wkbPolygon25D]:
                self._draw_polygon(draw, geom, context)
            elif geom_type in [ogr.wkbMultiPoint, ogr.wkbMultiPoint25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_point(draw, sub_geom, context)
            elif geom_type in [ogr.wkbMultiLineString, ogr.wkbMultiLineString25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_linestring(draw, sub_geom, context)
            elif geom_type in [ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D]:
                for i in range(geom.GetGeometryCount()):
                    sub_geom = geom.GetGeometryRef(i)
                    if sub_geom:
                        self._draw_polygon(draw, sub_geom, context)
        except Exception as e:
            # Não falha a renderização inteira por causa de uma geometria
            print(f"Aviso: Erro ao desenhar geometria: {e}")
            pass
    
    def _draw_point(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha um ponto"""
        x, y = geom.GetX(), geom.GetY()
        px, py = context.world_to_pixel(x, y)
        radius = self.point_size
        draw.ellipse([px-radius, py-radius, px+radius, py+radius], 
                    fill=self.fill_color, 
                    outline=self.outline_color)
    
    def _draw_linestring(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha uma linha"""
        point_count = geom.GetPointCount()
        if point_count < 2:
            return
        
        # OTIMIZAÇÃO: Pré-aloca lista e processa em lote
        points = [(0, 0)] * point_count
        for i in range(point_count):
            x, y = geom.GetX(i), geom.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points[i] = (px, py)
        
        draw.line(points, fill=self.outline_color, width=self.outline_width)
    
    def _draw_polygon(self, draw: ImageDraw.ImageDraw, geom, context: RenderContext):
        """Desenha um polígono"""
        # Desenha o anel externo
        ring = geom.GetGeometryRef(0)
        if ring is None:
            return
        
        point_count = ring.GetPointCount()
        if point_count < 3:
            return
        
        # OTIMIZAÇÃO: Pré-aloca lista e processa em lote
        points = [(0, 0)] * point_count
        for i in range(point_count):
            x, y = ring.GetX(i), ring.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points[i] = (px, py)
        
        draw.polygon(points, fill=self.fill_color, outline=self.outline_color)


# Para substituir por C++, você pode criar um wrapper assim:
# 
# class CppRenderer(Renderer):
#     """
#     Renderizador em C++ - wrapper para biblioteca nativa
#     Exemplo de como integrar com C++ usando ctypes ou pybind11
#     """
#     
#     def __init__(self, lib_path: str):
#         import ctypes
#         self._lib = ctypes.CDLL(lib_path)
#         # Configura assinaturas das funções C++
#         # self._lib.render_layer.argtypes = [...]
#         # self._lib.render_layer.restype = ctypes.c_void_p
#     
#     def render(self, layer, context: RenderContext) -> Optional[Image.Image]:
#         # Chama função C++ via ctypes
#         # result = self._lib.render_layer(...)
#         pass


