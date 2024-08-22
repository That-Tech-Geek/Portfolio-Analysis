import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Sidebar for ticker selection
st.sidebar.title("Stock Analysis")
ticker = st.sidebar.text_input("Enter Ticker", value="AAPL", max_chars=10)
period = st.sidebar.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "6mo", "YTD", "1y", "5y", "max"])

# Fetching data
st.write(f"### Stock Analysis for {ticker}")
data = yf.download(ticker, period=period)

# Line chart for closing prices
st.subheader(f"Closing Prices for {ticker}")
fig = go.Figure(data=go.Scatter(x=data.index, y=data['Close'], mode='lines'))
st.plotly_chart(fig)

# Display financial ratios
st.subheader(f"Financial Ratios for {ticker}")
info = yf.Ticker(ticker).info
st.write(pd.DataFrame({
    'P/E Ratio': [info.get('trailingPE')],
    'P/B Ratio': [info.get('priceToBook')],
    'ROE': [info.get('returnOnEquity')],
    'Market Cap': [info.get('marketCap')]
}))

# Additional features to be added...
