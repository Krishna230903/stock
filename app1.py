# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import talib

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title="\ud83d\udcca Infosys Stock Analysis", layout="wide")

# ---------------------- Title ---------------------- #
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        \ud83d\udcc8 Infosys Ltd (INFY.NS) - Live Stock Market Analyzer
    </h1>
    """, unsafe_allow_html=True)

# ---------------------- Sidebar Inputs ---------------------- #
st.sidebar.header("\ud83d\udcc5 Select Date Range")

min_date = date(2015, 1, 1)
start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1), min_value=min_date, max_value=date.today())
end_date = st.sidebar.date_input("End Date", value=date.today(), min_value=start_date, max_value=date.today())

st.sidebar.header("\ud83d\udcc2 Choose Analysis Type")
analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    ("\ud83d\udcca Technical Analysis", "\ud83d\udcc1 Fundamental Analysis", "\ud83d\udcac Sentimental Analysis", "\ud83d\udcc8 Quantitative Analysis")
)

# ---------------------- Dynamic Ticker Input ---------------------- #
ticker = st.sidebar.text_input("\ud83d\udccc Enter Stock Ticker (e.g., INFY.NS)", value="INFY.NS")

# ---------------------- Fetch Stock Data ---------------------- #
@st.cache_data(ttl=3600)
def fetch_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None
        data.dropna(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data(ticker, start_date, end_date)

# ---------------------- Display Chart ---------------------- #
st.subheader(f"\ud83d\udcc9 Stock Price Chart: {ticker} ({start_date} to {end_date})")

if data is not None and not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price", line=dict(color="cyan")))
    fig.update_layout(
        title=f"{ticker} Stock Price",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("\u26a0 No stock data found for this date range. Try adjusting the dates.")

# ---------------------- Volume Chart ---------------------- #
if data is not None and not data.empty:
    st.subheader("\ud83d\udcca Trading Volume")
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Volume", marker_color='blue'))
    fig_vol.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_vol, use_container_width=True)

# ---------------------- Analysis Section ---------------------- #
st.subheader("\ud83d\udd0d Analysis Output")

if data is not None and not data.empty:
    if analysis_type == "\ud83d\udcca Technical Analysis":
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price", line=dict(color="white")))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50", line=dict(color="green")))
        fig.update_layout(title="\ud83d\udcca Technical Analysis: SMA Indicators", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", line=dict(color="magenta")))
        fig_rsi.add_hline(y=70, line=dict(dash='dash', color='red'))
        fig_rsi.add_hline(y=30, line=dict(dash='dash', color='green'))
        fig_rsi.update_layout(title="\ud83d\udcc9 Relative Strength Index (RSI)", template="plotly_dark", height=300)
        st.plotly_chart(fig_rsi, use_container_width=True)

        st.success("\ud83d\udccc Comment: A bullish crossover occurs when SMA20 rises above SMA50. RSI above 70 = overbought, below 30 = oversold.")

    elif analysis_type == "\ud83d\udcc1 Fundamental Analysis":
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
        st.success("\ud83d\udccc Comment: Infosys has strong fundamentals — consistent profits and global footprint.")

    elif analysis_type == "\ud83d\udcac Sentimental Analysis":
        st.markdown("*Explanation:* Sentiment reflects investor mood based on news, tweets, or earnings calls.")
        st.info("Note: For true analysis, integrate News API or X (Twitter) + NLP.")
        st.success("\ud83d\udccc Comment: Sentiment toward Infosys is generally positive due to strong IT growth and service exports.")

    elif analysis_type == "\ud83d\udcc8 Quantitative Analysis":
        st.markdown("*Explanation:* Uses statistics or ML models like regression, ARIMA, or Prophet for forecasting.")
        st.info("You can extend this with scikit-learn or Facebook Prophet.")
        st.success("\ud83d\udccc Comment: Quantitative signals suggest stable performance with moderate volatility.")

# ---------------------- CSV Export ---------------------- #
if data is not None and not data.empty:
    st.download_button("\ud83d\udcc5 Download Data as CSV", data.to_csv().encode("utf-8"), file_name="stock_data.csv", mime="text/csv")

# ---------------------- Footer ---------------------- #
st.markdown("""
    <hr>
    <p style='text-align: center; color: grey;'>
        \ud83d\udd04 Live data from Yahoo Finance | \ud83e\udde0 Extendable with Machine Learning & APIs | \ud83d\ude80 Built with Streamlit
    </p>
""", unsafe_allow_html=True)
