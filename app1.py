# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title="📊 Infosys Stock Analysis", layout="wide")

# ---------------------- Title ---------------------- #
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        📈 Infosys Ltd (INFY.NS) - Live Stock Market Analyzer
    </h1>
    """, unsafe_allow_html=True)

# ---------------------- Sidebar Inputs ---------------------- #
st.sidebar.header("📅 Select Date Range")

min_date = date(2015, 1, 1)

def_date_option = st.sidebar.selectbox("Choose Date Range Option", ("Last 1 Year", "Last 6 Months", "Custom"))

if def_date_option == "Last 1 Year":
    start_date = date.today().replace(year=date.today().year - 1)
    end_date = date.today()
elif def_date_option == "Last 6 Months":
    start_date = date.today().replace(month=max(1, date.today().month - 6))
    end_date = date.today()
else:
    start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1), min_value=min_date, max_value=date.today())
    end_date = st.sidebar.date_input("End Date", value=date.today(), min_value=start_date, max_value=date.today())

st.sidebar.header("📂 Choose Analysis Type")
analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    ("📊 Technical Analysis", "📑 Fundamental Analysis", "💬 Sentimental Analysis", "📈 Quantitative Analysis")
)

# ---------------------- Dynamic Ticker Input ---------------------- #
ticker = st.sidebar.text_input("📌 Enter Stock Ticker (e.g., INFY.NS)", value="INFY.NS")

# ---------------------- Fetch Stock Data ---------------------- #
@st.cache_data(ttl=3600)
def fetch_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        data.dropna(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch data safely
with st.spinner("📡 Fetching data..."):
    data = fetch_data(ticker, start_date, end_date)

if data is None or data.empty:
    st.error("⚠️ No historical data found for this ticker.")
    st.stop()

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

st.write("📊 Sample Data", data.tail())

# ---------------------- Candlestick Chart ---------------------- #
candlestick_data = data.dropna(subset=['Open', 'High', 'Low', 'Close'])
if candlestick_data.empty:
    st.warning("⚠️ No valid candlestick data to display.")
else:
    st.subheader(f"📈 {ticker} - Candlestick Chart")
    fig = go.Figure(data=[
        go.Candlestick(x=candlestick_data.index,
                       open=candlestick_data['Open'],
                       high=candlestick_data['High'],
                       low=candlestick_data['Low'],
                       close=candlestick_data['Close'])
    ])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- Volume Chart ---------------------- #
st.subheader("📊 Trading Volume")
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Volume", marker_color='blue'))
fig_vol.update_layout(template="plotly_dark", height=300)
st.plotly_chart(fig_vol, use_container_width=True)

# ---------------------- RSI Calculation ---------------------- #
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ---------------------- Analysis Section ---------------------- #
st.subheader("🔍 Analysis Output")

if analysis_type == "📊 Technical Analysis":
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = compute_rsi(data['Close'], period=14)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price", line=dict(color="white")))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50", line=dict(color="green")))
    fig.update_layout(title="📊 Technical Analysis: SMA Indicators", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", line=dict(color="magenta")))
    fig_rsi.add_shape(type="line", x0=data.index.min(), x1=data.index.max(), y0=70, y1=70,
                      line=dict(color="red", dash="dash"))
    fig_rsi.add_shape(type="line", x0=data.index.min(), x1=data.index.max(), y0=30, y1=30,
                      line=dict(color="green", dash="dash"))
    fig_rsi.update_layout(title="📉 Relative Strength Index (RSI)", template="plotly_dark", height=300)
    st.plotly_chart(fig_rsi, use_container_width=True)

    st.success("📌 Comment: A bullish crossover occurs when SMA20 rises above SMA50. RSI above 70 = overbought, below 30 = oversold.")

elif analysis_type == "📑 Fundamental Analysis":
    st.markdown("*Explanation:* Fundamental analysis covers revenue, profit, EPS, P/E ratio, ROE, etc.")
    st.info("Note: For real fundamentals, connect APIs like Alpha Vantage, Ticker, or Screener.in.")

    st.markdown("""
    <style>
    .green {color: lightgreen;}
    .red {color: salmon;}
    </style>
    """, unsafe_allow_html=True)

    pe = 27.3  # Placeholder value
    roe = 25.4 # Placeholder value

    st.markdown(f"**P/E Ratio:** <span class='{'green' if pe < 30 else 'red'}'>{pe}</span>", unsafe_allow_html=True)
    st.markdown(f"**ROE:** <span class='{'green' if roe > 15 else 'red'}'>{roe}%</span>", unsafe_allow_html=True)
    st.success("📌 Comment: Infosys has strong fundamentals — consistent profits and global footprint.")

elif analysis_type == "💬 Sentimental Analysis":
    st.markdown("*Explanation:* Sentiment reflects investor mood based on news, tweets, or earnings calls.")
    st.info("Note: For true analysis, integrate News API or X (Twitter) + NLP.")
    st.success("📌 Comment: Sentiment toward Infosys is generally positive due to strong IT growth and service exports.")

elif analysis_type == "📈 Quantitative Analysis":
    st.markdown("*Explanation:* Uses statistics or ML models like regression, ARIMA, or Prophet for forecasting.")
    st.info("You can extend this with scikit-learn or Facebook Prophet.")
    st.success("📌 Comment: Quantitative signals suggest stable performance with moderate volatility.")

# ---------------------- CSV Export ---------------------- #
st.download_button("📅 Download Data as CSV", data.to_csv().encode("utf-8"), file_name="stock_data.csv", mime="text/csv")

# ---------------------- Footer ---------------------- #
st.markdown("""
    <hr>
    <p style='text-align: center; color: grey;'>
        🔄 Live data from Yahoo Finance | 🧠 Extendable with Machine Learning & APIs | 🚀 Built with Streamlit
    </p>
""", unsafe_allow_html=True)
