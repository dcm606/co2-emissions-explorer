import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CO₂ Emissions Explorer", layout="wide", page_icon="🌍")


@st.cache_data
def load_data():
    return pd.read_csv("df.csv")


df = load_data()

# ====================== CLASIFICACIÓN ======================
regiones_a_excluir = [
    'World', 'Africa (GCP)', 'Asia (GCP)', 'Europe (GCP)', 'North America (GCP)',
    'South America (GCP)', 'Oceania (GCP)', 'Asia', 'Europe', 'North America',
    'South America', 'Africa', 'Upper-middle-income countries', 'High-income countries',
    'Lower-middle-income countries', 'European Union (27)', 'European Union (28)'
]

paises = sorted([c for c in df['country'].unique() if c not in regiones_a_excluir])

# ====================== FILTROS ======================
st.sidebar.header("🔍 Filtros")

year_range = st.sidebar.slider("Rango de años", 1950, 2024, (1950, 2024))

st.sidebar.subheader("🌍 Regiones")
selected_regions = st.sidebar.multiselect("Selecciona regiones",
                                          ['World', 'Africa (GCP)', 'Asia (GCP)', 'Europe (GCP)', 'North America (GCP)',
                                           'South America (GCP)'],
                                          default=['World'])

st.sidebar.subheader("🏳️ Países")
default_paises = ['China', 'United States', 'India', 'Russia', 'Japan']
selected_countries = st.sidebar.multiselect("Selecciona países", paises, default=default_paises)

selected_entities = selected_regions + selected_countries

df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if selected_entities:
    df_filtered = df_filtered[df_filtered['country'].isin(selected_entities)]

# ====================== TÍTULO ======================
st.markdown("""
    <h1 style='text-align: center; color: #4ADE80; margin-bottom: 5px;'>
        🌍 CO₂ Emissions Explorer (1950-2024)
    </h1>
    <p style='text-align: center; color: #94A3B8; font-size: 17px; margin-bottom: 10px;'>
        Práctica Visualización de Datos - UOC
    </p>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Evolución Temporal",
    "🏆 Ranking de Países",
    "🗺️ Mapa Mundial",
    "⚡ Fuentes de Energía"
])

# ====================== TAB 1 ======================
with tab1:
    st.subheader("📈 Evolución Temporal de Emisiones")
    st.markdown("""
    **En esta sección puedes analizar cómo han evolucionado las emisiones de CO₂ desde 1950.**  
    Compara las emisiones totales (izquierda) con las emisiones por habitante (derecha).
    """)

    st.markdown(f"""
        <p style='text-align: center; font-size: 18px; font-weight: bold; color: #67E8F9; 
                   background-color: #1E2937; padding: 12px; border-radius: 8px; margin: 20px 0 25px 0;'>
            📅 Periodo analizado: <b>{year_range[0]} — {year_range[1]}</b>
        </p>
    """, unsafe_allow_html=True)

    use_log = st.checkbox("Usar escala logarítmica", value=False)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        fig1 = px.line(df_filtered, x='year', y='co2', color='country',
                       title="Emisiones Totales de CO₂",
                       labels={'co2': 'Millones de toneladas (Mt)', 'year': 'Año'},
                       log_y=use_log)
        fig1.update_traces(hovertemplate="%{fullData.name}<br>Año: %{x}<br>CO₂: %{y:,.0f} Mt")
        fig1.update_layout(legend_title="País / Región", legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.line(df_filtered, x='year', y='co2_per_capita', color='country',
                       title="Emisiones de CO₂ per cápita",
                       labels={'co2_per_capita': 'Toneladas por persona', 'year': 'Año'},
                       log_y=use_log)
        fig2.update_traces(hovertemplate="%{fullData.name}<br>Año: %{x}<br>Per cápita: %{y:.2f} t")
        fig2.update_layout(legend_title="País / Región", legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig2, use_container_width=True)

# ====================== TAB 2 ======================
with tab2:
    st.subheader("🏆 Ranking de Emisores (solo países)")
    st.markdown("""
    **En esta sección puedes ver el ranking de los países según sus emisiones de CO₂.**  
    Puedes cambiar entre **emisiones totales** y **emisiones por habitante**.
    """)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        year_sel = st.selectbox("Selecciona año", sorted(df['year'].unique()), index=len(df['year'].unique()) - 1)
    with col2:
        top_n = st.selectbox("Mostrar Top", [10, 15, 20, 25, 30, 40, 50], index=3)
    with col3:
        metric = st.radio("Métrica", ["Totales", "Per Cápita"], horizontal=True)

    df_paises_only = df[~df['country'].isin(regiones_a_excluir)].copy()
    grupos_excluir = ['Low-income', 'Lower-middle', 'Upper-middle', 'High-income', 'OECD', 'income']
    df_paises_only = df_paises_only[~df_paises_only['country'].str.contains('|'.join(grupos_excluir), na=False)]

    df_year = df_paises_only[df_paises_only['year'] == year_sel].copy()

    if metric == "Totales":
        sort_col = 'co2'
        title = f"Top {top_n} Países por Emisiones Totales en {year_sel}"
        unit = "Mt CO₂"
        text_format = '%{x:,.0f}'
    else:
        sort_col = 'co2_per_capita'
        title = f"Top {top_n} Países por Emisiones per Cápita en {year_sel}"
        unit = "toneladas por persona"
        text_format = '%{x:.1f}'

    df_year = df_year.nlargest(top_n, sort_col)

    fig_bar = px.bar(df_year, x=sort_col, y='country', orientation='h',
                     title=title, color=sort_col, color_continuous_scale='Blues', text=sort_col)

    fig_bar.update_traces(texttemplate=text_format, textposition="outside",
                          hovertemplate="<b>%{y}</b><br>" +
                                        (
                                            "Total: %{x:,.0f} Mt CO₂" if metric == "Totales" else "Per cápita: %{x:.2f} t"))

    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending', 'title': 'País'},
                          height=720, xaxis_title=unit, margin=dict(l=20, r=80, t=60, b=40))

    st.plotly_chart(fig_bar, use_container_width=True)

# ====================== TAB 3: MAPA MEJORADO ======================
with tab3:
    st.subheader("🗺️ Mapa Mundial de Emisiones")
    st.markdown("""
    **Explora las emisiones de CO₂ a nivel mundial.**  
    Cambia el año con el slider y alterna entre emisiones totales y per cápita.
    """)

    col_map1, col_map2 = st.columns([3, 1])
    with col_map1:
        year_map = st.slider("Selecciona el año", 1950, 2024, 2020)
    with col_map2:
        map_metric = st.radio("Tipo de emisión", ["Per Cápita", "Totales"], horizontal=True)

    df_map = df[df['year'] == year_map].copy()

    if map_metric == "Per Cápita":
        color_var = "co2_per_capita"
        title_map = f"Emisiones de CO₂ per cápita - {year_map}"
        hover_text = "<b>%{hovertext}</b><br>Per cápita: %{z:.2f} toneladas"
    else:
        color_var = "co2"
        title_map = f"Emisiones Totales de CO₂ - {year_map}"
        hover_text = "<b>%{hovertext}</b><br>Total: %{z:,.0f} Mt CO₂"

    fig_map = px.choropleth(df_map,
                            locations="iso_code",
                            color=color_var,
                            hover_name="country",
                            title=title_map,
                            color_continuous_scale="Reds")

    fig_map.update_traces(
        hovertemplate=hover_text,
        hoverlabel=dict(bgcolor="#1E2937", font_color="white", font_size=14)
    )

    fig_map.update_layout(height=800, margin=dict(l=20, r=20, t=50, b=20))

    st.plotly_chart(fig_map, use_container_width=True)

# ====================== TAB 4 ======================
with tab4:
    st.subheader("⚡ Desglose por Fuentes de Energía")
    default = 'World' if 'World' in df['country'].values else df['country'].iloc[0]
    country_sel = st.selectbox("Selecciona entidad", sorted(df['country'].unique()),
                               index=list(df['country'].unique()).index(default))
    df_country = df[df['country'] == country_sel]
    fuentes = ['coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2']
    fig_stack = px.area(df_country, x='year', y=fuentes, title=f"Fuentes de emisiones en {country_sel}")
    fig_stack.update_traces(hovertemplate="%{fullData.name}: %{y:,.0f} Mt")
    st.plotly_chart(fig_stack, use_container_width=True)

st.caption("Fuente: Our World in Data | Dashboard interactivo - Práctica UOC")