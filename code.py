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
    
    # Create a DataFrame to store ratios
    ratios = pd.DataFrame(index=last_4_years)
    
    # Data fields
    current_assets = balance_sheet.get('Total Current Assets', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    current_liabilities = balance_sheet.get('Total Current Liabilities', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    total_assets = balance_sheet.get('Total Assets', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    total_liabilities = balance_sheet.get('Total Liabilities Net Minority Interest', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    cash = (balance_sheet.get('Cash', pd.Series([np.nan] * len(last_4_years), index=last_4_years)) +
            balance_sheet.get('Cash And Cash Equivalents', pd.Series([np.nan] * len(last_4_years), index=last_4_years)))
    short_term_investments = balance_sheet.get('Short Term Investments', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    total_equity = balance_sheet.get('Total Stockholder Equity', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    total_debt = balance_sheet.get('Total Debt', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    retained_earnings = balance_sheet.get('Retained Earnings', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    ebit = financials.get('EBIT', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    net_income = financials.get('Net Income', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    revenue = financials.get('Total Revenue', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    cogs = financials.get('Cost Of Revenue', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    operating_expenses = financials.get('Total Operating Expenses', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    gross_profit = financials.get('Gross Profit', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    interest_expense = financials.get('Interest Expense', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    ebitda = financials.get('EBITDA', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    dividends_paid = cashflow_statement.get('Dividends Paid', pd.Series([np.nan] * len(last_4_years), index=last_4_years))
    capital_expenditures = cashflow_statement.get('Capital Expenditures', pd.Series([np.nan] * len(last_4_years), index=last_4_years))

    # Calculate financial ratios

    # Liquidity Ratios
    ratios['Current Ratio'] = np.where(current_liabilities != 0, current_assets / current_liabilities, np.nan)
    ratios['Quick Ratio'] = np.where(current_liabilities != 0, (cash + short_term_investments) / current_liabilities, np.nan)
    ratios['Cash Ratio'] = np.where(current_liabilities != 0, cash / current_liabilities, np.nan)

    # Leverage Ratios
    ratios['Debt to Equity Ratio'] = np.where(total_equity != 0, total_debt / total_equity, np.nan)
    ratios['Debt to Assets Ratio'] = np.where(total_assets != 0, total_debt / total_assets, np.nan)
    ratios['Equity Ratio'] = np.where(total_assets != 0, total_equity / total_assets, np.nan)
    ratios['Financial Leverage Ratio'] = np.where(total_equity != 0, total_assets / total_equity, np.nan)
    ratios['Interest Coverage Ratio'] = np.where(interest_expense != 0, ebit / interest_expense, np.nan)

    # Profitability Ratios
    ratios['Gross Profit Margin'] = np.where(revenue != 0, gross_profit / revenue, np.nan)
    ratios['Operating Profit Margin'] = np.where(revenue != 0, ebit / revenue, np.nan)
    ratios['Net Profit Margin'] = np.where(revenue != 0, net_income / revenue, np.nan)
    ratios['Return on Assets (ROA)'] = np.where(total_assets != 0, net_income / total_assets, np.nan)
    ratios['Return on Equity (ROE)'] = np.where(total_equity != 0, net_income / total_equity, np.nan)
    ratios['Return on Capital Employed (ROCE)'] = np.where((total_assets - current_liabilities) != 0, ebit / (total_assets - current_liabilities), np.nan)

    # Efficiency Ratios
    ratios['Asset Turnover Ratio'] = np.where(total_assets != 0, revenue / total_assets, np.nan)
    ratios['Inventory Turnover Ratio'] = np.where(balance_sheet.get('Inventory', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan) != 0, cogs / balance_sheet.get('Inventory', pd.Series([np.nan] * len(last_4_years), index=last_4_years)), np.nan)
    ratios['Receivables Turnover Ratio'] = np.where(balance_sheet.get('Net Receivables', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan) != 0, revenue / balance_sheet.get('Net Receivables', pd.Series([np.nan] * len(last_4_years), index=last_4_years)), np.nan)
    ratios['Payables Turnover Ratio'] = np.where(balance_sheet.get('Accounts Payable', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan) != 0, cogs / balance_sheet.get('Accounts Payable', pd.Series([np.nan] * len(last_4_years), index=last_4_years)), np.nan)
    ratios['Working Capital Turnover Ratio'] = np.where((current_assets - current_liabilities).replace(0, np.nan) != 0, revenue / (current_assets - current_liabilities), np.nan)

    # Dividend Ratios
    ratios['Dividend Payout Ratio'] = np.where(net_income.replace(0, np.nan) != 0, -dividends_paid / net_income, np.nan)
    ratios['Retention Ratio'] = np.where(net_income.replace(0, np.nan) != 0, retained_earnings / net_income, np.nan)

    # Coverage Ratios
    ratios['Cash Flow Coverage Ratio'] = np.where(total_debt.replace(0, np.nan) != 0, (cashflow_statement.get('Operating Cash Flow', pd.Series([np.nan] * len(last_4_years), index=last_4_years)) - capital_expenditures) / total_debt, np.nan)
    ratios['Fixed Charge Coverage Ratio'] = np.where((interest_expense + dividends_paid).replace(0, np.nan) != 0, (ebit + interest_expense) / (interest_expense + dividends_paid), np.nan)

    # Valuation Ratios
    stock = yf.Ticker(ticker)
    market_price = stock.history(period='1d')['Close'].iloc[-1]
    shares_outstanding = stock.info.get('sharesOutstanding', np.nan)
    earnings_per_share = np.where(shares_outstanding != 0, net_income / shares_outstanding, np.nan)
    book_value_per_share = np.where(shares_outstanding != 0, total_equity / shares_outstanding, np.nan)
    dividends_per_share = np.where(shares_outstanding != 0, -dividends_paid / shares_outstanding, np.nan)
    ratios['Price to Earnings Ratio (P/E)'] = np.where(earnings_per_share.replace(0, np.nan) != 0, market_price / earnings_per_share, np.nan)
    ratios['Price to Book Ratio (P/B)'] = np.where(book_value_per_share.replace(0, np.nan) != 0, market_price / book_value_per_share, np.nan)
    ratios['Dividend Yield'] = np.where(market_price != 0, dividends_per_share / market_price, np.nan)
    ratios['Earnings Yield'] = np.where(market_price != 0, earnings_per_share / market_price, np.nan)

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
