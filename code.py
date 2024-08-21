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
    current_assets = balance_sheet.get('Total Current Assets', pd.Series([np.nan]))
    current_liabilities = balance_sheet.get('Total Current Liabilities', pd.Series([np.nan]))
    cash = balance_sheet.get('Cash', pd.Series([np.nan])) + balance_sheet.get('Cash And Cash Equivalents', pd.Series([np.nan]))
    short_term_investments = balance_sheet.get('Short Term Investments', pd.Series([np.nan]))
    total_debt = balance_sheet.get('Total Debt', pd.Series([np.nan]))
    total_equity = balance_sheet.get('Total Stockholder Equity', pd.Series([np.nan]))
    net_income = financials.get('Net Income', pd.Series([np.nan]))
    total_assets = balance_sheet.get('Total Assets', pd.Series([np.nan]))
    
    # Calculate Current Ratio
    ratios['Current Ratio'] = current_assets / current_liabilities
    
    # Calculate Quick Ratio
    quick_assets = cash + short_term_investments
    ratios['Quick Ratio'] = quick_assets / current_liabilities
    
    # Calculate Debt to Equity Ratio
    ratios['Debt to Equity Ratio'] = total_debt / total_equity
    
    # Calculate Return on Assets (ROA)
    ratios['Return on Assets (ROA)'] = net_income / total_assets
    
    # Calculate Return on Equity (ROE)
    ratios['Return on Equity (ROE)'] = net_income / total_equity
    
    # Additional ratios can be calculated here with similar checks
    
    # Convert the ratios dictionary to a DataFrame
    ratios_df = pd.DataFrame(ratios)
    
    # Adjust the index to ensure all years are covered, even if missing
    ratios_df.index = pd.to_datetime(ratios_df.index).year
    all_years = pd.Series(index=range(ratios_df.index.min(), ratios_df.index.max() + 1))
    ratios_df = ratios_df.reindex(all_years.index)
    
    # Return the ratios for the most recent period (most recent index)
    return ratios_df

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
