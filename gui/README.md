# Estrutura Modular QML - Padrão Qt Design Studio

## Descrição

Esta pasta contém a interface gráfica (GUI) da aplicação, organizada seguindo o padrão modular recomendado pelo Qt Design Studio.

## Estrutura de Diretórios

```
gui/
├── Main.qml                 # Arquivo principal que orquestra toda a interface
├── components/              # Pasta com componentes reutilizáveis
│   ├── qmldir              # Arquivo de definição do módulo QML
│   ├── AppTheme.qml        # Tema/cores centralizado (Singleton)
│   ├── AppMenuBar.qml      # Barra de menus
│   ├── AppToolBar.qml      # Barra de ferramentas
│   ├── AppStatusBar.qml    # Barra de status
│   ├── SidePanel.qml       # Painel lateral com abas
│   ├── LayersPanel.qml     # Aba de camadas (Layers)
│   ├── PropertiesPanel.qml # Aba de propriedades
│   ├── ProcessingPanel.qml # Aba de processamento
│   ├── EmptyPanel.qml      # Painel genérico vazio (reutilizável)
│   ├── MapCanvas.qml       # Canvas do mapa
│   └── InfoPanel.qml       # Painel de informações (direita)
└── images/                 # Pasta de ícones (já existente)
    └── themes/default/     # Ícones SVG do QGIS
```

## Componentes

### AppTheme.qml (Singleton)
Define todas as cores e temas da aplicação. Centraliza a paleta de cores para facilitar manutenção.

**Propriedades:**
- `windowBg`, `baseBg`, `text`, `button`, etc.
- `accentColor`: Cor principal (#007acc)
- Cores para temas escuros e claros

**Uso:**
```qml
import "components"
color: AppTheme.windowBg
```

### AppMenuBar.qml
Barra de menus superior com:
- Menu Arquivo
- Menu Editar
- Menu Visualização
- Menu Ferramentas
- Menu Ajuda

**Sinais:**
- `toolChanged(string tool)`
- `statusMessageChanged(string message)`
- `zoomFullExtent()`
- `mapRefreshed()`

### AppToolBar.qml
Barra de ferramentas com ícones SVG agrupados por categoria:
- **Arquivos**: Adicionar camadas
- **Navegação**: Pan, Zoom In/Out, Zoom Total
- **Ferramentas**: Identificar
- **Desenho**: Ponto, Linha, Polígono
- **Utilitários**: Atualizar

### AppStatusBar.qml
Barra de status rodapé (altura 40px) com:
- Mensagem principal
- Ferramenta ativa atual

### SidePanel.qml
Painel lateral colapsável com sistema de abas com ícones

**Propriedades:**
- `collapsed`: boolean - estado colapsado
- `tabIndex`: índice da aba ativa

**Recursos:**
- Minimização/maximização ao clicar ícone
- 5 ícones no lado esquerdo
- Conteúdo expansível na direita

### LayersPanel.qml
Aba de camadas com:
- ListView das camadas carregadas
- Checkbox de visibilidade
- Botões Add/Remove

**Sinais:**
- `layerAdded(string fileName, string layerType)`
- `layerRemoved(string layerName)`
- `layerVisibilityChanged(string layerName, bool visible)`

### PropertiesPanel.qml
Aba de propriedades com:
- Exibição de propriedades da camada selecionada
- TextArea read-only

### ProcessingPanel.qml
Aba de processamento (placeholder para funcionalidades futuras)

### EmptyPanel.qml
Painel genérico reutilizável para espaços vazios

**Propriedades:**
- `title`: string - título do painel

### MapCanvas.qml
Canvas do mapa com:
- Image do mapa renderizado
- MouseArea para interação
- Zoom com scroll do mouse
- Exibição de coordenadas

### InfoPanel.qml
Painel lateral direito com informações sobre:
- Ferramentas de navegação
- Ferramentas de consulta
- Ferramentas de desenho
- Atalhos de teclado

## Fluxo de Carregamento

1. **main.py** → Define base_url e carrega `gui/Main.qml`
2. **Main.qml** → Importa componentes e orquestra layout
3. **Componentes** → Cada componente é carregado sob demanda

```
Main.qml
├── AppMenuBar
├── AppToolBar
├── SplitView
│   ├── SidePanel
│   │   ├── LayersPanel
│   │   ├── PropertiesPanel
│   │   ├── ProcessingPanel
│   │   ├── EmptyPanel x2
│   ├── MapCanvas
│   └── InfoPanel
└── AppStatusBar
```

## Adicionando Novos Componentes

1. Criar arquivo `NovoComponente.qml` em `components/`
2. Adicionar entrada em `components/qmldir`:
   ```
   NovoComponente 1.0 NovoComponente.qml
   ```
3. Importar em `Main.qml` ou outro componente:
   ```qml
   import "components"
   NovoComponente { }
   ```

## Comunicação entre Componentes

**Métodos recomendados:**

1. **Propriedades (Data Binding)**
   ```qml
   SidePanel { id: sidePanel }
   MapCanvas { layerModel: sidePanel.layerModel }
   ```

2. **Sinais**
   ```qml
   LayersPanel {
       onLayerAdded: (fileName, type) => { ... }
   }
   ```

3. **Context Properties (Python → QML)**
   ```python
   engine.rootContext().setContextProperty("mapBackend", bridge)
   ```

## Temas e Customização

Para mudar o tema:
1. Editar cores em `AppTheme.qml`
2. Todos os componentes usam `AppTheme.*` automaticamente

## Boas Práticas

- ✅ Mantenha componentes pequenos e focados
- ✅ Use `AppTheme` para cores
- ✅ Documente propriedades e sinais
- ✅ Reutilize componentes (`EmptyPanel`, etc)
- ✅ Isole lógica em componentes separados
- ❌ Não misture muita lógica em componentes grandes
- ❌ Não hardcode cores/valores

## Performance

- Componentes são carregados lazily (sob demanda)
- Use `visible: false` ao invés de `destroy` para elementos que aparecem/desaparecem
- `StackLayout` para abas (renderiza apenas a aba ativa)

## Suporte

Para dúvidas sobre Qt/QML, veja:
- [Qt 6 Documentation](https://doc.qt.io/qt-6/)
- [Qt Design Studio](https://www.qt.io/product/design-studio)

