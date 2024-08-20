import streamlit as st
import yfinance as yf
import numpy as np

# Helper function to extract the closest match for financial metrics
def get_closest_match(data, search_term):
    for term in data.index:
        if search_term.lower() in term.lower():
            return data.loc[term].iloc[0]
    return None

# Function to calculate DCF
def calculate_dcf(cash_flow, growth_rate, discount_rate, terminal_growth_rate, years=5):
    dcf_value = 0
    for year in range(1, years + 1):
        dcf_value += cash_flow * (1 + growth_rate) ** year / (1 + discount_rate) ** year
    terminal_value = (cash_flow * (1 + growth_rate) ** years * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    dcf_value += terminal_value / (1 + discount_rate) ** years
    return dcf_value

# Function to calculate ROE using DuPont Analysis
def calculate_roe(ticker):
    company = yf.Ticker(ticker)
    
    # Extract relevant data directly using yfinance methods
    net_income = get_closest_match(company.financials, 'Net Income')
    revenue = get_closest_match(company.financials, 'Total Revenue')
    total_assets = get_closest_match(company.balance_sheet, 'Total Assets')
    total_equity = get_closest_match(company.balance_sheet, 'Total Stockholder Equity')
    
    if None in (net_income, revenue, total_assets, total_equity):
        st.error("Some financial metrics could not be found. Please verify the data.")
        return None
    
    # DuPont components
    profit_margin = net_income / revenue
    asset_turnover = revenue / total_assets
    equity_multiplier = total_assets / total_equity
    
    roe = profit_margin * asset_turnover * equity_multiplier
    return roe

# Streamlit App
st.title('Investment Analysis using DuPont and DCF')

# Get user input for the ticker
ticker = st.text_input('Enter the stock ticker:', 'AAPL')

if ticker:
    company = yf.Ticker(ticker)
    
    # Get financials
    cash_flow_statement = company.cashflow
    
    # Get share price data
    historical_prices = company.history(period="5y")
    
    # Display Financial Statements
    st.header(f"{ticker} Financial Statements")
    
    st.subheader("Cash Flow Statement")
    st.dataframe(cash_flow_statement)
    
    # DuPont Analysis
    st.header('DuPont Analysis')
    roe = calculate_roe(ticker)
    if roe:
        st.write(f'Return on Equity (ROE): {roe:.2%}')
    
    # DCF Analysis
    st.header('Discounted Cash Flow (DCF) Analysis')
    
    # Assume some basic parameters for DCF
    last_year_cash_flow = get_closest_match(cash_flow_statement, 'Total Cash From Operating Activities')
    growth_rate = st.slider('Growth Rate (CAGR)', 0.0, 0.2, 0.05)
    discount_rate = st.slider('Discount Rate', 0.0, 0.2, 0.1)
    terminal_growth_rate = st.slider('Terminal Growth Rate', 0.0, 0.1, 0.02)
    
    if last_year_cash_flow:
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
    else:
        st.error("Unable to retrieve necessary cash flow data for DCF analysis.")
