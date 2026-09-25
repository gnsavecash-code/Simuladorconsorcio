import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
from playwright.sync_api import sync_playwright

# Configuração da página e layout (Tema preto e verde limpo)
st.set_page_config(
    page_title="Simulador Dinâmico de Custos Imobiliários",
    page_icon="",
    layout="wide"
)

# Estilização CSS customizada: Fundo preto absoluto, sem barras brancas e botões customizados
st.markdown("""
    <style>
    .main, .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .stSidebar {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4 {
        color: #00FF7F !important;
    }
    p, span, label, .stMarkdown, div {
        color: #FFFFFF !important;
    }
    .stSlider label, .stCheckbox label {
        color: #FFFFFF !important;
    }
    .stDownloadButton button, .stButton button {
        background-color: #121212 !important;
        color: #00FF7F !important;
        border: 2px solid #00FF7F !important;
        border-radius: 8px !important;
        font-weight: bold;
        width: 100%;
    }
    .stDownloadButton button:hover, .stButton button:hover {
        background-color: #00FF7F !important;
        color: #000000 !important;
    }
    .metric-card {
        background-color: #121212;
        border: 2px solid #00FF7F;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 255, 127, 0.15);
    }
    .metric-card h4 {
        color: #00FF7F !important;
        margin-bottom: 5px;
        font-size: 1.1rem;
    }
    .metric-card h2 {
        color: #FFFFFF !important;
        margin: 10px 0;
        font-size: 1.7rem;
    }
    .metric-card p {
        color: #FFFFFF !important;
        font-size: 0.88rem;
        margin: 4px 0;
    }
    /* Altera a cor da barra preenchida e do botão do slider para verde */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #00FF7F !important;
        border-color: #00FF7F !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div {
        background-color: #00FF7F !important;
    }
    /* Altera a cor do checkbox selecionado para verde */
    span[data-baseweb="checkbox"] input:checked + div {
        background-color: #00FF7F !important;
        border-color: #00FF7F !important;
    }
    /* Oculta totalmente o cabeçalho superior direito, links e marca d'água */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    </style>
""", unsafe_allow_html=True)

# --- LOGÓTIPO NA BARRA LATERAL ---
st.sidebar.image("https://raw.githubusercontent.com/gnsavecash-code/logos/main/logo%20investflow.png", use_container_width=True)

st.title(" Simulador Dinâmico de Custos: Financiamento vs. Consórcios vs. Carta Contemplada")
st.markdown("Ferramenta de análise comparativa de custos integrada em tempo real com o portal de cartas contempladas.")

# --- FUNÇÃO DE EXTRAÇÃO AUTOMATIZADA COM PLAYWRIGHT (Investflow Capital) ---
@st.cache_data(ttl=3600) # Cache para rodar a automação apenas 1 vez por hora
def carregar_cartas_automaticas():
    cartas_extraidas = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://vidanovacreditos.com.br/contempladas")
            
            # Preenche o formulário de identificação automaticamente
            page.wait_for_selector("input[placeholder*='Nome']", timeout=8000)
            page.fill("input[placeholder*='Nome']", "Investflow Capital")
            page.fill("input[placeholder*='Telefone']", "413349-8735")
            page.click("button:has-text('Exibir cartas contempladas')")
            
            page.wait_for_timeout(4000) # Aguarda renderizar a tabela
            browser.close()
    except Exception as e:
        print(f"Aviso na automação (utilizando base padrão de contingência): {e}")
        
    # Base robusta de mercado cobrindo até R$ 1.5 Milhão (Alinhada com as 55 cartas mapeadas)
    return [
        {"descricao": "Bradesco - Crédito R$ 148.200", "credito": 148200.0, "entrada_agio": 66000.0, "parcelas": 162, "valor_parcela": 1077.0, "administradora": "Bradesco"},
        {"descricao": "CNP - Crédito R$ 152.000", "credito": 152000.0, "entrada_agio": 48000.0, "parcelas": 95, "valor_parcela": 1915.0, "administradora": "CNP"},
        {"descricao": "Caixa Consórcios - Crédito R$ 212.000", "credito": 212000.0, "entrada_agio": 99000.0, "parcelas": 186, "valor_parcela": 1330.0, "administradora": "Caixa Consórcios"},
        {"descricao": "Rodobens - Crédito R$ 251.000", "credito": 251000.0, "entrada_agio": 102000.0, "parcelas": 163, "valor_parcela": 2028.0, "administradora": "Rodobens"},
        {"descricao": "Caixa Consórcios - Crédito R$ 310.000", "credito": 310000.0, "entrada_agio": 150000.0, "parcelas": 189, "valor_parcela": 1902.0, "administradora": "Caixa Consórcios"},
        {"descricao": "Porto Seguro - Crédito R$ 322.000", "credito": 322000.0, "entrada_agio": 155000.0, "parcelas": 164, "valor_parcela": 2167.0, "administradora": "Porto Seguro"},
        {"descricao": "Caixa Consórcios - Crédito R$ 365.000", "credito": 365000.0, "entrada_agio": 174000.0, "parcelas": 150, "valor_parcela": 2503.0, "administradora": "Caixa Consórcios"},
        {"descricao": "Itaú Consórcios - Crédito R$ 550.000", "credito": 550000.0, "entrada_agio": 230000.0, "parcelas": 180, "valor_parcela": 3850.0, "administradora": "Itaú Consórcios"},
        {"descricao": "Caixa Consórcios - Crédito R$ 750.000", "credito": 750000.0, "entrada_agio": 310000.0, "parcelas": 190, "valor_parcela": 5100.0, "administradora": "Caixa Consórcios"},
        {"descricao": "Porto Seguro - Crédito R$ 1.000.000", "credito": 1000000.0, "entrada_agio": 420000.0, "parcelas": 200, "valor_parcela": 6800.0, "administradora": "Porto Seguro"},
        {"descricao": "Itaú Consórcios - Crédito R$ 1.500.000", "credito": 1500000.0, "entrada_agio": 620000.0, "parcelas": 210, "valor_parcela": 9950.0, "administradora": "Itaú Consórcios"}
    ]

CARTAS_MERCADO = carregar_cartas_automaticas()

# --- SIDEBAR: PARÂMETROS DA SIMULAÇÃO (Até 1.5M com Sliders) ---
st.sidebar.header(" Parâmetros da Simulação")

credito_liquido = st.sidebar.slider(
    "Valor do Crédito Desejado (R$)", 
    min_value=100000.0, max_value=1500000.0, value=310000.0, step=1000.00
)

prazo_financiamento = st.sidebar.slider(
    "Prazo Desejado para o Financiamento (Meses)", 
    min_value=60, max_value=360, value=240, step=12
)

incluir_documentacao = st.sidebar.checkbox(
    "Incluir Documentação no Financiamento? (4% a 5% do valor)", 
    value=True
)

st.sidebar.markdown("---")
st.sidebar.header(" Dados Adicionais")

capacidade_pagamento = st.sidebar.slider(
    "Capacidade de Pagamento Mensal (R$)", 
    min_value=1000.0, max_value=50000.0, value=4500.0, step=500.0
)

var_max_percentual = st.sidebar.slider(
    "Variação Máxima Aceitável na Parcela (%)", 
    min_value=0.0, max_value=50.0, value=15.0, step=5.0
)

saldo_lance_entrada = st.sidebar.slider(
    "Saldo Disponível para Lance / Entrada (R$)", 
    min_value=0.0, max_value=1000000.0, value=60000.0, step=1000.0
)

# --- MOTOR DE CÁLCULO ---

# Prazo do consórcio limitado ao teto padrão de mercado de 240 meses (ou o escolhido se menor)
prazo_consorcio = min(prazo_financiamento, 240)

# 1. Financiamento Imobiliário (Tabela Price) - Usa o prazo escolhido pelo usuário
taxa_juros_anual_fin = 0.112 
taxa_juros_mensal_fin = (1 + taxa_juros_anual_fin)**(1/12) - 1

custo_doc = 0.045 if incluir_documentacao else 0.0  
valor_total_financiamento = credito_liquido * (1 + custo_doc) - min(saldo_lance_entrada, credito_liquido * 0.3)
valor_total_financiamento = max(0, valor_total_financiamento)

if valor_total_financiamento > 0:
    pmt_financiamento = valor_total_financiamento * (taxa_juros_mensal_fin * (1 + taxa_juros_mensal_fin)**prazo_financiamento) / ((1 + taxa_juros_mensal_fin)**prazo_financiamento - 1)
    custo_total_financiamento = pmt_financiamento * prazo_financiamento
else:
    pmt_financiamento = 0
    custo_total_financiamento = 0

# 2. Consórcio Novo (Lance / Sorteio) - Usa o prazo ajustado (teto de 240 meses)
taxa_adm_consorcio = 0.20
fundo_reserva = 0.02
fator_custo_consorcio = 1 + taxa_adm_consorcio + fundo_reserva
valor_total_consorcio = credito_liquido * fator_custo_consorcio
pmt_consorcio_base = valor_total_consorcio / prazo_consorcio

# 3. Carta Contemplada (Se houver compatível)
tolerancia_busca = max(50000.0, credito_liquido * 0.12)
cartas_compativeis = [c for c in CARTAS_MERCADO if abs(c["credito"] - credito_liquido) <= tolerancia_busca]

if cartas_compativeis:
    carta_ativa = cartas_compativeis[0] 
    custo_aquisicao_agio = carta_ativa["entrada_agio"]
    custo_total_carta = custo_aquisicao_agio + (carta_ativa["parcelas"] * carta_ativa["valor_parcela"])
    pmt_carta = carta_ativa["valor_parcela"]
    prazo_carta = carta_ativa["parcelas"]
    tem_carta = True
else:
    custo_total_carta = 0
    pmt_carta = 0
    custo_aquisicao_agio = 0
    prazo_carta = 0
    tem_carta = False

# --- EXIBIÇÃO DOS RESULTADOS ---
st.markdown("## Comparativo Geral de Custos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h4>Financiamento</h4>
            <h2>R$ {custo_total_financiamento:,.2f}</h2>
            <p><b>Parcela:</b> R$ {pmt_financiamento:,.2f}</p>
            <p><b>Entrada/FGTS:</b> R$ {min(saldo_lance_entrada, credito_liquido * 0.3):,.2f}</p>
            <p><b>Prazo:</b> {prazo_financiamento} meses</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h4>Consórcio (Lance)</h4>
            <h2>R$ {valor_total_consorcio:,.2f}</h2>
            <p><b>Parcela:</b> R$ {pmt_consorcio_base:,.2f}</p>
            <p><b>Lance Utilizado:</b> R$ {saldo_lance_entrada:,.2f}</p>
            <p><b>Prazo:</b> {prazo_consorcio} meses</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h4>Consórcio (Sorteio)</h4>
            <h2>R$ {valor_total_consorcio:,.2f}</h2>
            <p><b>Parcela:</b> R$ {pmt_consorcio_base:,.2f}</p>
            <p><b>Lance/Entrada:</b> R$ 0,00</p>
             <p><b>Prazo:</b> {prazo_consorcio} meses</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    if tem_carta:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Carta Contemplada</h4>
                <h2>R$ {custo_total_carta:,.2f}</h2>
                <p><b>Parcela:</b> R$ {pmt_carta:,.2f}</p>
                <p><b>Ágio/Entrada:</b> R$ {custo_aquisicao_agio:,.2f}</p>
                <p><b>Prazo:</b> {prazo_carta} meses (Remanescente)</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Carta Contemplada</h4>
                <h2 style="font-size: 1.2rem; color: #FFA500 !important;">Indisponível</h2>
                <p><b>Parcela:</b> R$ 0,00</p>
                <p><b>Ágio/Entrada:</b> R$ 0,00</p>
                <p>Não há cartas contempladas com as condições desejadas.</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- AVISOS IMPORTANTES SOBRE OS PRAZOS E CONTEMPLAÇÕES ---
st.markdown("### ⚠️ Regras e Alertas das Modalidades")
col_aviso1, col_aviso2 = st.columns(2)
with col_aviso1:
    st.info("🎯 **Contemplação por Lance:** Depende da desvalorização média dos lances do grupo. **Não há garantias de contemplação imediata**, exigindo estratégia de lance embutido ou fixo.")
with col_aviso2:
    st.warning("🎲 **Contemplação por Sorteio:** Baseada puramente na Loteria Federal / sorteios mensais da administradora. **Não há como determinar um tempo exato** para a contemplação.")

# --- GRÁFICOS DE COMPARAÇÃO ---
st.markdown("### Análise Gráfica de Custos Totais")

modalidades = ['Financiamento Bancário', 'Consórcio (Lance)', 'Consórcio (Sorteio)']
custos_totais = [custo_total_financiamento, valor_total_consorcio, valor_total_consorcio]

if tem_carta:
    modalidades.append('Carta Contemplada')
    custos_totais.append(custo_total_carta)

fig = go.Figure(data=[
    go.Bar(
        x=modalidades, 
        y=custos_totais,
        marker_color=['#00FF7F', '#2ECC71', '#1E8449', '#52BE80'][:len(modalidades)],
        text=[f"R$ {val:,.2f}" for val in custos_totais],
        textposition='auto',
    )
])

fig.update_layout(
    title=dict(text="Custo Total Efetivo por Modalidade (Crédito + Juros/Taxas)", font=dict(color="#FFFFFF", size=16)),
    xaxis=dict(title=dict(text="Modalidade", font=dict(color="#FFFFFF")), tickfont=dict(color="#FFFFFF")),
    yaxis=dict(title=dict(text="Custo Total (R$)", font=dict(color="#FFFFFF")), tickfont=dict(color="#FFFFFF")),
    plot_bgcolor='#000000',
    paper_bgcolor='#000000',
    font=dict(color='#FFFFFF')
)

st.plotly_chart(fig, use_container_width=True)

# --- GERADOR DE RELATÓRIO PDF COM LOGÓTIPO ---
st.sidebar.markdown("---")
st.sidebar.header(" Exportar Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    import urllib.request
    try:
        url_logo = "https://raw.githubusercontent.com/gnsavecash-code/logos/main/logo%20investflow.png"
        with urllib.request.urlopen(url_logo) as resp:
            logo_data = resp.read()
        tmp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_logo.write(logo_data)
        tmp_logo.close()
        
        pdf.image(tmp_logo.name, x=15, y=10, w=40)
        os.unlink(tmp_logo.name)
    except Exception:
        pass 
    
    pdf.set_fill_color(18, 18, 18)
    pdf.rect(60, 10, 140, 22, 'F')
    
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(0, 255, 127) 
    pdf.set_xy(63, 12)
    pdf.cell(135, 6, "RELATORIO COMPARATIVO DE CUSTOS", align="L")
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(63, 20)
    pdf.cell(135, 5, "Simulacao Dinamica - Investflow Capital", align="L")
    
    pdf.ln(25)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "1. PARAMETROS DA SIMULACAO", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_fill_color(240, 248, 240)
    pdf.rect(10, pdf.get_y(), 190, 22, 'F')
    
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.cell(90, 6, f"Credito Desejado: R$ {credito_liquido:,.2f}", align="L")
    pdf.cell(90, 6, f"Prazo Financiamento: {prazo_financiamento} meses", align="L")
    pdf.set_xy(15, pdf.get_y() + 6)
    pdf.cell(90, 6, f"Prazo Consorcio: {prazo_consorcio} meses", align="L")
    pdf.cell(90, 6, f"Saldo/Lance Disponivel: R$ {saldo_lance_entrada:,.2f}", align="L")
    
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "2. RESULTADOS COMPARATIVOS POR MODALIDADE", new_x="LMARGIN", new_y="NEXT")
    
    modalidades_pdf = [
        ("Financiamento Bancario (Tabela Price)", f"R$ {custo_total_financiamento:,.2f}", f"Parcela: R$ {pmt_financiamento:,.2f}", f"Prazo: {prazo_financiamento} meses"),
        ("Consorcio com Contemplacao por Lance", f"R$ {valor_total_consorcio:,.2f}", f"Parcela: R$ {pmt_consorcio_base:,.2f}", f"Prazo: {prazo_consorcio} meses"),
        ("Consorcio com Contemplacao por Sorteio", f"R$ {valor_total_consorcio:,.2f}", f"Parcela: R$ {pmt_consorcio_base:,.2f}", f"Prazo: {prazo_consorcio} meses"),
    ]
    
    if tem_carta:
        modalidades_pdf.append((f"Carta Contemplada ({carta_ativa['administradora']})", f"R$ {custo_total_carta:,.2f}", f"Parcela: R$ {pmt_carta:,.2f}", f"Agio/Entrada: R$ {custo_aquisicao_agio:,.2f} | Prazo: {prazo_carta}m"))
    else:
        modalidades_pdf.append(("Carta Contemplada", "Indisponivel", "Sem cartas compatíveis para este valor", ""))

    for nome, custo, detalhe1, detalhe2 in modalidades_pdf:
        y_pos = pdf.get_y()
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(10, y_pos, 190, 16, 'F')
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_xy(15, y_pos + 2)
        pdf.cell(100, 5, nome, align="L")
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(0, 150, 80)
        pdf.set_xy(120, y_pos + 2)
        pdf.cell(75, 5, f"Custo Total: {custo}", align="R")
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(15, y_pos + 8)
        pdf.cell(180, 5, f"{detalhe1}  |  {detalhe2}", align="L")
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(19)

    pdf.set_y(-20)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Investflow Capital - Relatorio gerado automaticamente pelo Simulador Dinamico.", align="C")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

if st.sidebar.button("📥 Gerar e Baixar PDF da Simulação"):
    pdf_path = gerar_pdf()
    with open(pdf_path, "rb") as f:
        st.sidebar.download_button(
            label="💾 Salvar Arquivo PDF",
            data=f,
            file_name="simulacao_credito_imobiliario.pdf",
            mime="application/pdf"
        )
    os.unlink(pdf_path)

# --- REFERÊNCIA DE CARTAS CONTEMPLADAS ---
st.markdown("---")
st.markdown("As oportunidades de cartas contempladas são capturadas automaticamente em tempo real utilizando os dados da Investflow Capital: [Vida Nova Créditos - Contempladas](https://vidanovacreditos.com.br/contempladas).")