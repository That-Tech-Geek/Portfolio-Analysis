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

# Function to calculate a comprehensive list of financial ratios
def calculate_financial_ratios(ticker):
    financials, balance_sheet, cashflow_statement = get_financial_data(ticker)
    
    # Select the last 4 years of data
    last_4_years = balance_sheet.index[:4]
    
    ratios = pd.DataFrame(index=last_4_years)
    
    # Data fields (assume all fields exist in balance_sheet, financials, and cashflow_statement)
    current_assets = balance_sheet.get('Total Current Assets', pd.Series([np.nan]))
    current_liabilities = balance_sheet.get('Total Current Liabilities', pd.Series([np.nan]))
    total_assets = balance_sheet.get('Total Assets', pd.Series([np.nan]))
    total_liabilities = balance_sheet.get('Total Liabilities Net Minority Interest', pd.Series([np.nan]))
    cash = balance_sheet.get('Cash', pd.Series([np.nan])) + balance_sheet.get('Cash And Cash Equivalents', pd.Series([np.nan]))
    short_term_investments = balance_sheet.get('Short Term Investments', pd.Series([np.nan]))
    total_equity = balance_sheet.get('Total Stockholder Equity', pd.Series([np.nan]))
    total_debt = balance_sheet.get('Total Debt', pd.Series([np.nan]))
    retained_earnings = balance_sheet.get('Retained Earnings', pd.Series([np.nan]))
    ebit = financials.get('EBIT', pd.Series([np.nan]))
    net_income = financials.get('Net Income', pd.Series([np.nan]))
    revenue = financials.get('Total Revenue', pd.Series([np.nan]))
    cogs = financials.get('Cost Of Revenue', pd.Series([np.nan]))
    operating_expenses = financials.get('Total Operating Expenses', pd.Series([np.nan]))
    gross_profit = financials.get('Gross Profit', pd.Series([np.nan]))
    interest_expense = financials.get('Interest Expense', pd.Series([np.nan]))
    ebitda = financials.get('EBITDA', pd.Series([np.nan]))
    dividends_paid = cashflow_statement.get('Dividends Paid', pd.Series([np.nan]))
    capital_expenditures = cashflow_statement.get('Capital Expenditures', pd.Series([np.nan]))

    # Calculate financial ratios

    # Liquidity Ratios
    ratios['Current Ratio'] = current_assets / current_liabilities
    ratios['Quick Ratio'] = (cash + short_term_investments) / current_liabilities
    ratios['Cash Ratio'] = cash / current_liabilities

    # Leverage Ratios
    ratios['Debt to Equity Ratio'] = total_debt / total_equity
    ratios['Debt to Assets Ratio'] = total_debt / total_assets
    ratios['Equity Ratio'] = total_equity / total_assets
    ratios['Financial Leverage Ratio'] = total_assets / total_equity
    ratios['Interest Coverage Ratio'] = ebit / interest_expense

    # Profitability Ratios
    ratios['Gross Profit Margin'] = gross_profit / revenue
    ratios['Operating Profit Margin'] = ebit / revenue
    ratios['Net Profit Margin'] = net_income / revenue
    ratios['Return on Assets (ROA)'] = net_income / total_assets
    ratios['Return on Equity (ROE)'] = net_income / total_equity
    ratios['Return on Capital Employed (ROCE)'] = ebit / (total_assets - current_liabilities)

    # Efficiency Ratios
    ratios['Asset Turnover Ratio'] = revenue / total_assets
    ratios['Inventory Turnover Ratio'] = cogs / balance_sheet.get('Inventory', pd.Series([np.nan]))
    ratios['Receivables Turnover Ratio'] = revenue / balance_sheet.get('Net Receivables', pd.Series([np.nan]))
    ratios['Payables Turnover Ratio'] = cogs / balance_sheet.get('Accounts Payable', pd.Series([np.nan]))
    ratios['Working Capital Turnover Ratio'] = revenue / (current_assets - current_liabilities)

    # Dividend Ratios
    ratios['Dividend Payout Ratio'] = -dividends_paid / net_income
    ratios['Retention Ratio'] = retained_earnings / net_income

    # Coverage Ratios
    ratios['Cash Flow Coverage Ratio'] = (cashflow_statement.get('Operating Cash Flow', pd.Series([np.nan])) - capital_expenditures) / total_debt
    ratios['Fixed Charge Coverage Ratio'] = (ebit + interest_expense) / (interest_expense + dividends_paid)

    # Valuation Ratios
    stock = yf.Ticker(ticker)
    market_price = stock.history(period='1d')['Close'].iloc[-1]
    shares_outstanding = stock.info.get('sharesOutstanding', np.nan)
    earnings_per_share = net_income / shares_outstanding
    book_value_per_share = total_equity / shares_outstanding
    dividends_per_share = -dividends_paid / shares_outstanding
    ratios['Price to Earnings Ratio (P/E)'] = market_price / earnings_per_share
    ratios['Price to Book Ratio (P/B)'] = market_price / book_value_per_share
    ratios['Dividend Yield'] = dividends_per_share / market_price
    ratios['Earnings Yield'] = earnings_per_share / market_price

    # Only return the last 4 years of ratios
    return ratios.head(4)

# Streamlit app
def main():
    st.title('Comprehensive Financial Analysis')
    st.write("Analyze a company's financial performance with a detailed set of ratios.")
    
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
