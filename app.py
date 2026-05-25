import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
from scipy import stats
from scipy.stats import (
    shapiro, normaltest, kstest, anderson,
    ttest_1samp, ttest_ind, ttest_rel,
    f_oneway, kruskal, mannwhitneyu, wilcoxon,
    chi2_contingency, fisher_exact,
    pearsonr, spearmanr, kendalltau,
    levene, bartlett, fligner
)
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Estatístico Completo",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2rem; font-weight: bold;
        color: #1f77b4; text-align: center;
        padding: 10px 0; border-bottom: 3px solid #1f77b4;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 1.3rem; font-weight: bold;
        color: #2c3e50; border-left: 5px solid #1f77b4;
        padding-left: 10px; margin: 15px 0;
    }
    .metric-card {
        background: white; border-radius: 10px;
        padding: 15px; border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .result-box {
        background: #f8f9fa; border-radius: 8px;
        padding: 15px; border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda; border-radius: 8px;
        padding: 10px; border-left: 4px solid #28a745;
    }
    .warning-box {
        background: #fff3cd; border-radius: 8px;
        padding: 10px; border-left: 4px solid #ffc107;
    }
    .danger-box {
        background: #f8d7da; border-radius: 8px;
        padding: 10px; border-left: 4px solid #dc3545;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6; border-radius: 8px;
        padding: 8px 16px; font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

@st.cache_data
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(uploaded_file, sep=sep)
                    if df.shape[1] > 1:
                        return df
                except:
                    continue
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

def converter_datas(df):
    for col in df.columns:
        if any(p in col.lower() for p in ['data', 'date', 'dia', 'time', 'hora']):
            try:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            except:
                pass
    return df

def detectar_outliers_iqr(series):
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR = Q3 - Q1
    lb, ub = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    return series[(series < lb) | (series > ub)], lb, ub

def detectar_outliers_zscore(series, threshold=3):
    z = np.abs(stats.zscore(series.dropna()))
    return series[np.abs(stats.zscore(series.fillna(series.mean()))) > threshold]

def regressao_linear(x, y):
    mask = ~np.isnan(x) & ~np.isnan(y)
    xc, yc = x[mask], y[mask]
    if len(xc) < 2:
        return None, None, None, None, None
    slope, intercept, r, p, se = stats.linregress(xc, yc)
    return slope, intercept, r**2, p, se

def interpretar_p(p, alpha=0.05):
    if p < 0.001:
        return "p < 0,001 ✅ Altamente significativo"
    elif p < alpha:
        return f"p = {p:.4f} ✅ Significativo (α={alpha})"
    else:
        return f"p = {p:.4f} ❌ Não significativo (α={alpha})"

def interpretar_correlacao(r):
    a = abs(r)
    if a >= 0.9: return "Muito forte"
    elif a >= 0.7: return "Forte"
    elif a >= 0.5: return "Moderada"
    elif a >= 0.3: return "Fraca"
    else: return "Muito fraca / negligenciável"

def estatisticas_descritivas(series):
    s = series.dropna()
    Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
    return {
        "N": len(s),
        "Faltantes": series.isna().sum(),
        "Média": s.mean(),
        "Mediana": s.median(),
        "Moda": s.mode().iloc[0] if not s.mode().empty else np.nan,
        "Desvio Padrão": s.std(),
        "Variância": s.var(),
        "Erro Padrão": s.sem(),
        "CV (%)": (s.std() / s.mean() * 100) if s.mean() != 0 else np.nan,
        "Mínimo": s.min(),
        "Máximo": s.max(),
        "Amplitude": s.max() - s.min(),
        "Q1 (25%)": Q1,
        "Q3 (75%)": Q3,
        "IQR": Q3 - Q1,
        "Assimetria": s.skew(),
        "Curtose": s.kurtosis(),
        "IC 95% Inf": s.mean() - 1.96 * s.sem(),
        "IC 95% Sup": s.mean() + 1.96 * s.sem(),
    }

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📁 Carregar Dados")
    uploaded_file = st.file_uploader(
        "Excel ou CSV",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file is None:
        st.info("Aguardando arquivo...")
        st.stop()

    st.success("✅ Arquivo carregado!")
    alpha = st.slider("Nível de significância (α)", 0.01, 0.10, 0.05, 0.01)

# ─────────────────────────────────────────────
# CARREGAR E PROCESSAR
# ─────────────────────────────────────────────
dados = carregar_dados(uploaded_file)
if dados is None:
    st.stop()

dados = converter_datas(dados)
num_cols = dados.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = dados.select_dtypes(include=['object', 'category']).columns.tolist()
date_cols = [c for c in dados.columns if pd.api.types.is_datetime64_any_dtype(dados[c])]

st.markdown('<div class="main-header">📊 Dashboard Estatístico Completo</div>', unsafe_allow_html=True)

# Filtro de período
with st.sidebar:
    st.markdown("## 🎛️ Filtros")
    if date_cols:
        dc = st.selectbox("Coluna de data", date_cols)
        dmin = dados[dc].min()
        dmax = dados[dc].max()
        dr = st.date_input("Período", value=(dmin, dmax), min_value=dmin, max_value=dmax)
        if len(dr) == 2:
            dados = dados[(dados[dc] >= pd.Timestamp(dr[0])) & (dados[dc] <= pd.Timestamp(dr[1]))]

    # Remoção de outliers global
    st.markdown("## 🔍 Outliers Globais")
    rem_out = st.checkbox("Remover outliers (IQR)")
    if rem_out and num_cols:
        col_out = st.selectbox("Coluna", num_cols, key="out_global")
        _, lb, ub = detectar_outliers_iqr(dados[col_out])
        n_before = len(dados)
        dados = dados[(dados[col_out] >= lb) & (dados[col_out] <= ub)]
        st.info(f"Removidos: {n_before - len(dados)} registros")

    st.markdown("## 💾 Exportar")
    csv = dados.to_csv(index=False)
    st.download_button("📥 Baixar dados filtrados", csv, "dados_filtrados.csv", "text/csv")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Visão Geral",
    "📋 Estatística Descritiva",
    "📈 Séries Temporais",
    "🔔 Normalidade",
    "🔥 Correlações",
    "📉 Regressão",
    "🧪 Testes de Hipótese",
    "🎯 ANOVA",
    "📦 Não-Paramétricos",
    "🌐 Multivariada / PCA",
    "🤖 Clustering",
    "🔍 Dispersão & Outliers",
    "📊 Distribuições Teóricas"
])

# ══════════════════════════════════════════════
# ABA 0 — VISÃO GERAL
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-header">📋 Visão Geral do Dataset</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Linhas", f"{dados.shape[0]:,}")
    c2.metric("Colunas", dados.shape[1])
    c3.metric("Numéricas", len(num_cols))
    c4.metric("Faltantes totais", dados.isna().sum().sum())

    st.markdown("### 📄 Primeiros registros")
    st.dataframe(dados.head(20), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔢 Tipos de dados")
        tipos = pd.DataFrame({"Tipo": dados.dtypes, "Faltantes": dados.isna().sum(),
                              "% Faltantes": (dados.isna().sum() / len(dados) * 100).round(2)})
        st.dataframe(tipos, use_container_width=True)
    with col2:
        st.markdown("### 📊 Distribuição de faltantes")
        miss = dados.isna().sum()
        miss = miss[miss > 0]
        if len(miss) > 0:
            fig = px.bar(x=miss.index, y=miss.values, labels={"x": "Coluna", "y": "Faltantes"},
                         title="Valores Faltantes por Coluna", color=miss.values,
                         color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ Nenhum valor faltante!")

    if num_cols:
        st.markdown("### 📈 Resumo estatístico")
        st.dataframe(dados[num_cols].describe().T.round(4), use_container_width=True)

# ══════════════════════════════════════════════
# ABA 1 — ESTATÍSTICA DESCRITIVA
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">📋 Estatística Descritiva Completa</div>', unsafe_allow_html=True)

    if not num_cols:
        st.warning("Nenhuma coluna numérica encontrada.")
    else:
        col_sel = st.selectbox("Selecione a coluna", num_cols, key="desc_col")
        series = dados[col_sel].dropna()

        stats_dict = estatisticas_descritivas(dados[col_sel])

        # Exibir em cards
        items = list(stats_dict.items())
        for row_start in range(0, len(items), 4):
            cols = st.columns(4)
            for i, (k, v) in enumerate(items[row_start:row_start+4]):
                with cols[i]:
                    val = f"{v:,.4f}" if isinstance(v, float) else str(v)
                    st.metric(k, val)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(dados, x=col_sel, nbins=40, marginal="box",
                               title=f"Histograma + Boxplot: {col_sel}",
                               color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.violin(dados, y=col_sel, box=True, points="outliers",
                            title=f"Violin Plot: {col_sel}",
                            color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig, use_container_width=True)

        # Tabela de frequência (para categóricas ou discretas)
        st.markdown("### 📊 Comparativo entre colunas numéricas")
        resumo_all = pd.DataFrame({c: estatisticas_descritivas(dados[c]) for c in num_cols}).T
        st.dataframe(resumo_all.round(4), use_container_width=True)

# ══════════════════════════════════════════════
# ABA 2 — SÉRIES TEMPORAIS
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-header">📈 Análise de Séries Temporais</div>', unsafe_allow_html=True)

    if not date_cols or not num_cols:
        st.warning("Necessário ao menos uma coluna de data e uma numérica.")
    else:
        c1, c2, c3 = st.columns(3)
        dc = c1.selectbox("Data", date_cols, key="ts_date")
        vc = c2.selectbox("Variável", num_cols, key="ts_var")
        tipo = c3.selectbox("Tipo", ["Linha", "Área", "Barra", "Scatter", "Boxplot Mensal"])

        ag = st.selectbox("Agregação", ["Nenhuma", "Diária", "Semanal", "Mensal", "Trimestral"])

        df_ts = dados[[dc, vc]].dropna().sort_values(dc)

        if ag != "Nenhuma":
            freq_map = {"Diária": "D", "Semanal": "W", "Mensal": "ME", "Trimestral": "QE"}
            df_ts = df_ts.set_index(dc).resample(freq_map[ag]).mean().reset_index()

        if tipo == "Linha":
            fig = px.line(df_ts, x=dc, y=vc, title=f"Evolução: {vc}")
        elif tipo == "Área":
            fig = px.area(df_ts, x=dc, y=vc, title=f"Evolução: {vc}")
        elif tipo == "Barra":
            fig = px.bar(df_ts, x=dc, y=vc, title=f"Evolução: {vc}")
        elif tipo == "Scatter":
            fig = px.scatter(df_ts, x=dc, y=vc, title=f"Dispersão temporal: {vc}",
                             trendline="lowess")
        else:
            df_ts['Mês'] = df_ts[dc].dt.to_period('M').astype(str)
            fig = px.box(df_ts, x='Mês', y=vc, title=f"Distribuição mensal: {vc}")

        # Adicionar média móvel
        if tipo in ["Linha", "Área"] and len(df_ts) > 7:
            janela = st.slider("Média móvel (períodos)", 2, 30, 7)
            df_ts['MM'] = df_ts[vc].rolling(janela).mean()
            fig.add_scatter(x=df_ts[dc], y=df_ts['MM'], mode='lines',
                            name=f'Média Móvel ({janela})',
                            line=dict(color='red', dash='dash', width=2))

        st.plotly_chart(fig, use_container_width=True)

        # Estatísticas temporais
        st.markdown("### 📊 Estatísticas da série")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média", f"{df_ts[vc].mean():.3f}")
        c2.metric("Desvio Padrão", f"{df_ts[vc].std():.3f}")
        c3.metric("Mínimo", f"{df_ts[vc].min():.3f}")
        c4.metric("Máximo", f"{df_ts[vc].max():.3f}")

        # Tendência
        x_num = np.arange(len(df_ts))
        slope, intercept, r2, p, _ = regressao_linear(x_num.astype(float), df_ts[vc].values)
        if slope is not None:
            tendencia = "↗️ Crescente" if slope > 0 else "↘️ Decrescente"
            st.markdown(f"**Tendência linear:** {tendencia} | Inclinação: {slope:.4f} | R² = {r2:.4f} | {interpretar_p(p, alpha)}")

# ══════════════════════════════════════════════
# ABA 3 — NORMALIDADE
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">🔔 Testes de Normalidade</div>', unsafe_allow_html=True)

    if not num_cols:
        st.warning("Nenhuma coluna numérica.")
    else:
        col_norm = st.selectbox("Coluna", num_cols, key="norm_col")
        series = dados[col_norm].dropna()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧪 Resultados dos Testes")

            resultados = []

            # Shapiro-Wilk (melhor para n < 5000)
            if len(series) <= 5000:
                stat, p = shapiro(series)
                resultados.append({"Teste": "Shapiro-Wilk", "Estatística": f"{stat:.4f}",
                                   "p-valor": f"{p:.4f}",
                                   "Conclusão": "Normal ✅" if p > alpha else "Não Normal ❌"})

            # D'Agostino-Pearson
            if len(series) >= 8:
                stat, p = normaltest(series)
                resultados.append({"Teste": "D'Agostino-Pearson", "Estatística": f"{stat:.4f}",
                                   "p-valor": f"{p:.4f}",
                                   "Conclusão": "Normal ✅" if p > alpha else "Não Normal ❌"})

            # Kolmogorov-Smirnov
            stat, p = kstest(series, 'norm', args=(series.mean(), series.std()))
            resultados.append({"Teste": "Kolmogorov-Smirnov", "Estatística": f"{stat:.4f}",
                               "p-valor": f"{p:.4f}",
                               "Conclusão": "Normal ✅" if p > alpha else "Não Normal ❌"})

            # Anderson-Darling
            result_ad = anderson(series)
            ad_p = "< 0,01" if result_ad.statistic > result_ad.critical_values[-1] else "> 0,05"
            resultados.append({"Teste": "Anderson-Darling", "Estatística": f"{result_ad.statistic:.4f}",
                               "p-valor": ad_p,
                               "Conclusão": "Normal ✅" if ">" in ad_p else "Não Normal ❌"})

            df_res = pd.DataFrame(resultados)
            st.dataframe(df_res, use_container_width=True, hide_index=True)

            st.markdown("### 📐 Medidas de Forma")
            skew = series.skew()
            kurt = series.kurtosis()
            c1i, c2i = st.columns(2)
            c1i.metric("Assimetria", f"{skew:.4f}",
                       delta="Simétrica" if abs(skew) < 0.5 else ("Mod. assimétrica" if abs(skew) < 1 else "Forte assimetria"))
            c2i.metric("Curtose", f"{kurt:.4f}",
                       delta="Normal" if abs(kurt) < 0.5 else ("Mod. diferente" if abs(kurt) < 1 else "Muito diferente"))

        with col2:
            # Histograma com curva normal
            fig = go.Figure()
            count, bins = np.histogram(series, bins=30, density=True)
            fig.add_trace(go.Bar(x=bins[:-1], y=count, name="Dados", opacity=0.7,
                                 marker_color="#1f77b4"))
            x_norm = np.linspace(series.min(), series.max(), 200)
            y_norm = stats.norm.pdf(x_norm, series.mean(), series.std())
            fig.add_trace(go.Scatter(x=x_norm, y=y_norm, mode='lines',
                                     name="Curva Normal", line=dict(color='red', width=2)))
            fig.update_layout(title=f"Distribuição vs Normal: {col_norm}")
            st.plotly_chart(fig, use_container_width=True)

        # Gráfico Q-Q
        st.markdown("### 📊 Gráfico Q-Q")
        (osm, osr), (slope, intercept, r) = stats.probplot(series, dist="norm")
        fig_qq = go.Figure()
        fig_qq.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name='Dados',
                                    marker=dict(color='#1f77b4', size=5)))
        x_line = np.array([min(osm), max(osm)])
        fig_qq.add_trace(go.Scatter(x=x_line, y=slope * x_line + intercept,
                                    mode='lines', name='Linha de referência',
                                    line=dict(color='red', dash='dash', width=2)))
        fig_qq.update_layout(title="Q-Q Plot (Normalidade)",
                             xaxis_title="Quantis Teóricos", yaxis_title="Quantis Amostrais")
        st.plotly_chart(fig_qq, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 4 — CORRELAÇÕES
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-header">🔥 Análise de Correlações</div>', unsafe_allow_html=True)

    if len(num_cols) < 2:
        st.warning("Necessário ao menos 2 colunas numéricas.")
    else:
        c1, c2 = st.columns(2)
        metodo = c1.selectbox("Método", ["pearson", "spearman", "kendall"], key="corr_method")
        vars_sel = st.multiselect("Variáveis", num_cols,
                                  default=num_cols[:min(10, len(num_cols))], key="corr_vars")

        if len(vars_sel) >= 2:
            corr = dados[vars_sel].corr(method=metodo)

            # Heatmap
            fig = px.imshow(corr.round(3), text_auto=True, aspect="auto",
                            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                            title=f"Matriz de Correlação ({metodo.capitalize()})")
            st.plotly_chart(fig, use_container_width=True)

            # Top correlações
            pairs = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    v1, v2 = corr.columns[i], corr.columns[j]
                    r_val = corr.iloc[i, j]
                    # p-valor
                    if metodo == "pearson":
                        _, pv = pearsonr(dados[v1].dropna(), dados[v2].dropna())
                    elif metodo == "spearman":
                        _, pv = spearmanr(dados[v1].dropna(), dados[v2].dropna())
                    else:
                        _, pv = kendalltau(dados[v1].dropna(), dados[v2].dropna())
                    pairs.append({"Var 1": v1, "Var 2": v2, "r": round(r_val, 4),
                                  "|r|": round(abs(r_val), 4), "p-valor": round(pv, 4),
                                  "Força": interpretar_correlacao(r_val),
                                  "Sig.": "✅" if pv < alpha else "❌"})

            df_pairs = pd.DataFrame(pairs).sort_values("|r|", ascending=False)
            st.markdown("### 🔝 Ranking de Correlações")
            st.dataframe(df_pairs.drop("|r|", axis=1), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# ABA 5 — REGRESSÃO
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-header">📉 Análise de Regressão</div>', unsafe_allow_html=True)

    if len(num_cols) < 2:
        st.warning("Necessário ao menos 2 colunas numéricas.")
    else:
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("Variável X (independente)", num_cols, key="reg_x")
        y_col = c2.selectbox("Variável Y (dependente)", num_cols, key="reg_y",
                              index=min(1, len(num_cols)-1))
        tipo_reg = c3.selectbox("Tipo", ["Linear", "Polinomial (grau 2)", "Polinomial (grau 3)"])

        df_reg = dados[[x_col, y_col]].dropna()
        x_vals = df_reg[x_col].values
        y_vals = df_reg[y_col].values

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Dados',
                                 marker=dict(color='#1f77b4', size=6, opacity=0.7)))

        x_line = np.linspace(x_vals.min(), x_vals.max(), 300)

        if tipo_reg == "Linear":
            slope, intercept, r2, p, se = regressao_linear(x_vals.astype(float), y_vals.astype(float))
            if slope is not None:
                y_line = slope * x_line + intercept
                eq = f"y = {slope:.4f}x + {intercept:.4f}"
                fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                         name='Regressão Linear', line=dict(color='red', width=2)))
                fig.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper",
                                   text=f"{eq}<br>R² = {r2:.4f}<br>{interpretar_p(p, alpha)}",
                                   showarrow=False, bgcolor="white", bordercolor="black")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Inclinação (β₁)", f"{slope:.4f}")
                col2.metric("Intercepto (β₀)", f"{intercept:.4f}")
                col3.metric("R²", f"{r2:.4f}")
                col4.metric("p-valor", f"{p:.4f}")

                # Resíduos
                y_pred = slope * x_vals + intercept
                residuos = y_vals - y_pred
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📊 Análise de Resíduos")
                col1, col2 = st.columns(2)
                with col1:
                    fig_res = px.scatter(x=y_pred, y=residuos, title="Resíduos vs Valores Ajustados",
                                         labels={"x": "Valores Ajustados", "y": "Resíduos"})
                    fig_res.add_hline(y=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig_res, use_container_width=True)
                with col2:
                    fig_hist_res = px.histogram(x=residuos, nbins=30, title="Distribuição dos Resíduos",
                                                 labels={"x": "Resíduos"})
                    st.plotly_chart(fig_hist_res, use_container_width=True)

        else:
            grau = 2 if "2" in tipo_reg else 3
            coefs = np.polyfit(x_vals, y_vals, grau)
            poly = np.poly1d(coefs)
            y_line = poly(x_line)
            y_pred = poly(x_vals)
            ss_res = np.sum((y_vals - y_pred)**2)
            ss_tot = np.sum((y_vals - y_vals.mean())**2)
            r2 = 1 - ss_res/ss_tot if ss_tot != 0 else 0

            fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines',
                                     name=f'Regressão Polinomial (grau {grau})',
                                     line=dict(color='red', width=2)))
            fig.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper",
                               text=f"R² = {r2:.4f}", showarrow=False,
                               bgcolor="white", bordercolor="black")
            st.metric("R²", f"{r2:.4f}")
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 6 — TESTES DE HIPÓTESE
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="section-header">🧪 Testes de Hipótese</div>', unsafe_allow_html=True)

    teste = st.selectbox("Selecione o teste", [
        "Teste t — Uma amostra",
        "Teste t — Duas amostras independentes",
        "Teste t — Amostras pareadas",
        "Teste Z — Uma proporção",
        "Teste de Levene (homogeneidade de variâncias)",
        "Teste de Bartlett (homogeneidade de variâncias)",
        "Teste Qui-Quadrado (independência)",
        "Teste Exato de Fisher"
    ])

    if teste == "Teste t — Uma amostra":
        c1, c2 = st.columns(2)
        col_t = c1.selectbox("Coluna", num_cols, key="t1_col")
        mu0 = c2.number_input("Média hipotética (μ₀)", value=float(dados[col_t].mean()))
        alternativa = st.selectbox("Hipótese alternativa", ["two-sided", "less", "greater"])

        series = dados[col_t].dropna()
        stat, p = ttest_1samp(series, mu0, alternative=alternativa)

        st.markdown(f"""
        **H₀:** μ = {mu0} | **H₁:** μ {'≠' if alternativa=='two-sided' else ('<' if alternativa=='less' else '>')} {mu0}

        **Estatística t:** {stat:.4f} | **{interpretar_p(p, alpha)}**

        **Média amostral:** {series.mean():.4f} | **IC 95%:** [{series.mean() - 1.96*series.sem():.4f}, {series.mean() + 1.96*series.sem():.4f}]

        **Conclusão:** {'✅ Rejeita H₀' if p < alpha else '❌ Não rejeita H₀'} — {'Há evidência de diferença' if p < alpha else 'Sem evidência de diferença'} em relação a μ = {mu0}.
        """)

    elif teste == "Teste t — Duas amostras independentes":
        c1, c2 = st.columns(2)
        col1_t = c1.selectbox("Grupo 1", num_cols, key="t2_c1")
        col2_t = c2.selectbox("Grupo 2", num_cols, key="t2_c2", index=min(1, len(num_cols)-1))
        igual_var = st.checkbox("Assumir variâncias iguais (Student)", value=False)

        s1 = dados[col1_t].dropna()
        s2 = dados[col2_t].dropna()
        stat, p = ttest_ind(s1, s2, equal_var=igual_var)
        tipo_nome = "Student" if igual_var else "Welch"

        st.markdown(f"""
        **Teste t de {tipo_nome}**

        **H₀:** μ₁ = μ₂ | **H₁:** μ₁ ≠ μ₂

        | | {col1_t} | {col2_t} |
        |---|---|---|
        | N | {len(s1)} | {len(s2)} |
        | Média | {s1.mean():.4f} | {s2.mean():.4f} |
        | Desvio Padrão | {s1.std():.4f} | {s2.std():.4f} |

        **Estatística t:** {stat:.4f} | **{interpretar_p(p, alpha)}**

        **Conclusão:** {'✅ Rejeita H₀ — médias significativamente diferentes' if p < alpha else '❌ Não rejeita H₀ — sem diferença significativa entre as médias'}.
        """)

        fig = go.Figure()
        fig.add_trace(go.Box(y=s1, name=col1_t, boxmean=True))
        fig.add_trace(go.Box(y=s2, name=col2_t, boxmean=True))
        fig.update_layout(title="Comparação entre grupos")
        st.plotly_chart(fig, use_container_width=True)

    elif teste == "Teste t — Amostras pareadas":
        c1, c2 = st.columns(2)
        col1_t = c1.selectbox("Antes", num_cols, key="tp_c1")
        col2_t = c2.selectbox("Depois", num_cols, key="tp_c2", index=min(1, len(num_cols)-1))

        df_par = dados[[col1_t, col2_t]].dropna()
        stat, p = ttest_rel(df_par[col1_t], df_par[col2_t])
        diff = df_par[col1_t] - df_par[col2_t]

        st.markdown(f"""
        **Teste t Pareado**

        **H₀:** μ_diff = 0 | **H₁:** μ_diff ≠ 0

        **Diferença média:** {diff.mean():.4f} ± {diff.std():.4f}

        **Estatística t:** {stat:.4f} | **{interpretar_p(p, alpha)}**

        **Conclusão:** {'✅ Rejeita H₀ — diferença significativa' if p < alpha else '❌ Não rejeita H₀ — sem diferença significativa'}.
        """)

    elif teste == "Teste de Levene (homogeneidade de variâncias)":
        cols_lev = st.multiselect("Grupos (colunas)", num_cols,
                                   default=num_cols[:min(3, len(num_cols))], key="lev_cols")
        if len(cols_lev) >= 2:
            grupos = [dados[c].dropna().values for c in cols_lev]
            stat, p = levene(*grupos)
            st.markdown(f"""
            **Teste de Levene**

            **H₀:** Variâncias iguais | **H₁:** Ao menos uma variância diferente

            **Estatística W:** {stat:.4f} | **{interpretar_p(p, alpha)}**

            **Conclusão:** {'✅ Rejeita H₀ — variâncias heterogêneas (use Welch)' if p < alpha else '❌ Não rejeita H₀ — variâncias homogêneas'}.
            """)

    elif teste == "Teste de Bartlett (homogeneidade de variâncias)":
        cols_bar = st.multiselect("Grupos (colunas)", num_cols,
                                   default=num_cols[:min(3, len(num_cols))], key="bar_cols")
        if len(cols_bar) >= 2:
            grupos = [dados[c].dropna().values for c in cols_bar]
            stat, p = bartlett(*grupos)
            st.markdown(f"""
            **Teste de Bartlett** (sensível à não-normalidade)

            **H₀:** Variâncias iguais | **H₁:** Ao menos uma variância diferente

            **Estatística χ²:** {stat:.4f} | **{interpretar_p(p, alpha)}**

            **Conclusão:** {'✅ Rejeita H₀ — variâncias heterogêneas' if p < alpha else '❌ Não rejeita H₀ — variâncias homogêneas'}.
            """)

    elif teste == "Teste Qui-Quadrado (independência)":
        if len(cat_cols) < 2:
            st.warning("Necessário ao menos 2 colunas categóricas.")
        else:
            c1, c2 = st.columns(2)
            col_a = c1.selectbox("Variável A", cat_cols, key="chi_a")
            col_b = c2.selectbox("Variável B", cat_cols, key="chi_b", index=min(1, len(cat_cols)-1))

            tabela = pd.crosstab(dados[col_a], dados[col_b])
            chi2, p, dof, expected = chi2_contingency(tabela)

            st.markdown(f"""
            **Qui-Quadrado de Pearson**

            **H₀:** Variáveis independentes | **H₁:** Variáveis associadas

            **χ²:** {chi2:.4f} | **gl:** {dof} | **{interpretar_p(p, alpha)}**

            **Conclusão:** {'✅ Rejeita H₀ — associação significativa' if p < alpha else '❌ Não rejeita H₀ — sem associação significativa'}.
            """)
            st.markdown("**Tabela de contingência:**")
            st.dataframe(tabela)

    elif teste == "Teste Exato de Fisher":
        if len(cat_cols) < 2:
            st.warning("Necessário ao menos 2 colunas categóricas (binárias).")
        else:
            c1, c2 = st.columns(2)
            col_a = c1.selectbox("Variável A", cat_cols, key="fish_a")
            col_b = c2.selectbox("Variável B", cat_cols, key="fish_b", index=min(1, len(cat_cols)-1))

            tabela = pd.crosstab(dados[col_a], dados[col_b])
            if tabela.shape == (2, 2):
                odds, p = fisher_exact(tabela)
                st.markdown(f"""
                **Teste Exato de Fisher**

                **Odds Ratio:** {odds:.4f} | **{interpretar_p(p, alpha)}**

                **Conclusão:** {'✅ Associação significativa' if p < alpha else '❌ Sem associação significativa'}.
                """)
                st.dataframe(tabela)
            else:
                st.warning("Teste de Fisher requer tabela 2×2.")

    elif teste == "Teste Z — Uma proporção":
        c1, c2, c3 = st.columns(3)
        n_total = c1.number_input("N total", min_value=1, value=100)
        n_sucess = c2.number_input("N sucessos", min_value=0, value=50)
        p0 = c3.number_input("Proporção hipotética (p₀)", min_value=0.0, max_value=1.0, value=0.5)

        p_hat = n_sucess / n_total
        se_z = np.sqrt(p0 * (1 - p0) / n_total)
        z = (p_hat - p0) / se_z
        p_val = 2 * (1 - stats.norm.cdf(abs(z)))

        st.markdown(f"""
        **Teste Z para Uma Proporção**

        **H₀:** p = {p0} | **H₁:** p ≠ {p0}

        **p̂ (amostral):** {p_hat:.4f} | **Z:** {z:.4f} | **{interpretar_p(p_val, alpha)}**

        **IC 95%:** [{p_hat - 1.96*se_z:.4f}, {p_hat + 1.96*se_z:.4f}]

        **Conclusão:** {'✅ Rejeita H₀' if p_val < alpha else '❌ Não rejeita H₀'}.
        """)

# ══════════════════════════════════════════════
# ABA 7 — ANOVA
# ══════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="section-header">🎯 ANOVA — Análise de Variância</div>', unsafe_allow_html=True)

    tipo_anova = st.selectbox("Tipo", ["ANOVA One-Way (por coluna)", "ANOVA One-Way (variável + grupo)"])

    if tipo_anova == "ANOVA One-Way (por coluna)":
        cols_anova = st.multiselect("Grupos (colunas numéricas)", num_cols,
                                     default=num_cols[:min(4, len(num_cols))], key="anova_cols")
        if len(cols_anova) >= 2:
            grupos = [dados[c].dropna().values for c in cols_anova]
            stat, p = f_oneway(*grupos)

            st.markdown(f"""
            **ANOVA One-Way**

            **H₀:** μ₁ = μ₂ = ... = μk | **H₁:** Ao menos uma média diferente

            **F:** {stat:.4f} | **{interpretar_p(p, alpha)}**

            **Conclusão:** {'✅ Rejeita H₀ — ao menos uma média significativamente diferente' if p < alpha else '❌ Não rejeita H₀ — sem diferença significativa entre as médias'}.
            """)

            # Boxplot comparativo
            df_melt = pd.melt(dados[cols_anova], var_name="Grupo", value_name="Valor")
            fig = px.box(df_melt, x="Grupo", y="Valor", title="Comparação entre grupos (ANOVA)",
                         color="Grupo", points="outliers")
            st.plotly_chart(fig, use_container_width=True)

            # Resumo por grupo
            resumo = pd.DataFrame({c: {"N": len(dados[c].dropna()), "Média": dados[c].mean(),
                                        "DP": dados[c].std(), "Min": dados[c].min(),
                                        "Max": dados[c].max()} for c in cols_anova}).T
            st.dataframe(resumo.round(4), use_container_width=True)

    else:
        if not cat_cols or not num_cols:
            st.warning("Necessário coluna numérica e categórica.")
        else:
            c1, c2 = st.columns(2)
            var_num = c1.selectbox("Variável numérica", num_cols, key="anova_num")
            var_grp = c2.selectbox("Variável grupo (categórica)", cat_cols, key="anova_grp")

            df_av = dados[[var_num, var_grp]].dropna()
            grupos_dict = {g: df_av[df_av[var_grp] == g][var_num].values
                           for g in df_av[var_grp].unique()}
            grupos_list = list(grupos_dict.values())

            if len(grupos_list) >= 2:
                stat, p = f_oneway(*grupos_list)

                st.markdown(f"""
                **ANOVA One-Way:** {var_num} por {var_grp}

                **F:** {stat:.4f} | **{interpretar_p(p, alpha)}**

                **Conclusão:** {'✅ Rejeita H₀' if p < alpha else '❌ Não rejeita H₀'}.
                """)

                fig = px.box(df_av, x=var_grp, y=var_num, color=var_grp,
                             title=f"{var_num} por {var_grp}", points="outliers")
                st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 8 — NÃO-PARAMÉTRICOS
# ══════════════════════════════════════════════
with tabs[8]:
    st.markdown('<div class="section-header">📦 Testes Não-Paramétricos</div>', unsafe_allow_html=True)

    teste_np = st.selectbox("Teste", [
        "Mann-Whitney U (2 grupos independentes)",
        "Wilcoxon (amostras pareadas)",
        "Kruskal-Wallis (k grupos independentes)",
        "Spearman (correlação não-paramétrica)",
        "Kendall Tau (correlação não-paramétrica)"
    ])

    if teste_np == "Mann-Whitney U (2 grupos independentes)":
        c1, c2 = st.columns(2)
        col1_mw = c1.selectbox("Grupo 1", num_cols, key="mw_c1")
        col2_mw = c2.selectbox("Grupo 2", num_cols, key="mw_c2", index=min(1, len(num_cols)-1))

        s1, s2 = dados[col1_mw].dropna(), dados[col2_mw].dropna()
        stat, p = mannwhitneyu(s1, s2, alternative='two-sided')

        st.markdown(f"""
        **Mann-Whitney U**

        **H₀:** Distribuições iguais | **H₁:** Distribuições diferentes

        **U:** {stat:.4f} | **{interpretar_p(p, alpha)}**

        | | {col1_mw} | {col2_mw} |
        |---|---|---|
        | Mediana | {s1.median():.4f} | {s2.median():.4f} |
        | IQR | {s1.quantile(0.75)-s1.quantile(0.25):.4f} | {s2.quantile(0.75)-s2.quantile(0.25):.4f} |

        **Conclusão:** {'✅ Rejeita H₀ — distribuições significativamente diferentes' if p < alpha else '❌ Não rejeita H₀'}.
        """)

    elif teste_np == "Wilcoxon (amostras pareadas)":
        c1, c2 = st.columns(2)
        col1_w = c1.selectbox("Antes", num_cols, key="wil_c1")
        col2_w = c2.selectbox("Depois", num_cols, key="wil_c2", index=min(1, len(num_cols)-1))

        df_w = dados[[col1_w, col2_w]].dropna()
        stat, p = wilcoxon(df_w[col1_w], df_w[col2_w])

        st.markdown(f"""
        **Teste de Wilcoxon (pareado)**

        **W:** {stat:.4f} | **{interpretar_p(p, alpha)}**

        **Conclusão:** {'✅ Rejeita H₀ — diferença significativa' if p < alpha else '❌ Não rejeita H₀'}.
        """)

    elif teste_np == "Kruskal-Wallis (k grupos independentes)":
        cols_kw = st.multiselect("Grupos", num_cols,
                                  default=num_cols[:min(4, len(num_cols))], key="kw_cols")
        if len(cols_kw) >= 2:
            grupos = [dados[c].dropna().values for c in cols_kw]
            stat, p = kruskal(*grupos)

            st.markdown(f"""
            **Kruskal-Wallis** (alternativa não-paramétrica à ANOVA)

            **H:** {stat:.4f} | **{interpretar_p(p, alpha)}**

            **Conclusão:** {'✅ Rejeita H₀ — ao menos um grupo diferente' if p < alpha else '❌ Não rejeita H₀'}.
            """)

            df_melt = pd.melt(dados[cols_kw], var_name="Grupo", value_name="Valor")
            fig = px.box(df_melt, x="Grupo", y="Valor", color="Grupo",
                         title="Kruskal-Wallis — Comparação de Grupos")
            st.plotly_chart(fig, use_container_width=True)

    elif teste_np in ["Spearman (correlação não-paramétrica)", "Kendall Tau (correlação não-paramétrica)"]:
        c1, c2 = st.columns(2)
        col_x = c1.selectbox("Variável X", num_cols, key="np_cx")
        col_y = c2.selectbox("Variável Y", num_cols, key="np_cy", index=min(1, len(num_cols)-1))

        s1, s2 = dados[col_x].dropna(), dados[col_y].dropna()
        n = min(len(s1), len(s2))
        s1, s2 = s1.iloc[:n], s2.iloc[:n]

        if "Spearman" in teste_np:
            r, p = spearmanr(s1, s2)
            nome = "Spearman (ρ)"
        else:
            r, p = kendalltau(s1, s2)
            nome = "Kendall (τ)"

        st.markdown(f"""
        **Correlação {nome}**

        **r = {r:.4f}** | **Força:** {interpretar_correlacao(r)} | **{interpretar_p(p, alpha)}**

        **Conclusão:** {'✅ Correlação significativa' if p < alpha else '❌ Correlação não significativa'}.
        """)

# ══════════════════════════════════════════════
# ABA 9 — PCA / MULTIVARIADA
# ══════════════════════════════════════════════
with tabs[9]:
    st.markdown('<div class="section-header">🌐 Análise Multivariada / PCA</div>', unsafe_allow_html=True)

    if len(num_cols) < 2:
        st.warning("Necessário ao menos 2 colunas numéricas.")
    else:
        vars_pca = st.multiselect("Variáveis para PCA", num_cols,
                                   default=num_cols[:min(8, len(num_cols))], key="pca_vars")
        if len(vars_pca) >= 2:
            df_pca = dados[vars_pca].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df_pca)

            n_comp = min(len(vars_pca), len(df_pca))
            pca = PCA(n_components=n_comp)
            scores = pca.fit_transform(X_scaled)

            var_exp = pca.explained_variance_ratio_
            var_cum = np.cumsum(var_exp)

            col1, col2 = st.columns(2)

            with col1:
                # Variância explicada
                fig_ve = go.Figure()
                fig_ve.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(n_comp)],
                                        y=var_exp * 100, name="Individual",
                                        marker_color="#1f77b4"))
                fig_ve.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(n_comp)],
                                            y=var_cum * 100, mode='lines+markers',
                                            name="Acumulada", line=dict(color='red', width=2)))
                fig_ve.add_hline(y=80, line_dash="dash", line_color="green",
                                 annotation_text="80%")
                fig_ve.update_layout(title="Variância Explicada por Componente (%)",
                                     yaxis_title="%")
                st.plotly_chart(fig_ve, use_container_width=True)

            with col2:
                # Biplot PC1 vs PC2
                df_scores = pd.DataFrame(scores[:, :2], columns=["PC1", "PC2"])
                fig_bi = px.scatter(df_scores, x="PC1", y="PC2",
                                    title="Biplot PC1 vs PC2",
                                    opacity=0.7)
                # Loadings
                loadings = pca.components_.T
                scale = max(scores[:, 0].max(), scores[:, 1].max()) * 0.5
                for i, var in enumerate(vars_pca):
                    fig_bi.add_annotation(x=loadings[i, 0] * scale,
                                          y=loadings[i, 1] * scale,
                                          text=var, showarrow=True,
                                          arrowhead=2, arrowcolor="red",
                                          font=dict(color="red", size=10))
                st.plotly_chart(fig_bi, use_container_width=True)

            # Tabela de loadings
            st.markdown("### 📋 Loadings (contribuições das variáveis)")
            n_show = min(4, n_comp)
            df_load = pd.DataFrame(
                pca.components_[:n_show].T,
                index=vars_pca,
                columns=[f"PC{i+1}" for i in range(n_show)]
            ).round(4)
            st.dataframe(df_load, use_container_width=True)

            # Resumo de variância
            st.markdown("### 📊 Variância explicada acumulada")
            df_var = pd.DataFrame({
                "Componente": [f"PC{i+1}" for i in range(n_comp)],
                "Variância (%)": (var_exp * 100).round(2),
                "Acumulada (%)": (var_cum * 100).round(2)
            })
            st.dataframe(df_var, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# ABA 10 — CLUSTERING
# ══════════════════════════════════════════════
with tabs[10]:
    st.markdown('<div class="section-header">🤖 Análise de Clustering (K-Means)</div>', unsafe_allow_html=True)

    if len(num_cols) < 2:
        st.warning("Necessário ao menos 2 colunas numéricas.")
    else:
        vars_cl = st.multiselect("Variáveis", num_cols,
                                  default=num_cols[:min(5, len(num_cols))], key="cl_vars")
        if len(vars_cl) >= 2:
            df_cl = dados[vars_cl].dropna()
            scaler_cl = StandardScaler()
            X_cl = scaler_cl.fit_transform(df_cl)

            col1, col2 = st.columns(2)

            with col1:
                # Método Elbow
                st.markdown("### 📐 Método Elbow (escolha do K)")
                k_max = min(10, len(df_cl) - 1)
                inertias = []
                sil_scores = []
                K_range = range(2, k_max + 1)
                for k in K_range:
                    km = KMeans(n_clusters=k, random_state=42, n_init=10)
                    km.fit(X_cl)
                    inertias.append(km.inertia_)
                    sil_scores.append(silhouette_score(X_cl, km.labels_))

                fig_elbow = go.Figure()
                fig_elbow.add_trace(go.Scatter(x=list(K_range), y=inertias,
                                               mode='lines+markers', name='Inércia',
                                               line=dict(color='#1f77b4', width=2)))
                fig_elbow.update_layout(title="Elbow Method", xaxis_title="K",
                                        yaxis_title="Inércia")
                st.plotly_chart(fig_elbow, use_container_width=True)

            with col2:
                # Silhouette
                st.markdown("### 📊 Silhouette Score")
                fig_sil = go.Figure()
                fig_sil.add_trace(go.Scatter(x=list(K_range), y=sil_scores,
                                             mode='lines+markers', name='Silhouette',
                                             line=dict(color='#ff7f0e', width=2)))
                fig_sil.update_layout(title="Silhouette Score vs K",
                                       xaxis_title="K", yaxis_title="Silhouette")
                st.plotly_chart(fig_sil, use_container_width=True)

            k_sel = st.slider("Número de clusters (K)", 2, k_max,
                              int(np.argmax(sil_scores)) + 2)
            km_final = KMeans(n_clusters=k_sel, random_state=42, n_init=10)
            labels = km_final.fit_predict(X_cl)
            df_cl = df_cl.copy()
            df_cl['Cluster'] = labels.astype(str)

            # PCA para visualização
            pca_cl = PCA(n_components=2)
            coords = pca_cl.fit_transform(X_cl)
            df_vis = pd.DataFrame(coords, columns=["PC1", "PC2"])
            df_vis['Cluster'] = labels.astype(str)

            fig_cl = px.scatter(df_vis, x="PC1", y="PC2", color="Cluster",
                                title=f"Clusters (K={k_sel}) — Projeção PCA",
                                color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig_cl, use_container_width=True)

            # Perfil dos clusters
            st.markdown("### 📋 Perfil dos Clusters")
            perfil = df_cl.groupby('Cluster')[vars_cl].mean().round(4)
            st.dataframe(perfil, use_container_width=True)

            sil_final = silhouette_score(X_cl, labels)
            st.metric("Silhouette Score final", f"{sil_final:.4f}",
                      delta="Bom (>0.5)" if sil_final > 0.5 else "Razoável (>0.25)" if sil_final > 0.25 else "Fraco")

# ══════════════════════════════════════════════
# ABA 11 — DISPERSÃO & OUTLIERS
# ══════════════════════════════════════════════
with tabs[11]:
    st.markdown('<div class="section-header">🔍 Dispersão & Detecção de Outliers</div>', unsafe_allow_html=True)

    if not num_cols:
        st.warning("Nenhuma coluna numérica.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Gráfico de Dispersão com Regressão")
            cx = st.selectbox("Eixo X", num_cols, key="sc_x")
            cy = st.selectbox("Eixo Y", num_cols, key="sc_y", index=min(1, len(num_cols)-1))

            df_sc = dados[[cx, cy]].dropna()
            slope, intercept, r2, p, _ = regressao_linear(df_sc[cx].values.astype(float),
                                                           df_sc[cy].values.astype(float))
            fig_sc = px.scatter(df_sc, x=cx, y=cy, title=f"{cy} vs {cx}", opacity=0.7)
            if slope is not None:
                x_l = np.linspace(df_sc[cx].min(), df_sc[cx].max(), 200)
                fig_sc.add_trace(go.Scatter(x=x_l, y=slope*x_l+intercept, mode='lines',
                                            name='Regressão', line=dict(color='red', width=2)))
                fig_sc.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper",
                                      text=f"R² = {r2:.4f}", showarrow=False,
                                      bgcolor="white", bordercolor="black")
            st.plotly_chart(fig_sc, use_container_width=True)

        with col2:
            st.markdown("### 🚨 Detecção de Outliers")
            col_out2 = st.selectbox("Coluna", num_cols, key="out2_col")
            metodo_out = st.selectbox("Método", ["IQR", "Z-Score", "Ambos"])

            series_out = dados[col_out2].dropna()
            out_iqr, lb, ub = detectar_outliers_iqr(series_out)
            out_z = detectar_outliers_zscore(series_out)

            if metodo_out == "IQR":
                outliers_show = out_iqr
                label = "IQR"
            elif metodo_out == "Z-Score":
                outliers_show = out_z
                label = "Z-Score"
            else:
                idx_both = out_iqr.index.intersection(out_z.index)
                outliers_show = series_out[idx_both]
                label = "IQR ∩ Z-Score"

            c1m, c2m, c3m = st.columns(3)
            c1m.metric("Total", len(series_out))
            c2m.metric(f"Outliers ({label})", len(outliers_show))
            c3m.metric("% Outliers", f"{len(outliers_show)/len(series_out)*100:.1f}%")

            # Boxplot com outliers destacados
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(y=series_out, name="Distribuição", boxmean=True,
                                     marker_color="#1f77b4"))
            if len(outliers_show) > 0:
                fig_box.add_trace(go.Scatter(
                    x=["Distribuição"] * len(outliers_show),
                    y=outliers_show.values, mode='markers',
                    marker=dict(color='red', size=8, symbol='x'),
                    name=f'Outliers ({label})'
                ))
            fig_box.update_layout(title=f"Outliers: {col_out2}")
            st.plotly_chart(fig_box, use_container_width=True)

            if len(outliers_show) > 0:
                with st.expander(f"📋 Ver {len(outliers_show)} outliers"):
                    st.dataframe(pd.DataFrame({"Índice": outliers_show.index,
                                               "Valor": outliers_show.values}),
                                 hide_index=True)

        # Mapa de calor de outliers
        st.markdown("### 🗺️ Mapa de Outliers por Coluna")
        out_summary = {}
        for c in num_cols:
            s = dados[c].dropna()
            out, _, _ = detectar_outliers_iqr(s)
            out_summary[c] = {"Outliers (IQR)": len(out),
                              "% Outliers": round(len(out)/len(s)*100, 2) if len(s) > 0 else 0,
                              "Limite Inf.": round(_, 4) if _ is not None else None,
                              "Limite Sup.": round(__, 4) if (__ := detectar_outliers_iqr(s)[2]) is not None else None}
        st.dataframe(pd.DataFrame(out_summary).T, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 12 — DISTRIBUIÇÕES TEÓRICAS
# ══════════════════════════════════════════════
with tabs[12]:
    st.markdown('<div class="section-header">📊 Ajuste a Distribuições Teóricas</div>', unsafe_allow_html=True)

    if not num_cols:
        st.warning("Nenhuma coluna numérica.")
    else:
        col_dist = st.selectbox("Coluna", num_cols, key="dist_col")
        series_d = dados[col_dist].dropna()

        distribuicoes = {
            "Normal": stats.norm,
            "Log-Normal": stats.lognorm,
            "Exponencial": stats.expon,
            "Gamma": stats.gamma,
            "Weibull": stats.weibull_min,
            "Beta": stats.beta,
            "Uniforme": stats.uniform,
        }

        resultados_dist = []
        for nome, dist in distribuicoes.items():
            try:
                params = dist.fit(series_d)
                ks_stat, ks_p = kstest(series_d, dist.cdf, args=params)
                resultados_dist.append({
                    "Distribuição": nome,
                    "KS Estatística": round(ks_stat, 4),
                    "KS p-valor": round(ks_p, 4),
                    "Ajuste": "✅ Bom" if ks_p > alpha else "❌ Ruim"
                })
            except:
                pass

        df_dist = pd.DataFrame(resultados_dist).sort_values("KS p-valor", ascending=False)
        st.markdown("### 🏆 Ranking de ajuste (Kolmogorov-Smirnov)")
        st.dataframe(df_dist, use_container_width=True, hide_index=True)

        melhor = df_dist.iloc[0]["Distribuição"]
        st.success(f"✅ Melhor ajuste: **{melhor}**")

        # Visualizar ajuste da melhor distribuição
        dist_sel = st.selectbox("Visualizar distribuição", list(distribuicoes.keys()),
                                 index=list(distribuicoes.keys()).index(melhor))
        dist_obj = distribuicoes[dist_sel]
        params_sel = dist_obj.fit(series_d)

        x_range = np.linspace(series_d.min(), series_d.max(), 300)
        y_pdf = dist_obj.pdf(x_range, *params_sel)

        fig_fit = go.Figure()
        count, bins = np.histogram(series_d, bins=40, density=True)
        fig_fit.add_trace(go.Bar(x=bins[:-1], y=count, name="Dados (densidade)",
                                  opacity=0.6, marker_color="#1f77b4"))
        fig_fit.add_trace(go.Scatter(x=x_range, y=y_pdf, mode='lines',
                                      name=f"PDF {dist_sel}",
                                      line=dict(color='red', width=2)))
        fig_fit.update_layout(title=f"Ajuste: {dist_sel} — {col_dist}",
                               xaxis_title=col_dist, yaxis_title="Densidade")
        st.plotly_chart(fig_fit, use_container_width=True)

        # CDF empírica vs teórica
        x_sorted = np.sort(series_d)
        cdf_emp = np.arange(1, len(x_sorted)+1) / len(x_sorted)
        cdf_teo = dist_obj.cdf(x_sorted, *params_sel)

        fig_cdf = go.Figure()
        fig_cdf.add_trace(go.Scatter(x=x_sorted, y=cdf_emp, mode='lines',
                                      name='CDF Empírica', line=dict(color='#1f77b4', width=2)))
        fig_cdf.add_trace(go.Scatter(x=x_sorted, y=cdf_teo, mode='lines',
                                      name=f'CDF {dist_sel}',
                                      line=dict(color='red', width=2, dash='dash')))
        fig_cdf.update_layout(title="CDF Empírica vs Teórica",
                               xaxis_title=col_dist, yaxis_title="Probabilidade acumulada")
        st.plotly_chart(fig_cdf, use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#666; font-size:13px;'>"
    "📊 Dashboard Estatístico Completo • Matheus Mendes • 2025"
    "</div>",
    unsafe_allow_html=True
)
