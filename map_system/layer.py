"""
Módulo de Camadas - Define as classes base para camadas vetoriais e raster
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from enum import Enum
import numpy as np
import sys
import threading

try:
    from osgeo import gdal, ogr, osr
    gdal.UseExceptions()
except ImportError:
    raise ImportError("GDAL não está instalado. Instale com: pip install gdal")


class LayerType(Enum):
    """Tipos de camadas suportadas"""
    VECTOR = "vector"
    RASTER = "raster"


class Layer(ABC):
    """
    Classe base abstrata para todas as camadas.
    Similar à QgsMapLayer do QGIS.
    """
    
    def __init__(self, name: str, source: str):
        """
        Inicializa uma camada.
        
        Args:
            name: Nome da camada
            source: Caminho para o arquivo de dados
        """
        self._name = name
        self._source = source
        self._visible = True
        self._opacity = 1.0
        self._crs = None
        self._extent = None
        self._valid = False
        
    @property
    def name(self) -> str:
        """Retorna o nome da camada"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Define o nome da camada"""
        self._name = value
    
    @property
    def visible(self) -> bool:
        """Retorna se a camada está visível"""
        return self._visible
    
    @visible.setter
    def visible(self, value: bool):
        """Define a visibilidade da camada"""
        self._visible = value
    
    @property
    def opacity(self) -> float:
        """Retorna a opacidade da camada (0.0 a 1.0)"""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float):
        """Define a opacidade da camada"""
        self._opacity = max(0.0, min(1.0, value))
    
    @property
    def crs(self):
        """Retorna o sistema de coordenadas da camada"""
        return self._crs
    
    @property
    def extent(self) -> Optional[Tuple[float, float, float, float]]:
        """Retorna a extensão da camada (minx, miny, maxx, maxy)"""
        return self._extent
    
    @property
    def is_valid(self) -> bool:
        """Retorna se a camada foi carregada com sucesso"""
        return self._valid
    
    @abstractmethod
    def get_type(self) -> LayerType:
        """Retorna o tipo da camada"""
        pass
    
    @abstractmethod
    def load(self) -> bool:
        """Carrega os dados da camada"""
        pass


class VectorLayer(Layer):
    """
    Camada vetorial - carrega dados de shapefile, geojson, etc usando GDAL/OGR
    Similar à QgsVectorLayer do QGIS.
    """
    
    def __init__(self, name: str, source: str):
        """
        Inicializa uma camada vetorial.
        
        Args:
            name: Nome da camada
            source: Caminho para o arquivo vetorial
        """
        super().__init__(name, source)
        self._datasource = None
        self._layer = None
        self._features = []
        self._geometry_type = None
        
    def get_type(self) -> LayerType:
        """Retorna o tipo da camada"""
        return LayerType.VECTOR
    
    def load(self) -> bool:
        """
        Carrega o arquivo vetorial usando GDAL/OGR.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            print(f"Tentando carregar: {self._source}")
            sys.stdout.flush()
            
            # Converte caminho para string simples
            source_path = str(self._source)
            print(f"DEBUG: Caminho: '{source_path}'")
            sys.stdout.flush()
            
            print("DEBUG: Chamando ogr.Open...")
            sys.stdout.flush()
            
            # Abre o datasource
            self._datasource = ogr.Open(source_path)
            
            print("DEBUG: ogr.Open retornou")
            sys.stdout.flush()
            
            if self._datasource is None:
                print(f"ERRO: Nao foi possivel abrir datasource: {source_path}")
                sys.stdout.flush()
                return False
            
            print(f"Datasource aberto com sucesso")
            sys.stdout.flush()
            
            # Obtém a primeira camada
            print("DEBUG: Obtendo layer...")
            sys.stdout.flush()
            self._layer = self._datasource.GetLayer(0)
            print("DEBUG: Layer obtida")
            sys.stdout.flush()
            
            if self._layer is None:
                print(f"ERRO: Nao foi possivel obter camada do datasource")
                return False
            
            print(f"Camada obtida, feature count: {self._layer.GetFeatureCount()}")
            sys.stdout.flush()
            
            # Obtém o CRS
            try:
                spatial_ref = self._layer.GetSpatialRef()
                if spatial_ref:
                    self._crs = spatial_ref.ExportToWkt()
            except Exception as crs_error:
                print(f"Aviso: Erro ao obter CRS: {crs_error}")
                self._crs = None
            
            # Obtém a extensão
            try:
                extent = self._layer.GetExtent()
                self._extent = (extent[0], extent[2], extent[1], extent[3])  # minx, miny, maxx, maxy
                print(f"Extensao: {self._extent}")
                sys.stdout.flush()
            except Exception as extent_error:
                print(f"ERRO: Nao foi possivel obter extensao: {extent_error}")
                return False
            
            # Obtém o tipo de geometria
            try:
                layer_defn = self._layer.GetLayerDefn()
                self._geometry_type = layer_defn.GetGeomType()
                print(f"Tipo de geometria: {self._geometry_type}")
            except Exception as geom_error:
                print(f"Aviso: Erro ao obter tipo de geometria: {geom_error}")
                self._geometry_type = None
            
            # Carrega as features
            print(f"DEBUG: Carregando {self._layer.GetFeatureCount()} features...")
            sys.stdout.flush()
            
            self._features = []
            self._layer.ResetReading()
            
            feature_count = 0
            print(f"DEBUG: Iniciando loop de features...")
            sys.stdout.flush()
            
            for feature in self._layer:
                try:
                    geom = feature.GetGeometryRef()
                    if geom:
                        # OTIMIZAÇÃO: Apenas clona a geometria via WKB
                        # Removido JSON desnecessário que era muito lento
                        geom_wkb = geom.ExportToWkb()
                        new_geom = ogr.CreateGeometryFromWkb(geom_wkb)
                        
                        self._features.append({
                            'geometry': new_geom,
                            'properties': {}
                        })
                        feature_count += 1
                        
                        if feature_count % 50 == 0:
                            print(f"Carregadas {feature_count} features...")
                            sys.stdout.flush()
                            
                except Exception as feat_error:
                    print(f"Aviso: Erro ao processar feature {feature_count}: {feat_error}")
                    continue
            
            print(f"DEBUG: Loop finalizado, total = {len(self._features)}")
            sys.stdout.flush()
            
            self._valid = True
            print(f"==> Camada vetorial carregada com SUCESSO: {self._name} ({len(self._features)} features)")
            sys.stdout.flush()
            
            # IMPORTANTE: Mantém o datasource aberto para evitar problemas
            # O datasource será fechado apenas quando a camada for destruída
            
            return True
            
        except Exception as e:
            print(f"ERRO CRITICO ao carregar camada vetorial {self._name}: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            self._valid = False
            return False
    
    @property
    def features(self) -> List[dict]:
        """Retorna a lista de features"""
        return self._features
    
    @property
    def geometry_type(self) -> Optional[int]:
        """Retorna o tipo de geometria OGR"""
        return self._geometry_type
    
    def get_feature_count(self) -> int:
        """Retorna o número de features"""
        return len(self._features)


class RasterLayer(Layer):
    """
    Camada raster - carrega dados de GeoTIFF, etc usando GDAL
    Similar à QgsRasterLayer do QGIS.
    """
    
    def __init__(self, name: str, source: str):
        """
        Inicializa uma camada raster.
        
        Args:
            name: Nome da camada
            source: Caminho para o arquivo raster
        """
        super().__init__(name, source)
        self._dataset = None
        self._bands = []
        self._width = 0
        self._height = 0
        self._geotransform = None
        
    def get_type(self) -> LayerType:
        """Retorna o tipo da camada"""
        return LayerType.RASTER
    
    def load(self) -> bool:
        """
        Carrega o arquivo raster usando GDAL.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            # Abre o dataset
            self._dataset = gdal.Open(self._source, gdal.GA_ReadOnly)
            if self._dataset is None:
                print(f"Erro ao abrir raster: {self._source}")
                return False
            
            # Obtém informações do raster
            self._width = self._dataset.RasterXSize
            self._height = self._dataset.RasterYSize
            self._geotransform = self._dataset.GetGeoTransform()
            
            # Obtém o CRS
            proj = self._dataset.GetProjection()
            if proj:
                self._crs = proj
            
            # Calcula a extensão
            if self._geotransform:
                minx = self._geotransform[0]
                maxy = self._geotransform[3]
                maxx = minx + self._geotransform[1] * self._width
                miny = maxy + self._geotransform[5] * self._height
                self._extent = (minx, miny, maxx, maxy)
            
            # Carrega informações das bandas
            self._bands = []
            for i in range(1, self._dataset.RasterCount + 1):
                band = self._dataset.GetRasterBand(i)
                self._bands.append({
                    'index': i,
                    'datatype': band.DataType,
                    'nodata': band.GetNoDataValue(),
                    'min': band.GetMinimum(),
                    'max': band.GetMaximum(),
                })
            
            self._valid = True
            print(f"Camada raster carregada: {self._name} ({self._width}x{self._height}, {len(self._bands)} bandas)")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar camada raster {self._name}: {e}")
            self._valid = False
            return False
    
    @property
    def width(self) -> int:
        """Retorna a largura do raster em pixels"""
        return self._width
    
    @property
    def height(self) -> int:
        """Retorna a altura do raster em pixels"""
        return self._height
    
    @property
    def band_count(self) -> int:
        """Retorna o número de bandas"""
        return len(self._bands)
    
    def read_band(self, band_index: int = 1) -> Optional[np.ndarray]:
        """
        Lê os dados de uma banda.
        
        Args:
            band_index: Índice da banda (1-based)
            
        Returns:
            Array numpy com os dados da banda ou None se erro
        """
        try:
            if self._dataset is None:
                return None
            
            band = self._dataset.GetRasterBand(band_index)
            data = band.ReadAsArray()
            return data
            
        except Exception as e:
            print(f"Erro ao ler banda {band_index}: {e}")
            return None
    
    def read_region(self, xoff: int, yoff: int, xsize: int, ysize: int, 
                    band_index: int = 1) -> Optional[np.ndarray]:
        """
        Lê uma região específica do raster.
        
        Args:
            xoff: Offset X em pixels
            yoff: Offset Y em pixels
            xsize: Tamanho X em pixels
            ysize: Tamanho Y em pixels
            band_index: Índice da banda (1-based)
            
        Returns:
            Array numpy com os dados da região ou None se erro
        """
        try:
            if self._dataset is None:
                return None
            
            band = self._dataset.GetRasterBand(band_index)
            data = band.ReadAsArray(xoff, yoff, xsize, ysize)
            return data
            
        except Exception as e:
            print(f"Erro ao ler região: {e}")
            return None

