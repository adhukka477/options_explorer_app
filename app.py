from PyQt5 import QtWidgets, uic
from resources.options_chain import OptionsChain
from resources.yahoo_finance_info import YahooFinance
import sys
import yfinance as yf
import pandas as pd
from support.pandas_model import PandasModel

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('./ui/mainWindow.ui', self) # Load the .ui file
        self.showMaximized()

        self.initalizeSlots()

    def initalizeSlots(self):
        self.OptionsChainManager = OptionsChain()

        self.symbol_line_edit.returnPressed.connect(self.getOptionsExpDates)
        self.exp_date_combobox.currentIndexChanged.connect(self.getOptionsChain)
    

    def getOptionsExpDates(self):

        ticker_input = self.symbol_line_edit.text()
        self.exp_date_combobox.clear()
        company_info = yf.Ticker(ticker_input).info

        if company_info is not None:
            if "longName" in company_info: 
                company_name = company_info["longName"] 
            else: company_name = None
        else:
            company_name = None

        try:
            price_history = yf.Ticker(ticker_input).history(period = '5d', interval='1d', actions=False)
            current_price = price_history.Close.values[-1]
            change_price = price_history.Close.values[-1] - price_history.Close.values[-2]
            change_pct = change_price/price_history.Close.values[-2]
        except:
            price_history = None

        if company_name is not None and price_history is not None:
            
            self.company_label.setText("{} \t ${} \t {}({} %)".format(company_name, 
                                                                      str(format(current_price, ".2f")), 
                                                                      str(format(change_price, ".2f")), 
                                                                      str(format(change_pct*100, ".2f"))))
            self.OptionsChainManager.ticker = ticker_input
            self.OptionsChainManager.getOptionsExpDates()
            [self.exp_date_combobox.addItem(e) for e in self.OptionsChainManager.exp_dates]
            self.getOptionsChain()

        else:
            chain_view = pd.DataFrame(columns= ["c_Bid", "c_Ask", "c_IV", "c_Volume", "c_OpenInterest", "Strike", "p_Bid", "p_Ask", "p_IV", "c_Volume", "c_OpenInterest"])
            model = PandasModel(chain_view)
            self.options_search_table_widget.setModel(model)
            col_widths = [100,100,100,125,150,75,100,100,100,125,150]
            [self.options_search_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
            self.company_label.setText("")

    def getOptionsChain(self):

        if self.exp_date_combobox.currentText() != "" and self.exp_date_combobox.currentText() is not None:
            self.OptionsChainManager.exp_date_selection = self.exp_date_combobox.currentText()
            self.OptionsChainManager.getOptionsChainByExpDate()

            chain_view = self.OptionsChainManager.options_chain
            chain_view = chain_view.loc[:, ["c_Bid", "c_Ask", "c_IV", "c_Volume", "c_OpenInterest", "Strike", "p_Bid", "p_Ask", "p_IV", "c_Volume", "c_OpenInterest"]]
            types = {
                        'c_Bid': float,
                        'c_Ask': float,
                        'c_IV': float,
                        'c_Volume': int,
                        'c_OpenInterest': int,
                        'Strike': float,
                        'p_Bid': float,
                        'p_Ask': float,
                        'p_IV': float,
                        'c_Volume': int,
                        'c_OpenInterest': int,
                    }

            for col in chain_view.columns:
                chain_view[col] = chain_view[col].astype(types[col])
                if types[col] == float:
                    chain_view[col] = [format(x, '.2f') for x in chain_view[col]]
            
            model = PandasModel(chain_view)
            self.options_search_table_widget.setModel(model)
            col_widths = [100,100,100,125,150,75,100,100,100,125,150]
            [self.options_search_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
            self.options_search_table_widget.clearSelection()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()