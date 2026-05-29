# ============================================================
# dashboard_vendedores.py
# Dashboard interactivo de ventas por vendedor y región
# Herramientas: Streamlit + Pandas + Plotly
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ----------------------------------------
st.set_page_config(
    page_title="Dashboard de Vendedores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------
# ESTILOS PERSONALIZADOS
# ----------------------------------------
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# CARGA DE DATOS
# ----------------------------------------
@st.cache_data
def cargar_datos(ruta: str) -> pd.DataFrame:
    """Lee el archivo Excel y devuelve un DataFrame limpio."""
    df = pd.read_excel(ruta)
    df["NOMBRE COMPLETO"] = df["NAME"].str.strip() + " " + df["LASTNAME"].str.strip()
    # Convertir SALES AVERAGE a porcentaje legible
    df["SALES AVERAGE %"] = (df["SALES AVERAGE"] * 100).round(2)
    return df

RUTA_EXCEL = "sellers.xlsx"
df = cargar_datos(RUTA_EXCEL)

# ----------------------------------------
# BARRA LATERAL – FILTROS GLOBALES
# ----------------------------------------
st.sidebar.title("🎛 Filtros")
st.sidebar.markdown("---")

# Selector de región
regiones_disponibles = sorted(df["REGION"].unique())
regiones_elegidas = st.sidebar.multiselect(
    "Filtrar por Región",
    options=regiones_disponibles,
    default=regiones_disponibles,
    help="Selecciona una o varias regiones",
)

st.sidebar.markdown("---")

# Rango de unidades vendidas
min_uv, max_uv = int(df["SOLD UNITS"].min()), int(df["SOLD UNITS"].max())
rango_uv = st.sidebar.slider(
    "Rango de Unidades Vendidas",
    min_value=min_uv,
    max_value=max_uv,
    value=(min_uv, max_uv),
)

st.sidebar.markdown("---")

# Botón reiniciar filtros
if st.sidebar.button("🔄 Reiniciar filtros"):
    st.rerun()

# ----------------------------------------
# APLICAR FILTROS AL DATAFRAME
# ----------------------------------------
df_filtrado = df[
    (df["REGION"].isin(regiones_elegidas)) &
    (df["SOLD UNITS"] >= rango_uv[0]) &
    (df["SOLD UNITS"] <= rango_uv[1])
].copy()

# ----------------------------------------
# ENCABEZADO PRINCIPAL
# ----------------------------------------
st.title("📊 Dashboard de Ventas por Vendedor")
st.markdown(
    "Explora el rendimiento de los vendedores por región, "
    "analiza métricas clave y filtra la información según tus necesidades."
)
st.markdown("---")

# ====================================================
# SECCIÓN 1 – MÉTRICAS RESUMEN (KPIs)
# ====================================================
st.subheader("🚀 Resumen General")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Vendedores", len(df_filtrado))

with col2:
    total_unidades = df_filtrado["SOLD UNITS"].sum()
    st.metric("Total Unidades Vendidas", f"{total_unidades:,}")

with col3:
    total_ventas = df_filtrado["TOTAL SALES"].sum()
    st.metric("Total Ventas", f"${total_ventas:,.0f}")

with col4:
    prom_ventas = df_filtrado["SALES AVERAGE %"].mean()
    st.metric("Promedio de Ventas", f"{prom_ventas:.2f}%")

st.markdown("---")

# ====================================================
# SECCIÓN 2 – TABLA INTERACTIVA CON FILTRO POR REGIÓN
# ====================================================
with st.container():
    st.subheader("📋 Tabla de Vendedores")

    col_tabla, col_vendedor = st.columns([2, 1])

    with col_tabla:
        region_tabla = st.selectbox(
            "Ver tabla para la región:",
            options=["Todas"] + regiones_disponibles,
            key="selector_tabla",
        )

        if region_tabla == "Todas":
            df_tabla = df_filtrado
        else:
            df_tabla = df_filtrado[df_filtrado["REGION"] == region_tabla]

        columnas_visibles = [
            "REGION", "ID", "NOMBRE COMPLETO", "INCOME",
            "SOLD UNITS", "TOTAL SALES", "SALES AVERAGE %"
        ]

        st.dataframe(
            df_tabla[columnas_visibles].reset_index(drop=True),
            use_container_width=True,
            height=320,
            column_config={
                "TOTAL SALES": st.column_config.NumberColumn("Total Ventas", format="$%d"),
                "SALES AVERAGE %": st.column_config.NumberColumn("Promedio Ventas (%)", format="%.2f%%"),
                "INCOME": st.column_config.NumberColumn("Ingreso", format="$%d"),
            },
        )
        st.caption(f"Mostrando {len(df_tabla)} de {len(df)} vendedores.")

    # ====================================================
    # SECCIÓN 3 – BÚSQUEDA DE VENDEDOR ESPECÍFICO
    # ====================================================
    with col_vendedor:
        st.subheader("🔍 Buscar Vendedor")

        vendedor_buscado = st.selectbox(
            "Selecciona un vendedor:",
            options=["— Seleccionar —"] + sorted(df["NOMBRE COMPLETO"].tolist()),
            key="selector_vendedor",
        )

        if vendedor_buscado != "— Seleccionar —":
            datos_v = df[df["NOMBRE COMPLETO"] == vendedor_buscado].iloc[0]
            st.markdown(f"""
            **Nombre:** {datos_v['NOMBRE COMPLETO']}  
            **ID:** {datos_v['ID']}  
            **Región:** {datos_v['REGION']}  
            **Ingreso:** ${datos_v['INCOME']:,}  
            **Unidades Vendidas:** {datos_v['SOLD UNITS']:,}  
            **Total Ventas:** ${datos_v['TOTAL SALES']:,}  
            **Promedio Ventas:** {datos_v['SALES AVERAGE %']:.2f}%  
            """)

            # Mini radar chart del vendedor vs promedio de su región
            region_v = datos_v["REGION"]
            df_region = df[df["REGION"] == region_v]

            categorias = ["SOLD UNITS", "TOTAL SALES", "SALES AVERAGE %"]
            labels_viz = ["Unid. Vendidas", "Total Ventas", "Prom. Ventas (%)"]

            # Normalizar 0-1 dentro de la región
            vals_vendedor = []
            vals_promedio = []
            for col in categorias:
                c_min, c_max = df_region[col].min(), df_region[col].max()
                rng = c_max - c_min if c_max != c_min else 1
                vals_vendedor.append((datos_v[col] - c_min) / rng)
                vals_promedio.append(0.5)  # promedio normalizado = 0.5

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_vendedor + [vals_vendedor[0]],
                theta=labels_viz + [labels_viz[0]],
                fill='toself',
                name=vendedor_buscado,
                line_color='#667eea',
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_promedio + [vals_promedio[0]],
                theta=labels_viz + [labels_viz[0]],
                fill='toself',
                name=f"Promedio {region_v}",
                line_color='#f97316',
                opacity=0.4,
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                height=280,
                margin=dict(t=20, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# ====================================================
# SECCIÓN 4 – GRÁFICAS DE DESEMPEÑO
# ====================================================
st.subheader("📈 Gráficas de Desempeño")

tab1, tab2, tab3, tab4 = st.tabs([
    "Unidades Vendidas",
    "Total de Ventas",
    "Promedio de Ventas",
    "Comparativa por Región",
])

# Tab 1: Unidades Vendidas
with tab1:
    fig_uv = px.bar(
        df_filtrado.sort_values("SOLD UNITS", ascending=False),
        x="NOMBRE COMPLETO",
        y="SOLD UNITS",
        color="REGION",
        title="Unidades Vendidas por Vendedor",
        labels={"NOMBRE COMPLETO": "Vendedor", "SOLD UNITS": "Unidades Vendidas"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_uv.update_layout(xaxis_tickangle=-45, legend_title="Región", height=450)
    st.plotly_chart(fig_uv, use_container_width=True)

# Tab 2: Total de Ventas
with tab2:
    fig_tv = px.bar(
        df_filtrado.sort_values("TOTAL SALES", ascending=False),
        x="NOMBRE COMPLETO",
        y="TOTAL SALES",
        color="REGION",
        title="Total de Ventas por Vendedor",
        labels={"NOMBRE COMPLETO": "Vendedor", "TOTAL SALES": "Total de Ventas ($)"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_tv.update_layout(xaxis_tickangle=-45, legend_title="Región", height=450)
    st.plotly_chart(fig_tv, use_container_width=True)

# Tab 3: Promedio de Ventas
with tab3:
    fig_pv = px.bar(
        df_filtrado.sort_values("SALES AVERAGE %", ascending=False),
        x="NOMBRE COMPLETO",
        y="SALES AVERAGE %",
        color="REGION",
        title="Promedio de Ventas por Vendedor (%)",
        labels={"NOMBRE COMPLETO": "Vendedor", "SALES AVERAGE %": "Promedio (%)"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_pv.update_layout(xaxis_tickangle=-45, legend_title="Región", height=450)
    st.plotly_chart(fig_pv, use_container_width=True)

# Tab 4: Comparativa por Región
with tab4:
    col_a, col_b = st.columns(2)

    with col_a:
        # Unidades vendidas promedio por región
        resumen_region = df_filtrado.groupby("REGION").agg(
            Vendedores=("ID", "count"),
            Unidades=("SOLD UNITS", "sum"),
            Ventas=("TOTAL SALES", "sum"),
            Promedio=("SALES AVERAGE %", "mean"),
        ).reset_index()

        fig_pie = px.pie(
            resumen_region,
            names="REGION",
            values="Ventas",
            title="Participación en Ventas por Región",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        # Scatter: Unidades vs Ventas por vendedor
        fig_scatter = px.scatter(
            df_filtrado,
            x="SOLD UNITS",
            y="TOTAL SALES",
            color="REGION",
            hover_name="NOMBRE COMPLETO",
            size="SALES AVERAGE %",
            title="Unidades vs Total de Ventas",
            labels={"SOLD UNITS": "Unidades Vendidas", "TOTAL SALES": "Total Ventas ($)"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Tabla de resumen por región
    st.markdown("#### Resumen por Región")
    resumen_region["Ventas"] = resumen_region["Ventas"].apply(lambda x: f"${x:,.0f}")
    resumen_region["Promedio"] = resumen_region["Promedio"].apply(lambda x: f"{x:.2f}%")
    st.dataframe(resumen_region, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Dashboard de Vendedores · Datos: sellers.xlsx · Hecho con Streamlit + Plotly")
