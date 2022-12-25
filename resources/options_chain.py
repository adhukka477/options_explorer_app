import yfinance as yf

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
        self.options_chain = sym.option_chain(date = self.exp_date_selection)