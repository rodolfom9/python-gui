"""
Demonstração do Sistema de Mapa Interativo
Mostra o uso de Map Tools similar ao QGIS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from map_system import VectorLayer, RasterLayer
from map_system.map_canvas_interactive import MapCanvasInteractive
from map_system.map_tool import MapToolType


class MapInteractiveApp:
    """
    Aplicação de demonstração do sistema de mapa interativo.
    Com ferramentas de mapa (Map Tools) similar ao QGIS.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Mapa Interativo - Map Tools")
        self.root.geometry("1400x900")
        
        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_status_bar()
        
        self.update_status("Pronto - Ferramenta ativa: Pan")
    
    def _create_menu(self):
        """Cria menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Adicionar Vetor...", command=self.add_vector)
        file_menu.add_command(label="Adicionar Raster...", command=self.add_raster)
        file_menu.add_separator()
        file_menu.add_command(label="Salvar Imagem...", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Pan (Arrastar)", command=lambda: self.set_tool(MapToolType.PAN))
        tools_menu.add_command(label="Zoom In", command=lambda: self.set_tool(MapToolType.ZOOM_IN))
        tools_menu.add_command(label="Zoom Out", command=lambda: self.set_tool(MapToolType.ZOOM_OUT))
        tools_menu.add_command(label="Identificar", command=lambda: self.set_tool(MapToolType.IDENTIFY))
        tools_menu.add_separator()
        tools_menu.add_command(label="Adicionar Ponto", command=lambda: self.set_tool(MapToolType.ADD_POINT))
        tools_menu.add_command(label="Adicionar Linha", command=lambda: self.set_tool(MapToolType.ADD_LINE))
        tools_menu.add_command(label="Adicionar Polígono", command=lambda: self.set_tool(MapToolType.ADD_POLYGON))
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualização", menu=view_menu)
        view_menu.add_command(label="Zoom Total", command=self.zoom_full)
        view_menu.add_command(label="Atualizar", command=self.refresh)
    
    def _create_toolbar(self):
        """Cria toolbar de ferramentas"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Grupo: Arquivos
        ttk.Label(toolbar, text="Arquivos:").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📂 Vetor", command=self.add_vector, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🖼 Raster", command=self.add_raster, width=10).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Grupo: Navegação
        ttk.Label(toolbar, text="Navegação:").pack(side=tk.LEFT, padx=5)
        self.btn_pan = ttk.Button(toolbar, text="✋ Pan", 
                                   command=lambda: self.set_tool(MapToolType.PAN), width=10)
        self.btn_pan.pack(side=tk.LEFT, padx=2)
        
        self.btn_zoom_in = ttk.Button(toolbar, text="🔍+ Zoom In", 
                                       command=lambda: self.set_tool(MapToolType.ZOOM_IN), width=12)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=2)
        
        self.btn_zoom_out = ttk.Button(toolbar, text="🔍- Zoom Out", 
                                        command=lambda: self.set_tool(MapToolType.ZOOM_OUT), width=12)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="🗺 Zoom Total", command=self.zoom_full, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Grupo: Ferramentas
        ttk.Label(toolbar, text="Ferramentas:").pack(side=tk.LEFT, padx=5)
        self.btn_identify = ttk.Button(toolbar, text="ℹ️ Identificar", 
                                        command=lambda: self.set_tool(MapToolType.IDENTIFY), width=12)
        self.btn_identify.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Grupo: Desenho
        ttk.Label(toolbar, text="Desenho:").pack(side=tk.LEFT, padx=5)
        self.btn_point = ttk.Button(toolbar, text="• Ponto", 
                                     command=lambda: self.set_tool(MapToolType.ADD_POINT), width=10)
        self.btn_point.pack(side=tk.LEFT, padx=2)
        
        self.btn_line = ttk.Button(toolbar, text="/ Linha", 
                                    command=lambda: self.set_tool(MapToolType.ADD_LINE), width=10)
        self.btn_line.pack(side=tk.LEFT, padx=2)
        
        self.btn_polygon = ttk.Button(toolbar, text="⬡ Polígono", 
                                       command=lambda: self.set_tool(MapToolType.ADD_POLYGON), width=12)
        self.btn_polygon.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Botão atualizar
        ttk.Button(toolbar, text="🔄 Atualizar", command=self.refresh, width=10).pack(side=tk.LEFT, padx=2)
        
        # Armazena botões para highlight
        self.tool_buttons = {
            MapToolType.PAN: self.btn_pan,
            MapToolType.ZOOM_IN: self.btn_zoom_in,
            MapToolType.ZOOM_OUT: self.btn_zoom_out,
            MapToolType.IDENTIFY: self.btn_identify,
            MapToolType.ADD_POINT: self.btn_point,
            MapToolType.ADD_LINE: self.btn_line,
            MapToolType.ADD_POLYGON: self.btn_polygon,
        }
    
    def _create_main_area(self):
        """Cria área principal"""
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Painel de camadas
        layer_panel = ttk.Frame(main_frame)
        main_frame.add(layer_panel, weight=1)
        
        ttk.Label(layer_panel, text="Camadas", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.layer_listbox = tk.Listbox(layer_panel, selectmode=tk.SINGLE)
        self.layer_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas de mapa
        canvas_frame = ttk.Frame(main_frame)
        main_frame.add(canvas_frame, weight=3)
        
        ttk.Label(canvas_frame, text="Mapa Interativo com Map Tools", 
                 font=("Arial", 12, "bold")).pack(pady=5)
        
        # MapCanvas Interativo
        self.map_canvas = MapCanvasInteractive(canvas_frame, width=900, height=700)
        
        # Info panel
        info_panel = ttk.Frame(main_frame)
        main_frame.add(info_panel, weight=1)
        
        ttk.Label(info_panel, text="Informações", font=("Arial", 12, "bold")).pack(pady=5)
        
        info_text = tk.Text(info_panel, wrap=tk.WORD, width=30, height=20)
        info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        instructions = """FERRAMENTAS DE MAPA

🖱️ NAVEGAÇÃO:
• Pan: Arrastar mapa
• Zoom In: Clique para aproximar
• Zoom Out: Clique para afastar
• Wheel: Zoom no cursor

ℹ️ CONSULTA:
• Identificar: Clique em features

✏️ DESENHO:
• Ponto: Clique para adicionar
• Linha: Cliques para vértices
  Botão direito: Finalizar
• Polígono: Cliques para vértices
  Botão direito: Fechar

⌨️ ATALHOS:
• ESC: Cancelar desenho
• Enter: Finalizar desenho

Similar ao QGIS com Map Tools!
"""
        info_text.insert("1.0", instructions)
        info_text.config(state=tk.DISABLED)
    
    def _create_status_bar(self):
        """Cria barra de status"""
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message: str):
        """Atualiza status"""
        self.status_bar.config(text=message)
    
    def set_tool(self, tool_type: MapToolType):
        """Define ferramenta ativa"""
        self.map_canvas.set_tool(tool_type)
        
        # Atualiza visual dos botões
        for t, btn in self.tool_buttons.items():
            if t == tool_type:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])
        
        # Atualiza status
        tool_names = {
            MapToolType.PAN: "Pan (Arrastar)",
            MapToolType.ZOOM_IN: "Zoom In (Clique)",
            MapToolType.ZOOM_OUT: "Zoom Out (Clique)",
            MapToolType.IDENTIFY: "Identificar (Clique)",
            MapToolType.ADD_POINT: "Adicionar Ponto (Clique)",
            MapToolType.ADD_LINE: "Adicionar Linha (Clique vértices, Direito finaliza)",
            MapToolType.ADD_POLYGON: "Adicionar Polígono (Clique vértices, Direito fecha)",
        }
        self.update_status(f"Ferramenta ativa: {tool_names.get(tool_type, str(tool_type))}")
    
    def add_vector(self):
        """Adiciona camada vetorial"""
        filename = filedialog.askopenfilename(
            title="Selecione arquivo vetorial",
            filetypes=[("Shapefiles", "*.shp"), ("GeoJSON", "*.geojson *.json"), ("Todos", "*.*")]
        )
        if not filename:
            return
        
        try:
            name = os.path.splitext(os.path.basename(filename))[0]
            layer = VectorLayer(name, filename)
            
            if not layer.load():
                messagebox.showerror("Erro", f"Não foi possível carregar: {filename}")
                return
            
            self.map_canvas.add_layer(layer)
            self.update_layer_list()
            self.update_status(f"Camada adicionada: {name} ({layer.get_feature_count()} features)")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar camada: {str(e)}")
    
    def add_raster(self):
        """Adiciona camada raster"""
        filename = filedialog.askopenfilename(
            title="Selecione arquivo raster",
            filetypes=[("GeoTIFF", "*.tif *.tiff"), ("Todos", "*.*")]
        )
        if not filename:
            return
        
        try:
            name = os.path.splitext(os.path.basename(filename))[0]
            layer = RasterLayer(name, filename)
            
            if not layer.load():
                messagebox.showerror("Erro", f"Não foi possível carregar: {filename}")
                return
            
            self.map_canvas.add_layer(layer)
            self.update_layer_list()
            self.update_status(f"Raster adicionado: {name} ({layer.width}x{layer.height})")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar camada: {str(e)}")
    
    def update_layer_list(self):
        """Atualiza lista de camadas"""
        self.layer_listbox.delete(0, tk.END)
        for layer in reversed(self.map_canvas.get_layer_manager().get_all_layers()):
            visibility = "👁" if layer.visible else "🚫"
            self.layer_listbox.insert(tk.END, f"{visibility} {layer.name}")
    
    def zoom_full(self):
        """Zoom total"""
        self.map_canvas.zoom_to_full_extent()
        self.update_status("Zoom total")
    
    def refresh(self):
        """Atualiza mapa"""
        self.map_canvas.refresh()
        self.update_status("Mapa atualizado")
    
    def save_image(self):
        """Salva imagem"""
        filename = filedialog.asksaveasfilename(
            title="Salvar imagem",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")]
        )
        if filename:
            self.map_canvas.save_image(filename)
            self.update_status(f"Imagem salva: {filename}")


def main():
    """Função principal"""
    root = tk.Tk()
    app = MapInteractiveApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
