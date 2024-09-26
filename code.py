import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import numpy as np

# Function to fetch stock data and calculate returns
def get_stock_data(ticker):
    data = yf.download(ticker, period='max', progress=False)
    
    # Calculate additional stock data
    data['50-Day Moving Avg'] = data['Adj Close'].rolling(window=50).mean()
    data['200-Day Moving Avg'] = data['Adj Close'].rolling(window=200).mean()
    
    # Calculate daily returns
    data['Daily Return'] = data['Adj Close'].pct_change()
    
    # Calculate weekly returns
    weekly_data = data.resample('W').agg({'Open': 'first', 'Close': 'last'})
    weekly_data['Weekly Return'] = (weekly_data['Close'] / weekly_data['Open']) - 1
    weekly_data = weekly_data.rename(columns={'Open': 'Weekly Open', 'Close': 'Weekly Close'})
    
    # Calculate monthly returns
    monthly_data = data.resample('M').agg({'Open': 'first', 'Close': 'last'})
    monthly_data['Monthly Return'] = (monthly_data['Close'] / monthly_data['Open']) - 1
    monthly_data = monthly_data.rename(columns={'Open': 'Monthly Open', 'Close': 'Monthly Close'})
    
    return data, weekly_data, monthly_data

# Function to fetch key metrics
def get_key_metrics(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.transpose()
    balance_sheet = stock.balance_sheet.transpose()
    cashflow = stock.cashflow.transpose()
    info = stock.info
    
    metrics = {
        'Market Cap': info.get('marketCap', np.nan),
        'P/E Ratio': info.get('trailingPE', np.nan),
        'P/B Ratio': info.get('priceToBook', np.nan),
        'EV/EBITDA': info.get('enterpriseToEbitda', np.nan),
        'Current Ratio': (balance_sheet['Total Current Assets'] / balance_sheet['Total Current Liabilities']) 
                        if 'Total Current Assets' in balance_sheet and 'Total Current Liabilities' in balance_sheet else np.nan,
        'Quick Ratio': ((balance_sheet['Total Current Assets'] - balance_sheet['Inventory']) / balance_sheet['Total Current Liabilities']) 
                       if 'Total Current Assets' in balance_sheet and 'Inventory' in balance_sheet and 'Total Current Liabilities' in balance_sheet else np.nan,
        'Debt to Equity Ratio': (balance_sheet['Total Debt'] / balance_sheet['Total Stockholder Equity']) 
                                if 'Total Debt' in balance_sheet and 'Total Stockholder Equity' in balance_sheet else np.nan,
        'Return on Equity (ROE)': info.get('returnOnEquity', np.nan),
        'Gross Margin': (financials['Gross Profit'] / financials['Total Revenue']) 
                        if 'Gross Profit' in financials and 'Total Revenue' in financials else np.nan,
        'Operating Margin': (financials['Operating Income'] / financials['Total Revenue']) 
                            if 'Operating Income' in financials and 'Total Revenue' in financials else np.nan,
        'Net Profit Margin': (financials['Net Income'] / financials['Total Revenue']) 
                             if 'Net Income' in financials and 'Total Revenue' in financials else np.nan,
        'Return on Assets (ROA)': info.get('returnOnAssets', np.nan),
        'Dividend Yield': info.get('dividendYield', np.nan),
        'Free Cash Flow': cashflow.get('Free Cash Flow', np.nan),
        'Payout Ratio': info.get('payoutRatio', np.nan),
        'EPS': info.get('trailingEps', np.nan),
    }
    
    metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=[ticker])
    
    return metrics_df

# Function to simulate a portfolio
def portfolio_simulation(portfolio, tickers):
    portfolio_value = 0
    portfolio_df = pd.DataFrame(columns=['Ticker', 'Shares', 'Current Price', 'Total Value'])
    
    for ticker, shares in portfolio.items():
        data = yf.download(ticker, period='1d', progress=False)
        current_price = data['Adj Close'].iloc[-1]
        total_value = current_price * shares
        portfolio_value += total_value
        portfolio_df = portfolio_df.append({'Ticker': ticker, 'Shares': shares, 'Current Price': current_price, 'Total Value': total_value}, ignore_index=True)
    
    return portfolio_value, portfolio_df

# Streamlit UI for Portfolio Management
st.title("BSE 500 Real-Time Portfolio Simulator")

# List of BSE 500 tickers (for simplicity, limited to a few here, you can expand this list)
bse_500_tickers = ['RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO']

# Input for portfolio management
portfolio = {}
for ticker in bse_500_tickers:
    shares = st.number_input(f"Enter number of shares for {ticker}:", min_value=0, value=0)
    if shares > 0:
        portfolio[ticker] = shares

# Simulate portfolio based on user input
if st.button("Simulate Portfolio"):
    portfolio_value, portfolio_df = portfolio_simulation(portfolio, bse_500_tickers)
    st.subheader("Portfolio Summary")
    st.write(portfolio_df)
    st.write(f"Total Portfolio Value: ₹{portfolio_value:.2f}")

# Input for individual stock analysis
ticker = st.text_input("Enter a ticker symbol to analyze:", "RELIANCE.BO")

# Fetch stock data and key metrics
stock_data, weekly_data, monthly_data = get_stock_data(ticker)
metrics_df = get_key_metrics(ticker)

# Display stock data
st.header(f"Stock Data for {ticker}")
st.write(stock_data)

# Plot stock prices and moving averages
st.subheader(f"{ticker} Stock Price and Moving Averages")
stock_fig = go.Figure()
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adjusted Close'))
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['50-Day Moving Avg'], mode='lines', name='50-Day Moving Avg'))
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['200-Day Moving Avg'], mode='lines', name='200-Day Moving Avg'))
stock_fig.update_layout(title=f'{ticker} Stock Price and Moving Averages', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(stock_fig)

# Display key metrics
st.header(f"Key Metrics for {ticker}")
st.write(metrics_df)
