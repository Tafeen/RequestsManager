from PySide2.QtCore import (Qt, QAbstractListModel, QModelIndex,
                            QItemSelectionModel)
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QListView)
from modules.requestItem import RequestInListWidget


# Model
class NewRequestListModel(QAbstractListModel):
    def __init__(self, parent):
        self.parent = parent
        super(NewRequestListModel, self).__init__(parent)
        self.load_data(parent.parent._requestsData)

    def load_data(self, data):
        self._requestsData = self.parent.parent._requestsData
        self.row_count = len(data)
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def flags(self, index):
        original_flags = super(NewRequestListModel, self).flags(index)
        return original_flags | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return 1

    def getIndex(self, row):
        return self.createIndex(row, 0, QModelIndex())

    def createRequestWidget(self, requestName, requestType,
                            requestEndpoint):
        # Create QCustomQWidget
        newRequestInListWidget = RequestInListWidget()
        newRequestInListWidget.setRequestName(requestName)
        newRequestInListWidget.setRequestType(requestType)
        newRequestInListWidget.setRequestEndpoint(requestEndpoint)
        return newRequestInListWidget

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()
        requestName = self._requestsData[row]["name"]

        if role == Qt.DisplayRole:
            if(column == 0):
                return requestName
        return None


# List Layout
class RequestsList(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(RequestsList, self).__init__(parent)

        # Create List
        self.requestsListModel = NewRequestListModel(self)
        self.requestsList = QListView()
        self.requestsList.setModel(self.requestsListModel)

        # Set layout
        self.requestHeadersLayout = QHBoxLayout()
        self.requestHeadersLayout.addWidget(self.requestsList)
        self.setLayout(self.requestHeadersLayout)

    def updateRequestsData(self, requests_data):
        self.parent._requestsData = requests_data

    def selectRow(self, row):
        self.requestsList.selectionModel().clearSelection()
        self.requestsList.selectionModel().setCurrentIndex(
            self.requestsListModel.createIndex(row, 0, QModelIndex), QItemSelectionModel.Select)

    def clearSelection(self):
        self.requestsList.selectionModel().clearSelection()