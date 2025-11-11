"""
Módulo de Transformação de Coordenadas - Usa PROJ para reprojetar coordenadas
"""

from typing import Tuple, Optional, List
import numpy as np

try:
    from osgeo import osr
except ImportError:
    raise ImportError("GDAL não está instalado. Instale com: pip install gdal")

try:
    from pyproj import Transformer, CRS
    PYPROJ_AVAILABLE = True
except ImportError:
    PYPROJ_AVAILABLE = False
    print("Aviso: pyproj não está disponível. Usando apenas osr do GDAL.")


class CoordinateTransform:
    """
    Classe para transformação de coordenadas entre diferentes sistemas de referência.
    Similar ao QgsCoordinateTransform do QGIS.
    
    Suporta transformações usando GDAL/OSR e PyProj.
    """
    
    def __init__(self, source_crs: str, dest_crs: str, use_pyproj: bool = True):
        """
        Inicializa o transformador de coordenadas.
        
        Args:
            source_crs: CRS de origem (WKT, PROJ4, EPSG:code, etc)
            dest_crs: CRS de destino (WKT, PROJ4, EPSG:code, etc)
            use_pyproj: Se True, usa PyProj; se False, usa OSR do GDAL
        """
        self.source_crs = source_crs
        self.dest_crs = dest_crs
        self._transformer = None
        self._osr_transform = None
        self._use_pyproj = use_pyproj and PYPROJ_AVAILABLE
        self._is_valid = False
        
        self._initialize_transform()
    
    def _initialize_transform(self):
        """Inicializa o transformador"""
        try:
            if self._use_pyproj:
                self._initialize_pyproj()
            else:
                self._initialize_osr()
        except Exception as e:
            print(f"Erro ao inicializar transformação: {e}")
            self._is_valid = False
    
    def _initialize_pyproj(self):
        """Inicializa usando PyProj"""
        try:
            # Tenta criar CRS a partir das strings fornecidas
            source = self._parse_crs(self.source_crs)
            dest = self._parse_crs(self.dest_crs)
            
            # Cria o transformador
            self._transformer = Transformer.from_crs(
                source, dest, always_xy=True
            )
            self._is_valid = True
            
        except Exception as e:
            print(f"Erro ao inicializar PyProj: {e}")
            self._is_valid = False
    
    def _initialize_osr(self):
        """Inicializa usando OSR do GDAL"""
        try:
            # Cria SpatialReference de origem
            source_sr = osr.SpatialReference()
            if self.source_crs.startswith('EPSG:'):
                epsg_code = int(self.source_crs.split(':')[1])
                source_sr.ImportFromEPSG(epsg_code)
            elif self.source_crs.startswith('+proj'):
                source_sr.ImportFromProj4(self.source_crs)
            else:
                source_sr.ImportFromWkt(self.source_crs)
            
            # Cria SpatialReference de destino
            dest_sr = osr.SpatialReference()
            if self.dest_crs.startswith('EPSG:'):
                epsg_code = int(self.dest_crs.split(':')[1])
                dest_sr.ImportFromEPSG(epsg_code)
            elif self.dest_crs.startswith('+proj'):
                dest_sr.ImportFromProj4(self.dest_crs)
            else:
                dest_sr.ImportFromWkt(self.dest_crs)
            
            # Cria o transformador
            self._osr_transform = osr.CoordinateTransformation(source_sr, dest_sr)
            self._is_valid = True
            
        except Exception as e:
            print(f"Erro ao inicializar OSR: {e}")
            self._is_valid = False
    
    def _parse_crs(self, crs_string: str):
        """
        Parseia uma string CRS para objeto CRS do PyProj.
        
        Args:
            crs_string: String CRS (EPSG:code, WKT, PROJ4, etc)
            
        Returns:
            Objeto CRS do PyProj
        """
        # Tenta diferentes formatos
        if crs_string.startswith('EPSG:'):
            return CRS.from_epsg(int(crs_string.split(':')[1]))
        elif crs_string.startswith('+proj'):
            return CRS.from_proj4(crs_string)
        else:
            # Assume WKT
            return CRS.from_wkt(crs_string)
    
    @property
    def is_valid(self) -> bool:
        """Retorna se a transformação é válida"""
        return self._is_valid
    
    def transform(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        """
        Transforma um único ponto.
        
        Args:
            x: Coordenada X no CRS de origem
            y: Coordenada Y no CRS de origem
            
        Returns:
            Tupla (x, y) no CRS de destino ou None se erro
        """
        if not self._is_valid:
            return None
        
        try:
            if self._use_pyproj and self._transformer:
                x_out, y_out = self._transformer.transform(x, y)
                return x_out, y_out
            elif self._osr_transform:
                point = self._osr_transform.TransformPoint(x, y)
                return point[0], point[1]
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao transformar ponto ({x}, {y}): {e}")
            return None
    
    def transform_points(self, points: List[Tuple[float, float]]) -> Optional[List[Tuple[float, float]]]:
        """
        Transforma uma lista de pontos.
        
        Args:
            points: Lista de tuplas (x, y) no CRS de origem
            
        Returns:
            Lista de tuplas (x, y) no CRS de destino ou None se erro
        """
        if not self._is_valid or not points:
            return None
        
        try:
            transformed = []
            for x, y in points:
                result = self.transform(x, y)
                if result:
                    transformed.append(result)
                else:
                    return None
            return transformed
            
        except Exception as e:
            print(f"Erro ao transformar pontos: {e}")
            return None
    
    def transform_array(self, x_array: np.ndarray, y_array: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Transforma arrays de coordenadas.
        
        Args:
            x_array: Array numpy com coordenadas X
            y_array: Array numpy com coordenadas Y
            
        Returns:
            Tupla (x_out, y_out) com arrays transformados ou None se erro
        """
        if not self._is_valid:
            return None
        
        try:
            if self._use_pyproj and self._transformer:
                x_out, y_out = self._transformer.transform(x_array, y_array)
                return x_out, y_out
            elif self._osr_transform:
                # OSR não suporta arrays diretamente, transforma ponto a ponto
                x_out = np.zeros_like(x_array)
                y_out = np.zeros_like(y_array)
                
                flat_x = x_array.flatten()
                flat_y = y_array.flatten()
                
                for i in range(len(flat_x)):
                    point = self._osr_transform.TransformPoint(flat_x[i], flat_y[i])
                    x_out.flat[i] = point[0]
                    y_out.flat[i] = point[1]
                
                return x_out, y_out
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao transformar arrays: {e}")
            return None
    
    def transform_extent(self, extent: Tuple[float, float, float, float]) -> Optional[Tuple[float, float, float, float]]:
        """
        Transforma uma extensão (bounding box).
        
        Args:
            extent: Tupla (minx, miny, maxx, maxy) no CRS de origem
            
        Returns:
            Tupla (minx, miny, maxx, maxy) no CRS de destino ou None se erro
        """
        if not self._is_valid:
            return None
        
        try:
            minx, miny, maxx, maxy = extent
            
            # Transforma os 4 cantos
            corners = [
                (minx, miny),
                (minx, maxy),
                (maxx, miny),
                (maxx, maxy),
            ]
            
            transformed = self.transform_points(corners)
            if not transformed:
                return None
            
            # Calcula nova extensão
            xs = [p[0] for p in transformed]
            ys = [p[1] for p in transformed]
            
            new_extent = (min(xs), min(ys), max(xs), max(ys))
            return new_extent
            
        except Exception as e:
            print(f"Erro ao transformar extensão: {e}")
            return None


class CRSManager:
    """
    Gerenciador de sistemas de coordenadas.
    Utilitário para trabalhar com CRS comuns.
    """
    
    # CRS comuns
    WGS84 = "EPSG:4326"
    WEB_MERCATOR = "EPSG:3857"
    UTM_ZONE_23S = "EPSG:31983"  # Exemplo: UTM Zone 23S (Brasil)
    
    @staticmethod
    def get_epsg_code(crs_string: str) -> Optional[int]:
        """
        Extrai o código EPSG de uma string CRS.
        
        Args:
            crs_string: String CRS
            
        Returns:
            Código EPSG ou None se não encontrado
        """
        if crs_string.startswith('EPSG:'):
            try:
                return int(crs_string.split(':')[1])
            except:
                return None
        
        # Tenta extrair de WKT
        try:
            sr = osr.SpatialReference()
            if crs_string.startswith('+proj'):
                sr.ImportFromProj4(crs_string)
            else:
                sr.ImportFromWkt(crs_string)
            
            if sr.IsProjected() or sr.IsGeographic():
                auth = sr.GetAuthorityName(None)
                code = sr.GetAuthorityCode(None)
                if auth == 'EPSG' and code:
                    return int(code)
        except:
            pass
        
        return None
    
    @staticmethod
    def is_geographic(crs_string: str) -> bool:
        """
        Verifica se o CRS é geográfico (lat/lon).
        
        Args:
            crs_string: String CRS
            
        Returns:
            True se geográfico, False caso contrário
        """
        try:
            sr = osr.SpatialReference()
            if crs_string.startswith('EPSG:'):
                epsg_code = int(crs_string.split(':')[1])
                sr.ImportFromEPSG(epsg_code)
            elif crs_string.startswith('+proj'):
                sr.ImportFromProj4(crs_string)
            else:
                sr.ImportFromWkt(crs_string)
            
            return sr.IsGeographic() == 1
        except:
            return False
    
    @staticmethod
    def is_projected(crs_string: str) -> bool:
        """
        Verifica se o CRS é projetado.
        
        Args:
            crs_string: String CRS
            
        Returns:
            True se projetado, False caso contrário
        """
        try:
            sr = osr.SpatialReference()
            if crs_string.startswith('EPSG:'):
                epsg_code = int(crs_string.split(':')[1])
                sr.ImportFromEPSG(epsg_code)
            elif crs_string.startswith('+proj'):
                sr.ImportFromProj4(crs_string)
            else:
                sr.ImportFromWkt(crs_string)
            
            return sr.IsProjected() == 1
        except:
            return False




