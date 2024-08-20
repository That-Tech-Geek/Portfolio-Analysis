import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np

# Function to calculate DCF
def calculate_dcf(cash_flow, growth_rate, discount_rate, terminal_growth_rate, years=5):
    dcf_value = 0
    for year in range(1, years + 1):
        dcf_value += cash_flow * (1 + growth_rate) ** year / (1 + discount_rate) ** year
    terminal_value = (cash_flow * (1 + growth_rate) ** years * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    dcf_value += terminal_value / (1 + discount_rate) ** years
    return dcf_value

# Function to calculate ROE using DuPont Analysis
def calculate_roe(income_statement, balance_sheet):
    profit_margin = income_statement['Net Income'] / income_statement['Revenue']
    asset_turnover = income_statement['Revenue'] / balance_sheet['Total Assets']
    equity_multiplier = balance_sheet['Total Assets'] / balance_sheet['Total Shareholder Equity']
    roe = profit_margin * asset_turnover * equity_multiplier
    return roe

# Streamlit App
st.title('Investment Analysis using DuPont and DCF')

# Get user input for the ticker
ticker = st.text_input('Enter the stock ticker:', 'AAPL')

if ticker:
    # Fetch data
    company = yf.Ticker(ticker)
    
    # Get financials
    income_statement = company.financials.T
    balance_sheet = company.balance_sheet.T
    cash_flow_statement = company.cashflow.T
    
    # Get share price data
    historical_prices = company.history(period="5y")
    
    # Display Financial Statements
    st.header(f"{ticker} Financial Statements")
    
    st.subheader("Income Statement")
    st.dataframe(income_statement)
    
    st.subheader("Balance Sheet")
    st.dataframe(balance_sheet)
    
    st.subheader("Cash Flow Statement")
    st.dataframe(cash_flow_statement)
    
    # DuPont Analysis
    st.header('DuPont Analysis')
    roe = calculate_roe(income_statement, balance_sheet)
    st.write(f'Return on Equity (ROE): {roe:.2%}')
    
    # DCF Analysis
    st.header('Discounted Cash Flow (DCF) Analysis')
    
    # Assume some basic parameters for DCF
    last_year_cash_flow = cash_flow_statement['Total Cash From Operating Activities'].iloc[0]
    growth_rate = st.slider('Growth Rate (CAGR)', 0.0, 0.2, 0.05)
    discount_rate = st.slider('Discount Rate', 0.0, 0.2, 0.1)
    terminal_growth_rate = st.slider('Terminal Growth Rate', 0.0, 0.1, 0.02)
    
    dcf_value = calculate_dcf(last_year_cash_flow, growth_rate, discount_rate, terminal_growth_rate)
    
    st.write(f"DCF Value: ${dcf_value:,.2f}")
    
    # Current Share Price
    current_price = historical_prices['Close'].iloc[-1]
    st.write(f"Current Share Price: ${current_price:,.2f}")
    
    # Decision based on DCF
    if dcf_value > current_price:
        st.success("The stock appears to be undervalued. It might be worth investing in.")
    else:
        st.warning("The stock appears to be overvalued. Caution is advised before investing.")

