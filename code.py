import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to get financial data
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    balance_sheet = stock.balance_sheet.T
    cashflow_statement = stock.cashflow.T
    return financials, balance_sheet, cashflow_statement

# Function for DuPont Analysis
def dupont_analysis(financials, balance_sheet):
    try:
        # Extract values from financials and balance sheet
        net_income = financials.loc['Net Income'].values[0]
        revenue = financials.loc['Total Revenue'].values[0]
        total_assets = balance_sheet.loc['Total Assets'].values[0]
        total_equity = balance_sheet.loc['Total Stockholder Equity'].values[0]
    except KeyError as e:
        st.error(f"Missing data: {e}")
        return None
    
    # Components
    net_profit_margin = net_income / revenue
    asset_turnover = revenue / total_assets
    equity_multiplier = total_assets / total_equity
    
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
    if 'Free Cash Flow' not in financials.index:
        st.error("Free Cash Flow data is missing.")
        return None
    
    free_cash_flow = financials.loc['Free Cash Flow'].values
    growth_rate = (free_cash_flow[1:] / free_cash_flow[:-1] - 1).mean()

    # Project future cash flows
    future_cash_flows = []
    for i in range(5):
        future_cash_flows.append(free_cash_flow[-1] * ((1 + growth_rate) ** (i + 1)))
    
    # Terminal value
    terminal_value = future_cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    
    # Discount the future cash flows to present value
    discounted_cash_flows = [cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(future_cash_flows)]
    discounted_terminal_value = terminal_value / (1 + discount_rate) ** len(future_cash_flows)
    
    # Sum of discounted cash flows and terminal value
    dcf_value = sum(discounted_cash_flows) + discounted_terminal_value
    
    # Compare with current market capitalization
    market_cap = balance_sheet.loc['Market Cap'].values[0] if 'Market Cap' in balance_sheet.index else None
    
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
            financials, balance_sheet, cashflow_statement = get_financial_data(ticker)
            
            st.header(f'Financial Statements for {ticker}')
            
            # Display Income Statement
            st.subheader('Income Statement')
            st.dataframe(financials)
            
            # Display Balance Sheet
            st.subheader('Balance Sheet')
            st.dataframe(balance_sheet)
            
            # Display Cash Flow Statement
            st.subheader('Cash Flow Statement')
            st.dataframe(cashflow_statement)
            
            # DuPont Analysis
            st.header(f'DuPont Analysis for {ticker}')
            dupont_results = dupont_analysis(financials, balance_sheet)
            if dupont_results:
                for key, value in dupont_results.items():
                    st.write(f"{key}: {value:.2f}")
            
            # DCF Analysis
            st.header(f'DCF Analysis for {ticker}')
            dcf_results = dcf_analysis(financials, balance_sheet)
            if dcf_results:
                for key, value in dcf_results.items():
                    st.write(f"{key}: {value:,.2f}" if isinstance(value, (int, float)) else f"{key}: {value}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
