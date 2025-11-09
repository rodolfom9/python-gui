"""
Sistema de Mapa Python - Arquitetura modular similar ao QGIS
"""

__version__ = "1.0.0"

from .layer import Layer, VectorLayer, RasterLayer
from .renderer import Renderer, SimpleRenderer, VectorRenderer, RenderContext
from .map_canvas import MapCanvas
from .coordinate_transform import CoordinateTransform, CRSManager
from .layer_manager import LayerManager

try:
    from .qml_bridge import MapCanvasQML, MapImageProvider
    from .qml_bridge_interactive import MapCanvasQMLInteractive, MapImageProviderInteractive
    QML_AVAILABLE = True
except ImportError:
    QML_AVAILABLE = False
    MapCanvasQML = None
    MapImageProvider = None
    MapCanvasQMLInteractive = None
    MapImageProviderInteractive = None

try:
    from .map_canvas_interactive import MapCanvasInteractive
    from .map_tool import (MapTool, PanTool, ZoomInTool, ZoomOutTool, 
                          IdentifyTool, AddPointTool, AddLineTool, AddPolygonTool,
                          MapToolManager, MapToolType, MouseEvent, Geometry)
    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False
    MapCanvasInteractive = None
    MapToolManager = None

__all__ = [
    'Layer',
    'VectorLayer',
    'RasterLayer',
    'Renderer',
    'SimpleRenderer',
    'VectorRenderer',
    'RenderContext',
    'MapCanvas',
    'CoordinateTransform',
    'CRSManager',
    'LayerManager',
    'MapCanvasQML',
    'MapImageProvider',
    'MapCanvasQMLInteractive',
    'MapImageProviderInteractive',
    'QML_AVAILABLE',
    'MapCanvasInteractive',
    'MapToolManager',
    'MapToolType',
    'INTERACTIVE_AVAILABLE',
]

