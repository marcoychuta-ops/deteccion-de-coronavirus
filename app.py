import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard Bibliométrico",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
}

[data-testid="metric-container"]{
    background-color:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    border:1px solid #EAEAEA;
}

h1{
    color:#0A3D62;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("coronavirus_detection.csv")

df = load_data()

# --------------------------------------------------
# LIMPIEZA
# --------------------------------------------------

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.title("🔎 Filtros")

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year_range = st.sidebar.slider(
    "Year",
    min_year,
    max_year,
    (min_year, max_year)
)

source_filter = st.sidebar.multiselect(
    "Source title",
    sorted(df["Source title"].dropna().unique())
)

document_filter = st.sidebar.multiselect(
    "Document Type",
    sorted(df["Document Type"].dropna().unique())
)

filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

if source_filter:
    filtered_df = filtered_df[
        filtered_df["Source title"].isin(source_filter)
    ]

if document_filter:
    filtered_df = filtered_df[
        filtered_df["Document Type"].isin(document_filter)
    ]


# Obtener autores únicos
autores = (
    filtered_df["Authors"]
    .dropna()
    .str.split(";")
    .explode()
    .str.strip()
    .unique()
)

autor_seleccionado = st.sidebar.selectbox(
    "👨‍🔬 Autor",
    ["Todos"] + sorted(autores)
)

if autor_seleccionado != "Todos":
    filtered_df = filtered_df[
        filtered_df["Authors"]
        .str.contains(
            autor_seleccionado,
            case=False,
            na=False
        )
    ]
# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

st.title("📚 Dashboard Bibliométrico")
st.markdown("### Coronavirus Detection Research")

# --------------------------------------------------
# KPIs
# --------------------------------------------------

# =========================
# KPIs
# =========================

total_publicaciones = len(filtered_df)
total_revistas = filtered_df["Source title"].nunique()
total_citas = filtered_df["Cited by"].sum()
promedio_citas = filtered_df["Cited by"].mean()

st.markdown("""
<style>

.kpi-card{
    background: #111827;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.35);
    text-align:center;
    transition: 0.3s;
}

.kpi-card:hover{
    transform: translateY(-5px);
    border: 1px solid rgba(255,255,255,0.20);
}

.kpi-icon{
    font-size:32px;
    margin-bottom:10px;
}

.kpi-title{
    font-size:16px;
    color:#B8C1CC;
    margin-bottom:10px;
}

.kpi-value{
    font-size:42px;
    font-weight:700;
    color:white;
}

.blue{
    border-left:5px solid #3B82F6;
}

.green{
    border-left:5px solid #10B981;
}

.yellow{
    border-left:5px solid #FACC15;
}

.red{
    border-left:5px solid #EF4444;
}

</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-icon">📄</div>
        <div class="kpi-title">Publicaciones</div>
        <div class="kpi-value">{total_publicaciones}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-icon">📚</div>
        <div class="kpi-title">Revistas</div>
        <div class="kpi-value">{total_revistas}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card yellow">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-title">Promedio Citaciones</div>
        <div class="kpi-value">{promedio_citas:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card red">
        <div class="kpi-icon">📈</div>
        <div class="kpi-title">Total Citaciones</div>
        <div class="kpi-value">{int(total_citas)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
# --------------------------------------------------
# PUBLICACIONES POR AÑO
# --------------------------------------------------

import pandas as pd
import plotly.graph_objects as go

# Publicaciones por año
pub_year = (
    filtered_df.groupby("Year")
    .size()
    .reset_index(name="Publicaciones")
)

# Completar años faltantes
all_years = pd.DataFrame({
    "Year": range(
        int(pub_year["Year"].min()),
        int(pub_year["Year"].max()) + 1
    )
})

pub_year = (
    all_years
    .merge(pub_year, on="Year", how="left")
    .fillna(0)
)

pub_year["Publicaciones"] = pub_year["Publicaciones"].astype(int)

# Figura
fig_year = go.Figure()

# Barras
fig_year.add_trace(
    go.Bar(
        x=pub_year["Year"],
        y=pub_year["Publicaciones"],
        name="Publicaciones",
        opacity=0.75
    )
)

# Línea
fig_year.add_trace(
    go.Scatter(
        x=pub_year["Year"],
        y=pub_year["Publicaciones"],
        mode="lines+markers",
        name="Tendencia",
        line=dict(
            color="#FF4B4B",
            width=5
        ),
        marker=dict(
            size=10,
            color="#FF4B4B",
            line=dict(
                color="white",
                width=2
            )
        )
    )
)

# Diseño
fig_year.update_layout(
    title={
        "text": "📈 Evolución de Publicaciones por Año",
        "x": 0.5,
        "font": {"size": 28}
    },
    height=650,
    xaxis=dict(
        title="Año",
        dtick=1,
        tickangle=-45,
        title_font=dict(size=20),
        tickfont=dict(size=14)
    ),
    yaxis=dict(
        title="Número de Publicaciones",
        title_font=dict(size=20),
        tickfont=dict(size=14)
    ),
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(
        orientation="h",
        y=1.05,
        x=0.5,
        xanchor="center"
    )
)

st.plotly_chart(
    fig_year,
    use_container_width=True
)
# --------------------------------------------------
# TOP REVISTAS
# --------------------------------------------------

col1, col2 = st.columns(2)

top_sources = (
    filtered_df["Source title"]
    .value_counts()
    .head(5)
    .reset_index()
)

top_sources.columns = ["Revista", "Cantidad"]

fig_sources = px.bar(
    top_sources,
    x="Revista",
    y="Cantidad",
    color="Cantidad",
    color_continuous_scale="Viridis",
    title="🏛 Top Revistas"
)

fig_sources.update_traces(width=0.6)

fig_sources.update_layout(
    height=600,
    xaxis_title="Revista",
    yaxis_title="Cantidad",
    xaxis_tickangle=-45
)

col1.plotly_chart(
    fig_sources,
    use_container_width=True
)

# --------------------------------------------------
# TOP AUTORES
# --------------------------------------------------

authors = (
    filtered_df["Authors"]
    .dropna()
    .str.split(";")
    .explode()
    .str.strip()
)

top_authors = (
    authors.value_counts()
    .head(15)
    .reset_index()
)

top_authors.columns = ["Autor", "Publicaciones"]

fig_authors = px.bar(
    top_authors,
    x="Publicaciones",
    y="Autor",
    orientation="h",
    color="Publicaciones",
    color_continuous_scale="Plasma",
    title="👨‍🔬 Top 15 Autores"
)

col2.plotly_chart(
    fig_authors,
    use_container_width=True
)

# --------------------------------------------------
# TOP ARTÍCULOS MÁS CITADOS
# --------------------------------------------------

top_cited = (
    filtered_df
    .sort_values(by="Cited by", ascending=False)
    .head(10)
)

fig_cited = px.bar(
    top_cited,
    x="Cited by",
    y="Title",
    orientation="h",
    color="Cited by",
    color_continuous_scale="Turbo",
    title="🏆 Top 10 Artículos Más Citados"
)

fig_cited.update_yaxes(autorange="reversed")

st.plotly_chart(
    fig_cited,
    use_container_width=True
)


# --------------------------------------------------
# TIPO DE DOCUMENTOS
# --------------------------------------------------



doc_type = (
    filtered_df["Document Type"]
    .value_counts()
    .reset_index()
)

doc_type.columns = ["Tipo", "Cantidad"]

fig_doc = px.pie(
    doc_type,
    names="Tipo",
    values="Cantidad",
    hole=0.55,   # Dona
    title="📑 Distribución por Tipo de Documento"
)

fig_doc.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig_doc.update_layout(
    height=600,
    title=dict(
        x=0.5,
        font=dict(size=28)
    ),
    legend=dict(
        font=dict(size=14)
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(
    fig_doc,
    use_container_width=True
)



# --------------------------------------------------
# TABLA
# --------------------------------------------------

st.subheader("📑 Registro Bibliográfico")

cols = [
    "Title",
    "Author full names",
    "Year",
    "Source title",
    "Cited by",
    "DOI"
]

st.dataframe(
    filtered_df[cols],
    use_container_width=True,
    height=500
)

# --------------------------------------------------
# DESCARGA
# --------------------------------------------------

csv = filtered_df.to_csv(index=False)

st.download_button(
    "⬇ Descargar Datos Filtrados",
    csv,
    "bibliometria_filtrada.csv",
    "text/csv"
)
