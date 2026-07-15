"""
Dashboard - Detecção de Risco e Inadimplência em E-commerce
"""

import streamlit as st
import pandas as pd
import plotly.express as px


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Detecção de Risco - E-commerce",
    page_icon="🛡️",
    layout="wide"
)

# PALETA E TEMA VISUAL

COR_PRIMARIA = "#1e3a5f"     # azul petróleo (barras principais)
COR_ACENTO = "#e63946"       # vermelho suave (alertas / não concluídas)
COR_SECUNDARIA = "#457b9d"   # azul médio (segunda série)
COR_MUTED = "#a8dadc"        # azul claro (apoio)
COR_TEXTO = "#111827"
COR_TEXTO_SUAVE = "#6b7280"
COR_GRID = "#eef0f2"

st.markdown(
    f"""
    <style>
        .stApp {{ background-color: #fafbfc; }}

        h1, h2, h3 {{ color: {COR_TEXTO}; font-weight: 700; }}
        p, .stMarkdown, .stCaption {{ color: {COR_TEXTO_SUAVE}; font-size: 16px; }}

        .kpi-card {{
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 8px;
        }}
        .kpi-label {{
            font-size: 15px;
            color: {COR_TEXTO_SUAVE};
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            font-size: 34px;
            color: {COR_TEXTO};
            font-weight: 700;
        }}

        .insight-box {{
            border-radius: 10px;
            padding: 16px 20px;
            font-size: 16px;
            line-height: 1.5;
            margin-top: 4px;
            margin-bottom: 8px;
        }}
        .insight-confirmado {{ background-color: #ecfdf5; border-left: 4px solid #10b981; }}
        .insight-descartado {{ background-color: #fffbeb; border-left: 4px solid #f59e0b; }}
        .insight-neutro {{ background-color: #eff6ff; border-left: 4px solid #3b82f6; }}

        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: {COR_TEXTO};
            margin-bottom: 8px;
        }}

        div[data-testid="stMetric"] {{
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        div[data-testid="stMetricValue"] {{ font-size: 30px; }}
        div[data-testid="stMetricLabel"] {{ font-size: 15px; }}

        table {{ font-size: 15px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(label, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(texto, tipo="neutro"):
    classe = {
        "confirmado": "insight-confirmado",
        "descartado": "insight-descartado",
        "neutro": "insight-neutro",
    }.get(tipo, "insight-neutro")
    st.markdown(f'<div class="insight-box {classe}">📌 {texto}</div>', unsafe_allow_html=True)


def style_fig(fig, show_legend=True):
    """Aplica um visual limpo e consistente a qualquer gráfico Plotly."""
    # Remove o título nativo do Plotly Express de forma segura (title="" em vez de
    # None evita o bug de renderização que mostra "undefined" dentro do gráfico)
    fig.update_layout(title_text="")

    layout_kwargs = dict(
        template="plotly_white",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color=COR_TEXTO_SUAVE),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=show_legend,
    )
    if show_legend:
        layout_kwargs["legend"] = dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""
        )
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e5e7eb", tickfont=dict(size=13))
    fig.update_yaxes(showgrid=True, gridcolor=COR_GRID, zeroline=False, tickfont=dict(size=13))
    return fig


def chart_title(texto):
    st.markdown(f'<div class="chart-title">{texto}</div>', unsafe_allow_html=True)


# CARREGAMENTO DOS DADOS
@st.cache_data
def load_data():
    df_orders = pd.read_csv("orders_modeling.csv")
    df_clients = pd.read_csv("features_modeling.csv")
    return df_orders, df_clients

try:
    df_orders, df_clients = load_data()
except FileNotFoundError:
    st.error(
        "Arquivos 'orders_modeling.csv' e/ou 'features_modeling.csv' não encontrados. "
        "Rode o pipeline (eda_and_etl2.py) primeiro e coloque os CSVs na mesma pasta deste app."
    )
    st.stop()


# FEATURE ENGINEERING - faixas replicadas do Power BI, agora em Python
def faixa_etaria(age):
    if age <= 25:
        return "1. 18-25"
    elif age <= 35:
        return "2. 26-35"
    elif age <= 45:
        return "3. 36-45"
    elif age <= 60:
        return "4. 46-60"
    else:
        return "5. 60+"


def faixa_clv(valor):
    if valor <= 100:
        return "1. Até R$100"
    elif valor <= 300:
        return "2. R$100-300"
    elif valor <= 600:
        return "3. R$300-600"
    elif valor <= 1000:
        return "4. R$600-1000"
    else:
        return "5. Acima de R$1000"


df_clients["Faixa_Etaria"] = df_clients["age"].apply(faixa_etaria)
df_clients["Faixa_CLV"] = df_clients["customer_lifetime_value"].apply(faixa_clv)


# CABEÇALHO (comum às duas abas)
st.title("🛡️ Detecção de Risco e Inadimplência em E-commerce")
st.markdown(
    "Pipeline de dados + análise de segmentação de risco para identificar padrões "
    "comportamentais de maus pagadores (`is_bad_payer`), cruzando turno, tempo de conta, "
    "perfil demográfico, geografia e valor do cliente."
)
st.caption("Fonte: bigquery-public-data.thelook_ecommerce (dataset público, dados sintéticos)")

st.write("")


# KPIs GERAIS (comuns às duas abas) - estilo card
total_pedidos = len(df_orders)
total_clientes = len(df_clients)
receita_total = df_orders["total_order_value"].sum()
taxa_inadimplencia_geral = df_clients["is_bad_payer"].mean()
ordens_nao_concluidas = df_orders[
    (df_orders["is_cancelled"] == 1) | (df_orders["is_returned"] == 1)
].shape[0]
taxa_conversao = 1 - (ordens_nao_concluidas / total_pedidos)

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total de Pedidos", f"{total_pedidos:,.0f}".replace(",", "."))
with col2:
    kpi_card("Clientes Únicos", f"{total_clientes:,.0f}".replace(",", "."))
with col3:
    kpi_card("Receita Total", f"R$ {receita_total / 1e6:.2f} Mi")
with col4:
    kpi_card("Taxa de Inadimplência Geral", f"{taxa_inadimplencia_geral:.2%}")

st.write("")


# ABAS: VISÃO EXECUTIVA / PERFIL DE RISCO
tab_executiva, tab_risco = st.tabs(["📊  Visão Executiva", "🔍  Perfil de Risco"])


# ABA 1 - VISÃO EXECUTIVA
with tab_executiva:

    st.subheader("Turno: Noite/Madrugada x Manhã/Tarde")
    st.caption(
        "Hipótese inicial: o turno noite/madrugada concentraria mais risco. "
        "Testamos comparando o volume de detratores entre os dois turnos."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        chart_title("Detratores por Turno")
        detratores_turno = (
            df_orders[df_orders["is_bad_payer"] == 1]
            .groupby("turno_pedido")
            .size()
            .reset_index(name="detratores")
        )
        fig_turno = px.bar(
            detratores_turno,
            x="detratores",
            y="turno_pedido",
            orientation="h",
            text="detratores",
            color_discrete_sequence=[COR_PRIMARIA],
        )
        fig_turno.update_traces(textposition="outside", textfont=dict(size=14))
        fig_turno.update_layout(yaxis_title="", xaxis_title="")
        st.plotly_chart(style_fig(fig_turno, show_legend=False), use_container_width=True)

    with col_b:
        chart_title("Taxa de Inadimplência por Hora")
        taxa_por_hora = (
            df_orders.groupby("order_hour_formatted")
            .agg(taxa=("is_bad_payer", "mean"), hora=("order_hour", "first"))
            .sort_values("hora")
            .reset_index()
        )
        fig_hora = px.line(
            taxa_por_hora,
            x="order_hour_formatted",
            y="taxa",
            markers=True,
            color_discrete_sequence=[COR_PRIMARIA],
        )
        fig_hora.update_traces(line=dict(width=2), marker=dict(size=5))
        fig_hora.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="")
        st.plotly_chart(style_fig(fig_hora, show_legend=False), use_container_width=True)

    if len(detratores_turno) >= 2:
        diff_pct = abs(
            detratores_turno["detratores"].iloc[0] - detratores_turno["detratores"].iloc[1]
        ) / detratores_turno["detratores"].sum()
        insight_box(
            f"<b>Conclusão:</b> a diferença entre turnos é de apenas {diff_pct:.1%} — "
            "insuficiente para justificar priorizar um turno sobre o outro. A hipótese "
            "inicial não se confirmou, o que também é um resultado válido de análise.",
            tipo="descartado",
        )

    st.write("")
    st.subheader("Conversão de Pedidos")

    col_e, col_f = st.columns([1, 1.4])

    with col_e:
        chart_title("Total de Ordens x Ordens Não Concluídas")
        df_pizza = pd.DataFrame({
            "status": ["Concluídas", "Não Concluídas"],
            "qtd": [total_pedidos - ordens_nao_concluidas, ordens_nao_concluidas],
        })
        fig_pizza = px.pie(
            df_pizza,
            names="status",
            values="qtd",
            color_discrete_sequence=[COR_PRIMARIA, COR_ACENTO],
            hole=0.55,
        )
        fig_pizza.update_traces(textinfo="percent+label")
        st.plotly_chart(style_fig(fig_pizza, show_legend=False), use_container_width=True)

    with col_f:
        st.write("")
        kpi_card("Taxa de Conversão", f"{taxa_conversao:.2%}")
        st.write("")
        kpi_card(
            "Ordens Não Concluídas (canceladas ou devolvidas)",
            f"{ordens_nao_concluidas:,.0f}".replace(",", "."),
        )
        st.write("")
        insight_box(
            "Sinal relevante para separar clientes legítimos de possíveis "
            "detratores — vale acompanhar junto com a taxa de inadimplência geral.",
            tipo="neutro",
        )

# ABA 2 - PERFIL DE RISCO
with tab_risco:

    st.subheader("Tempo de Conta")
    st.caption("Contas recém-criadas concentram mais risco de inadimplência?")

    taxa_tempo_conta = (
        df_orders.groupby("faixa_tempo_conta")["is_bad_payer"]
        .mean()
        .reset_index()
        .sort_values("faixa_tempo_conta")
    )

    chart_title("Taxa de Inadimplência por Tempo de Conta")
    fig_tempo = px.bar(
        taxa_tempo_conta,
        x="faixa_tempo_conta",
        y="is_bad_payer",
        text=taxa_tempo_conta["is_bad_payer"].apply(lambda x: f"{x:.1%}"),
        color_discrete_sequence=[COR_PRIMARIA],
    )
    fig_tempo.update_traces(textposition="outside", textfont=dict(size=14))
    fig_tempo.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="")
    st.plotly_chart(style_fig(fig_tempo, show_legend=False), use_container_width=True)

    insight_box(
        "<b>Conclusão:</b> a taxa de inadimplência cai de forma consistente conforme a "
        "conta 'amadurece' — contas com menos de 30 dias têm taxa visivelmente mais alta "
        "que contas com mais de um ano. Padrão compatível com o comportamento clássico de "
        "risco em contas recém-criadas.",
        tipo="confirmado",
    )

    st.write("")
    st.subheader("Perfil Demográfico")
    st.caption("Idade e gênero explicam parte do risco?")

    taxa_demografico = (
        df_clients.groupby(["Faixa_Etaria", "gender"])["is_bad_payer"]
        .mean()
        .reset_index()
        .sort_values("Faixa_Etaria")
    )

    chart_title("Taxa de Inadimplência por Faixa Etária e Gênero")
    fig_demo = px.bar(
        taxa_demografico,
        x="is_bad_payer",
        y="Faixa_Etaria",
        color="gender",
        orientation="h",
        barmode="group",
        color_discrete_sequence=[COR_PRIMARIA, COR_SECUNDARIA],
    )
    fig_demo.update_layout(xaxis_tickformat=".0%", xaxis_title="", yaxis_title="", legend_title="")
    st.plotly_chart(style_fig(fig_demo), use_container_width=True)

    insight_box(
        "<b>Conclusão:</b> nenhum padrão relevante identificado — variação de menos de "
        "1,5 ponto percentual entre faixas etárias. Uma leve elevação na faixa 60+ foi "
        "investigada e <b>descartada</b> como sinal de risco: ao cruzar com tempo de conta, "
        "a elevação vinha de contas antigas, não de contas recém-criadas — o que invalida "
        "a hipótese de fraude por conta falsa.",
        tipo="descartado",
    )

    st.write("")
    st.subheader("Geografia")
    st.caption("Existe concentração de risco por estado?")

    amostra_minima = st.slider(
        "Amostra mínima de clientes por estado (evita ruído estatístico)",
        min_value=0, max_value=500, value=200, step=50
    )

    taxa_estado = (
        df_clients.groupby("state")
        .agg(qtd_clientes=("user_id", "count"), taxa=("is_bad_payer", "mean"))
        .reset_index()
        .sort_values("taxa", ascending=False)
    )
    taxa_estado_filtrado = taxa_estado[taxa_estado["qtd_clientes"] >= amostra_minima]

    col_c, col_d = st.columns([2, 1])

    with col_c:
        chart_title(f"Taxa de Inadimplência por Estado (amostra ≥ {amostra_minima} clientes)")
        fig_estado = px.bar(
            taxa_estado_filtrado,
            x="state",
            y="taxa",
            color_discrete_sequence=[COR_PRIMARIA],
        )
        fig_estado.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="")
        st.plotly_chart(style_fig(fig_estado, show_legend=False), use_container_width=True)

    with col_d:
        chart_title("Tabela completa (todos os estados)")
        tabela_exibir = taxa_estado.copy()
        tabela_exibir["taxa"] = tabela_exibir["taxa"].apply(lambda x: f"{x:.2%}")
        st.dataframe(tabela_exibir, use_container_width=True, height=380)

    insight_box(
        "<b>Conclusão:</b> estados com percentuais extremos (ex: West Virginia, Nebraska) "
        "têm amostras muito pequenas (&lt; 40 clientes) para sustentar conclusão. Entre os "
        "estados com volume relevante, a variação é moderada, sem concentração geográfica "
        "forte de risco.",
        tipo="descartado",
    )

    st.write("")
    st.subheader("Valor do Cliente (CLV)")
    st.caption("Clientes de maior valor tendem a ser mais confiáveis?")

    taxa_clv = (
        df_clients.groupby("Faixa_CLV")["is_bad_payer"]
        .mean()
        .reset_index()
        .sort_values("Faixa_CLV")
    )

    chart_title("Taxa de Inadimplência por Faixa de CLV")
    fig_clv = px.bar(
        taxa_clv,
        x="Faixa_CLV",
        y="is_bad_payer",
        text=taxa_clv["is_bad_payer"].apply(lambda x: f"{x:.1%}"),
        color_discrete_sequence=[COR_PRIMARIA],
    )
    fig_clv.update_traces(textposition="outside", textfont=dict(size=14))
    fig_clv.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="")
    st.plotly_chart(style_fig(fig_clv, show_legend=False), use_container_width=True)

    st.write("")
    st.subheader("Resumo dos Insights")
    st.markdown(
        """
| Dimensão | Resultado |
|---|---|
| ⏰ Turno | Hipótese **descartada** — diferença menor que 2% entre turnos |
| 📅 Tempo de conta | **Confirmado** — contas novas apresentam risco mais alto |
| 👤 Idade/Gênero | Hipótese **descartada** — sem padrão relevante |
| 🌎 Estado | Sem concentração geográfica forte (após controlar amostra) |
| 💰 CLV | Ver gráfico acima |
"""
    )

st.write("")
st.caption(
    "Projeto de portfólio — Engenharia e Inteligência de Dados aplicadas a "
    "Segurança Digital, Prevenção a Fraude e Modelagem de Risco."
)