import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to get financial data
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch and transpose dataframes
    financials = stock.financials.T
    balance_sheet = stock.balance_sheet.T
    cashflow_statement = stock.cashflow.T

    # Replace missing values with default values
    financials = financials.fillna(0)
    balance_sheet = balance_sheet.fillna(0)
    cashflow_statement = cashflow_statement.fillna(0)
    
    return financials, balance_sheet, cashflow_statement

# Function to get additional data if missing
def fetch_additional_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch additional data
    market_cap = stock.info.get('marketCap', 0)  # Get market cap from stock info
    return {
        'Market Cap': market_cap
    }

# Function for DuPont Analysis
def dupont_analysis(financials, balance_sheet):
    # Use default value 0 if data is missing
    income_statement = financials.loc['Net Income'].values[0] if 'Net Income' in financials.index else 0
    revenue = financials.loc['Total Revenue'].values[0] if 'Total Revenue' in financials.index else 0
    total_assets = balance_sheet.loc['Total Assets'].values[0] if 'Total Assets' in balance_sheet.index else 0
    total_equity = balance_sheet.loc['Total Stockholder Equity'].values[0] if 'Total Stockholder Equity' in balance_sheet.index else 0
    
    # Avoid division by zero
    net_profit_margin = income_statement / revenue if revenue != 0 else 0
    asset_turnover = revenue / total_assets if total_assets != 0 else 0
    equity_multiplier = total_assets / total_equity if total_equity != 0 else 0
    
    # Return on Equity (ROE)
    roe = net_profit_margin * asset_turnover * equity_multiplier
    
    return {
        'Net Profit Margin': net_profit_margin,
        'Asset Turnover': asset_turnover,
        'Equity Multiplier': equity_multiplier,
        'ROE': roe
    }

# Function for DCF Analysis
def dcf_analysis(financials, balance_sheet, discount_rate=0.1, terminal_growth_rate=0.02):
    # Use default value 0 if data is missing
    free_cash_flow = financials.loc['Free Cash Flow'].values if 'Free Cash Flow' in financials.index else [0]
    if len(free_cash_flow) < 0:
        st.error("Not enough Free Cash Flow data to perform DCF analysis.")
        return None

    growth_rate = np.mean(np.diff(free_cash_flow) / free_cash_flow[:-1]) if len(free_cash_flow) > 1 else 0

    # Project future cash flows
    future_cash_flows = [free_cash_flow[-1] * ((1 + growth_rate) ** (i + 1)) for i in range(5)]
    
    # Terminal value
    terminal_value = future_cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    
    # Discount the future cash flows to present value
    discounted_cash_flows = [cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(future_cash_flows)]
    discounted_terminal_value = terminal_value / (1 + discount_rate) ** len(future_cash_flows)
    
    # Sum of discounted cash flows and terminal value
    dcf_value = sum(discounted_cash_flows) + discounted_terminal_value
    
    # Compare with current market capitalization
    market_cap = balance_sheet.loc['Market Cap'].values[0] if 'Market Cap' in balance_sheet.index else fetch_additional_data(ticker)['Market Cap']
    
    return {
        'DCF Value': dcf_value,
        'Market Cap': market_cap,
        'Undervalued/Overvalued': 'Undervalued' if market_cap and dcf_value > market_cap else 'Overvalued'
    }

# Streamlit app
def main():
    st.title('Investment Analysis using DuPont and DCF')
    
    ticker = st.text_input('Enter the stock ticker symbol:', 'AAPL').upper()
    
    if ticker:
        try:
            # Fetch financial data
            financials, balance_sheet, cashflow_statement = get_financial_data(ticker)
            
            # Make datasets editable
            st.header(f'Financial Statements for {ticker}')
            st.subheader('Income Statement')
            financials_editable = st.data_editor(financials, use_container_width=True)
            
            st.subheader('Balance Sheet')
            balance_sheet_editable = st.data_editor(balance_sheet, use_container_width=True)
            
            st.subheader('Cash Flow Statement')
            cashflow_statement_editable = st.data_editor(cashflow_statement, use_container_width=True)
            
            # DuPont Analysis
            st.header(f'DuPont Analysis for {ticker}')
            dupont_results = dupont_analysis(financials_editable, balance_sheet_editable)
            if dupont_results:
                for key, value in dupont_results.items():
                    st.write(f"{key}: {value:.2f}")
            
            # DCF Analysis
            st.header(f'DCF Analysis for {ticker}')
            dcf_results = dcf_analysis(financials_editable, balance_sheet_editable)
            if dcf_results:
                for key, value in dcf_results.items():
                    st.write(f"{key}: {value:,.2f}" if isinstance(value, (int, float)) else f"{key}: {value}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
