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
    
    # Merge weekly and monthly returns back into the original dataset
    data = data.join(weekly_data[['Weekly Return']], how='left')
    data = data.join(monthly_data[['Monthly Return']], how='left')
    
    return data, weekly_data, monthly_data

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

# Streamlit UI
st.title("Financial Analysis Dashboard")
st.subheader("This is your one-stop solution to understanding everything you'd want on a company!")
st.write("Note: This program is built for educational/research services and is not to be held liable for any losses and/or damages to the user")

# Input for ticker symbol
ticker = st.text_input("Enter the ticker symbol:", "AAPL")

# Fetching data
stock_data, weekly_data, monthly_data = get_stock_data(ticker)
metrics_df = get_key_metrics(ticker)
profit_loss_df = get_profit_loss(ticker)

# Displaying the stock data
st.header(f"Stock Data for {ticker}")
st.write(stock_data)

# Plotting Stock Data with Plotly
st.subheader(f"{ticker} Stock Price and Moving Averages")
stock_fig = go.Figure()
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adjusted Close'))
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['50-Day Moving Avg'], mode='lines', name='50-Day Moving Avg'))
stock_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['200-Day Moving Avg'], mode='lines', name='200-Day Moving Avg'))
stock_fig.update_layout(title=f'{ticker} Stock Price and Moving Averages', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(stock_fig)

# Plotting Returns
st.subheader(f"{ticker} Returns")
returns_fig = go.Figure()
returns_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Weekly Return'], mode='lines', name='Weekly Return'))
returns_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Monthly Return'], mode='lines', name='Monthly Return'))
returns_fig.update_layout(title=f'{ticker} Returns', xaxis_title='Date', yaxis_title='Return')
st.plotly_chart(returns_fig)

# Correlation Heatmaps
def plot_correlation_heatmap(df, title):
    corr = df.corr()
    heatmap_fig = px.imshow(corr, text_auto=True, color_continuous_scale='Viridis', aspect='auto')
    heatmap_fig.update_layout(title=title, xaxis_title='Variables', yaxis_title='Variables')
    return heatmap_fig

# Displaying Correlation Heatmaps
st.header(f"Correlation Heatmaps for {ticker}")

# Stock Data Correlation
st.subheader("Correlation Heatmap of Stock Data")
stock_corr_fig = plot_correlation_heatmap(stock_data, f'{ticker} Stock Data Correlation Heatmap')
st.plotly_chart(stock_corr_fig)

# Weekly Returns Correlation
st.subheader("Correlation Heatmap of Weekly Returns")
weekly_corr_fig = plot_correlation_heatmap(weekly_data, f'{ticker} Weekly Returns Correlation Heatmap')
st.plotly_chart(weekly_corr_fig)

# Monthly Returns Correlation
st.subheader("Correlation Heatmap of Monthly Returns")
monthly_corr_fig = plot_correlation_heatmap(monthly_data, f'{ticker} Monthly Returns Correlation Heatmap')
st.plotly_chart(monthly_corr_fig)

# Key Metrics Correlation
st.subheader("Correlation Heatmap of Key Metrics")
st.write(metrics_df.T)  # Transposed for better readability
metrics_corr_fig = plot_correlation_heatmap(metrics_df.T, f'{ticker} Key Metrics Correlation Heatmap')
st.plotly_chart(metrics_corr_fig)

# Displaying and plotting annual statement data
st.header(f"Annual Statement Data for {ticker}")
st.write(profit_loss_df)

st.subheader(f"{ticker} Profit and Loss Over Time")
pl_fig = go.Figure()
for column in profit_loss_df.columns:
    pl_fig.add_trace(go.Scatter(x=profit_loss_df.index, y=profit_loss_df[column], mode='lines', name=column))
pl_fig.update_layout(title=f'{ticker} Profit and Loss Over Time', xaxis_title='Date', yaxis_title='Amount (in $)')
st.plotly_chart(pl_fig)

# Displaying key metrics
st.header(f"Key Metrics for {ticker}")
st.write(metrics_df)
