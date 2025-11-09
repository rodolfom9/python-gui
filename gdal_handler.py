"""
TopoCAD Pro - GDAL Handler
Gerenciador de operações com dados geoespaciais usando GDAL/OGR
"""

# Primeiro, tentar setup do GDAL vendored
import sys
from pathlib import Path
try:
    from gdal_loader import setup_gdal_path
    setup_gdal_path()
except ImportError:
    pass  # gdal_loader não encontrado, continuar com imports padrão

try:
    from osgeo import gdal, ogr, osr
    import geopandas as gpd
    from shapely.geometry import Point, Polygon, LineString
    import rasterio
    from pyproj import Transformer
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("⚠️ GDAL não disponível. Funcionalidades geoespaciais limitadas.")
    # Criar tipos dummy para evitar erros de tipo
    osr = None

import numpy as np
from typing import List, Dict, Tuple, Optional, Any

# Habilitar exceções GDAL
if GDAL_AVAILABLE:
    gdal.UseExceptions()


class GDALHandler:
    """Gerenciador de operações GDAL/OGR para dados geoespaciais"""
    
    def __init__(self):
        self.current_dataset = None
        self.current_srs = None
        
    # ==========================================
    # LEITURA DE VETORES
    # ==========================================
    
    def read_shapefile(self, filepath: str) -> Tuple[List[Dict], Optional[Any]]:
        """
        Lê shapefile usando GDAL/OGR
        
        Args:
            filepath: Caminho para o arquivo .shp
            
        Returns:
            Tupla com (lista de pontos, sistema de referência espacial)
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        driver = ogr.GetDriverByName('ESRI Shapefile')
        datasource = driver.Open(filepath, 0)
        
        if datasource is None:
            raise ValueError(f"Não foi possível abrir: {filepath}")
        
        layer = datasource.GetLayer()
        srs = layer.GetSpatialRef()
        
        points = []
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom.GetGeometryName() == 'POINT':
                x, y = geom.GetX(), geom.GetY()
                z = geom.GetZ() if geom.GetCoordinateDimension() == 3 else 0
                
                # Extrair atributos
                attributes = {}
                for i in range(feature.GetFieldCount()):
                    field_name = feature.GetFieldDefnRef(i).GetName()
                    attributes[field_name] = feature.GetField(i)
                
                points.append({
                    'id': feature.GetFID(),
                    'x': x,
                    'y': y,
                    'z': z,
                    'desc': attributes.get('descricao', attributes.get('desc', '')),
                    'attributes': attributes
                })
        
        datasource = None
        return points, srs
    
    def read_dxf(self, filepath: str) -> List[Dict]:
        """
        Lê arquivo DXF usando GDAL
        
        Args:
            filepath: Caminho para o arquivo .dxf
            
        Returns:
            Lista de feições do DXF
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        datasource = ogr.Open(filepath)
        
        if datasource is None:
            raise ValueError(f"Não foi possível abrir DXF: {filepath}")
        
        features = []
        for layer_idx in range(datasource.GetLayerCount()):
            layer = datasource.GetLayerByIndex(layer_idx)
            layer_name = layer.GetName()
            
            for feature in layer:
                geom = feature.GetGeometryRef()
                if geom:
                    features.append({
                        'layer': layer_name,
                        'geometry_type': geom.GetGeometryName(),
                        'geometry': geom.ExportToWkt(),
                        'attributes': {
                            feature.GetFieldDefnRef(i).GetName(): feature.GetField(i)
                            for i in range(feature.GetFieldCount())
                        }
                    })
        
        datasource = None
        return features
    
    # ==========================================
    # ESCRITA DE VETORES
    # ==========================================
    
    def write_shapefile(self, filepath: str, points: List[Dict], srs_epsg: int = 31983) -> bool:
        """
        Escreve shapefile usando GDAL/OGR
        
        Args:
            filepath: Caminho para salvar o arquivo .shp
            points: Lista de pontos com coordenadas
            srs_epsg: Código EPSG do sistema de referência
            
        Returns:
            True se sucesso
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        driver = ogr.GetDriverByName('ESRI Shapefile')
        
        # Deletar se já existe
        if Path(filepath).exists():
            driver.DeleteDataSource(filepath)
        
        datasource = driver.CreateDataSource(filepath)
        
        # Criar SRS
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(srs_epsg)
        
        # Criar camada
        layer = datasource.CreateLayer('pontos', srs, ogr.wkbPoint25D)
        
        # Adicionar campos
        layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('descricao', ogr.OFTString))
        
        cota_field = ogr.FieldDefn('cota', ogr.OFTReal)
        cota_field.SetPrecision(3)
        layer.CreateField(cota_field)
        
        # Adicionar feições
        for point in points:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField('id', point.get('id', 0))
            feature.SetField('descricao', point.get('desc', ''))
            feature.SetField('cota', point.get('z', 0.0))
            
            geom = ogr.Geometry(ogr.wkbPoint25D)
            geom.AddPoint(point['x'], point['y'], point.get('z', 0.0))
            feature.SetGeometry(geom)
            
            layer.CreateFeature(feature)
            feature = None
        
        datasource = None
        return True
    
    def export_to_dxf(self, filepath: str, geometries: List[Dict], layer_name: str = 'topografia') -> bool:
        """
        Exporta para DXF usando GDAL
        
        Args:
            filepath: Caminho para salvar o arquivo .dxf
            geometries: Lista de geometrias em formato WKT
            layer_name: Nome da camada no DXF
            
        Returns:
            True se sucesso
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        driver = ogr.GetDriverByName('DXF')
        
        if Path(filepath).exists():
            driver.DeleteDataSource(filepath)
        
        datasource = driver.CreateDataSource(filepath)
        layer = datasource.CreateLayer(layer_name)
        
        for geom_data in geometries:
            feature = ogr.Feature(layer.GetLayerDefn())
            geom = ogr.CreateGeometryFromWkt(geom_data['wkt'])
            feature.SetGeometry(geom)
            layer.CreateFeature(feature)
        
        datasource = None
        return True
    
    # ==========================================
    # RASTERS - MDT/MDS
    # ==========================================
    
    def read_raster(self, filepath: str) -> Tuple[np.ndarray, Dict]:
        """
        Lê raster (GeoTIFF, etc) usando GDAL
        
        Args:
            filepath: Caminho para o arquivo raster
            
        Returns:
            Tupla com (array de dados, metadados)
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        dataset = gdal.Open(filepath)
        
        if dataset is None:
            raise ValueError(f"Não foi possível abrir raster: {filepath}")
        
        band = dataset.GetRasterBand(1)
        data = band.ReadAsArray()
        
        # Metadados
        metadata = {
            'width': dataset.RasterXSize,
            'height': dataset.RasterYSize,
            'bands': dataset.RasterCount,
            'projection': dataset.GetProjection(),
            'geotransform': dataset.GetGeoTransform(),
            'nodata': band.GetNoDataValue()
        }
        
        dataset = None
        return data, metadata
    
    def extract_elevation_at_point(self, raster_path: str, x: float, y: float) -> Optional[float]:
        """
        Extrai elevação de um ponto no raster
        
        Args:
            raster_path: Caminho para o raster (MDT)
            x, y: Coordenadas do ponto
            
        Returns:
            Elevação no ponto ou None se fora dos limites
        """
        if not GDAL_AVAILABLE:
            return None
            
        dataset = gdal.Open(raster_path)
        
        if dataset is None:
            return None
        
        # Transformação inversa: coordenadas geográficas -> pixel
        gt = dataset.GetGeoTransform()
        inv_gt = gdal.InvGeoTransform(gt)
        
        if inv_gt is None:
            return None
        
        px, py = gdal.ApplyGeoTransform(inv_gt, x, y)
        px, py = int(px), int(py)
        
        # Verificar limites
        if px < 0 or py < 0 or px >= dataset.RasterXSize or py >= dataset.RasterYSize:
            return None
        
        band = dataset.GetRasterBand(1)
        data = band.ReadAsArray(px, py, 1, 1)
        
        dataset = None
        return float(data[0, 0]) if data is not None else None
    
    def create_contour_lines(self, raster_path: str, output_shp: str, interval: float = 1.0) -> bool:
        """
        Gera curvas de nível a partir de MDT
        
        Args:
            raster_path: Caminho para o MDT
            output_shp: Caminho para salvar as curvas de nível
            interval: Intervalo entre curvas (metros)
            
        Returns:
            True se sucesso
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL não está disponível")
            
        src_ds = gdal.Open(raster_path)
        src_band = src_ds.GetRasterBand(1)
        
        # Criar shapefile de saída
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if Path(output_shp).exists():
            driver.DeleteDataSource(output_shp)
        
        dst_ds = driver.CreateDataSource(output_shp)
        
        # Criar camada
        srs = osr.SpatialReference()
        srs.ImportFromWkt(src_ds.GetProjection())
        dst_layer = dst_ds.CreateLayer('contours', srs, ogr.wkbLineString25D)
        
        # Adicionar campo de elevação
        field_defn = ogr.FieldDefn('elevation', ogr.OFTReal)
        field_defn.SetPrecision(2)
        dst_layer.CreateField(field_defn)
        
        # Gerar curvas de nível
        gdal.ContourGenerate(src_band, interval, 0, [], 0, 0, dst_layer, 0, -1)
        
        dst_ds = None
        src_ds = None
        
        return True
    
    # ==========================================
    # TRANSFORMAÇÕES DE COORDENADAS
    # ==========================================
    
    def transform_coordinates(self, points: List[Dict], from_epsg: int, to_epsg: int) -> List[Dict]:
        """
        Transforma coordenadas entre sistemas de referência
        
        Args:
            points: Lista de pontos
            from_epsg: EPSG de origem
            to_epsg: EPSG de destino
            
        Returns:
            Lista de pontos transformados
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL/PyProj não está disponível")
            
        transformer = Transformer.from_crs(
            f"EPSG:{from_epsg}", 
            f"EPSG:{to_epsg}",
            always_xy=True
        )
        
        transformed = []
        for point in points:
            x_new, y_new = transformer.transform(point['x'], point['y'])
            transformed.append({
                **point,
                'x': x_new,
                'y': y_new
            })
        
        return transformed
    
    def get_utm_zone(self, lon: float, lat: float) -> Tuple[int, str, int]:
        """
        Calcula zona UTM a partir de coordenadas geográficas
        
        Args:
            lon, lat: Longitude e latitude em graus decimais
            
        Returns:
            Tupla com (zona, hemisfério, código EPSG)
        """
        zone = int((lon + 180) / 6) + 1
        hemisphere = 'north' if lat >= 0 else 'south'
        epsg = 32600 + zone if hemisphere == 'north' else 32700 + zone
        return zone, hemisphere, epsg
