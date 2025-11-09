"""
Módulo de Gerenciamento de Camadas - Controla a ordem e visibilidade de camadas
"""

from typing import List, Optional
from .layer import Layer


class LayerManager:
    """
    Gerenciador de camadas - controla múltiplas camadas e sua ordem de exibição.
    Similar ao QgsLayerTreeModel do QGIS.
    
    As camadas são armazenadas em ordem, onde o índice 0 é desenhado primeiro (fundo)
    e o último índice é desenhado por último (topo).
    """
    
    def __init__(self):
        """Inicializa o gerenciador de camadas"""
        self._layers: List[Layer] = []
        self._layer_ids = {}  # Mapeamento nome -> índice
    
    def add_layer(self, layer: Layer, position: Optional[int] = None) -> bool:
        """
        Adiciona uma camada ao gerenciador.
        
        Args:
            layer: Camada a ser adicionada
            position: Posição onde inserir (None = no topo)
            
        Returns:
            True se adicionado com sucesso, False caso contrário
        """
        if not layer:
            return False
        
        # Verifica se já existe camada com o mesmo nome
        if layer.name in self._layer_ids:
            print(f"Aviso: Camada com nome '{layer.name}' já existe")
            return False
        
        # Adiciona na posição especificada ou no topo
        if position is None:
            self._layers.append(layer)
            self._layer_ids[layer.name] = len(self._layers) - 1
        else:
            position = max(0, min(position, len(self._layers)))
            self._layers.insert(position, layer)
            self._rebuild_layer_ids()
        
        print(f"Camada '{layer.name}' adicionada na posição {self._layer_ids[layer.name]}")
        return True
    
    def remove_layer(self, layer_name: str) -> bool:
        """
        Remove uma camada do gerenciador.
        
        Args:
            layer_name: Nome da camada a ser removida
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if layer_name not in self._layer_ids:
            return False
        
        idx = self._layer_ids[layer_name]
        del self._layers[idx]
        self._rebuild_layer_ids()
        
        print(f"Camada '{layer_name}' removida")
        return True
    
    def remove_layer_at(self, index: int) -> bool:
        """
        Remove uma camada pelo índice.
        
        Args:
            index: Índice da camada
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if 0 <= index < len(self._layers):
            layer_name = self._layers[index].name
            del self._layers[index]
            self._rebuild_layer_ids()
            print(f"Camada '{layer_name}' removida")
            return True
        return False
    
    def get_layer(self, layer_name: str) -> Optional[Layer]:
        """
        Obtém uma camada pelo nome.
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            Objeto Layer ou None se não encontrado
        """
        if layer_name in self._layer_ids:
            idx = self._layer_ids[layer_name]
            return self._layers[idx]
        return None
    
    def get_layer_at(self, index: int) -> Optional[Layer]:
        """
        Obtém uma camada pelo índice.
        
        Args:
            index: Índice da camada
            
        Returns:
            Objeto Layer ou None se índice inválido
        """
        if 0 <= index < len(self._layers):
            return self._layers[index]
        return None
    
    def get_all_layers(self) -> List[Layer]:
        """
        Retorna todas as camadas.
        
        Returns:
            Lista de camadas
        """
        return self._layers.copy()
    
    def get_visible_layers(self) -> List[Layer]:
        """
        Retorna apenas as camadas visíveis.
        
        Returns:
            Lista de camadas visíveis
        """
        return [layer for layer in self._layers if layer.visible]
    
    def layer_count(self) -> int:
        """
        Retorna o número total de camadas.
        
        Returns:
            Número de camadas
        """
        return len(self._layers)
    
    def move_layer(self, layer_name: str, new_position: int) -> bool:
        """
        Move uma camada para uma nova posição.
        
        Args:
            layer_name: Nome da camada
            new_position: Nova posição
            
        Returns:
            True se movido com sucesso, False caso contrário
        """
        if layer_name not in self._layer_ids:
            return False
        
        old_idx = self._layer_ids[layer_name]
        layer = self._layers[old_idx]
        
        # Remove da posição antiga
        del self._layers[old_idx]
        
        # Insere na nova posição
        new_position = max(0, min(new_position, len(self._layers)))
        self._layers.insert(new_position, layer)
        
        # Reconstrói índices
        self._rebuild_layer_ids()
        
        print(f"Camada '{layer_name}' movida para posição {new_position}")
        return True
    
    def move_layer_up(self, layer_name: str) -> bool:
        """
        Move uma camada uma posição acima (mais próxima do topo).
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            True se movido com sucesso, False caso contrário
        """
        if layer_name not in self._layer_ids:
            return False
        
        idx = self._layer_ids[layer_name]
        if idx >= len(self._layers) - 1:
            return False  # Já está no topo
        
        return self.move_layer(layer_name, idx + 1)
    
    def move_layer_down(self, layer_name: str) -> bool:
        """
        Move uma camada uma posição abaixo (mais próxima do fundo).
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            True se movido com sucesso, False caso contrário
        """
        if layer_name not in self._layer_ids:
            return False
        
        idx = self._layer_ids[layer_name]
        if idx <= 0:
            return False  # Já está no fundo
        
        return self.move_layer(layer_name, idx - 1)
    
    def move_layer_to_top(self, layer_name: str) -> bool:
        """
        Move uma camada para o topo (desenhada por último).
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            True se movido com sucesso, False caso contrário
        """
        return self.move_layer(layer_name, len(self._layers) - 1)
    
    def move_layer_to_bottom(self, layer_name: str) -> bool:
        """
        Move uma camada para o fundo (desenhada primeiro).
        
        Args:
            layer_name: Nome da camada
            
        Returns:
            True se movido com sucesso, False caso contrário
        """
        return self.move_layer(layer_name, 0)
    
    def set_layer_visibility(self, layer_name: str, visible: bool) -> bool:
        """
        Define a visibilidade de uma camada.
        
        Args:
            layer_name: Nome da camada
            visible: True para visível, False para oculto
            
        Returns:
            True se alterado com sucesso, False caso contrário
        """
        layer = self.get_layer(layer_name)
        if layer:
            layer.visible = visible
            print(f"Camada '{layer_name}' {'visível' if visible else 'oculta'}")
            return True
        return False
    
    def set_layer_opacity(self, layer_name: str, opacity: float) -> bool:
        """
        Define a opacidade de uma camada.
        
        Args:
            layer_name: Nome da camada
            opacity: Opacidade de 0.0 a 1.0
            
        Returns:
            True se alterado com sucesso, False caso contrário
        """
        layer = self.get_layer(layer_name)
        if layer:
            layer.opacity = opacity
            print(f"Opacidade da camada '{layer_name}' definida para {opacity:.2f}")
            return True
        return False
    
    def clear(self):
        """Remove todas as camadas"""
        self._layers.clear()
        self._layer_ids.clear()
        print("Todas as camadas removidas")
    
    def get_combined_extent(self) -> Optional[tuple]:
        """
        Calcula a extensão combinada de todas as camadas válidas.
        
        Returns:
            Tupla (minx, miny, maxx, maxy) ou None se não houver camadas
        """
        valid_extents = [layer.extent for layer in self._layers 
                        if layer.is_valid and layer.extent]
        
        if not valid_extents:
            return None
        
        # Calcula extensão combinada
        minx = min(ext[0] for ext in valid_extents)
        miny = min(ext[1] for ext in valid_extents)
        maxx = max(ext[2] for ext in valid_extents)
        maxy = max(ext[3] for ext in valid_extents)
        
        return (minx, miny, maxx, maxy)
    
    def _rebuild_layer_ids(self):
        """Reconstrói o mapeamento de nomes para índices"""
        self._layer_ids.clear()
        for idx, layer in enumerate(self._layers):
            self._layer_ids[layer.name] = idx
    
    def print_layer_tree(self):
        """Imprime a árvore de camadas para debug"""
        print("\n=== Árvore de Camadas ===")
        if not self._layers:
            print("  (vazio)")
        else:
            for idx, layer in enumerate(self._layers):
                visibility = "👁" if layer.visible else "🚫"
                print(f"  [{idx}] {visibility} {layer.name} ({layer.get_type().value}) - Opacidade: {layer.opacity:.2f}")
        print("========================\n")


