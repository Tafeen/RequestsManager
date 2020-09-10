from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtWidgets import (QWidget, QHBoxLayout,
                               QHeaderView, QTableView)


# Model
class NewRequestHeadersTableModel(QAbstractTableModel):
    def __init__(self, parent, headers_data=None):
        self.parent = parent
        super(NewRequestHeadersTableModel, self).__init__(parent)
        self.load_data(headers_data)

    # TODO: Optimise to not update if same value as before
    def update_data(self):
        updateHeadersData = RequestHeadersTable.updateHeadersData
        headersDict = {}
        # Convert data to json
        for index, key in enumerate(self.headers_keys):
            headersDict[key] = self.headers_values[index]
        updateHeadersData(self.parent, headersDict)

    def load_data(self, data):
        self.row_count = len(data)
        keys_list = []
        values_list = []
        for index, key in enumerate(data):
            keys_list.append(key)
            values_list.append(data[key])

        self.headers_keys = keys_list
        self.headers_values = values_list
        self.addBlankRow()
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return 2

    def beginInsertRow(self, QModelIndex, row):
        return self.beginInsertRows(QModelIndex, row, row)

    def endInsertRow(self):
        return self.endInsertRows()

    def flags(self, index):
        original_flags = super(NewRequestHeadersTableModel, self).flags(index)
        return original_flags | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Headers keys", "Headers values")[section]
        else:
            return "{}".format(section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return self.headers_keys[row]
            elif column == 1:
                return self.headers_values[row]
        return None

    def addBlankRow(self):
        self.beginInsertRows(QModelIndex(), len(self.headers_keys),
                             len(self.headers_keys))
        self.headers_keys.append("")
        self.headers_values.append("")
        self.row_count = len(self.headers_values)
        self.layoutChanged.emit()
        self.endInsertRows()

    def setData(self, QModelIndex, Text, role=None):
        print("Changed data")
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.EditRole:
            if column == 0:
                self.headers_keys[row] = Text
            elif column == 1:
                self.headers_values[row] = Text

            self.data(QModelIndex)
            self.update_data()

            if(row == len(self.headers_keys)-1
               and self.headers_keys[row] != ""
               and self.headers_values[row] != ""):
                print("adding blank row")
                self.addBlankRow()
            self.dataChanged.emit(QModelIndex, QModelIndex)
            return True
        return False


# Table Layout
class RequestHeadersTable(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(RequestHeadersTable, self).__init__(parent)

        # Create Table
        self.requestHeadersModel = NewRequestHeadersTableModel(
            self, self.parent._headersData)
        self.requestHeadersTable = QTableView()
        self.requestHeadersTable.setModel(self.requestHeadersModel)

        # Stylize Table
        self.requestHeadersTable.horizontalHeader().setStretchLastSection(True)
        (self.requestHeadersTable
             .horizontalHeader()
             .setSectionResizeMode(QHeaderView.Stretch))

        # Set layout
        self.requestHeadersLayout = QHBoxLayout()
        self.requestHeadersLayout.addWidget(self.requestHeadersTable)
        self.setLayout(self.requestHeadersLayout)

    def updateHeadersData(self, headers_data):
        self.parent._headersData = headers_data
