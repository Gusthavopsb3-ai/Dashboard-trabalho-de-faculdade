import copy
import io
import re

import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer

# =========================
# CONFIGURANDO A PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Criando o controle de tema na barra lateral
st.sidebar.markdown("### 🎨 Visualização")

if "tema_claro" not in st.session_state:
    st.session_state.tema_claro = False

def alternar_tema():
    st.session_state.tema_claro = not st.session_state.tema_claro

label_botao = "☀️ Modo Claro" if not st.session_state.tema_claro else "🌙 Modo Escuro"
st.sidebar.button(label_botao, on_click=alternar_tema, use_container_width=True)

tema_claro = st.session_state.tema_claro

# =========================
# PALETA DE CORES
# =========================
if tema_claro:
    bg_color = "#f7f7f2"
    app_background = (
        "linear-gradient(135deg, #f7f7f2 0%, #eef7f4 52%, #f8f1ee 100%)"
    )
    text_color = "#1f2933"
    sidebar_bg = "linear-gradient(180deg, rgba(255,255,255,0.96), rgba(246,248,245,0.92))"
    panel_bg = "#ffffff"
    plot_bg_color = "#fbfbf8"
    panel_border = "#d9ded8"
    input_bg = "#ffffff"
    input_border = "#cbd5cf"
    tag_bg = "#e8f3ef"
    tag_text = "#18352f"
    icon_color = "#18352f"
    caption_color = "#5f6f68"
    accent_color = "#2f7d6d"
    accent_hover = "#256b5e"
    soft_accent = "rgba(47, 125, 109, 0.11)"
    grid_line = "rgba(31, 41, 51, 0.045)"
    panel_shadow = "0 16px 36px rgba(31, 41, 51, 0.10)"

    axis_color = "#1f2933"
    png_bg_color = "#ffffff"
    hover_label_bg = "#ffffff"
    hover_label_text = "#1f2933"

    cursor_style = "default"
    caret_color = "#111827"
else:
    bg_color = "#111214"
    app_background = (
        "linear-gradient(135deg, #111214 0%, #171411 48%, #0f1a17 100%)"
    )
    text_color = "#f5f7fa"
    sidebar_bg = "linear-gradient(180deg, rgba(24,27,33,0.97), rgba(18,23,21,0.94))"
    panel_bg = "#181b21"
    plot_bg_color = "#14171d"
    panel_border = "#303741"
    input_bg = "#1f232b"
    input_border = "#3a424d"
    tag_bg = "#243d38"
    tag_text = "#f5f7fa"
    icon_color = "#f5f7fa"
    caption_color = "#a7b2bd"
    accent_color = "#5fc7b2"
    accent_hover = "#7bd9c6"
    soft_accent = "rgba(95, 199, 178, 0.12)"
    grid_line = "rgba(245, 247, 250, 0.045)"
    panel_shadow = "0 18px 44px rgba(0, 0, 0, 0.28)"

    axis_color = "#f5f7fa"
    png_bg_color = "#181b21"
    hover_label_bg = "#1f232b"
    hover_label_text = "#f5f7fa"

    cursor_style = "auto"
    caret_color = "#ffffff"

# =========================
# CSS GERAL DA APLICAÇÃO
# =========================
style_css = f"""
<style>
:root {{
    --app-bg: {bg_color};
    --text-color: {text_color};
    --panel-bg: {panel_bg};
    --plot-bg: {plot_bg_color};
    --panel-border: {panel_border};
    --input-bg: {input_bg};
    --input-border: {input_border};
    --caption-color: {caption_color};
    --accent-color: {accent_color};
    --accent-hover: {accent_hover};
    --soft-accent: {soft_accent};
}}

#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
[data-testid="stAppDeployButton"] {{display: none !important;}}
[data-testid="stStatusWidget"] {{visibility: hidden !important;}}

[data-testid="stHeader"] {{
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    border: none !important;
}}

[data-testid="collapsedControl"] {{
    background-color: {panel_bg} !important;
    border-right: 1px solid {panel_border} !important;
    border-bottom: 1px solid {panel_border} !important;
    border-top: 1px solid {panel_border} !important;
    border-radius: 0 8px 8px 0 !important;
    top: 12px !important;
    display: flex !important;
    visibility: visible !important;
    box-shadow: 4px 4px 10px rgba(0,0,0,0.15) !important;
}}

.stApp {{
    background-color: {bg_color} !important;
    background-image: {app_background} !important;
    color: {text_color} !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient({grid_line} 1px, transparent 1px),
        linear-gradient(90deg, {grid_line} 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.95), transparent 86%);
}}

.main .block-container {{
    position: relative;
    z-index: 1;
    max-width: 1480px;
    padding-top: 2rem !important;
    padding-bottom: 3rem;
}}

[data-testid="stSidebar"] {{
    position: relative;
    z-index: 2;
    background: {sidebar_bg} !important;
    border-right: 1px solid {panel_border} !important;
    box-shadow: 14px 0 35px rgba(0, 0, 0, 0.10);
}}

[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.4rem;
}}

html, body, .stApp, input, select, textarea, div, span, label, p, h1, h2, h3, h4, h5, h6 {{
    cursor: {cursor_style} !important;
    caret-color: {caret_color} !important;
}}

.js-plotly-plot .plotly .nsewdrag,
.js-plotly-plot .plotly .drag {{
    cursor: {cursor_style} !important;
}}

button, a, [role="button"], [data-baseweb="tab"], .stCheckbox, .stRadio {{
    cursor: pointer !important;
}}

h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{
    color: {text_color} !important;
}}

.dashboard-title {{
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    margin: 0.1rem 0 1.4rem;
    padding: 0.95rem 1.1rem;
    color: {text_color} !important;
    background: linear-gradient(135deg, {soft_accent}, rgba(255,255,255,0.02));
    border: 1px solid {panel_border};
    border-radius: 8px;
    box-shadow: {panel_shadow};
    font-size: clamp(2rem, 4vw, 3.25rem);
    line-height: 1.05;
    letter-spacing: 0;
}}

[data-testid="stCaptionContainer"] {{
    color: {caption_color} !important;
}}

[data-testid="stCaptionContainer"] * {{
    color: {caption_color} !important;
}}

div[data-testid="stTextInput"],
div[data-testid="stSelectbox"],
div[data-testid="stMultiSelect"],
div[data-testid="stRadio"],
div[data-testid="stFileUploader"] {{
    margin-bottom: 0.35rem;
}}

div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
input, select, textarea {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border-color: {input_border} !important;
    border-radius: 8px !important;
}}

div[class*="stMultiSelect"] div[data-baseweb="select"] > div {{
    background-color: {input_bg} !important;
}}

span[data-baseweb="tag"], div[data-baseweb="tag"] {{
    background-color: {tag_bg} !important;
    color: {tag_text} !important;
    border: 1px solid {input_border} !important;
    border-radius: 8px !important;
}}

span[data-baseweb="tag"] span, div[data-baseweb="tag"] span {{
    color: {tag_text} !important;
    background: transparent !important; 
}}

span[data-baseweb="tag"] button, div[data-baseweb="tag"] button,
span[data-baseweb="tag"] svg, div[data-baseweb="tag"] svg {{
    fill: {icon_color} !important;
    color: {icon_color} !important;
    background: transparent !important;
}}

div[data-baseweb="select"] svg {{
    fill: {text_color} !important;
    color: {text_color} !important;
}}

div[role="listbox"],
ul[role="listbox"],
div[role="option"],
li[role="option"] {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
}}

[data-testid="stFileUploader"] section {{
    background: linear-gradient(135deg, {input_bg}, {soft_accent}) !important;
    border: 1px dashed {input_border} !important;
    border-radius: 8px !important;
    color: {text_color} !important;
}}

[data-testid="stFileUploaderFileContainer"] {{
    background-color: {input_bg} !important;
    border-color: {input_border} !important;
    border-radius: 8px !important;
    color: {text_color} !important;
}}

[data-testid="stFileUploader"] section div,
[data-testid="stFileUploaderFileContainer"] span,
[data-testid="stFileUploaderFileContainer"] div,
[data-testid="stFileUploaderFileContainer"] * {{
    color: {text_color} !important;
}}

[data-testid="stPlotlyChart"] {{
    background: {panel_bg} !important;
    border: 1px solid {panel_border} !important;
    border-radius: 8px !important;
    box-shadow: {panel_shadow};
    padding: 0.65rem 0.75rem;
    margin-top: 0.4rem;
    margin-bottom: 1.4rem;
}}

[data-testid="stPlotlyChart"] > div {{
    border-radius: 8px !important;
    overflow: hidden;
}}

hr {{
    border-color: {panel_border} !important;
}}

.plotly-notifier {{
    display: none !important;
    visibility: hidden !important;
}}

.stButton > button {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 1px solid {input_border} !important;
    border-radius: 8px !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}}

.stButton > button:hover {{
    background-color: {soft_accent} !important;
    border-color: {accent_color} !important;
    color: {text_color} !important;
    transform: translateY(-1px);
}}

.stButton > button:focus {{
    box-shadow: 0 0 0 3px {soft_accent} !important;
}}

[data-testid="stDownloadButton"] {{
    position: fixed !important;
    top: 0.65rem !important;
    right: 4.5rem !important;
    z-index: 999999 !important;
    margin: 0 !important;
}}

[data-testid="stDownloadButton"] button {{
    background-color: {accent_color} !important;
    color: #ffffff !important;
    border: 1px solid {accent_color} !important;
    border-radius: 8px !important;
    transition: all 0.22s ease;
    padding: 0.25rem 0.75rem !important;
    min-height: 0 !important;
    height: 2.25rem !important;
    font-size: 0.9rem !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.16);
}}

[data-testid="stDownloadButton"] button:hover {{
    background-color: {accent_hover} !important;
    border-color: {accent_hover} !important;
    color: #ffffff !important;
}}

[data-testid="collapsedControl"] button,
[data-testid="collapsedControl"] svg,
[data-testid="stSidebar"] button[title="Collapse sidebar"] svg {{
    color: {text_color} !important;
    fill: {text_color} !important;
    opacity: 1 !important;
}}

@media (max-width: 768px) {{
    .main .block-container {{
        padding-top: 3.2rem !important;
    }}

    .dashboard-title {{
        width: 100%;
        font-size: 2rem;
        justify-content: center;
    }}

    [data-testid="stDownloadButton"] {{
        right: 3.6rem !important;
    }}
}}
</style>
"""

st.markdown(style_css, unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.markdown('<h1 class="dashboard-title">📊 Dashboard PRO</h1>', unsafe_allow_html=True)

# =========================
# UPLOAD
# =========================
file = st.file_uploader("Carregar Arquivo", type=["csv", "xlsx", "json"])


# =========================
# FUNÇÕES
# =========================
def gerar_cores_unicas(valores):
    n = len(valores)
    if n == 0:
        return {}
    return {v: f"hsl({i * 360 / n},75%,50%)" for i, v in enumerate(valores)}


def quebrar_texto(label, tamanho=15):
    palavras = str(label).split()
    linhas = []
    atual = ""

    for p in palavras:
        if len(atual) + len(p) + 1 <= tamanho:
            atual += (" " if atual else "") + p
        else:
            linhas.append(atual)
            atual = p

    if atual:
        linhas.append(atual)

    return "<br>".join(linhas)


def padronizar_legenda(label):
    texto = str(label).lower().strip()
    texto = texto.replace("r$", "")
    nums = re.findall(r"\d[\d\.]*,?\d*", texto)

    def formatar(valor):
        valor = str(valor)
        valor = valor.replace(".", "")
        if "," in valor:
            valor = valor.split(",")[0]

        if not valor.strip():
            return "0,00"

        valor = int(valor)
        return f"{valor:,.0f}".replace(",", ".") + ",00"

    if "até" in texto or "ate" in texto:
        if nums:
            # Mantém a linha única se for curto
            return f"Até {formatar(nums[0])}"

    if len(nums) >= 2:
        inicio = formatar(nums[0])
        fim = formatar(nums[1])
        # A tag <br> quebra a frase em duas linhas
        return f"De {inicio}<br>a {fim}"

    if len(nums) == 1:
        return formatar(nums[0])

    return str(label)


def ordenar_faixa(valor):
    texto_limpo = str(valor).replace(".", "")
    nums = re.findall(r"\d+", texto_limpo)
    return int(nums[0]) if nums else 0


def exportar_graficos_para_pdf(lista_de_graficos, cor_fundo_png):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    estilos = getSampleStyleSheet()
    elementos_pdf = []

    elementos_pdf.append(
        Paragraph(
            "<b>Relatório de Análise Estatística</b>",
            estilos["Title"],
        )
    )

    elementos_pdf.append(Spacer(1, 20))

    for idx, item in enumerate(lista_de_graficos):
        bloco_grafico = []
        tipo = item["tipo"]

        bloco_grafico.append(
            Paragraph(
                f"<b>Gráfico {tipo}:</b> {item['titulo']}",
                estilos["Heading2"],
            )
        )

        bloco_grafico.append(Spacer(1, 10))

        fig_pdf = copy.deepcopy(item["figura"])
        fig_pdf.update_layout(paper_bgcolor=cor_fundo_png, plot_bgcolor=cor_fundo_png)

        if tipo == "Pizza":
            fig_pdf.update_layout(
                showlegend=True,
                margin=dict(l=40, r=300, t=40, b=40),
                legend=dict(
                    font=dict(size=12),
                    orientation="v",
                    x=1.02,
                    y=0.5,
                    xanchor="left",
                    yanchor="middle",
                ),
            )
        else:
            margem_esq = 180 if tipo == "Barra" else 80
            margem_inf = 150 if tipo in ["Histograma", "Ogiva"] else 60

            fig_pdf.update_layout(
                showlegend=False,
                margin=dict(l=margem_esq, r=40, t=40, b=margem_inf),
            )
            # Mantemos tickangle=0 (reto) aqui também
            fig_pdf.update_xaxes(automargin=True, tickangle=0, dtick=1)
            fig_pdf.update_yaxes(automargin=True)

        if tipo == "Ogiva":
            fig_pdf.update_traces(cliponaxis=False)

        img_bytes = fig_pdf.to_image(
            format="png",
            width=1000,
            height=480,
            scale=2,
            engine="kaleido",
        )

        img_buffer = io.BytesIO(img_bytes)
        img_pdf = Image(img_buffer, width=520, height=250)

        bloco_grafico.append(img_pdf)
        bloco_grafico.append(Spacer(1, 25))

        elementos_pdf.append(KeepTogether(bloco_grafico))

        if idx % 2 == 1 and idx < len(lista_de_graficos) - 1:
            elementos_pdf.append(PageBreak())

    doc.build(elementos_pdf)
    buffer.seek(0)
    return buffer


# =========================
# PROCESSAMENTO
# =========================
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

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.title("⚙️ Filtros")

    colunas_selecionadas = st.sidebar.multiselect(
        "📌 Perguntas",
        colunas,
        default=[colunas[0]],
    )

    if "curso_anterior" not in st.session_state:
        st.session_state.curso_anterior = "Todos"

    filtro_curso = st.sidebar.radio(
        "🎓 Filtrar por curso",
        ["Todos", "Engenharia de Software", "Segurança da Informação"],
    )

    if filtro_curso != st.session_state.curso_anterior:
        keys_para_remover = [
            k for k in st.session_state.keys() if k.startswith("filtro_")
        ]
        for k in keys_para_remover:
            del st.session_state[k]

        if "pdf_pronto" in st.session_state:
            del st.session_state["pdf_pronto"]

        st.session_state.curso_anterior = filtro_curso

    # =========================
    # FILTRO DATAFRAME
    # =========================
    df_filtrado = df.copy()

    if "Curso" in df.columns:
        if filtro_curso == "Engenharia de Software":
            df_filtrado = df_filtrado[
                df_filtrado["Curso"].astype(str).str.contains("Engenharia", na=False)
            ]
        elif filtro_curso == "Segurança da Informação":
            df_filtrado = df_filtrado[
                df_filtrado["Curso"].astype(str).str.contains("Segurança", na=False)
            ]

    # =========================
    # FILTROS RESPOSTAS
    # =========================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧩 Filtrar respostas")

    filtros_respostas = {}

    for coluna in colunas_selecionadas:
        respostas_unicas = df_filtrado[coluna].dropna().astype(str).unique().tolist()
        respostas_unicas.sort()

        respostas_escolhidas = st.sidebar.multiselect(
            "Selecionar respostas — " + coluna,
            respostas_unicas,
            default=respostas_unicas,
            key=f"filtro_{filtro_curso}_{coluna}",
        )

        filtros_respostas[coluna] = respostas_escolhidas

    for coluna, respostas in filtros_respostas.items():
        if respostas:
            df_filtrado = df_filtrado[df_filtrado[coluna].astype(str).isin(respostas)]

    # =========================
    # LISTA PDF E ÁREA DE GRÁFICOS
    # =========================
    graficos_gerados = []

    area_graficos = st.empty()

    with area_graficos.container():
        # =========================
        # GRÁFICOS
        # =========================
        for i, col in enumerate(colunas_selecionadas):
            if i % 2 == 0:
                cols = st.columns(2)

            container = cols[i % 2]

            with container:
                nome_grafico = st.text_input(
                    f"✏️ Nome do gráfico — {col}",
                    value=col,
                    key=f"titulo_{col}",
                )

                st.subheader(nome_grafico)

                c1, c2 = st.columns(2)

                with c1:
                    tipo_grafico = st.selectbox(
                        f"📊 Tipo — {col}",
                        ["Barra", "Pizza", "Histograma", "Ogiva"],
                        key=f"grafico_{col}",
                    )

                with c2:
                    tamanho_grafico = st.selectbox(
                        f"📏 Tamanho — {col}",
                        ["Pequeno", "Médio", "Grande"],
                        index=1,
                        key=f"tamanho_{col}",
                    )

                if tamanho_grafico == "Pequeno":
                    altura = 480
                elif tamanho_grafico == "Médio":
                    altura = 550
                else:
                    altura = 650

                df_temp = df_filtrado.copy()
                df_temp = df_temp[df_temp[col].notna()]

                if df_temp.empty:
                    st.info("Sem registros para os critérios selecionados.")
                    continue

                if "pretensao" in col.lower() or "salari" in col.lower():
                    df_temp["_label"] = df_temp[col].astype(str).apply(padronizar_legenda)
                else:
                    df_temp["_label"] = df_temp[col].astype(str).apply(quebrar_texto)

                dados = df_temp["_label"].value_counts().reset_index()
                dados.columns = ["Resposta", "Quantidade"]
                cores = gerar_cores_unicas(dados["Resposta"].tolist())

                st.caption(f"Filtro aplicado: {filtro_curso}")

                if tipo_grafico == "Pizza":
                    fig = px.pie(
                        dados,
                        names="Resposta",
                        values="Quantidade",
                        color="Resposta",
                        color_discrete_map=cores,
                    )
                    fig.update_traces(
                        textinfo="percent",
                        textposition="inside",
                        textfont_color="#000000",
                    )
                    fig.update_layout(
                        legend_itemclick=False,
                        legend_itemdoubleclick=False,
                        height=altura,
                        dragmode=False,
                        margin=dict(l=20, r=150, t=40, b=40), 
                        legend=dict(
                            orientation="v",
                            x=0.98, 
                            y=0.5,
                            xanchor="left",
                            yanchor="middle",
                            font=dict(size=12, color=axis_color),
                        ),
                    )

                elif tipo_grafico == "Barra":
                    if "satisfação" in col.lower() or "satisfacao" in col.lower():
                        dados_ordenados = dados.sort_values(
                            "Resposta", key=lambda x: x.map(ordenar_faixa)
                        )
                    else:
                        dados_ordenados = dados.sort_values("Quantidade")

                    fig = px.bar(
                        dados_ordenados,
                        x="Quantidade",
                        y="Resposta",
                        orientation="h",
                        text="Quantidade",
                        color="Resposta",
                        color_discrete_map=cores,
                    )
                    fig.update_traces(textfont=dict(color=axis_color, size=12))

                    fig.update_layout(
                        height=altura,
                        dragmode=False,
                        showlegend=False,
                        margin=dict(l=10, r=20, t=40, b=40),
                        yaxis={
                            "categoryorder": "array",
                            "categoryarray": dados_ordenados["Resposta"].tolist(),
                        },
                    )

                elif tipo_grafico == "Histograma":
                    fig = px.histogram(
                        df_temp,
                        x="_label",
                        color="_label",
                        color_discrete_map=cores,
                    )
                    fig.update_traces(
                        texttemplate="%{y}",
                        textposition="outside",
                        textfont=dict(color=axis_color, size=12),
                        hovertemplate="<b>%{x}</b><br>Quantidade: %{y}<extra></extra>",
                    )
                    fig.update_layout(
                        height=altura,
                        dragmode=False,
                        showlegend=False,
                        bargap=0,
                        margin=dict(l=80, r=40, t=40, b=80),
                    )

                elif tipo_grafico == "Ogiva":
                    dados_ogiva = dados.copy()
                    dados_ogiva = dados_ogiva.sort_values(
                        by="Resposta", key=lambda x: x.map(ordenar_faixa)
                    )
                    dados_ogiva["Acumulado"] = dados_ogiva["Quantidade"].cumsum()

                    fig = px.line(dados_ogiva, x="Resposta", y="Acumulado", markers=True)
                    fig.update_xaxes(
                        type="category",
                        tickangle=0,
                        dtick=1,
                        tickmode="array",
                        tickvals=dados_ogiva["Resposta"],
                        ticktext=dados_ogiva["Resposta"],
                    )
                    fig.update_traces(
                        line=dict(color="#888"),
                        marker=dict(
                            size=10,
                            color=[
                                cores.get(r, "#888") for r in dados_ogiva["Resposta"]
                            ],
                        ),
                        customdata=dados_ogiva["Quantidade"],
                        hovertemplate=(
                            "<b>%{x}</b><br>Quantidade: %{customdata}"
                            "<br>Acumulado: %{y}<extra></extra>"
                        ),
                    )
                    fig.update_layout(
                        height=altura,
                        dragmode=False,
                        margin=dict(l=80, r=40, t=40, b=120),
                    )

                # LAYOUT FINAL
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    paper_bgcolor=panel_bg,
                    plot_bgcolor=plot_bg_color,
                    font=dict(color=axis_color),
                    hoverlabel=dict(
                        bgcolor=hover_label_bg,
                        font=dict(color=hover_label_text, size=12),
                    ),
                )
                fig.update_xaxes(
                    tickfont=dict(color=axis_color, size=11),
                    gridcolor="rgba(128,128,128,0.15)",
                    automargin=True,
                )
                fig.update_yaxes(
                    tickfont=dict(color=axis_color, size=11),
                    gridcolor="rgba(128,128,128,0.15)",
                    automargin=True,
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
                            "scale": 2,
                            "setBackground": png_bg_color,
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
                            "toggleSpikelines",
                            "resetScale2d",
                        ],
                    },
                )

                graficos_gerados.append(
                    {
                        "titulo": nome_grafico,
                        "figura": fig,
                        "tipo": tipo_grafico,
                    }
                )

    # =========================
    # EXPORTAR PDF
    # =========================
    if graficos_gerados:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Exportar Resultados")

        if st.sidebar.button("⚙️ Preparar PDF", use_container_width=True):
            with st.spinner("Gerando imagens e montando o PDF... Isso pode levar alguns segundos."):
                st.session_state["pdf_pronto"] = exportar_graficos_para_pdf(
                    graficos_gerados,
                    png_bg_color,
                )

        if "pdf_pronto" in st.session_state:
            st.sidebar.success("✅ PDF pronto! Clique no botão no canto superior direito da tela.")

            st.download_button(
                label="📥 Baixar Relatório PDF",
                data=st.session_state["pdf_pronto"],
                file_name="relatorio_dashboard.pdf",
                mime="application/pdf",
            )

else:
    st.info("👋 Bem-vindo! Por favor, faça o upload de um arquivo para iniciar a análise.")
