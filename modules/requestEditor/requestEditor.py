from PySide2.QtCore import Qt
import json
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox, QTabWidget)

from utils.requestWrapper import requestWrapper
from modules.requestEditor.headersTable import RequestHeadersTable
from modules.requestEditor.response import RequestsResponseWidget
from modules.requestEditor.requestDocumentation import RequestDocumentation


class RequestAdvancedEditingWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(RequestAdvancedEditingWidget, self).__init__(parent)

        self.tabWidget = QTabWidget()

        # Request Body
        self.requestBody = QTextEdit("")

        # Request Headers defaults
        self._headersData = parent._headersData
        self.requestHeadersTable = RequestHeadersTable(self)

        # Request Documentation
        self.requestDocumentation = RequestDocumentation(self)

        self.tabWidget.addTab(self.requestHeadersTable, "Headers")
        self.tabWidget.addTab(self.requestBody, "Body")
        self.tabWidget.addTab(self.requestDocumentation, "Documentation")

        allQGridLayout = QGridLayout()
        allQGridLayout.addWidget(self.tabWidget, 0, 0)

        self.setLayout(allQGridLayout)


class RequestEditorWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(RequestEditorWidget, self).__init__(parent)

        self.defaultRequestHeadersData = {
            "User-Agent": "RequestsManager.0.2020.0.2",
            "Content-Type": "application/json"
        }

        # Check if any requests has been loaded
        if(parent.selectedRequest is not None):
            self._headersData = (parent.
                                 _requestsData[parent.selectedRequest]
                                 ["headers"])
        else:
            self._headersData = self.defaultRequestHeadersData
        self.data = {}

        # Request ID
        self.requestId = None

        # Request overall information
        self.requestName = QLineEdit()
        self.requestName.setPlaceholderText("New request name")
        self.requestLastModificationDate = QLabel("Not Saved")

        self.informationQHBoxLayout = QHBoxLayout()
        self.informationQHBoxLayout.addWidget(self.requestName)
        self.informationQHBoxLayout.addWidget(self.requestLastModificationDate)

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

        # Set buttons layout
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.sendRequest, 0, 1)
        self.ButtonsLayout.addWidget(self.saveRequestInList, 0, 2)
        self.ButtonsLayout.addWidget(self.deleteRequestFromList, 0, 3)

        # Set endpoint layout
        self.endpointQVBoxLayout = QHBoxLayout()
        self.endpointQVBoxLayout.addWidget(self.requestType)
        self.endpointQVBoxLayout.addWidget(self.requestEndpoint)

        # Set final layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.setRowStretch(2, 3)
        self.allQGridLayout.setRowStretch(3, 2)
        self.allQGridLayout.addLayout(self.informationQHBoxLayout, 0, 0)
        self.allQGridLayout.addLayout(self.endpointQVBoxLayout, 1, 0)
        self.allQGridLayout.addWidget(self.RequestAdvancedEditing, 2, 0)
        self.allQGridLayout.addWidget(self.RequestResponse, 3, 0)
        self.allQGridLayout.addLayout(self.ButtonsLayout, 4, 0, Qt.AlignRight)

        self.setLayout(self.allQGridLayout)

        self.requestName.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.requestEndpoint.textChanged[str].connect(
            parent.checkDisableSaveAndDelete)
        self.saveRequestInList.clicked.connect(parent.saveRequest)
        self.sendRequest.clicked.connect(self.sendRequestSignal)
        self.deleteRequestFromList.clicked.connect(parent.deleteRequest)

    def sendRequestSignal(self):
        requestResponseData = requestWrapper(self.requestType.currentText(),
                                             self.requestEndpoint.text(),
                                             self.data,
                                             self.RequestAdvancedEditing.
                                             requestBody.toPlainText())
        requestResponseCodeType = {
            "Info": "orange",
            "Success": "green",
            "Redirect": "silver",
            "ClientErr": "#ff2a00",
            "ServerErr": "#7d1710"
        }
        if(requestResponseData.status_code >= 100):
            responseColor = requestResponseCodeType['Info']
        if(requestResponseData.status_code >= 200):
            responseColor = requestResponseCodeType['Success']
        if(requestResponseData.status_code >= 300):
            responseColor = requestResponseCodeType['Redirect']
        if(requestResponseData.status_code >= 400):
            responseColor = requestResponseCodeType['ClientErr']
        if(requestResponseData.status_code >= 500):
            responseColor = requestResponseCodeType['ServerErr']

        (self.RequestResponse.responseStatus.
         setStyleSheet(f'color: {responseColor}'))
        (self.RequestResponse.responseStatus.
         setText(f'Status Code: {str(requestResponseData.status_code)}'))

        # Check if body is json type
        try:
            parsedBody = json.loads(str(requestResponseData.text))
            formatedBody = json.dumps(parsedBody, indent=4)
            self.RequestResponse.responseBody.setTextColor(Qt.white)
            self.RequestResponse.responseBody.setText(formatedBody)
        except Exception as ex:
            print(f'Its not json file - {ex}')
            self.RequestResponse.responseBody.setText(requestResponseData.text)
