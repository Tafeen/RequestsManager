from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtWidgets import (QWidget, QHBoxLayout,
                               QHeaderView, QTableView)


# Model
class NewRequestHeadersTableModel(QAbstractTableModel):
    def __init__(self, parent, headers_data=None):
        super(NewRequestHeadersTableModel, self).__init__(parent)
        self.load_data(headers_data)
        self.addBlankRow()

    def load_data(self, data):
        keys_list = []
        values_list = []
        for index, key in enumerate(data):
            keys_list.append(key)
            values_list.append(data[key])

        self.headers_keys = keys_list
        self.headers_values = values_list

        self.column_count = 2
        self.row_count = len(self.headers_values)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

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

        if role == Qt.DisplayRole:
            if column == 0:
                return self.headers_keys[row]
            elif column == 1:
                return self.headers_values[row]

        if role == Qt.EditRole:
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
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.endInsertRows()

    def setData(self, QModelIndex, Text, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.EditRole:
            if column == 0:
                self.headers_keys[row] = Text
            elif column == 1:
                self.headers_values[row] = Text
            self.data(QModelIndex)
            # TODO: if data changed -> update main holder of headers data
            self.dataChanged.emit(QModelIndex, QModelIndex, [])

            # After editing Check if both key and value are filled in last row of table -> add new row
            if(row == len(self.headers_keys)-1
               and self.headers_keys[row] != ""
               and self.headers_values[row] != ""):
                self.addBlankRow()
            return True
        return False


# Table Layout
class RequestHeadersTable(QWidget):
    def __init__(self, parent, headers_data=None):
        super(RequestHeadersTable, self).__init__(parent)

        # Create Table
        self.requestHeadersModel = NewRequestHeadersTableModel(self, headers_data)
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
