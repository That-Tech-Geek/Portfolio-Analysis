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
    
    # Fetch historical data for more years
    hist = stock.history(period='10y')  # Get 10 years of historical data
    annual_cashflows = stock.cashflow.T.resample('A').sum()  # Aggregate cashflows annually
    
    return financials, balance_sheet, cashflow_statement, annual_cashflows

# Function to get additional data if missing
def fetch_additional_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch additional data
    market_cap = stock.info.get('marketCap', 0)  # Get market cap from stock info
    return {
        'Market Cap': market_cap
    }

# Function to calculate financial ratios
def calculate_ratios(financials, balance_sheet, cashflow_statement):
    try:
        # Calculate ratios
        ratios = {}
        
        # Profitability Ratios
        ratios['Gross Profit Margin'] = financials['Gross Profit'] / financials['Total Revenue']
        ratios['Operating Profit Margin'] = financials['Operating Income'] / financials['Total Revenue']
        ratios['Net Profit Margin'] = financials['Net Income'] / financials['Total Revenue']
        
        # Liquidity Ratios
        ratios['Current Ratio'] = balance_sheet['Total Current Assets'] / balance_sheet['Total Current Liabilities']
        ratios['Quick Ratio'] = (balance_sheet['Total Current Assets'] - balance_sheet['Inventory']) / balance_sheet['Total Current Liabilities']
        ratios['Cash Ratio'] = balance_sheet['Cash'] / balance_sheet['Total Current Liabilities']
        
        # Leverage Ratios
        ratios['Debt to Equity Ratio'] = balance_sheet['Total Liabilities'] / balance_sheet['Total Stockholder Equity']
        ratios['Debt to Assets Ratio'] = balance_sheet['Total Liabilities'] / balance_sheet['Total Assets']
        ratios['Financial Leverage Ratio'] = balance_sheet['Total Assets'] / balance_sheet['Total Stockholder Equity']
        
        # Efficiency Ratios
        ratios['Total Assets Turnover Ratio'] = financials['Total Revenue'] / balance_sheet['Total Assets']
        ratios['Inventory Turnover Ratio'] = financials['Cost Of Revenue'] / balance_sheet['Inventory']
        
        # Cash Flow Ratios
        ratios['Operating Cash Flow Ratio'] = cashflow_statement['Total Cash From Operating Activities'] / balance_sheet['Total Current Liabilities']
        ratios['Free Cash Flow to Firm'] = cashflow_statement['Total Cash From Operating Activities'] - cashflow_statement['Capital Expenditures']
        
        # Convert to DataFrame
        ratios_df = pd.DataFrame(ratios)
        
        return ratios_df
    
    except Exception as e:
        st.error(f"Error calculating ratios: {e}")
        return pd.DataFrame()

# Function for DCF Analysis
def dcf_analysis(financials, balance_sheet, ticker, annual_cashflows, discount_rate=0.1, terminal_growth_rate=0.02):
    try:
        free_cash_flow = annual_cashflows['Free Cash Flow'].values if 'Free Cash Flow' in annual_cashflows.columns else [0]
        
        if len(free_cash_flow) < 2:
            st.error("Not enough Free Cash Flow data to perform DCF analysis.")
            return None

        try:
            if len(free_cash_flow) > 1 and np.all(free_cash_flow[:-1] != 0):
                growth_rate = np.mean(np.diff(free_cash_flow) / free_cash_flow[:-1])
            else:
                growth_rate = 0
        except Exception as e:
            st.error(f"Error calculating growth rate: {e}")
            growth_rate = 0
        
        future_cash_flows = [free_cash_flow[-1] * ((1 + growth_rate) ** (i + 1)) for i in range(5)]
        terminal_value = future_cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
        discounted_cash_flows = [cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(future_cash_flows)]
        discounted_terminal_value = terminal_value / (1 + discount_rate) ** len(future_cash_flows)
        
        dcf_value = sum(discounted_cash_flows) + discounted_terminal_value
        
        market_cap = balance_sheet.loc['Market Cap'].values[0] if 'Market Cap' in balance_sheet.index else fetch_additional_data(ticker)['Market Cap']
        
        return {
            'DCF Value': dcf_value,
            'Market Cap': market_cap,
            'Undervalued/Overvalued': 'Undervalued' if market_cap and dcf_value > market_cap else 'Overvalued',
            'Future Cash Flows': future_cash_flows,
            'Discounted Cash Flows': discounted_cash_flows,
            'Discounted Terminal Value': discounted_terminal_value
        }
    
    except Exception as e:
        st.error(f"Error in DCF Analysis: {e}")
        return None

# Streamlit app
def main():
    st.title('Investment Analysis: Analyze everything you need to know about a company, right here!')
    st.write("This is built for educational purposes and is not liable to any losses and/or damages to the user.")
    
    ticker = st.text_input('Enter the stock ticker symbol:', 'RELIANCE.NS').upper()
    
    if ticker:
        try:
            financials, balance_sheet, cashflow_statement, annual_cashflows = get_financial_data(ticker)
            
            st.header(f'Financial Statements for {ticker}')
            st.subheader('Income Statement')
            financials_editable = st.data_editor(financials, use_container_width=True)
            
            st.subheader('Balance Sheet')
            balance_sheet_editable = st.data_editor(balance_sheet, use_container_width=True)
            
            st.subheader('Cash Flow Statement')
            cashflow_statement_editable = st.data_editor(cashflow_statement, use_container_width=True)
            
            st.header(f'Financial Ratios for {ticker}')
            ratios_df = calculate_ratios(financials_editable, balance_sheet_editable, cashflow_statement_editable)
            if not ratios_df.empty:
                st.write(ratios_df)
            
            st.header(f'DCF Analysis for {ticker}')
            dcf_results = dcf_analysis(financials_editable, balance_sheet_editable, ticker, annual_cashflows)
            if dcf_results:
                st.subheader('DCF Analysis Results')
                st.write(f"**DCF Value:** ${dcf_results['DCF Value']:,.2f}")
                st.write(f"**Market Cap:** ${dcf_results['Market Cap']:,.2f}")
                st.write(f"**Valuation:** {dcf_results['Undervalued/Overvalued']}")
                
                st.subheader('Future Cash Flows')
                st.write(pd.DataFrame({'Year': range(1, 6), 'Projected Cash Flow': dcf_results['Future Cash Flows']}))
                
                st.subheader('Discounted Cash Flows')
                st.write(pd.DataFrame({'Year': range(1, 6), 'Discounted Cash Flow': dcf_results['Discounted Cash Flows']}))
                
                st.write(f"**Discounted Terminal Value:** ${dcf_results['Discounted Terminal Value']:,.2f}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
