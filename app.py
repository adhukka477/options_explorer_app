from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from resources.options_chain import OptionsChain
from order_window import OrderWindow
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
        self.options_chain_manager = OptionsChain()
        orders_table_columns =["Contract", "Type", "Strike", "Exp_Date",  "DTE", "Qty", "Price", "Debit_Credit"]
        self.orders_table_model = PandasModel(pd.DataFrame(columns=orders_table_columns))
        self.orders_table_widget.setModel(self.orders_table_model)
        col_widths = [250,100,100,125,100,100,100,125]
        [self.orders_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
        self.orders_table_widget.clearSelection()

        self.symbol_line_edit.returnPressed.connect(self.getOptionsExpDates)
        self.exp_date_combobox.currentIndexChanged.connect(self.getOptionsChain)
        self.long_button.clicked.connect(self.addLongLeg)
        self.short_button.clicked.connect(self.addShortLeg)
    

    def getOptionsExpDates(self):

        self.symbol_line_edit.setText(self.symbol_line_edit.text().upper())
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
            self.options_chain_manager.ticker = ticker_input
            self.options_chain_manager.getOptionsExpDates()
            [self.exp_date_combobox.addItem(e) for e in self.options_chain_manager.exp_dates]
            self.getOptionsChain()

        else:
            chain_view = pd.DataFrame(columns= ["c_Bid", "c_Ask", "c_IV", "c_Volume", "c_Open_Interest", "Strike", "p_Bid", "p_Ask", "p_IV", "c_Volume", "c_Open_Interest"])
            self.options_search_table_model = PandasModel(chain_view)
            self.options_search_table_widget.setModel(self.options_search_table_model)
            col_widths = [100,100,100,125,150,75,100,100,100,125,150]
            [self.options_search_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
            self.company_label.setText("")

    def getOptionsChain(self):

        if self.exp_date_combobox.currentText() != "" and self.exp_date_combobox.currentText() is not None:
            self.options_chain_manager.exp_date_selection = self.exp_date_combobox.currentText()
            self.options_chain_manager.getOptionsChainByExpDate()

            chain_view = self.options_chain_manager.options_chain
            chain_view = chain_view.loc[:, ["c_Bid", "c_Ask", "c_IV", "c_Volume", "c_Open_Interest", "Strike", "p_Bid", "p_Ask", "p_IV", "p_Volume", "p_Open_Interest"]]
            types = {
                        'c_Bid': float,
                        'c_Ask': float,
                        'c_IV': float,
                        'c_Volume': int,
                        'c_Open_Interest': int,
                        'Strike': float,
                        'p_Bid': float,
                        'p_Ask': float,
                        'p_IV': float,
                        'p_Volume': int,
                        'p_Open_Interest': int,
                    }

            for col in chain_view.columns:
                chain_view[col] = chain_view[col].astype(types[col])
                if types[col] == float:
                    chain_view[col] = [format(x, '.2f') for x in chain_view[col]]
            
            self.options_search_table_model = PandasModel(chain_view)
            self.options_search_table_widget.setModel(self.options_search_table_model)
            col_widths = [100,100,100,125,150,75,100,100,100,125,150]
            [self.options_search_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
            self.options_search_table_widget.clearSelection()

    def addLongLeg(self):
        if len(self.options_search_table_widget.selectedIndexes()) > 0:
            selected_row = self.options_search_table_widget.selectedIndexes()[0].row()
            selected_contracts = self.options_chain_manager.options_chain.iloc[selected_row, ]

            self.order_window = OrderWindow(selected_contracts = selected_contracts)
            self.order_window.show()
            self.order_window.ok_button.clicked.connect(self.confirmLeg)
            self.order_window.cancel_button.clicked.connect(self.cancelLeg)

    def confirmLeg(self):

        contract_name = self.order_window.contract_name_label.text()
        print(contract_name)
        options_chains = self.options_chain_manager.options_chain
        selected_contract = options_chains.loc[((options_chains.c_Contract == contract_name) | 
                                                (options_chains.p_Contract == contract_name)), :]
        current_order = pd.DataFrame(self.orders_table_model._df.copy())
        
        new_order = {
                    "Contract": contract_name, 
                    "Type": self.order_window.type_combobox.currentText(), 
                    "Strike": selected_contract["Strike"].values[0], 
                    "Exp_Date": self.options_chain_manager.exp_date_selection,  
                    "DTE":"", 
                    "Qty": self.order_window.qty, 
                    "Price": self.order_window.price, 
                    "Debit_Credit": self.order_window.credi_debit_label.text()
                    }

        current_order = current_order.append(new_order, ignore_index=True)
        self.orders_table_model = PandasModel(current_order)
        self.orders_table_widget.setModel(self.orders_table_model)
        col_widths = [250,100,100,125,100,100,100,125]
        [self.orders_table_widget.setColumnWidth(i, col_widths[i]) for i in range(len(col_widths))]
        self.orders_table_widget.clearSelection()

        self.order_window.close()

    def cancelLeg(self):
        pass

    def addShortLeg(self):
        pass

    def removeLeg(self):
        pass


            
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()