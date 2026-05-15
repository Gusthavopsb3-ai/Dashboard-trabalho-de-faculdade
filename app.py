import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

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

/* REMOVE BOTÃO IMPLANTAR */
[data-testid="stToolbar"] {
    right: 10px;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stStatusWidget"] {
    visibility: hidden;
}

button[kind="header"] {
    display: none;
}

</style>
"""

st.markdown(hide_streamlit, unsafe_allow_html=True)

st.title("📊 Dashboard PRO (Filtros Avançados)")

file = st.file_uploader(
    "Carregar Arquivo"
)

def gerar_cores_unicas(valores):

    n = len(valores)

    return {
        v: f"hsl({i*360/n},75%,50%)"
        for i, v in enumerate(valores)
    }

def quebrar_texto(label, tamanho=15):

    palavras = str(label).split()

    linhas = []

    atual = ""

    for p in palavras:

        if len(atual) + len(p) + 1 <= tamanho:
            atual += ((" " if atual else "") + p)

        else:
            linhas.append(atual)
            atual = p

    if atual:
        linhas.append(atual)

    return "<br>".join(linhas)

def ordenar_faixa(valor):

    nums = re.findall(
        r'\d+',
        str(valor)
    )

    return int(nums[0]) if nums else 0

if file:

    nome_arquivo = file.name.lower()

    if nome_arquivo.endswith(".xlsx"):
        df = pd.read_excel(file)

    elif nome_arquivo.endswith(".csv"):
        df = pd.read_csv(file)

    elif nome_arquivo.endswith(".json"):
        df = pd.read_json(file)

    else:
        st.error("Formato não suportado.")
        st.stop()

    df = df.iloc[:, 1:]

    colunas = df.columns.tolist()

    if not colunas:
        st.warning("Nenhuma coluna válida encontrada.")
        st.stop()

    st.sidebar.title("⚙️ Filtros")

    colunas_selecionadas = st.sidebar.multiselect(
        "📌 Perguntas",
        colunas,
        default=[colunas[0]]
    )

    filtro_curso = st.sidebar.radio(
        "🎓 Filtrar por curso",
        [
            "Todos",
            "Engenharia de Software",
            "Segurança da Informação"
        ]
    )

    df_filtrado = df.copy()

    if "Curso" in df.columns:

        if filtro_curso == "Engenharia de Software":

            df_filtrado = df_filtrado[
                df_filtrado["Curso"]
                .astype(str)
                .str.contains("Engenharia", na=False)
            ]

        elif filtro_curso == "Segurança da Informação":

            df_filtrado = df_filtrado[
                df_filtrado["Curso"]
                .astype(str)
                .str.contains("Segurança", na=False)
            ]

    for col in colunas_selecionadas:

        nome_grafico = st.text_input(
            f"✏️ Nome do gráfico — {col}",
            value=col,
            key=f"titulo_{col}"
        )

        st.subheader(nome_grafico)

        c1, c2 = st.columns(2)

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

        if tamanho_grafico == "Pequeno":
            altura = 500

        elif tamanho_grafico == "Médio":
            altura = 550

        else:
            altura = 600

        df_temp = df_filtrado.copy()

        df_temp = df_temp[df_temp[col].notna()]

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

        cores = gerar_cores_unicas(
            dados["Resposta"].tolist()
        )

        st.caption(f"Filtro aplicado: {filtro_curso}")

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
                legend_itemclick=False,
                legend_itemdoubleclick=False,

                height=altura,
                dragmode=False,

                margin=dict(
                    l=20,
                    r=600,
                    t=40,
                    b=40
                ),

                legend=dict(
                    orientation="v",
                    x=1.05,
                    y=1,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=12)
                )
            )

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
                showlegend=False,

                margin=dict(
                    l=250,
                    r=40,
                    t=40,
                    b=40
                )
            )

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
                showlegend=False,
                bargap=0,

                margin=dict(
                    l=80,
                    r=40,
                    t=40,
                    b=80
                )
            )

            fig.update_traces(
                texttemplate="%{y}",
                textposition="outside",

                hovertemplate=
                "<b>%{x}</b><br>" +
                "Quantidade: %{y}<extra></extra>"
            )

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
                line=dict(color="#888"),

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
                dragmode=False,

                margin=dict(
                    l=80,
                    r=40,
                    t=40,
                    b=80
                )
            )

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
                    "scale": 1
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
