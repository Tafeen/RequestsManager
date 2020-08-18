from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox,
                               QTableWidget, QHeaderView, QTableWidgetItem,
                               QTabWidget)
from utils.requestWrapper import requestWrapper
from modules.response import RequestsResponseWidget


class RequestHeadersTable(QWidget):
    def __init__(self, parent):
        super(RequestHeadersTable, self).__init__(parent)

        title = ["Header name", "Header value"]
        self.data = parent.data
        self.currentlyAccessingData = False
        colcnt = 2
        self.tablewidget = QTableWidget()

        self.tablewidget.setColumnCount(colcnt)
        hheader = QHeaderView(Qt.Orientation.Horizontal)
        self.tablewidget.setHorizontalHeader(hheader)
        self.tablewidget.setHorizontalHeaderLabels(title)
        self.tablewidget.horizontalHeader().setStretchLastSection(True)
        (self.tablewidget.horizontalHeader()
                         .setSectionResizeMode(QHeaderView.Stretch))

        rowcnt = len(self.data)+1
        self.tablewidget.setRowCount(rowcnt)
        for index, key in enumerate(self.data):
            self.tablewidget.setItem(index, 0, QTableWidgetItem(key))
            self.tablewidget.setItem(
                index, 1, QTableWidgetItem(self.data.get(key)))
        # Add empty new header
        self.tablewidget.setItem(rowcnt, 0, QTableWidgetItem(""))
        self.tablewidget.setItem(rowcnt, 1, QTableWidgetItem(""))

        # detect which element selected
        self.tablewidget.selectionModel().currentChanged.connect(
            self.onRowChanged)

        # detect when element item changed and lost focus
        self.tablewidget.itemChanged.connect(self.itemDataChanged)

        layout = QHBoxLayout()
        layout.addWidget(self.tablewidget)
        self.setLayout(layout)

    def setData(self, parent):
        self.currentlyAccessingData = True
        self.tablewidget.clearContents()
        self.data = parent.data

        rowcnt = len(self.data)+1
        self.tablewidget.setRowCount(rowcnt)
        for index, key in enumerate(self.data):
            self.tablewidget.setItem(index, 0, QTableWidgetItem(key))
            self.tablewidget.setItem(
                index, 1, QTableWidgetItem(self.data.get(key)))
        # Add empty new header
        self.tablewidget.setItem(rowcnt, 0, QTableWidgetItem(""))
        self.tablewidget.setItem(rowcnt, 1, QTableWidgetItem(""))
        self.accessHeadersData()

        self.currentlyAccessingData = False

    def accessHeadersData(self):
        currentData = {}
        for index, key in enumerate(self.data):
            keyItem = self.tablewidget.item(index, 0)
            if(keyItem is not None):
                if(keyItem.text() != ""):
                    keyItem.text()
                else:
                    continue
            else:
                continue

            valueItem = self.tablewidget.item(index, 1)
            if(valueItem is None):
                value = ""
            else:
                value = valueItem.text()

            currentData[key] = value
        return currentData

    def itemDataChanged(self):
        if not self.currentlyAccessingData:
            self.currentlyAccessingData = True

            # Set new key and value
            new_key = self.tablewidget.item(self.rowSelected, 0)
            self.new_key = new_key.text() if new_key is not None else ""
            new_value = self.tablewidget.item(self.rowSelected, 1)
            self.new_value = new_value.text() if new_value is not None else ""

            # Check if edited value changed
            keyChanged = False

            if(self.new_key != ""):
                if(self.old_key != "" and self.old_key != self.new_key):
                    print("!Updated key name")
                    del self.data[self.old_key]
                    self.data[self.new_key] = self.old_value
                    keyChanged = True
                else:
                    print("!Added new key with empty value")
                    self.data[self.new_key] = ""

            if(self.new_value != ""):
                if(self.old_value != self.new_value):
                    print("!Updated key value")
                    if keyChanged:
                        self.data[self.new_key] = self.new_value
                    else:
                        self.data[self.old_key] = self.new_value

            self.updateOldKeyToValue()

            # Add new item if last key is empty
            lastKey = self.tablewidget.item(self.tablewidget.rowCount()-1, 0)
            lastKeyIsSet = False

            if(lastKey is not None):
                if(lastKey.text() != ""):
                    lastKeyIsSet = True

            if(lastKeyIsSet):
                self.tablewidget.insertRow(self.tablewidget.rowCount())
                self.tablewidget.setItem(self.tablewidget.rowCount(),
                                         0, QTableWidgetItem(""))
                self.tablewidget.setItem(self.tablewidget.rowCount(),
                                         1, QTableWidgetItem(""))

            self.currentlyAccessingData = False

    def onRowChanged(self, current, previous):
        self.rowSelected = current.row()
        self.updateOldKeyToValue()

    def updateOldKeyToValue(self):
        old_key = self.tablewidget.item(self.rowSelected, 0)
        self.old_key = old_key.text() if old_key is not None else ""
        old_value = self.tablewidget.item(self.rowSelected, 1)
        self.old_value = old_value.text() if old_value is not None else ""


class RequestAdvancedEditingWidget(QWidget):
    def __init__(self, parent):
        super(RequestAdvancedEditingWidget, self).__init__(parent)

        self.data = parent.requestHeadersData
        self.tabWidget = QTabWidget()

        # Request Body
        self.requestBody = QTextEdit("{}")

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
        self.requestLastModificationDate = QLabel("Saved just a while ago")

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

        # Set request response widget
        self.RequestResponse = RequestsResponseWidget(self)
        # self.RequestResponse.setFixedWidth(600)

        self.endpointQVBoxLayout = QHBoxLayout()
        self.endpointQVBoxLayout.addWidget(self.requestType)
        self.endpointQVBoxLayout.addWidget(self.requestEndpoint)

        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addLayout(
            self.informationQHBoxLayout, 0, 0, 0, 3, Qt.AlignTop)
        self.allQGridLayout.addLayout(self.endpointQVBoxLayout, 2, 0, 1, 3)
        self.allQGridLayout.addWidget(
            self.RequestAdvancedEditing, 3, 0, 1, 0, Qt.AlignVCenter)
        self.allQGridLayout.addWidget(self.RequestResponse, 5, 0, 1, 4)
        self.allQGridLayout.addWidget(
            self.sendRequest, 6, 1, Qt.AlignBottom)
        self.allQGridLayout.addWidget(
            self.saveRequestInList, 6, 2, Qt.AlignBottom)
        self.allQGridLayout.addWidget(
            self.deleteRequestFromList, 6, 3, Qt.AlignBottom)

        self.setLayout(self.allQGridLayout)

        self.requestName.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.requestEndpoint.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.saveRequestInList.clicked.connect(parent.guiSaveRequest)
        self.sendRequest.clicked.connect(self.sendRequestSignal)
        self.deleteRequestFromList.clicked.connect(parent.guiDeleteRequest)

    def printRequestHeaders(self):
        self.data = self.requestHeadersData
        self.RequestAdvancedEditing.requestHeaders.setData(self)

    def sendRequestSignal(self):
        requestResponseData = requestWrapper(self.requestType.currentText(),
                                         self.requestEndpoint.text(),
                                         self.data,
                                         self.RequestAdvancedEditing.requestBody.toPlainText())
        self.RequestResponse.responseStatus.setText("Status Code: " + str(requestResponseData.status_code))
        self.RequestResponse.responseBody.setText(requestResponseData.text)
