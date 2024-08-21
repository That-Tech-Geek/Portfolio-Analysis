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

    # Ensure all necessary fields are present by filling missing values
    financials.fillna(0, inplace=True)
    balance_sheet.fillna(0, inplace=True)
    cashflow_statement.fillna(0, inplace=True)
    
    return financials, balance_sheet, cashflow_statement

# Function to calculate financial ratios directly from yfinance data
def calculate_financial_ratios(ticker):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet.T
    financials = stock.financials.T
    
    # Ensure data is filled
    balance_sheet.fillna(0, inplace=True)
    financials.fillna(0, inplace=True)

    ratios = {}

    # Directly source necessary data
    current_assets = balance_sheet.get('Total Current Assets', 0)
    current_liabilities = balance_sheet.get('Total Current Liabilities', 0)
    cash = balance_sheet.get('Cash', 0) + balance_sheet.get('Cash And Cash Equivalents', 0)
    short_term_investments = balance_sheet.get('Short Term Investments', 0)
    total_debt = balance_sheet.get('Total Debt', 0)
    total_equity = balance_sheet.get('Total Stockholder Equity', 0)
    net_income = financials.get('Net Income', 0)
    total_assets = balance_sheet.get('Total Assets', 0)
    
    # Calculate Current Ratio
    ratios['Current Ratio'] = current_assets / current_liabilities if current_liabilities != 0 else np.nan
    
    # Calculate Quick Ratio
    quick_assets = cash + short_term_investments
    ratios['Quick Ratio'] = quick_assets / current_liabilities if current_liabilities != 0 else np.nan
    
    # Calculate Debt to Equity Ratio
    ratios['Debt to Equity Ratio'] = total_debt / total_equity if total_equity != 0 else np.nan
    
    # Calculate Return on Assets (ROA)
    ratios['Return on Assets (ROA)'] = net_income / total_assets if total_assets != 0 else np.nan
    
    # Calculate Return on Equity (ROE)
    ratios['Return on Equity (ROE)'] = net_income / total_equity if total_equity != 0 else np.nan
    
    # Additional ratios can be calculated here with similar checks
    
    return pd.DataFrame(ratios, index=[0])

# Streamlit app
def main():
    st.title('Investment Analysis: Analyze everything you need to know about a company, right here!')
    st.write("This is built for educational purposes and is not liable to any losses and/or damages to the user.")
    
    ticker = st.text_input('Enter the stock ticker symbol:', 'RELIANCE.NS').upper()
    
    if ticker:
        try:
            # Fetch financial data
            financials, balance_sheet, cashflow_statement = get_financial_data(ticker)
            
            # Display the financial statements
            st.header(f'Financial Statements for {ticker}')
            st.subheader('Income Statement')
            st.dataframe(financials)
            
            st.subheader('Balance Sheet')
            st.dataframe(balance_sheet)
            
            st.subheader('Cash Flow Statement')
            st.dataframe(cashflow_statement)
            
            # Calculate and display financial ratios
            st.header('Financial Ratios')
            financial_ratios = calculate_financial_ratios(ticker)
            st.dataframe(financial_ratios)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
