from PyQt5 import QtWidgets, uic
from resources.options_chain import OptionsChain
import sys

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
        self.OptionsChainManager.ticker = self.symbol_line_edit.text()
        self.OptionsChainManager.getOptionsExpDates()
        [self.exp_date_combobox.addItem(e) for e in self.OptionsChainManager.exp_dates]

    def getOptionsChain(self):
        self.OptionsChainManager.exp_date_selection = self.exp_date_combobox.currentText()
        self.OptionsChainManager.getOptionsChainByExpDate()
        self.options_search_table_widget.setModel(PandasModel(self.OptionsChainManager.options_chain))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()