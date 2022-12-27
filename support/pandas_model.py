import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QFont, QBrush

import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QFont

class PandasModel(QAbstractTableModel):

    def __init__(self, df=pd.DataFrame(), parent=None, bold_cols = []):
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self.bold_cols = bold_cols
        self.bold_font = QFont()
        self.bold_font.setBold(True)


    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # Return the data for the cells
        if role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        elif role == Qt.FontRole:
            # Set the font for the cells in the specified column to bold
            if index.column() in self.bold_cols:
                return self.bold_font

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return None
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError,):
                return None

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()
