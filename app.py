import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
st.set_page_config(
    page_title="Inclusão em Dados - SP",
    page_icon="📊",
    layout="wide",
)

# ------------------------------------------------------------
# Carregar os dados (a base já tratada no Colab)
# ------------------------------------------------------------
@st.cache_data
def carregar_dados():
    df = pd.read_csv("base_dashboard.csv", sep=";")
    return df

df = carregar_dados()

# ------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------
st.title("Painel de inclusão escolar — estado de São Paulo")
st.caption(
    "Distribuição de profissionais de apoio nas escolas da educação básica, "
    "com base nos microdados do Censo Escolar 2025 (INEP)."
)

# ------------------------------------------------------------
# Filtro na barra lateral
# ------------------------------------------------------------
st.sidebar.header("Filtros")
niveis = st.sidebar.multiselect(
    "Nível de déficit",
    options=df["NIVEL"].unique(),
    default=list(df["NIVEL"].unique()),
)
df_filtrado = df[df["NIVEL"].isin(niveis)]

# ------------------------------------------------------------
# Indicadores (KPIs) no topo
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Municípios analisados", f"{df_filtrado.shape[0]}")
col2.metric("Total de escolas", f"{int(df_filtrado['QT_ESCOLAS'].sum()):,}".replace(",", "."))
col3.metric("Profissionais de apoio", f"{int(df_filtrado['QT_PROF_APOIO'].sum()):,}".replace(",", "."))
deficit_alto = df_filtrado[df_filtrado["NIVEL"] == "Déficit alto"].shape[0]
col4.metric("Municípios em déficit alto", f"{deficit_alto}")

st.divider()

# ------------------------------------------------------------
# Gráficos
# ------------------------------------------------------------
col_a, col_b = st.columns(2)

# Quantos municípios em cada nível de déficit
with col_a:
    st.subheader("Municípios por nível de déficit")
    contagem = df_filtrado["NIVEL"].value_counts().reset_index()
    contagem.columns = ["Nível", "Quantidade"]
    cores = {"Déficit alto": "#E24B4A", "Déficit médio": "#EF9F27", "Déficit baixo": "#1D9E75"}
    fig1 = px.bar(
        contagem, x="Nível", y="Quantidade", color="Nível",
        color_discrete_map=cores, text="Quantidade",
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

# Média de profissionais por escola em cada nível
with col_b:
    st.subheader("Média de profissionais por escola")
    media = df_filtrado.groupby("NIVEL")["PROF_POR_ESCOLA"].mean().round(2).reset_index()
    fig2 = px.bar(
        media, x="NIVEL", y="PROF_POR_ESCOLA", color="NIVEL",
        color_discrete_map=cores, text="PROF_POR_ESCOLA",
        labels={"PROF_POR_ESCOLA": "Profissionais por escola", "NIVEL": "Nível"},
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# Tabela: municípios com maior déficit
# ------------------------------------------------------------
st.subheader("Municípios com maior déficit (menos profissionais por escola)")
tabela = df_filtrado.sort_values("PROF_POR_ESCOLA")[
    ["NO_MUNICIPIO", "QT_ESCOLAS", "QT_PROF_APOIO", "PROF_POR_ESCOLA", "NIVEL"]
].head(20)
tabela.columns = ["Município", "Escolas", "Prof. de apoio", "Prof. por escola", "Nível"]
st.dataframe(tabela, use_container_width=True, hide_index=True)

st.caption("Fonte: elaborado pela autora com base nos microdados do Censo Escolar 2025 (INEP).")
