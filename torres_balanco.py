import streamlit as st
import pandas as pd

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Calculadora de Torre de Resfriamento",
    layout="wide"
)

# =====================================================
# FUNÇÃO DE FORMATAÇÃO NUMÉRICA (PT-BR)
# =====================================================
def formatar_numero(valor, casas_decimais=2):
    try:
        if valor is None or pd.isna(valor):
            return "0,00"

        formato = f"{{:,.{casas_decimais}f}}"
        numero = formato.format(float(valor))
        numero = numero.replace(",", "X").replace(".", ",").replace("X", ".")
        return numero
    except:
        return str(valor)

# =====================================================
# CSS GLOBAL – LIMPEZA TOTAL DE ESPAÇOS
# =====================================================
st.markdown("""
<style>

/* ===============================
   RESET DE ESPAÇAMENTO STREAMLIT
   =============================== */
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

.stMarkdown,
.stMarkdown > div,
.stVerticalBlock,
div[data-testid="stVerticalBlock"] {
    margin: 0 !important;
    padding: 0 !important;
}

hr {
    display: none !important;
}

/* ===============================
   DIVISOR CONTROLADO
   =============================== */
.divider {
    height: 1px;
    background-color: #e0e0e0;
    margin: 14px 0;
}

/* ===============================
   TÍTULOS
   =============================== */
h1, h2 {
    margin: 10px 0 !important;
}

/* ===============================
   CARDS
   =============================== */
.card {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}

.card-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
    border-bottom: 2px solid #4CAF50;
    padding-bottom: 6px;
    color: #2c3e50;
}

/* ===============================
   TABELAS
   =============================== */
.table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
}

.table th {
    background-color: #2c3e50;
    color: white;
    padding: 10px;
    text-align: left;
}

.table td {
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.value {
    text-align: right;
    font-weight: bold;
}

/* ===============================
   BALANÇO HÍDRICO
   =============================== */
.balance {
    background-color: #e8f5e9;
    border: 2px solid #4CAF50;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
    text-align: center;
}

.balance strong {
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TÍTULO PRINCIPAL
# =====================================================
st.title("🏭 Calculadora de Torre de Resfriamento")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =====================================================
# ESTADO
# =====================================================
if "calcular" not in st.session_state:
    st.session_state.calcular = False

# =====================================================
# SIDEBAR – ENTRADAS
# =====================================================
with st.sidebar:
    st.header("⚙️ Parâmetros de Entrada")

    VZ_rec = st.number_input("Vazão de Recirculação (m³/h)", min_value=0.0, value=10000.0)
    Vol_estatico = st.number_input("Volume Estático (m³)", min_value=0.0, value=50.0)
    T_retorno = st.number_input("Temperatura de Retorno (°C)", min_value=0.0, value=35.0)
    T_bacia = st.number_input("Temperatura da Bacia (°C)", min_value=0.0, value=30.0)
    perc_arraste = st.number_input("% Arraste", min_value=0.0, value=0.05)
    perc_utilizacao = st.number_input("% Utilização", min_value=0.0, max_value=100.0, value=100.0)
    ciclos = st.number_input("Ciclos de Concentração", min_value=1.1, value=5.0)

    if st.button("📊 CALCULAR", use_container_width=True):
        st.session_state.calcular = True
        st.rerun()

# =====================================================
# CÁLCULOS
# =====================================================
if st.session_state.calcular:

    delta_T = T_retorno - T_bacia
    evaporacao = VZ_rec * delta_T * (0.85 / 556) * (perc_utilizacao / 100)

    perda_liquida = evaporacao / (ciclos - 1)
    perda_arraste = (perc_arraste / 100) * VZ_rec
    purga = max(perda_liquida - perda_arraste, 0)

    reposicao = evaporacao + perda_liquida
    HTI = 0.693 * (Vol_estatico / perda_liquida) if perda_liquida > 0 else 0

    # =================================================
    # RESULTADOS – DADOS DE ENTRADA
    # =================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📥 Dados de Entrada</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <table class="table">
        <tr><td>Vazão de Recirculação</td><td class="value">{formatar_numero(VZ_rec)}</td></tr>
        <tr><td>Volume Estático</td><td class="value">{formatar_numero(Vol_estatico)}</td></tr>
        <tr><td>Temperatura de Retorno</td><td class="value">{formatar_numero(T_retorno)}</td></tr>
        <tr><td>Temperatura da Bacia</td><td class="value">{formatar_numero(T_bacia)}</td></tr>
        <tr><td>% Arraste</td><td class="value">{formatar_numero(perc_arraste)}</td></tr>
        <tr><td>Ciclos</td><td class="value">{formatar_numero(ciclos)}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # RESULTADOS – CÁLCULO
    # =================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Resultados</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <table class="table">
        <tr><td>ΔT</td><td class="value">{formatar_numero(delta_T)}</td></tr>
        <tr><td>Evaporação</td><td class="value">{formatar_numero(evaporacao)}</td></tr>
        <tr><td>Perda Líquida</td><td class="value">{formatar_numero(perda_liquida)}</td></tr>
        <tr><td>Arraste</td><td class="value">{formatar_numero(perda_arraste)}</td></tr>
        <tr><td>Purga</td><td class="value">{formatar_numero(purga)}</td></tr>
        <tr><td>Reposição</td><td class="value">{formatar_numero(reposicao)}</td></tr>
        <tr><td>HTI (h)</td><td class="value">{formatar_numero(HTI)}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # BALANÇO HÍDRICO
    # =================================================
    st.markdown('<div class="balance">', unsafe_allow_html=True)
    st.markdown(f"""
        💨 Evaporação: <strong>{formatar_numero(evaporacao)} m³/h</strong><br>
        💧 Perdas Totais: <strong>{formatar_numero(perda_liquida)} m³/h</strong><br><br>
        🚰 <strong>Reposição Total: {formatar_numero(reposicao)} m³/h</strong>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Novo Cálculo"):
        st.session_state.calcular = False
        st.rerun()

# =====================================================
# RODAPÉ
# =====================================================
st.markdown("""
<div style="text-align:center; color:#777; font-size:13px; margin-top:20px;">
🏭 Calculadora de Torre de Resfriamento • Layout limpo • Versão estável
</div>
""", unsafe_allow_html=True)
