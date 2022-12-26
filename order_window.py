from PyQt5 import QtWidgets, uic
import numpy as np


class OrderWindow(QtWidgets.QMainWindow):

    def __init__(self, selected_contracts):
        super(OrderWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('./ui/orderWindow.ui', self) # Load the .ui file

        self.contracts = selected_contracts

        self.put_contract = selected_contracts["p_Contract"]
        self.put_price = np.mean(selected_contracts.loc[["p_Bid", "p_Ask"]].to_list())
        self.call_contract = selected_contracts["c_Contract"]
        self.call_price = np.mean(selected_contracts.loc[["c_Bid", "c_Ask"]].to_list())

        self.qty = 1
        self.price = self.put_price
        self.contract_name_label.setText(self.put_contract)
        self.price_spinbox.setValue(self.price)
        self.calculateOptionsOrder()

        self.initializeSlots()


    def initializeSlots(self):

        self.type_combobox.currentTextChanged.connect(self.typeChanged)
        self.qty_spinbox.valueChanged.connect(self.qtyChanged)
        self.price_spinbox.valueChanged.connect(self.priceChanged)


    def calculateOptionsOrder(self):

        self.credi_debit_label.setText("$" + str(format(self.qty*self.price, '.2f')))

    def typeChanged(self):

        if self.type_combobox.currentText() == "PUT":
            self.price = self.put_price
            self.price_spinbox.setValue(self.price)
            self.contract_name_label.setText(self.put_contract)
        if self.type_combobox.currentText() == "CALL":
            self.price = self.call_price
            self.price_spinbox.setValue(self.price)
            self.contract_name_label.setText(self.call_contract)
        
        self.calculateOptionsOrder()

    def qtyChanged(self):

        self.qty = self.qty_spinbox.value()
        self.calculateOptionsOrder()

    def priceChanged(self):
        
        self.price = self.price_spinbox.value()
        self.calculateOptionsOrder()



