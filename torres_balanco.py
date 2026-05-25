import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Torre de Resfriamento", layout="wide")

def formatar_numero(valor, casas_decimais=3):
    """Formata número com vírgula como separador decimal e ponto como separador de milhar"""
    try:
        if valor is None or valor == 0:
            return "0,00"
        
        if pd.isna(valor):
            return "0,00"
            
        format_string = f"{{:.{casas_decimais}f}}"
        numero_formatado = format_string.format(float(valor))
        
        partes = numero_formatado.split('.')
        parte_inteira = partes[0]
        parte_decimal = partes[1] if len(partes) > 1 else ''
        
        parte_inteira_com_pontos = ""
        for i, char in enumerate(reversed(parte_inteira)):
            if i > 0 and i % 3 == 0:
                parte_inteira_com_pontos = '.' + parte_inteira_com_pontos
            parte_inteira_com_pontos = char + parte_inteira_com_pontos
        
        if parte_decimal:
            return f"{parte_inteira_com_pontos},{parte_decimal}"
        else:
            return f"{parte_inteira_com_pontos}"
            
    except Exception as e:
        return f"{valor}"

# CSS para melhorar a aparência e remover barras brancas
st.markdown("""
<style>
    /* Reset de margens e paddings para remover espaçamentos indesejados */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Remover espaçamento entre elementos */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
    }
    
    /* Remover margens de todos os elementos */
    .stMarkdown, .stMarkdown > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Estilo dos botões */
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    .sidebar-header {
        color: #4CAF50;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 16px;
    }
    
    /* Caixa de instruções */
    .instruction-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px !important;
        border-left: 5px solid #4CAF50;
    }
    
    /* Parâmetros */
    .param-box {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .param-title {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
        font-size: 16px;
    }
    .param-unit {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* Diagrama de fluxo */
    .flow-diagram {
        background-color: #f5f9ff;
        border-radius: 20px;
        border: 2px solid #d0e3ff;
        overflow: hidden;
    }
    
    .flow-step {
        background-color: white;
        padding: 20px;
        border-left: 6px solid;
    }
    
    .flow-title {
        font-weight: bold;
        margin-bottom: 15px;
        font-size: 18px;
        padding-bottom: 8px;
        border-bottom: 2px solid;
        text-align: center;
    }
    
    .flow-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
        line-height: 1.2;
        text-align: center;
    }
    
    .flow-unit {
        color: #555;
        font-size: 14px;
        margin-top: 5px;
        font-weight: 500;
        text-align: center;
    }
    
    .flow-descricao {
        font-size: 12px;
        color: #777;
        margin-top: 5px;
        text-align: center;
    }
    
    .flow-arrow {
        text-align: center;
        font-size: 30px;
        color: #4CAF50;
        padding: 5px 0;
        background-color: #f5f9ff;
    }
    
    .flow-column-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    /* Cores específicas */
    .step-entrada {
        border-left-color: #FF6B6B;
    }
    .step-entrada .flow-title {
        color: #FF6B6B;
        border-bottom-color: #FF6B6B;
    }
    .step-entrada .flow-value {
        color: #FF6B6B;
    }
    
    .step-resfriamento {
        border-left-color: #4ECDC4;
    }
    .step-resfriamento .flow-title {
        color: #4ECDC4;
        border-bottom-color: #4ECDC4;
    }
    .step-resfriamento .flow-value {
        color: #4ECDC4;
    }
    
    .step-perdas {
        border-left-color: #FFD166;
    }
    .step-perdas .flow-title {
        color: #FFD166;
        border-bottom-color: #FFD166;
    }
    .step-perdas .flow-value {
        color: #FFD166;
    }
    
    .step-reposicao {
        border-left-color: #06D6A0;
    }
    .step-reposicao .flow-title {
        color: #06D6A0;
        border-bottom-color: #06D6A0;
    }
    .step-reposicao .flow-value {
        color: #06D6A0;
    }
    
    /* Seção de Resumo */
    .resumo-section {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        border-top: 5px solid #4CAF50;
    }
    
    .resumo-header {
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid #4CAF50;
    }
    
    .resumo-title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    
    .resumo-subtitle {
        font-size: 16px;
        color: #666;
        font-weight: 500;
    }
    
    /* Tabelas */
    .info-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid;
        margin-bottom: 15px !important;
    }
    
    .info-card-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px !important;
        padding-bottom: 8px !important;
        color: #2c3e50;
        border-bottom: 2px solid;
    }
    
    .secao-dados {
        border-left-color: #FF6B6B;
    }
    .secao-dados .info-card-title {
        border-bottom-color: #FF6B6B;
        color: #FF6B6B;
    }
    
    .secao-resultados {
        border-left-color: #4ECDC4;
    }
    .secao-resultados .info-card-title {
        border-bottom-color: #4ECDC4;
        color: #4ECDC4;
    }
    
    .secao-perdas {
        border-left-color: #FFD166;
    }
    .secao-perdas .info-card-title {
        border-bottom-color: #FFD166;
        color: #FFD166;
    }
    
    /* Tabelas estilizadas */
    .dados-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dados-table th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        font-size: 14px;
    }
    
    .dados-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: middle;
    }
    
    .dados-table tr:hover {
        background-color: #f8f9fa;
    }
    
    .valor-cell {
        text-align: right;
        font-weight: bold;
        color: #2c3e50;
        font-size: 15px;
        white-space: nowrap;
    }
    
    .unidade-cell {
        text-align: center;
        color: #666;
        font-size: 13px;
        white-space: nowrap;
        width: 80px;
    }
    
    .observacao-cell {
        font-size: 12px;
        color: #666;
        font-style: italic;
    }
    
    /* Balanço Hídrico */
    .balanco-container {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px !important;
        border: 2px solid #4CAF50;
        text-align: center;
    }
    
    .balanco-title {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .balanco-equacao {
        font-size: 18px;
        margin: 10px 0;
        line-height: 1.6;
    }
    
    .balanco-total {
        font-size: 22px;
        font-weight: bold;
        color: #4CAF50;
        margin-top: 15px;
    }
    
    /* Remover espaçamento extra dos elementos do Streamlit */
    hr {
        margin: 10px 0 !important;
    }
    
    h1, h2, h3 {
        margin-bottom: 10px !important;
    }
    
    /* Centralização */
    .center-container {
        display: flex;
        justify-content: center;
        margin: 10px 0;
    }
    
    /* Tooltips */
    .info-tooltip {
        cursor: help;
        border-bottom: 1px dotted #999;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Calculadora de Torre de Resfriamento")
st.markdown("---")

# Inicializar estado da sessão
if 'calcular' not in st.session_state:
    st.session_state.calcular = False

# Sidebar para parâmetros de entrada
with st.sidebar:
    st.header("⚙️ Parâmetros de Entrada")
    
    st.markdown('<div class="sidebar-header">Dados Básicos</div>', unsafe_allow_html=True)
    VZ_rec = st.number_input("Vazão de Recirculação (m³/h)", min_value=0.0, value=None, step=50.0, format="%.1f", placeholder="Ex: 1.000,0")
    Vol_estatico = st.number_input("Volume Estático (m³)", min_value=0.0, value=None, step=5.0, format="%.1f", placeholder="Ex: 50,0")
    T_retorno = st.number_input("Temperatura de Retorno (°C)", min_value=0.0, value=None, step=1.0, format="%.1f", placeholder="Ex: 40,0")
    T_bacia = st.number_input("Temperatura de Bacia (°C)", min_value=0.0, value=None, step=1.0, format="%.1f", placeholder="Ex: 30,0")
    perc_arraste = st.number_input("% Arraste", min_value=0.0, max_value=100.0, value=None, step=0.01, format="%.2f", placeholder="Ex: 0,10")
    perc_utilizacao = st.number_input("% Utilização", min_value=0.0, max_value=100.0, value=100.0, step=5.0, format="%.1f")
    
    st.markdown("---")
    st.markdown('<div class="sidebar-header">Ciclos de Concentração</div>', unsafe_allow_html=True)
    
    parametros = {
        "Sílica": {"torre": None, "reposicao": None, "unidade": "ppm"},
        "Cloreto": {"torre": None, "reposicao": None, "unidade": "ppm"},
        "Dureza Total": {"torre": None, "reposicao": None, "unidade": "ppm CaCO₃"},
        "Alcalinidade Total": {"torre": None, "reposicao": None, "unidade": "ppm CaCO₃"},
        "Ferro Total": {"torre": None, "reposicao": None, "unidade": "ppm"}
    }
    
    ciclos_calculados = {}
    
    for param, dados in parametros.items():
        col1, col2 = st.columns(2)
        with col1:
            torre_val = st.number_input(
                f"{param} Torre", 
                min_value=0.0, 
                value=dados["torre"],
                step=10.0 if "ppm" in dados["unidade"] else 0.1,
                key=f"torre_{param}",
                format="%.1f",
                help=f"{param} na torre ({dados['unidade']})",
                placeholder="Ex: 150,0"
            )
        with col2:
            repos_val = st.number_input(
                f"{param} Reposição", 
                min_value=0.0,
                value=dados["reposicao"],
                step=5.0 if "ppm" in dados["unidade"] else 0.1,
                key=f"repos_{param}",
                format="%.1f",
                help=f"{param} na reposição ({dados['unidade']})",
                placeholder="Ex: 50,0"
            )
        
        if repos_val is not None and repos_val > 0 and torre_val is not None:
            ciclo = torre_val / repos_val
            ciclos_calculados[param] = ciclo
    
    # Selecionar qual ciclo usar
    st.markdown("---")
    st.markdown('<div class="sidebar-header">Selecionar Ciclo para Cálculos</div>', unsafe_allow_html=True)
    
    if ciclos_calculados:
        opcoes = list(ciclos_calculados.keys())
        opcoes.insert(0, "Usar valor manual")
        
        ciclo_selecionado = st.selectbox("Escolha o ciclo para os cálculos:", opcoes)
        
        if ciclo_selecionado == "Usar valor manual":
            ciclos = st.number_input("Ciclos de Concentração (manual)", 
                                     min_value=1.0, value=None, step=0.5, format="%.2f",
                                     placeholder="Ex: 3,00")
        else:
            ciclos = ciclos_calculados[ciclo_selecionado]
            st.success(f"**Usando ciclo de {ciclo_selecionado}:** {formatar_numero(ciclos, 2)} vezes")
    else:
        st.warning("Insira valores de parâmetros para calcular ciclos")
        ciclos = st.number_input("Ciclos de Concentração", 
                                 min_value=1.0, value=None, step=0.5, format="%.2f",
                                 placeholder="Ex: 3,00")
    
    st.markdown("---")
    
    # Botão de calcular
    if st.button("📠 CALCULAR", type="primary", use_container_width=True):
        st.session_state.calcular = True
        st.rerun()

# Área principal para resultados
if st.session_state.calcular:
    try:
        # Tratar valores None
        VZ_rec = VZ_rec if VZ_rec is not None else 0.0
        Vol_estatico = Vol_estatico if Vol_estatico is not None else 0.0
        T_retorno = T_retorno if T_retorno is not None else 0.0
        T_bacia = T_bacia if T_bacia is not None else 0.0
        perc_arraste = perc_arraste if perc_arraste is not None else 0.0
        perc_utilizacao = perc_utilizacao if perc_utilizacao is not None else 100.0
        ciclos = ciclos if ciclos is not None else 1.0
        
        # Converter porcentagens para decimal
        perc_utilizacao_decimal = perc_utilizacao / 100.0
        
        # Cálculos
        delta_T = T_retorno - T_bacia
        evaporacao = VZ_rec * delta_T * (0.85 / 556) * perc_utilizacao_decimal
        
        if ciclos > 1:
            perda_liquida = evaporacao / (ciclos - 1)
        else:
            perda_liquida = 0.0
            if ciclos <= 1 and ciclos > 0:
                st.error("⚠️ Ciclos de concentração devem ser maiores que 1!")
        
        if perda_liquida > 0:
            HTI = 0.693 * (Vol_estatico / perda_liquida)
        else:
            HTI = 0.0
        
        perda_arraste = (perc_arraste / 100.0) * VZ_rec * perc_utilizacao_decimal
        purgas = perda_liquida - perda_arraste
        if purgas < 0:
            purgas = 0.0
            st.warning("Perda por arraste maior que perda líquida - purga ajustada para zero")
        
        reposicao = evaporacao + perda_liquida
        
        # SEÇÃO 1: FLUXO DA TORRE
        st.markdown('<h2 style="text-align: center; color: #1f77b4; margin: 10px 0; font-size: 28px;">📊 FLUXO DA TORRE DE RESFRIAMENTO</h2>', unsafe_allow_html=True)
        
        # Diagrama do Fluxo da Torre
        st.markdown('<div class="flow-diagram">', unsafe_allow_html=True)
        
        # Seção 1: Entrada de Água Quente
        st.markdown('<div class="flow-step step-entrada">', unsafe_allow_html=True)
        st.markdown('<div class="flow-title">🔥 ENTRADA - ÁGUA QUENTE DO PROCESSO</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">🌡️ {formatar_numero(T_retorno, 1)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Temperatura de Retorno (°C)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">💧 {formatar_numero(VZ_rec, 1)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Vazão de Recirculação (m³/h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">⚙️ {formatar_numero(perc_utilizacao, 1)}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Utilização da Torre</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="flow-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Seção 2: Resfriamento na Torre
        st.markdown('<div class="flow-step step-resfriamento">', unsafe_allow_html=True)
        st.markdown('<div class="flow-title">🏭 RESFRIAMENTO NA TORRE</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">🌡️ {formatar_numero(delta_T, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">ΔT (Redução de Temperatura) (°C)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">🌡️ {formatar_numero(T_bacia, 1)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Temperatura da Bacia (°C)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">💨 {formatar_numero(evaporacao, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Evaporação (m³/h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="flow-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Seção 3: Perdas e Controle
        st.markdown('<div class="flow-step step-perdas">', unsafe_allow_html=True)
        st.markdown('<div class="flow-title">💧 PERDAS E CONTROLE</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">💧 {formatar_numero(perda_liquida, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Perda Líquida Total (m³/h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">🌪️ {formatar_numero(perda_arraste, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Perda por Arraste (m³/h)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-descricao">({formatar_numero(perc_arraste, 2)}% do recirculado)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">⬇️ {formatar_numero(purgas, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Purga do Sistema (m³/h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="flow-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Seção 4: Reposição e Balanço Hídrico
        st.markdown('<div class="flow-step step-reposicao">', unsafe_allow_html=True)
        st.markdown('<div class="flow-title">🔄 REPOSIÇÃO E BALANÇO HÍDRICO</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">🚰 {formatar_numero(reposicao, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Reposição Total (m³/h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">♻️ {formatar_numero(ciclos, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">Ciclos de Concentração</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="flow-column-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="flow-value">⏱️ {formatar_numero(HTI, 2)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="flow-unit">HTI - Tempo Retenção (h)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Fecha flow-diagram
        
        # SEÇÃO 2: RESUMO COMPACTO
        st.markdown('<div class="resumo-section">', unsafe_allow_html=True)
        
        # Cabeçalho do resumo
        st.markdown('<div class="resumo-header">', unsafe_allow_html=True)
        st.markdown('<div class="resumo-title">📋 RESUMO DO CÁLCULO</div>', unsafe_allow_html=True)
        st.markdown('<div class="resumo-subtitle">Dados principais e balanço hídrico</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabela 1: Dados de Entrada
        st.markdown('<div class="info-card secao-dados">', unsafe_allow_html=True)
        st.markdown('<div class="info-card-title">📥 DADOS DE ENTRADA</div>', unsafe_allow_html=True)
        
        tabela_entrada_html = f"""
        <table class="dados-table">
            <thead>
                <tr>
                    <th>Parâmetro</th>
                    <th style="text-align: center;">Valor</th>
                    <th style="text-align: center;">Unidade</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Vazão de Recirculação</td><td class="valor-cell">{formatar_numero(VZ_rec, 1)}</td><td class="unidade-cell">m³/h</td></tr>
                <tr><td>Volume Estático</td><td class="valor-cell">{formatar_numero(Vol_estatico, 1)}</td><td class="unidade-cell">m³</td></tr>
                <tr><td>Temperatura de Retorno</td><td class="valor-cell">{formatar_numero(T_retorno, 1)}</td><td class="unidade-cell">°C</td></tr>
                <tr><td>Temperatura da Bacia</td><td class="valor-cell">{formatar_numero(T_bacia, 1)}</td><td class="unidade-cell">°C</td></tr>
                <tr><td>% Arraste</td><td class="valor-cell">{formatar_numero(perc_arraste, 2)}</td><td class="unidade-cell">%</td></tr>
                <tr><td>% Utilização</td><td class="valor-cell">{formatar_numero(perc_utilizacao, 1)}</td><td class="unidade-cell">%</td></tr>
                <tr><td>Ciclos de Concentração</td><td class="valor-cell">{formatar_numero(ciclos, 2)}</td><td class="unidade-cell">vezes</td></tr>
            </tbody>
        </table>
        """
        st.markdown(tabela_entrada_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tabela 2: Resultados do Cálculo
        st.markdown('<div class="info-card secao-resultados">', unsafe_allow_html=True)
        st.markdown('<div class="info-card-title">📈 RESULTADOS DO CÁLCULO</div>', unsafe_allow_html=True)
        
        tabela_resultados_html = f"""
        <table class="dados-table">
            <thead><tr><th>Parâmetro</th><th style="text-align: center;">Valor</th><th style="text-align: center;">Unidade</th></tr></thead>
            <tbody>
                <tr><td>ΔT (Redução de Temperatura)</td><td class="valor-cell">{formatar_numero(delta_T, 2)}</td><td class="unidade-cell">°C</td></tr>
                <tr><td>Evaporação</td><td class="valor-cell">{formatar_numero(evaporacao, 2)}</td><td class="unidade-cell">m³/h</td></tr>
                <tr><td>Perda Líquida Total</td><td class="valor-cell">{formatar_numero(perda_liquida, 2)}</td><td class="unidade-cell">m³/h</td></tr>
                <tr><td>Reposição Total</td><td class="valor-cell">{formatar_numero(reposicao, 2)}</td><td class="unidade-cell">m³/h</td></tr>
                <tr><td>HTI (Tempo de Retenção)</td><td class="valor-cell">{formatar_numero(HTI, 2)}</td><td class="unidade-cell">horas</td></tr>
            </tbody>
        </table>
        """
        st.markdown(tabela_resultados_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tabela 3: Detalhamento das Perdas
        st.markdown('<div class="info-card secao-perdas">', unsafe_allow_html=True)
        st.markdown('<div class="info-card-title">📉 DETALHAMENTO DAS PERDAS</div>', unsafe_allow_html=True)
        
        tabela_perdas_html = f"""
        <table class="dados-table">
            <thead><tr><th>Tipo de Perda</th><th style="text-align: center;">Valor</th><th style="text-align: center;">Unidade</th><th>Observação</th></tr></thead>
            <tbody>
                <tr><td>Perda por Arraste</td><td class="valor-cell">{formatar_numero(perda_arraste, 2)}</td><td class="unidade-cell">m³/h</td><td class="observacao-cell">({formatar_numero(perc_arraste, 2)}% da vazão)</td></tr>
                <tr><td>Purga do Sistema</td><td class="valor-cell">{formatar_numero(purgas, 2)}</td><td class="unidade-cell">m³/h</td><td class="observacao-cell">(Controle de qualidade)</td></tr>
                <tr><td>Perda Líquida Total</td><td class="valor-cell">{formatar_numero(perda_liquida, 2)}</td><td class="unidade-cell">m³/h</td><td class="observacao-cell">(Soma: Arraste + Purga)</td></tr>
            </tbody>
        </table>
        """
        st.markdown(tabela_perdas_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Balanço Hídrico Destacado
        st.markdown('<div class="balanco-container">', unsafe_allow_html=True)
        st.markdown('<div class="balanco-title">⚖️ BALANÇO HÍDRICO</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="balanco-equacao"><strong>💨 Evaporação:</strong> {formatar_numero(evaporacao, 2)} m³/h</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="balanco-equacao"><strong>💧 Perda Líquida Total:</strong> {formatar_numero(perda_liquida, 2)} m³/h</div>', unsafe_allow_html=True)
        st.markdown('<div class="balanco-equacao" style="font-size: 20px; margin: 10px 0;">+</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="balanco-total">🚰 <strong>REPOSIÇÃO TOTAL:</strong> {formatar_numero(reposicao, 2)} m³/h</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Fecha balanço-container
        
        st.markdown('</div>', unsafe_allow_html=True)  # Fecha resumo-section
        
        # BOTÕES DE AÇÃO
        col_b1, col_b2, col_b3 = st.columns(3)
        
        with col_b1:
            if st.button("🔄 Novo Cálculo", use_container_width=True):
                st.session_state.calcular = False
                st.rerun()
        
        with col_b2:
            # Criar dados para exportação
            dados_exportacao = {
                "Parâmetro": [
                    "Vazão de Recirculação (m³/h)",
                    "Volume Estático (m³)",
                    "Temperatura de Retorno (°C)",
                    "Temperatura de Bacia (°C)",
                    "% Arraste",
                    "% Utilização",
                    "Ciclos de Concentração (vezes)",
                    "Delta Temperatura (°C)",
                    "Evaporação (m³/h)",
                    "Perda Líquida (m³/h)",
                    "HTI (h)",
                    "Perda por Arraste (m³/h)",
                    "Purga do Sistema (m³/h)",
                    "Reposição (m³/h)"
                ],
                "Valor": [
                    formatar_numero(VZ_rec, 1),
                    formatar_numero(Vol_estatico, 1),
                    formatar_numero(T_retorno, 1),
                    formatar_numero(T_bacia, 1),
                    formatar_numero(perc_arraste, 2),
                    formatar_numero(perc_utilizacao, 1),
                    formatar_numero(ciclos, 2),
                    formatar_numero(delta_T, 1),
                    formatar_numero(evaporacao, 2),
                    formatar_numero(perda_liquida, 2),
                    formatar_numero(HTI, 1),
                    formatar_numero(perda_arraste, 2),
                    formatar_numero(purgas, 2),
                    formatar_numero(reposicao, 2)
                ]
            }
            
            export_df = pd.DataFrame(dados_exportacao)
            csv = export_df.to_csv(index=False, sep=';', decimal=',')
            
            st.download_button(
                label="📥 Exportar para CSV",
                data=csv,
                file_name="resultados_torre_resfriamento.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_b3:
            # Mostrar informações adicionais
            taxa_evaporacao = (evaporacao / VZ_rec * 100) if VZ_rec > 0 else 0
            taxa_reposicao = (reposicao / VZ_rec * 100) if VZ_rec > 0 else 0
            
            st.markdown(f'''
            <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 14px; color: #666;">Taxa de Evaporação</div>
                <div style="font-size: 18px; font-weight: bold; color: #4CAF50;">{formatar_numero(taxa_evaporacao, 2)}%</div>
                <div style="font-size: 12px; color: #888;">da vazão de recirculação</div>
            </div>
            ''', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro nos cálculos: {str(e)}")

else:
    # Tela inicial
    st.markdown("## 📋 Instruções")
    
    st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
    st.markdown("""
    **Para usar a calculadora:**
    
    1. **Preencha todos os parâmetros** na barra lateral
    2. **Insira valores** para os 5 parâmetros químicos (Torre e Reposição)
    3. **Selecione qual ciclo** de concentração usar nos cálculos
    4. **Clique em 📠 CALCULAR** na barra lateral para visualizar o fluxo da torre
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔬 Parâmetros Químicos Disponíveis")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="param-box"><div class="param-title">🔬 Sílica</div><div class="param-unit">ppm</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="param-box"><div class="param-title">🧪 Cloreto</div><div class="param-unit">ppm</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="param-box"><div class="param-title">💎 Dureza Total</div><div class="param-unit">ppm CaCO₃</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="param-box"><div class="param-title">⚗️ Alcalinidade Total</div><div class="param-unit">ppm CaCO₃</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="param-box"><div class="param-title">🧲 Ferro Total</div><div class="param-unit">ppm</div></div>', unsafe_allow_html=True)
    
    st.info("⚡ **Clique no botão CALCULAR na barra lateral para visualizar o fluxo da torre**")

# Rodapé
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #666; padding: 10px; font-size: 14px;'>🏭 Calculadora de Torre de Resfriamento • Diagrama de Fluxo • Versão 2.0</div>", unsafe_allow_html=True)
