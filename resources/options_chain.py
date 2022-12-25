import yfinance as yf
import pandas as pd
class OptionsChain():

    def __init__(self) -> None:

        self.ticker = None

        self.exp_date_selection = None
        self.exp_dates = []

        self.options_chain = None


    def getOptionsExpDates(self):
        sym = yf.Ticker(self.ticker)
        self.exp_dates = sym.options
    
    def getOptionsChainByExpDate(self):
        
        sym = yf.Ticker(self.ticker)
        options_chain = sym.option_chain(date = self.exp_date_selection)
        calls = options_chain.calls
        puts = options_chain.puts
        self.options_chain = pd.merge(left=calls, right=puts, on="strike", how='inner')
        self.options_chain.columns = ['c_Contract', 'c_LastTradeDate', 'Strike', 'c_LastPrice', 'c_Bid',
                                     'c_Ask', 'c_Change', 'c_PercentChange', 'c_Volume', 'c_OpenInterest',
                                     'c_ImpliedVolatility', 'c_inTheMoney', 'c_ContractSize', 'c_currency',
                                     'p_Contract', 'p_LastTradeDate', 'p_LastPrice', 'p_Bid', 'p_Ask',
                                     'p_Change', 'p_PercentChange', 'p_Volume', 'p_OpenInterest',
                                     'p_ImpliedVolatility', 'p_inTheMoney', 'p_ContractSize', 'p_currency']

