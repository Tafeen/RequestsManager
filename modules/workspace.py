from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox,
                               QTableWidget, QHeaderView, QTableWidgetItem,
                               QTabWidget)


class RequestHeadersTable(QWidget):
    def __init__(self, parent):
        super(RequestHeadersTable, self).__init__(parent)

        title = ["Header name", "Header value"]
        self.data = parent.data
        colcnt = 2
        self.tablewidget = QTableWidget()

        self.tablewidget.setColumnCount(colcnt)
        hheader = QHeaderView(Qt.Orientation.Horizontal)
        self.tablewidget.setHorizontalHeader(hheader)
        self.tablewidget.setHorizontalHeaderLabels(title)
        self.tablewidget.horizontalHeader().setStretchLastSection(True)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        rowcnt = len(self.data)
        self.tablewidget.setRowCount(rowcnt)
        for index, key in enumerate(self.data):
            self.tablewidget.setItem(index, 0, QTableWidgetItem(key))
            self.tablewidget.setItem(
                index, 1, QTableWidgetItem(self.data.get(key)))

        layout = QHBoxLayout()
        layout.addWidget(self.tablewidget)
        self.setLayout(layout)

    def setData(self, parent):
        self.tablewidget.clear()
        self.data = parent.data
        rowcnt = len(self.data)
        self.tablewidget.setRowCount(rowcnt)
        for index, key in enumerate(self.data):
            self.tablewidget.setItem(index, 0, QTableWidgetItem(key))
            self.tablewidget.setItem(
                index, 1, QTableWidgetItem(self.data.get(key)))
        self.accessHeadersData()

    def accessHeadersData(self):
        currentData = {}
        for index, key in enumerate(self.data):
            key = self.tablewidget.item(index, 0).text()
            value = self.tablewidget.item(index, 1).text()
            currentData[key] = value
        return currentData


class RequestAdvancedEditingWidget(QWidget):
    def __init__(self, parent):
        super(RequestAdvancedEditingWidget, self).__init__(parent)

        self.data = parent.requestHeadersData
        self.tabWidget = QTabWidget()

        # Request Body
        self.requestBody = QTextEdit()

        # Request Headers
        self.requestHeaders = RequestHeadersTable(self)

        self.tabWidget.addTab(self.requestHeaders, "Headers")
        self.tabWidget.addTab(self.requestBody, "Body")

        allQGridLayout = QGridLayout()
        allQGridLayout.addWidget(self.tabWidget, 0, 0)

        self.setLayout(allQGridLayout)


class RequestWorkspaceWidget(QWidget):
    def __init__(self, parent):
        super(RequestWorkspaceWidget, self).__init__(parent)

        defaultRequestHeadersData = {
            "User-Agent": "RequestsManager.0.2020.0.1",
            "Content-Type": "application/json"
        }
        self.requestHeadersData = defaultRequestHeadersData
        self.data = {}
        # Request ID
        self.requestId = None

        # Request overall information
        self.requestName = QLineEdit()
        self.requestName.setPlaceholderText("Request name")
        self.requestLastModificationDate = QLabel("Just a while ago")

        self.informationQHBoxLayout = QHBoxLayout()
        self.informationQHBoxLayout.addWidget(self.requestName)
        self.informationQHBoxLayout.addWidget(
            self.requestLastModificationDate)

        # Request type
        TYPE_OPTIONS = (
            "GET",
            "POST",
            "DELETE",
            "PATCH"
        )

        self.requestType = QComboBox()
        for option in TYPE_OPTIONS:
            self.requestType.addItem(option)

        # Request endpoint
        self.requestEndpoint = QLineEdit()
        self.requestEndpoint.setPlaceholderText("Request endpoint")

        # Request 'request button' with disabling
        self.saveRequestInList = QPushButton("Save request")
        self.sendRequest = QPushButton("Send Request")
        self.deleteRequestFromList = QPushButton("Delete Request")
        self.saveRequestInList.setEnabled(False)
        self.deleteRequestFromList.setEnabled(False)

        # Set request editing widget
        self.RequestAdvancedEditing = RequestAdvancedEditingWidget(self)

        self.endpointQVBoxLayout = QHBoxLayout()
        self.endpointQVBoxLayout.addWidget(self.requestType)
        self.endpointQVBoxLayout.addWidget(self.requestEndpoint)

        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addLayout(
            self.informationQHBoxLayout, 0, 0, 0, 3, Qt.AlignTop)
        self.allQGridLayout.addLayout(self.endpointQVBoxLayout, 1, 0)
        self.allQGridLayout.addWidget(
            self.RequestAdvancedEditing, 2, 0, 1, 0, Qt.AlignVCenter)
        self.allQGridLayout.addWidget(
            self.sendRequest, 4, 1, Qt.AlignBottom)
        self.allQGridLayout.addWidget(
            self.saveRequestInList, 4, 2, Qt.AlignBottom)
        self.allQGridLayout.addWidget(
            self.deleteRequestFromList, 4, 3, Qt.AlignBottom)

        self.setLayout(self.allQGridLayout)

        self.requestName.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.requestEndpoint.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.saveRequestInList.clicked.connect(parent.guiSaveRequest)
        self.deleteRequestFromList.clicked.connect(parent.guiDeleteRequest)

    def printRequestHeaders(self):
        self.data = self.requestHeadersData
        self.RequestAdvancedEditing.requestHeaders.setData(self)
