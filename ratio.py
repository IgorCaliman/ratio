# Para rodar este app:
# pip install streamlit yfinance python-dateutil matplotlib
# streamlit run streamlit_app.py

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date
from dateutil.relativedelta import relativedelta

# --- Configuração da página
st.set_page_config(page_title="Razão de Tickers", layout="wide")

# --- CSS customizado
st.markdown(
    """
    <style>
    /* 1) Todo texto padrão da sidebar em branco */
    section[data-testid="stSidebar"] * {
        color: #FFF !important;
    }

    /* 2) Somente os campos de input dentro da sidebar em preto */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="number"],
    section[data-testid="stSidebar"] div[data-baseweb="datepicker"] input {
        color: #000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Título principal
st.title('Razão de Tickers')

# --- Sidebar
st.sidebar.title("Parâmetros")

# Inicializa datas em session_state
today = date.today()
if 'start_date' not in st.session_state:
    st.session_state.start_date = date(2020, 1, 1)
if 'end_date' not in st.session_state:
    st.session_state.end_date = today

# Campos de entrada de ticker
ticker1 = st.sidebar.text_input('Ticker 1', 'ITUB3').strip().upper()
ticker2 = st.sidebar.text_input('Ticker 2', 'ITUB4').strip().upper()

# Subtítulo e botões de período rápido
st.sidebar.subheader("Selecione um período rápido")
periodos = {
    "YTD": lambda: (date(today.year, 1, 1), today),
    "1M":  lambda: (today - relativedelta(months=1), today),
    "3M":  lambda: (today - relativedelta(months=3), today),
    "6M":  lambda: (today - relativedelta(months=6), today),
    "1Y":  lambda: (today - relativedelta(years=1), today),
    "2Y":  lambda: (today - relativedelta(years=2), today),
    "5Y":  lambda: (today - relativedelta(years=5), today),
    "10Y": lambda: (today - relativedelta(years=10), today),
}

# Primeira fileira: YTD, 1M, 3M, 6M
cols1 = st.sidebar.columns(4)
for col, key in zip(cols1, ["YTD", "1M", "3M", "6M"]):
    if col.button(key):
        st.session_state.start_date, st.session_state.end_date = periodos[key]()

# Segunda fileira: 1Y, 2Y, 5Y, 10Y
cols2 = st.sidebar.columns(4)
for col, key in zip(cols2, ["1Y", "2Y", "5Y", "10Y"]):
    if col.button(key):
        st.session_state.start_date, st.session_state.end_date = periodos[key]()

# Entradas de data manual
start_date = st.sidebar.date_input(
    'Data Início',
    value=st.session_state.start_date,
    format='DD/MM/YYYY'
)
end_date = st.sidebar.date_input(
    'Data Fim',
    value=st.session_state.end_date,
    format='DD/MM/YYYY'
)

# Botão para plotar
atualizar = st.sidebar.button('Plotar Razão')


# --- Função de plotagem
def plotar_ratio(t1, t2, start, end):
    t1_full = t1 if t1.upper().endswith('.SA') else f'{t1}.SA'
    t2_full = t2 if t2.upper().endswith('.SA') else f'{t2}.SA'
    df = yf.download([t1_full, t2_full], start=start, end=end)['Close'].dropna()

    if df.empty:
        st.warning("Não foi possível obter dados para os tickers informados no período selecionado.")
        return

    ratio = df[t1_full] / df[t2_full]
    media = ratio.mean()
    mediana = ratio.median()
    std = ratio.std()
    y_min = ratio.min() * 0.95
    y_max = ratio.max() * 1.05

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(ratio.index, ratio, label=f'{t1_full} ÷ {t2_full}')
    ax.axhline(media, linestyle='--', label='Média')
    ax.axhline(mediana, color='green', linestyle='-.', label='Mediana')
    ax.axhline(media + std, linestyle=':', label='+1σ')
    ax.axhline(media - std, linestyle=':', label='-1σ')
    ax.set_title(f'Razão entre {t1_full} e {t2_full}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Ratio')
    ax.set_ylim(y_min, y_max)
    ax.grid(False)
    ax.legend()
    st.pyplot(fig)


# --- Plotagem inicial ou após clique
if not atualizar:
    plotar_ratio(ticker1, ticker2, st.session_state.start_date, st.session_state.end_date)
else:
    plotar_ratio(ticker1, ticker2, start_date, end_date)
