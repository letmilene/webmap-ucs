import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import Geocoder, MeasureControl, MiniMap
import os

# Configuração da página
st.set_page_config(
    page_title="Webmap - Unidades de Conservação",
    page_icon="🌿",
    layout="wide"
)

# Título da aplicação
st.title("🌿 Webmap - Unidades de Conservação")
st.markdown("---")

# Sidebar para controles
st.sidebar.header("Configurações do Mapa")

# Função para carregar dados
@st.cache_data
def carregar_dados():
    """Carrega os shapefiles necessários"""
    try:
        # Verificar se os arquivos existem
        uc_path = 'data/unidades_conservacao/unidades_conservacao.shp'
        municipios_path = 'data/municipios/municipios.shp'
        rios_path = 'data/rios/rios.shp'
        
        # Verificar se os diretórios existem
        if not os.path.exists(uc_path):
            st.error(f"Arquivo não encontrado: {uc_path}")
            return None, None, None
        if not os.path.exists(municipios_path):
            st.error(f"Arquivo não encontrado: {municipios_path}")
            return None, None, None
        if not os.path.exists(rios_path):
            st.error(f"Arquivo não encontrado: {rios_path}")
            return None, None, None
        
        # Carregar os dados
        uc_gdf = gpd.read_file(uc_path)
        municipios_gdf = gpd.read_file(municipios_path)
        rios_gdf = gpd.read_file(rios_path)
        
        return uc_gdf, municipios_gdf, rios_gdf
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return None, None, None

# Carregar os dados
uc_gdf, municipios_gdf, rios_gdf = carregar_dados()

if uc_gdf is not None and municipios_gdf is not None and rios_gdf is not None:
    
    # Controles na sidebar
    st.sidebar.subheader("Camadas do Mapa")
    
    # Checkboxes para controlar a visibilidade das camadas
    mostrar_uc_protecao = st.sidebar.checkbox("Unidades de Proteção Integral", value=True)
    mostrar_uc_uso = st.sidebar.checkbox("Unidades de Uso Sustentável", value=True)
    mostrar_municipios = st.sidebar.checkbox("Municípios", value=True)
    mostrar_rios = st.sidebar.checkbox("Rios", value=True)
    
    # Seletor de tile base
    st.sidebar.subheader("Mapa Base")
    tile_option = st.sidebar.selectbox(
        "Escolha o tipo de mapa:",
        ["OpenStreetMap", "Satélite (Esri)", "CartoDB Positron"]
    )
    
    # Configurações do mapa
    st.sidebar.subheader("Configurações")
    zoom_inicial = st.sidebar.slider("Zoom inicial", 5, 12, 7)
    
    # Coordenadas centrais
    latitude_centro = -22.268
    longitude_centro = -48.433
    
    # Criar o mapa base
    if tile_option == "OpenStreetMap":
        m = folium.Map(
            location=[latitude_centro, longitude_centro], 
            zoom_start=zoom_inicial, 
            tiles='OpenStreetMap'
        )
    elif tile_option == "Satélite (Esri)":
        m = folium.Map(
            location=[latitude_centro, longitude_centro], 
            zoom_start=zoom_inicial, 
            tiles=None
        )
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr='Esri',
            name='Satélite (Esri)',
            overlay=False,
            control=True
        ).add_to(m)
    else:  # CartoDB Positron
        m = folium.Map(
            location=[latitude_centro, longitude_centro], 
            zoom_start=zoom_inicial, 
            tiles='CartoDB positron'
        )
    
    # Filtrar por tipo de unidade de conservação
    if mostrar_uc_protecao or mostrar_uc_uso:
        uc_protecao_integral = uc_gdf[uc_gdf['tipo'] == 'Unidade de Conservação de Proteção Integral']
        uc_uso_sustentavel = uc_gdf[uc_gdf['tipo'] == 'Unidade de Conservação de Uso Sustentável']
        
        # Adicionar camada de Unidades de Proteção Integral
        if mostrar_uc_protecao:
            folium.GeoJson(
                uc_protecao_integral,
                name='Unidades de Proteção Integral',
                style_function=lambda x: {
                    'fillColor': 'darkgreen',
                    'color': 'darkgreen',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['uc', 'categoria','area_ha'],
                    aliases=['Nome:', 'Categoria:', 'Área (ha):']
                )
            ).add_to(m)
        
        # Adicionar camada de Unidades de Uso Sustentável
        if mostrar_uc_uso:
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
            ).add_to(m)
    
    # Adicionar camada de Municípios
    if mostrar_municipios:
        folium.GeoJson(
            municipios_gdf,
            name='Municípios',
            style_function=lambda x: {
                'fillColor': 'gray', 
                'color': 'gray', 
                'weight': 0.3, 
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NOME'], 
                aliases=['Município:']
            )
        ).add_to(m)
    
    # Adicionar camada de Rios
    if mostrar_rios:
        folium.GeoJson(
            rios_gdf,
            name='Rios',
            style_function=lambda x: {
                'color': 'blue', 
                'weight': 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['nome'], 
                aliases=['Rio:']
            )
        ).add_to(m)
    
    # Adicionar controles ao mapa
    folium.LayerControl(
        position='topright',
        collapsed=False
    ).add_to(m)
    
    # Adicionar campo de pesquisa
    Geocoder(
        collapsed=False,
        position='topleft',
        placeholder='Pesquisar local...'
    ).add_to(m)
    
    # Adicionar ferramenta de medição
    MeasureControl().add_to(m)
    
    # Adicionar mini mapa
    minimap = MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Exibir o mapa no Streamlit
    st.subheader("Mapa Interativo")
    
    # Usar st_folium para exibir o mapa
    map_data = st_folium(m, width=1200, height=600)
    
    # Informações sobre os dados
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Unidades de Conservação", len(uc_gdf))
    
    with col2:
        st.metric("Municípios", len(municipios_gdf))
    
    with col3:
        st.metric("Rios", len(rios_gdf))
    
    # Mostrar informações detalhadas se solicitado
    if st.sidebar.checkbox("Mostrar dados detalhados"):
        st.subheader("Dados das Unidades de Conservação")
        st.dataframe(uc_gdf.drop(columns=['geometry']))
        
        st.subheader("Dados dos Municípios")
        st.dataframe(municipios_gdf.drop(columns=['geometry']))
        
        st.subheader("Dados dos Rios")
        st.dataframe(rios_gdf.drop(columns=['geometry']))

else:
    st.error("Não foi possível carregar os dados. Verifique se os arquivos shapefile estão no diretório correto.")
    st.info("""
    **Estrutura de diretórios esperada:**
    ```
    data/
    ├── unidades_conservacao/
    │   └── unidades_conservacao.shp (+ arquivos associados)
    ├── municipios/
    │   └── municipios.shp (+ arquivos associados)
    └── rios/
        └── rios.shp (+ arquivos associados)
    ```
    """)

# Rodapé
st.markdown("---")
st.markdown("**Webmap de Unidades de Conservação** - Desenvolvido com Streamlit e Folium")

