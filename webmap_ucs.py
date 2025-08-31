import geopandas as gpd
# path = caminho // gdf = GeoDataFrame

# Unidades de Conservação
uc_path = 'data/unidades_conservacao/unidades_conservacao.shp'
uc_gdf = gpd.read_file(uc_path)

# Municípios
municipios_path = 'data/municipios/municipios.shp'
municipios_gdf = gpd.read_file(municipios_path)

# Rios
rios_path = 'data/rios/rios.shp'
rios_gdf = gpd.read_file(rios_path)

print("Shapefiles carregados com sucesso!")
# print("Unidades de Conservação:", uc_gdf.head())
# print("Municípios:", municipios_gdf.head())
# print("Rios:", rios_gdf.head())

import folium

# Definir as coordenadas centrais para o mapa (aqui foi no olhômetro)
# Dá pra ajustar isso para a área de interesse dos dados 
latitude_centro = -22.268
longitude_centro = -48.433

# Criar o mapa base
m = folium.Map(
    location=[latitude_centro, longitude_centro], 
    zoom_start=7, 
    tiles='OpenStreetMap')

# Adicionar tiles alternativos
folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Esri',
        name='Satélite (Esri)',
        overlay=False,
        control=True
        ).add_to(m)
    
folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Positron',
        overlay=False,
        control=True
        ).add_to(m)

print("Mapa base criado!")

# Filtrar por tipo de unidade de conservação
uc_protecao_integral = uc_gdf[uc_gdf['tipo'] == 'Unidade de Conservação de Proteção Integral']
uc_uso_sustentavel = uc_gdf[uc_gdf['tipo'] == 'Unidade de Conservação de Uso Sustentável']

# Adiciona a camada de Unidades de Proteção Integral
folium.GeoJson(
    uc_protecao_integral,                   # Passa o GeoDataFrame filtrado para o Folium
    name='Unidades de Proteção Integral',   # Define o nome da camada que aparecerá no controle de camadas do mapa
        style_function=lambda x: {          # Define o estilo visual da camada usando uma função 'style_function'
        'fillColor': 'darkgreen',           # Cor de preenchimento dos polígonos
        'color': 'darkgreen',               # Cor da borda
        'weight': 1,                        # Espessura da borda
        'fillOpacity': 0.5                  # Transparência do preenchimento (0 a 1)
    },
    tooltip=folium.GeoJsonTooltip(          # Adiciona um tooltip (caixa de informação ao passar o mouse) para a camada
        fields=['uc', 'categoria','area_ha'],           # Campos do GeoDataFrame que serão exibidos
        aliases=['Nome:', 'Categoria:', 'Área (ha):']   # Rótulos personalizados para os campos
    )
).add_to(m) # Adiciona a camada ao objeto de mapa 'm'

# Adiciona a camada de Unidades de Uso Sustentável -- a configuração é a mesma, só troquei a simbologia
folium.GeoJson(
    uc_uso_sustentavel,
    name='Unidades de Uso Sustentável',
    style_function=lambda x: {
        'fillColor': 'lightgreen', 
        'color': 'lightgreen',
        'weight': 1,
        'fillOpacity': 0.5
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['uc', 'categoria','area_ha'], 
        aliases=['Nome:', 'Categoria:', 'Área (ha):']
    )
).add_to(m) # Adiciona a segunda camada ao mapa 'm'

print("Camadas de Unidades de Conservação adicionadas!")

# Municípios
folium.GeoJson(
    municipios_gdf,
    name='Municípios',
    style_function=lambda x: {'fillColor': 'gray', 'color': 'gray', 'weight': 0.3, 'fillOpacity': 0},
    tooltip=folium.GeoJsonTooltip(fields=['NOME'], aliases=['Município:'])
).add_to(m)

# Rios (são linhas, então 'fillColor' não se aplica)
folium.GeoJson(
    rios_gdf,
    name='Rios',
    style_function=lambda x: {'color': 'blue', 'weight': 0.3},
    tooltip=folium.GeoJsonTooltip(fields=['nome'], aliases=['Rio:'])
).add_to(m)

print("Camadas de Municípios e Rios adicionadas!")

folium.LayerControl(
    position='topright',    # Posição da caixa de controle no mapa
    collapsed=False         # 'False' faz com que a caixa seja exibida aberta por padrão
    ).add_to(m)             # Adiciona o controle de camadas ao mapa 'm'

print("Controle de camadas adicionado!")

from folium.plugins import Geocoder

# Adicionar o campo de pesquisa
Geocoder(
    collapsed=False,                    # 'False' exibe a barra de pesquisa expandida por padrão
    position='topleft',                 # Posição da barra de pesquisa no mapa
    placeholder='Pesquisar local...'    # Texto de dica exibido na barra de pesquisa
).add_to(m)

print("Campo de pesquisa de locais adicionado!")

from folium.plugins import MeasureControl

MeasureControl().add_to(m) # Adiciona a ferramenta de medição com configurações padrão

from folium.plugins import MiniMap

minimap = MiniMap(toggle_display=True)  # 'toggle_display=True' permite ligar/desligar o mini mapa
m.add_child(minimap)                    # Adiciona o mini mapa como um "filho" do mapa principal

# Salvar o mapa como um arquivo HTML
output_path = 'webmap_unidades_conservacao.html'
m.save(output_path)

print(f"Webmap salvo em: {output_path}")
print("Para visualizar, abra o arquivo 'webmap_unidades_conservacao.html' em seu navegador web.")