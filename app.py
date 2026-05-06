import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(layout="wide")

st.title("📊 Dashboard PRO (Filtros Avançados)")

file = st.file_uploader("Carregar Excel", type=["xlsx"])

# =========================
# 🎨 CORES
# =========================
def gerar_cores_unicas(valores):
    n = len(valores)
    return {v: f"hsl({i*360/n},75%,50%)" for i, v in enumerate(valores)}


# =========================
# 🔥 QUEBRA DE TEXTO
# =========================
def quebrar_texto(label, tamanho=15):
    palavras = str(label).split()
    linhas, atual = [], ""

    for p in palavras:
        if len(atual) + len(p) + 1 <= tamanho:
            atual += (" " if atual else "") + p
        else:
            linhas.append(atual)
            atual = p

    if atual:
        linhas.append(atual)

    return "<br>".join(linhas)


def ordenar_faixa(valor):
    nums = re.findall(r'\d+', str(valor))
    return int(nums[0]) if nums else 0


# =========================
# 📊 APP
# =========================
if file:
    df = pd.read_excel(file)

    ignorar = ["data","hora","date","time","timestamp","carimbo"]
    colunas = [c for c in df.columns if not any(i in c.lower() for i in ignorar)]

    if not colunas:
        st.warning("Nenhuma coluna válida encontrada.")
        st.stop()

    st.sidebar.title("⚙️ Filtros")

    tipo_grafico = st.sidebar.selectbox(
        "📊 Tipo de gráfico",
        ["Barra", "Pizza", "Histograma", "Ogiva"]
    )

    col = st.sidebar.selectbox("📌 Pergunta", colunas)

    nome_grafico = st.sidebar.text_input("✏️ Nome do gráfico", col)

    filtro_curso = st.sidebar.radio(
        "🎓 Filtrar por curso",
        ["Todos", "Engenharia de Software", "Segurança da Informação"]
    )

    # =========================
    # 📏 TAMANHO
    # =========================
    tamanho = st.sidebar.selectbox(
        "📏 Tamanho do gráfico",
        ["Pequeno", "Médio", "Grande"],
        index=1
    )

    if tamanho == "Pequeno":
        altura = 400
    elif tamanho == "Médio":
        altura = 500
    else:
        altura = 600

    # =========================
    # FILTRO POR CURSO
    # =========================
    df_filtrado = df.copy()

    if "Curso" in df.columns:
        if filtro_curso == "Engenharia de Software":
            df_filtrado = df_filtrado[df_filtrado["Curso"].str.contains("Engenharia", na=False)]

        elif filtro_curso == "Segurança da Informação":
            df_filtrado = df_filtrado[df_filtrado["Curso"].str.contains("Segurança", na=False)]

   

    # =========================
    # DADOS (USANDO CÓPIA SEGURA)
    # =========================
    df_temp = df_filtrado.copy()
    df_temp["_label"] = df_temp[col].astype(str).apply(quebrar_texto)

    dados = df_temp["_label"].value_counts().reset_index()
    dados.columns = ["Resposta", "Quantidade"]

    cores = gerar_cores_unicas(dados["Resposta"].tolist())

    # =========================
    # TÍTULO MELHORADO
    # =========================
    st.subheader(nome_grafico)
    st.caption(f"Filtro aplicado: {filtro_curso}")

    # =========================
    # GRÁFICOS
    # =========================
    if tipo_grafico == "Pizza":
        fig = px.pie(
            dados,
            names="Resposta",
            values="Quantidade",
            color="Resposta",
            color_discrete_map=cores
        )

        fig.update_traces(textinfo="percent", textposition="inside")

        fig.update_layout(
            height=altura,
            margin=dict(l=20, r=180, t=20, b=20),
            legend=dict(
                orientation="v",
                x=0.95,
                y=1,
                xanchor="left",
                yanchor="top",
                font=dict(size=11)
            )
        )

    elif tipo_grafico == "Barra":
        dados_ordenados = dados.sort_values("Quantidade")

        media_tamanho = dados["Resposta"].astype(str).apply(len).mean()
        qtd_itens = len(dados)

        usar_horizontal = (media_tamanho > 12) or (qtd_itens > 6)

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

        if tamanho == "Pequeno":
            fig.update_layout(
                height=altura,
                margin=dict(l=150, r=20, t=20, b=20),
                yaxis=dict(tickfont=dict(size=10))
            )
        else:
            fig.update_layout(
                height=altura,
                margin=dict(l=100, r=20, t=20, b=20),
                yaxis=dict(tickfont=dict(size=12))
            )

        fig.update_layout(showlegend=False)

    elif tipo_grafico == "Histograma":
        fig = px.histogram(df_temp, x="_label")
        fig.update_layout(height=altura)

    elif tipo_grafico == "Ogiva":
        dados_ogiva = dados.copy()

        dados_ogiva = dados_ogiva.sort_values(
            by="Resposta",
            key=lambda x: x.map(ordenar_faixa)
        )

        dados_ogiva["Acumulado"] = dados_ogiva["Quantidade"].cumsum()

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
                color=[cores[r] for r in dados_ogiva["Resposta"]]
            )
        )

        fig.update_layout(height=altura)

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
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d","pan2d","select2d","lasso2d",
                "zoomIn2d","zoomOut2d","autoScale2d",
                "hoverClosestCartesian","hoverCompareCartesian","toggleSpikelines"
            ]
        }
    )
