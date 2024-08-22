import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Function to calculate returns
def calculate_returns(data):
    daily_return = data['Adj Close'].pct_change().dropna().rename("Daily Return")
    weekly_return = data['Adj Close'].resample('W').ffill().pct_change().dropna().rename("Weekly Return")
    monthly_return = data['Adj Close'].resample('M').ffill().pct_change().dropna().rename("Monthly Return")
    return daily_return, weekly_return, monthly_return

# Function to fetch key metrics (using financials and key statistics)
def get_key_metrics(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.transpose()
    balance_sheet = stock.balance_sheet.transpose()
    cashflow = stock.cashflow.transpose()
    info = stock.info
    
    # Safely calculate metrics with default values if data is missing
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

# Function to fetch profit and loss statement
def get_profit_loss(ticker):
    stock = yf.Ticker(ticker)
    return stock.financials.transpose()

# Function to fetch peers
def get_peers(ticker):
    stock = yf.Ticker(ticker)
    return stock.get_info().get('symbol', [])

# Function to perform peer comparison
def peer_comparison(ticker):
    peers = get_peers(ticker)
    metrics = {}
    for peer in peers:
        metrics[peer] = get_key_metrics(peer)
    return pd.concat(metrics.values(), axis=1) if metrics else pd.DataFrame()

# Streamlit UI
st.title("Financial Analysis Dashboard")

# Input for ticker symbol
ticker = st.text_input("Enter the ticker symbol:", "AAPL")

# Fetching data from yfinance
data = yf.download(ticker, period='5y', progress=False)

# Calculate additional stock data
data['50-Day Moving Avg'] = data['Adj Close'].rolling(window=50).mean()
data['200-Day Moving Avg'] = data['Adj Close'].rolling(window=200).mean()
data['Daily Volume'] = data['Volume']

# Calculate returns
daily_return, weekly_return, monthly_return = calculate_returns(data)

# Fetch key metrics and profit & loss statement
metrics_df = get_key_metrics(ticker)
profit_loss_df = get_profit_loss(ticker)

# Combine all data into one dataset
combined_df = pd.DataFrame(index=data.index)
combined_df = combined_df.join(data[['Adj Close', 'Daily Volume', '50-Day Moving Avg', '200-Day Moving Avg']], how='outer')
combined_df = combined_df.join(daily_return, how='outer')
combined_df = combined_df.join(weekly_return, how='outer')
combined_df = combined_df.join(monthly_return, how='outer')
combined_df = pd.concat([combined_df, metrics_df.T], axis=1)
combined_df = pd.concat([combined_df, profit_loss_df], axis=1)

# Displaying the combined data
st.header(f"Combined Financial Data for {ticker}")
st.write(combined_df)

# Peer Comparison
st.header(f"Peer Comparison for {ticker}")
peer_comparison_df = peer_comparison(ticker)
if peer_comparison_df.empty:
    st.write("No peers found or no data available for peers.")
else:
    st.write(peer_comparison_df)
