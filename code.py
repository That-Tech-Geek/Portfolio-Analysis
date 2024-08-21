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
    ratios['Current Ratio'] = current_assets / current_liabilities.replace(0, np.nan)
    ratios['Quick Ratio'] = (cash + short_term_investments) / current_liabilities.replace(0, np.nan)
    ratios['Cash Ratio'] = cash / current_liabilities.replace(0, np.nan)

    # Leverage Ratios
    ratios['Debt to Equity Ratio'] = total_debt / total_equity.replace(0, np.nan)
    ratios['Debt to Assets Ratio'] = total_debt / total_assets.replace(0, np.nan)
    ratios['Equity Ratio'] = total_equity / total_assets.replace(0, np.nan)
    ratios['Financial Leverage Ratio'] = total_assets / total_equity.replace(0, np.nan)
    ratios['Interest Coverage Ratio'] = ebit / interest_expense.replace(0, np.nan)

    # Profitability Ratios
    ratios['Gross Profit Margin'] = gross_profit / revenue.replace(0, np.nan)
    ratios['Operating Profit Margin'] = ebit / revenue.replace(0, np.nan)
    ratios['Net Profit Margin'] = net_income / revenue.replace(0, np.nan)
    ratios['Return on Assets (ROA)'] = net_income / total_assets.replace(0, np.nan)
    ratios['Return on Equity (ROE)'] = net_income / total_equity.replace(0, np.nan)
    ratios['Return on Capital Employed (ROCE)'] = ebit / (total_assets - current_liabilities).replace(0, np.nan)

    # Efficiency Ratios
    ratios['Asset Turnover Ratio'] = revenue / total_assets.replace(0, np.nan)
    ratios['Inventory Turnover Ratio'] = cogs / balance_sheet.get('Inventory', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan)
    ratios['Receivables Turnover Ratio'] = revenue / balance_sheet.get('Net Receivables', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan)
    ratios['Payables Turnover Ratio'] = cogs / balance_sheet.get('Accounts Payable', pd.Series([np.nan] * len(last_4_years), index=last_4_years)).replace(0, np.nan)
    ratios['Working Capital Turnover Ratio'] = revenue / (current_assets - current_liabilities).replace(0, np.nan)

    # Dividend Ratios
    ratios['Dividend Payout Ratio'] = -dividends_paid / net_income.replace(0, np.nan)
    ratios['Retention Ratio'] = retained_earnings / net_income.replace(0, np.nan)

    # Coverage Ratios
    ratios['Cash Flow Coverage Ratio'] = (cashflow_statement.get('Operating Cash Flow', pd.Series([np.nan] * len(last_4_years), index=last_4_years)) - capital_expenditures) / total_debt.replace(0, np.nan)
    ratios['Fixed Charge Coverage Ratio'] = (ebit + interest_expense) / (interest_expense + dividends_paid).replace(0, np.nan)

    # Valuation Ratios
    stock = yf.Ticker(ticker)
    market_price = stock.history(period='1d')['Close'].iloc[-1]
    shares_outstanding = stock.info.get('sharesOutstanding', np.nan)
    earnings_per_share = net_income / shares_outstanding if shares_outstanding and shares_outstanding != 0 else np.nan
    book_value_per_share = total_equity / shares_outstanding if shares_outstanding and shares_outstanding != 0 else np.nan
    dividends_per_share = -dividends_paid / shares_outstanding if shares_outstanding and shares_outstanding != 0 else np.nan
    ratios['Price to Earnings Ratio (P/E)'] = market_price / earnings_per_share if earnings_per_share and earnings_per_share != 0 else np.nan
    ratios['Price to Book Ratio (P/B)'] = market_price / book_value_per_share if book_value_per_share and book_value_per_share != 0 else np.nan
    ratios['Dividend Yield'] = dividends_per_share / market_price if market_price and market_price != 0 else np.nan
    ratios['Earnings Yield'] = earnings_per_share / market_price if market_price and market_price != 0 else np.nan

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
