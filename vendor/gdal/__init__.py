"""Vendor GDAL - Bundled com TopoCAD Pro"""
import sys
from pathlib import Path

# Adicionar GDAL vendored ao path
vendor_path = Path(__file__).parent
if str(vendor_path / "python") not in sys.path:
    sys.path.insert(0, str(vendor_path / "python"))
if str(vendor_path / "lib") not in sys.path:
    sys.path.insert(0, str(vendor_path / "lib"))

__all__ = ["gdal"]
