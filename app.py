import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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

# Preparar GDP per cápita para la Tab 5
df['gdp_per_capita'] = df['gdp'] / df['population']

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Evolución Temporal",
    "🏆 Ranking de Países",
    "🗺️ Mapa Mundial",
    "⚡ Fuentes de Energía",
    "💰 Emisiones vs Economía"
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

    st.markdown("**Datos detallados**")
    cols_mostrar = ['country', 'co2', 'co2_per_capita']
    st.dataframe(
        df_year[cols_mostrar].round(2).rename(columns={
            'co2': 'Emisiones Totales (Mt)',
            'co2_per_capita': 'Emisiones per cápita (t)'
        }),
        use_container_width=True,
        hide_index=True
    )

# ====================== TAB 3 ======================
with tab3:
    st.subheader("🗺️ Mapa Mundial de Emisiones")
    st.markdown("""
    **Explora las emisiones de CO₂ a nivel mundial.**  
    Cambia el año con el slider y alterna entre emisiones totales y per cápita.
    """)

    col_map1, col_map2, col_map3 = st.columns([3, 1.5, 1])
    with col_map1:
        year_map = st.slider("Selecciona el año", 1950, 2024, 2020)
    with col_map2:
        map_metric = st.radio("Tipo de emisión", ["Per Cápita", "Totales"], horizontal=True)
    with col_map3:
        use_log_map = st.checkbox("Usar escala logarítmica", value=True)

    df_map = df[df['year'] == year_map].copy()

    if map_metric == "Per Cápita":
        color_var = "co2_per_capita"
        title_map = f"Emisiones de CO₂ per cápita - {year_map}"
        hover_text = "<b>%{hovertext}</b><br>Per cápita: %{customdata[0]:.2f} toneladas"
    else:
        color_var = "co2"
        title_map = f"Emisiones Totales de CO₂ - {year_map}"
        hover_text = "<b>%{hovertext}</b><br>Total: %{customdata[0]:,.0f} Mt CO₂"

    if use_log_map:
        df_map['color_value'] = df_map[color_var].replace(0, 0.001)
        df_map['color_value'] = np.log10(df_map['color_value'])
        color_col = 'color_value'
        title_map += " (Escala Logarítmica)"
    else:
        color_col = color_var

    fig_map = px.choropleth(df_map,
                            locations="iso_code",
                            color=color_col,
                            hover_name="country",
                            title=title_map,
                            color_continuous_scale="OrRd" if use_log_map else "Reds",
                            custom_data=[df_map[color_var]])

    fig_map.update_traces(
        hovertemplate=hover_text,
        hoverlabel=dict(bgcolor="#1E2937", font_color="white", font_size=14)
    )

    fig_map.update_layout(height=800, margin=dict(l=20, r=20, t=50, b=20))

    st.plotly_chart(fig_map, use_container_width=True)

# ====================== TAB 4 ======================
with tab4:
    st.subheader("⚡ Desglose por Fuentes de Energía")
    st.markdown("""
    **Analiza de qué fuentes provienen las emisiones de CO₂ en cada país o región.**
    """)

    default = 'World' if 'World' in df['country'].values else df['country'].iloc[0]
    country_sel = st.selectbox("Selecciona país o región",
                               sorted(df['country'].unique()),
                               index=list(df['country'].unique()).index(default))

    df_country = df[df['country'] == country_sel].copy()

    col_opt1, col_opt2 = st.columns([2, 1])
    with col_opt1:
        view_mode = st.radio("Tipo de visualización", ["Valores Absolutos (Mt)", "Porcentajes (%)"],
                             horizontal=True)
    with col_opt2:
        show_total = st.checkbox("Mostrar línea total", value=True)

    fuentes_dict = {
        'coal_co2': 'Carbón',
        'oil_co2': 'Petróleo',
        'gas_co2': 'Gas Natural',
        'cement_co2': 'Producción de Cemento',
        'flaring_co2': 'Quema de Gas'
    }

    fuentes = list(fuentes_dict.keys())
    colores = ['#E63939', '#F4A261', '#2A9D8F', '#8D46B8', '#F4D35E']

    if view_mode == "Valores Absolutos (Mt)":
        y_values = fuentes
        title = f"Fuentes de emisiones en {country_sel}"
        hover_text = "%{fullData.name}: %{y:,.0f} Mt"
    else:
        df_country['total'] = df_country[fuentes].sum(axis=1)
        for fuente in fuentes:
            df_country[fuente + '_pct'] = df_country[fuente] / df_country['total'] * 100
        y_values = [f + '_pct' for f in fuentes]
        title = f"Composición porcentual de emisiones en {country_sel}"
        hover_text = "%{fullData.name}: %{y:.1f}%"

    fig_stack = px.area(df_country, x='year', y=y_values,
                        title=title,
                        color_discrete_sequence=colores)

    for trace in fig_stack.data:
        old_name = trace.name
        trace.name = fuentes_dict.get(old_name.replace('_pct', ''), old_name)

    fig_stack.update_traces(hovertemplate=hover_text)

    fig_stack.update_layout(
        height=650,
        legend_title="Fuente de Energía",
        legend=dict(orientation="h", y=-0.28, x=0.5, xanchor="center"),
        margin=dict(l=20, r=20, t=60, b=130),
        xaxis_title="Año",
        yaxis_title="Millones de toneladas (Mt)" if view_mode == "Valores Absolutos (Mt)" else "Porcentaje (%)"
    )

    if show_total and view_mode == "Valores Absolutos (Mt)":
        fig_stack.add_trace(
            go.Scatter(x=df_country['year'], y=df_country[fuentes].sum(axis=1),
                       mode='lines', name='Total Emisiones',
                       line=dict(color='white', width=3, dash='dash'))
        )

    st.plotly_chart(fig_stack, use_container_width=True)

# ====================== TAB 5: EMISIONES VS ECONOMÍA ======================
with tab5:
    st.subheader("💰 Emisiones vs Desarrollo Económico")
    st.markdown("""
    **Esta visualización muestra la relación entre el nivel de riqueza de un país y sus emisiones de CO₂.**  
    El eje horizontal representa el **PIB per cápita** (mayor riqueza hacia la derecha).  
    El eje vertical muestra las **emisiones per cápita**.  
    El tamaño de cada burbuja indica el volumen total de emisiones del país o la población, puede elegir.
    """)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        year_anim = st.slider("Selecciona el año", 1950, 2024, 2000, key="year_anim")
    with col_b:
        bubble_size = st.radio("Tamaño de burbuja", ["Emisiones Totales", "Población"], horizontal=True)

    size_var = 'co2' if bubble_size == "Emisiones Totales" else 'population'

    df_anim = df[df['year'] == year_anim].copy()
    df_anim = df_anim[~df_anim['country'].isin(regiones_a_excluir)]
    df_anim = df_anim.dropna(subset=['gdp_per_capita', 'co2_per_capita', size_var])
    df_anim = df_anim[df_anim[size_var] > 0]

    fig_bubble = px.scatter(df_anim,
                            x="gdp_per_capita",
                            y="co2_per_capita",
                            size=size_var,
                            color="co2_per_capita",
                            hover_name="country",
                            title=f"Emisiones vs PIB per cápita — {year_anim}",
                            color_continuous_scale="RdYlBu_r",
                            size_max=70,
                            labels={
                                "gdp_per_capita": "PIB per cápita (USD)",
                                "co2_per_capita": "Emisiones de CO₂ per cápita (toneladas)"
                            })

    # Hover mejorado
    fig_bubble.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "PIB per cápita: %{x:,.0f} USD<br>" +
                      "CO₂ per cápita: %{y:.2f} toneladas<br>" +
                      "Emisiones Totales: %{marker.size:,.0f} Mt"
    )

    fig_bubble.update_layout(
        height=720,
        margin=dict(l=20, r=20, t=80, b=40),
        coloraxis_colorbar=dict(title="CO₂ per cápita (t)")
    )

    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("""
    ### Cómo interpretar las posiciones:

    - **Arriba a la derecha** → Países ricos con **altas emisiones per cápita** (ej. EE.UU., Canadá, Australia)
    - **Abajo a la derecha** → Países ricos pero **más eficientes** (bajas emisiones relativas)
    - **Arriba a la izquierda** → Países con **altas emisiones per cápita** a pesar de tener bajo nivel económico
    - **Abajo a la izquierda** → Países con bajo PIB y bajas emisiones per cápita
    """)

st.caption("Fuente: Our World in Data | Dashboard interactivo - Práctica UOC")