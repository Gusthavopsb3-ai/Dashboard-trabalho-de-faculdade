import streamlit as st
import pandas as pd
import plotly.express as px
import re

# =========================
# CONFIG
# =========================
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESCONDER ELEMENTOS
# =========================
hide_streamlit = """
<style>

/* MENU VISÍVEL */
#MainMenu {
    visibility: visible;
}

footer {
    visibility: hidden;
}

header {
    background: transparent;
}

</style>
"""

st.markdown(hide_streamlit, unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.title("📊 Dashboard PRO (Filtros Avançados)")

# =========================
# UPLOAD
# =========================
file = st.file_uploader(
    "Carregar Excel",
    type=["xlsx"]
)

# =========================
# CORES
# =========================
def gerar_cores_unicas(valores):

    n = len(valores)

    return {
        v: f"hsl({i*360/n},75%,50%)"
        for i, v in enumerate(valores)
    }

# =========================
# QUEBRA TEXTO
# =========================
def quebrar_texto(label, tamanho=15):

    palavras = str(label).split()

    linhas = []

    atual = ""

    for p in palavras:

        if len(atual) + len(p) + 1 <= tamanho:

            atual += (
                (" " if atual else "") + p
            )

        else:

            linhas.append(atual)

            atual = p

    if atual:

        linhas.append(atual)

    return "<br>".join(linhas)

# =========================
# ORDENAR FAIXAS
# =========================
def ordenar_faixa(valor):

    nums = re.findall(
        r'\d+',
        str(valor)
    )

    return int(nums[0]) if nums else 0

# =========================
# APP
# =========================
if file:

    df = pd.read_excel(file)

    # =========================
    # IGNORAR DATAS
    # =========================
    ignorar = [
        "data",
        "hora",
        "date",
        "time",
        "timestamp",
        "carimbo"
    ]

    colunas = [

        c for c in df.columns

        if not any(
            i in c.lower()
            for i in ignorar
        )
    ]

    if not colunas:

        st.warning(
            "Nenhuma coluna válida encontrada."
        )

        st.stop()

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.title("⚙️ Filtros")

    # =========================
    # PERGUNTAS
    # =========================
    colunas_selecionadas = st.sidebar.multiselect(

        "📌 Perguntas",

        colunas,

        default=[colunas[0]]
    )

    # =========================
    # FILTRO CURSO
    # =========================
    filtro_curso = st.sidebar.radio(

        "🎓 Filtrar por curso",

        [
            "Todos",
            "Engenharia de Software",
            "Segurança da Informação"
        ]
    )

    # =========================
    # FILTRAR DF
    # =========================
    df_filtrado = df.copy()

    if "Curso" in df.columns:

        if filtro_curso == "Engenharia de Software":

            df_filtrado = df_filtrado[

                df_filtrado["Curso"]
                .astype(str)
                .str.contains(
                    "Engenharia",
                    na=False
                )
            ]

        elif filtro_curso == "Segurança da Informação":

            df_filtrado = df_filtrado[

                df_filtrado["Curso"]
                .astype(str)
                .str.contains(
                    "Segurança",
                    na=False
                )
            ]

    # =========================
    # LOOP DOS GRÁFICOS
    # =========================
    for col in colunas_selecionadas:

        # =========================
        # EDITAR TÍTULO
        # =========================
        nome_grafico = st.text_input(
            f"✏️ Nome do gráfico — {col}",
            value=col,
            key=f"titulo_{col}"
        )

        # =========================
        # TÍTULO
        # =========================
        st.subheader(nome_grafico)

        # =========================
        # CONFIGURAÇÕES
        # =========================
        c1, c2 = st.columns(2)

        # =========================
        # TIPO
        # =========================
        with c1:

            tipo_grafico = st.selectbox(

                f"📊 Tipo — {col}",

                [
                    "Barra",
                    "Pizza",
                    "Histograma",
                    "Ogiva"
                ],

                key=f"grafico_{col}"
            )

        # =========================
        # TAMANHO
        # =========================
        with c2:

            tamanho_grafico = st.selectbox(

                f"📏 Tamanho — {col}",

                [
                    "Pequeno",
                    "Médio",
                    "Grande"
                ],

                index=1,

                key=f"tamanho_{col}"
            )

        # =========================
        # ALTURA
        # =========================
        if tamanho_grafico == "Pequeno":

            altura = 400

        elif tamanho_grafico == "Médio":

            altura = 500

        else:

            altura = 600

        # =========================
        # DADOS
        # =========================
        df_temp = df_filtrado.copy()

        df_temp = df_temp[
            df_temp[col].notna()
        ]

        df_temp["_label"] = (

            df_temp[col]
            .astype(str)
            .apply(quebrar_texto)
        )

        dados = (

            df_temp["_label"]
            .value_counts()
            .reset_index()
        )

        dados.columns = [
            "Resposta",
            "Quantidade"
        ]

        # =========================
        # CORES
        # =========================
        cores = gerar_cores_unicas(
            dados["Resposta"].tolist()
        )

        st.caption(
            f"Filtro aplicado: {filtro_curso}"
        )

        # =========================
        # PIZZA
        # =========================
        if tipo_grafico == "Pizza":

            fig = px.pie(

                dados,

                names="Resposta",

                values="Quantidade",

                color="Resposta",

                color_discrete_map=cores
            )

            fig.update_traces(

                textinfo="percent",

                textposition="inside"
            )

            fig.update_layout(

                height=altura,

                dragmode=False,

                margin=dict(
                    l=20,
                    r=180,
                    t=20,
                    b=20
                ),

                legend=dict(

                    orientation="v",

                    x=0.95,

                    y=1,

                    xanchor="left",

                    yanchor="top",

                    font=dict(size=11)
                )
            )

        # =========================
        # BARRA
        # =========================
        elif tipo_grafico == "Barra":

            dados_ordenados = dados.sort_values(
                "Quantidade"
            )

            media_tamanho = (

                dados["Resposta"]
                .astype(str)
                .apply(len)
                .mean()
            )

            qtd_itens = len(dados)

            usar_horizontal = (
                media_tamanho > 12
                or qtd_itens > 6
            )

            if usar_horizontal:

                fig = px.bar(

                    dados_ordenados,

                    x="Quantidade",

                    y="Resposta",

                    orientation="h",

                    text="Quantidade",

                    color="Resposta",

                    color_discrete_map=cores
                )

            else:

                fig = px.bar(

                    dados_ordenados,

                    x="Resposta",

                    y="Quantidade",

                    text="Quantidade",

                    color="Resposta",

                    color_discrete_map=cores
                )

            fig.update_layout(

                height=altura,

                dragmode=False,

                showlegend=False
            )

        # =========================
        # HISTOGRAMA
        # =========================
        elif tipo_grafico == "Histograma":
        
            fig = px.histogram(

                df_temp,

                x="_label",

                color="_label",

                color_discrete_map=cores
            )

            fig.update_layout(

                height=altura,

                dragmode=False,

                showlegend=False
            )

        # =========================
        # OGIVA
        # =========================
        elif tipo_grafico == "Ogiva":

            dados_ogiva = dados.copy()

            dados_ogiva = dados_ogiva.sort_values(

                by="Resposta",

                key=lambda x: x.map(
                    ordenar_faixa
                )
            )

            dados_ogiva["Acumulado"] = (

                dados_ogiva["Quantidade"]
                .cumsum()
            )

            fig = px.line(

                dados_ogiva,

                x="Resposta",

                y="Acumulado",

                markers=True
            )

            fig.update_traces(

    line=dict(
        color="#888"
    ),

    marker=dict(

        size=10,

        color=[
            cores[r]
            for r in dados_ogiva["Resposta"]
        ]
    ),

    customdata=dados_ogiva["Quantidade"],

    hovertemplate=
    "<b>%{x}</b><br>" +
    "Quantidade: %{customdata}<br>" +
    "Acumulado: %{y}<extra></extra>"
)

            fig.update_layout(

                height=altura,

                dragmode=False
            )

        # =========================
        # FINAL
        # =========================
        fig.update_layout(

            xaxis_title=None,

            yaxis_title=None
        )

        st.plotly_chart(

            fig,

            use_container_width=True,

            config={

                "scrollZoom": False,

                "doubleClick": False,

                "displaylogo": False,

                "toImageButtonOptions": {

                    "format": "png",

                    "filename": nome_grafico,

                    "height": altura,

                    "width": 1200,

                    "scale": 2
                },

                "modeBarButtonsToRemove": [

                    "zoom2d",
                    "pan2d",
                    "select2d",
                    "lasso2d",

                    "zoomIn2d",
                    "zoomOut2d",
                    "autoScale2d",

                    "hoverClosestCartesian",
                    "hoverCompareCartesian",
                    "toggleSpikelines"
                ]
            }
        )

        st.divider()
