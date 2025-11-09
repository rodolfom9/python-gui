"""
Renderizador Qt QML - Substitui PIL + Tkinter
Renderiza mapas diretamente com Qt Graphics, sem PIL
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from PyQt6.QtCore import QUrl, Qt, QSize, QRect
from PyQt6.QtGui import QImage, QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtQuick import QQuickItem, QQuickPaintedItem

try:
    from osgeo import ogr
except ImportError:
    raise ImportError("GDAL não está instalado. Instale com: pip install gdal")


class RenderContext:
    """Contexto de renderização - idêntico ao da versão PIL"""
    
    def __init__(self, 
                 width: int, 
                 height: int, 
                 extent: Tuple[float, float, float, float],
                 dpi: int = 96):
        self.width = width
        self.height = height
        self.extent = extent
        self.dpi = dpi
        
        self.minx, self.miny, self.maxx, self.maxy = extent
        self.scale_x = width / (self.maxx - self.minx)
        self.scale_y = height / (self.maxy - self.miny)
    
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """Converte coordenadas geográficas para pixel"""
        px = int((x - self.minx) * self.scale_x)
        py = int((self.maxy - y) * self.scale_y)
        return px, py


class QtMapCanvas(QQuickPaintedItem):
    """
    Canvas de mapa usando Qt QML - Renderiza diretamente com QPainter
    Substitui o Canvas do Tkinter + PIL
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)
        self.setAcceptHoverEvents(True)
        
        self._extent = None
        self._current_image = None
        self._layer_manager = None
        self._renderer = None
        
        print("QtMapCanvas criado (QML compatible)")
    
    def paint(self, painter):
        """Chamado quando precisa redesenhar"""
        if self._current_image:
            rect = self.boundingRect()
            painter.drawImage(0, 0, self._current_image)
    
    def refresh(self):
        """Força redesenho"""
        self.update()
    
    def set_layer_manager(self, manager):
        """Define o gerenciador de camadas"""
        self._layer_manager = manager
    
    def set_renderer(self, renderer):
        """Define o renderizador"""
        self._renderer = renderer


class QtImageRenderer(ABC):
    """Classe base para renderizadores Qt - idêntica interface da versão PIL"""
    
    @abstractmethod
    def render(self, layer, context: RenderContext) -> Optional[QImage]:
        """Renderiza uma camada retornando QImage"""
        pass
    
    @abstractmethod
    def supports_layer_type(self, layer_type: str) -> bool:
        """Verifica se suporta tipo de camada"""
        pass


class QtSimpleRenderer(QtImageRenderer):
    """
    Renderizador Qt simples - renderiza direto com QPainter em QImage
    Substitui SimpleRenderer do PIL
    """
    
    def __init__(self):
        self._default_color = QColor(100, 100, 255, 180)
        self._default_outline_color = QColor(0, 0, 0, 255)
        self._default_outline_width = 1
    
    def supports_layer_type(self, layer_type: str) -> bool:
        return layer_type in ["vector", "raster"]
    
    def render(self, layer, context: RenderContext) -> Optional[QImage]:
        """Renderiza camada usando QPainter em QImage"""
        from .layer import LayerType
        
        if layer.get_type() == LayerType.VECTOR:
            return self._render_vector(layer, context)
        elif layer.get_type() == LayerType.RASTER:
            return self._render_raster(layer, context)
        
        return None
    
    def _render_vector(self, layer, context: RenderContext) -> Optional[QImage]:
        """Renderiza camada vetorial com Qt"""
        # Cria QImage transparente
        img = QImage(context.width, context.height, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        
        # Cria painter
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # Renderiza features
        for feature in layer.features:
            geom = feature['geometry']
            if geom:
                self._draw_geometry(painter, geom, context)
        
        painter.end()
        return img
    
    def _render_raster(self, layer, context: RenderContext) -> Optional[QImage]:
        """Renderiza camada raster"""
        try:
            import numpy as np
            
            # Lê primeira banda
            data = layer.read_band(1)
            if data is None:
                return None
            
            # Normaliza
            data_min = np.nanmin(data)
            data_max = np.nanmax(data)
            if data_max > data_min:
                data_norm = ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)
            else:
                data_norm = np.zeros_like(data, dtype=np.uint8)
            
            # Cria QImage diretamente do numpy array
            height, width = data_norm.shape
            bytes_per_line = 3 * width
            rgb_data = np.stack([data_norm, data_norm, data_norm], axis=2)
            
            from PyQt6.QtCore import QByteArray
            img = QImage(rgb_data.tobytes(), width, height, 
                        bytes_per_line, QImage.Format.Format_RGB888)
            
            # Redimensiona se necessário
            if img.size() != QSize(context.width, context.height):
                img = img.scaledToSize(QSize(context.width, context.height), 
                                      Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
            
            return img
        
        except Exception as e:
            print(f"Erro ao renderizar raster: {e}")
            return None
    
    def _draw_geometry(self, painter: QPainter, geom, context: RenderContext):
        """Desenha geometria com Qt"""
        try:
            geom_type = geom.GetGeometryType()
            
            if geom_type in [ogr.wkbPoint, ogr.wkbPoint25D]:
                self._draw_point(painter, geom, context)
            elif geom_type in [ogr.wkbLineString, ogr.wkbLineString25D]:
                self._draw_linestring(painter, geom, context)
            elif geom_type in [ogr.wkbPolygon, ogr.wkbPolygon25D]:
                self._draw_polygon(painter, geom, context)
            elif geom_type in [ogr.wkbMultiPoint, ogr.wkbMultiPoint25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_point(painter, sub, context)
            elif geom_type in [ogr.wkbMultiLineString, ogr.wkbMultiLineString25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_linestring(painter, sub, context)
            elif geom_type in [ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_polygon(painter, sub, context)
        except Exception as e:
            print(f"Aviso: Erro ao desenhar: {e}")
    
    def _draw_point(self, painter: QPainter, geom, context: RenderContext):
        """Desenha ponto com Qt"""
        x, y = geom.GetX(), geom.GetY()
        px, py = context.world_to_pixel(x, y)
        
        painter.setBrush(QBrush(self._default_color))
        painter.setPen(QPen(self._default_outline_color))
        painter.drawEllipse(px - 3, py - 3, 6, 6)
    
    def _draw_linestring(self, painter: QPainter, geom, context: RenderContext):
        """Desenha linha com Qt"""
        point_count = geom.GetPointCount()
        if point_count < 2:
            return
        
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QPolygon
        
        points = QPolygon()
        for i in range(point_count):
            x, y = geom.GetX(i), geom.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points.append(QPoint(px, py))
        
        painter.setPen(QPen(self._default_outline_color, self._default_outline_width))
        painter.drawPolyline(points)
    
    def _draw_polygon(self, painter: QPainter, geom, context: RenderContext):
        """Desenha polígono com Qt"""
        ring = geom.GetGeometryRef(0)
        if not ring:
            return
        
        point_count = ring.GetPointCount()
        if point_count < 3:
            return
        
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QPolygon
        
        points = QPolygon()
        for i in range(point_count):
            x, y = ring.GetX(i), ring.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points.append(QPoint(px, py))
        
        painter.setBrush(QBrush(self._default_color))
        painter.setPen(QPen(self._default_outline_color))
        painter.drawPolygon(points)


class QtVectorRenderer(QtImageRenderer):
    """
    Renderizador vetorial configurável com Qt
    Substitui VectorRenderer do PIL
    """
    
    def __init__(self, 
                 fill_color: Tuple[int, int, int, int] = (100, 100, 255, 180),
                 outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                 outline_width: int = 1,
                 point_size: int = 3):
        self.fill_color = QColor(*fill_color)
        self.outline_color = QColor(*outline_color)
        self.outline_width = outline_width
        self.point_size = point_size
    
    def supports_layer_type(self, layer_type: str) -> bool:
        return layer_type == "vector"
    
    def render(self, layer, context: RenderContext) -> Optional[QImage]:
        """Renderiza camada vetorial com estilos"""
        from .layer import LayerType
        
        if layer.get_type() != LayerType.VECTOR:
            return None
        
        img = QImage(context.width, context.height, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        for feature in layer.features:
            geom = feature['geometry']
            if geom:
                self._draw_geometry(painter, geom, context)
        
        painter.end()
        return img
    
    def _draw_geometry(self, painter: QPainter, geom, context: RenderContext):
        """Desenha geometria com estilos configuráveis"""
        try:
            geom_type = geom.GetGeometryType()
            
            if geom_type in [ogr.wkbPoint, ogr.wkbPoint25D]:
                self._draw_point(painter, geom, context)
            elif geom_type in [ogr.wkbLineString, ogr.wkbLineString25D]:
                self._draw_linestring(painter, geom, context)
            elif geom_type in [ogr.wkbPolygon, ogr.wkbPolygon25D]:
                self._draw_polygon(painter, geom, context)
            elif geom_type in [ogr.wkbMultiPoint, ogr.wkbMultiPoint25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_point(painter, sub, context)
            elif geom_type in [ogr.wkbMultiLineString, ogr.wkbMultiLineString25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_linestring(painter, sub, context)
            elif geom_type in [ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D]:
                for i in range(geom.GetGeometryCount()):
                    sub = geom.GetGeometryRef(i)
                    if sub:
                        self._draw_polygon(painter, sub, context)
        except Exception as e:
            print(f"Aviso: Erro ao desenhar: {e}")
    
    def _draw_point(self, painter: QPainter, geom, context: RenderContext):
        """Desenha ponto com estilos"""
        x, y = geom.GetX(), geom.GetY()
        px, py = context.world_to_pixel(x, y)
        
        painter.setBrush(QBrush(self.fill_color))
        painter.setPen(QPen(self.outline_color))
        painter.drawEllipse(px - self.point_size, py - self.point_size, 
                           self.point_size * 2, self.point_size * 2)
    
    def _draw_linestring(self, painter: QPainter, geom, context: RenderContext):
        """Desenha linha com estilos"""
        point_count = geom.GetPointCount()
        if point_count < 2:
            return
        
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QPolygon
        
        points = QPolygon()
        for i in range(point_count):
            x, y = geom.GetX(i), geom.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points.append(QPoint(px, py))
        
        painter.setPen(QPen(self.outline_color, self.outline_width))
        painter.drawPolyline(points)
    
    def _draw_polygon(self, painter: QPainter, geom, context: RenderContext):
        """Desenha polígono com estilos"""
        ring = geom.GetGeometryRef(0)
        if not ring:
            return
        
        point_count = ring.GetPointCount()
        if point_count < 3:
            return
        
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QPolygon
        
        points = QPolygon()
        for i in range(point_count):
            x, y = ring.GetX(i), ring.GetY(i)
            px, py = context.world_to_pixel(x, y)
            points.append(QPoint(px, py))
        
        painter.setBrush(QBrush(self.fill_color))
        painter.setPen(QPen(self.outline_color))
        painter.drawPolygon(points)
