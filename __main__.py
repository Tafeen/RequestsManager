#!/usr/bin/env python3.8.3
import sys
import json
import datetime

from PySide2.QtWidgets import (QApplication, QMainWindow, QListWidget,
                               QListWidgetItem, QGridLayout,
                               QWidget, QPushButton)
from modules.workspace import RequestWorkspaceWidget
from modules.requestItem import RequestInListWidget
from utils.fileOperations import loadRequests, saveRequest, removeRequest


class RequestsMainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._data = loadRequests()
        self.ROW_TO_DATA = []

        # LEFT - LIST LAYOUT
        self.requestsListLayout = QGridLayout()

        self.requestsListWidget = QListWidget()
        self.requestsListWidget.setMaximumWidth(320)
        self.createNewRequest = QPushButton("Create new request")

        self.requestsListLayout.addWidget(self.requestsListWidget, 0, 0)
        self.requestsListLayout.addWidget(self.createNewRequest, 1, 0)

        # RIGHT - WORKSPACE LAYOUT
        self.requestWorkspaceWidget = RequestWorkspaceWidget(self)

        # Set general layout
        allQGridLayout = QGridLayout()
        allQGridLayout.setColumnStretch(0, 2)
        allQGridLayout.setColumnStretch(1, 5)
        allQGridLayout.addLayout(self.requestsListLayout, 0, 0)
        allQGridLayout.addWidget(self.requestWorkspaceWidget, 0, 1)
        self.setLayout(allQGridLayout)

        # Connections
        self.requestsListWidget.selectionModel().currentChanged.connect(
            self.onRowChanged)
        # Creating new Request - remove selection
        self.createNewRequest.clicked.connect(self.removeCurrentSelection)

        # Fill Requests List
        self.fill_list()

    def createRequestWidget(self, requestName, requestType,
                            requestEndpoint):
        # Create QCustomQWidget
        newRequestInListWidget = RequestInListWidget()
        newRequestInListWidget.setRequestName(requestName)
        newRequestInListWidget.setRequestType(requestType)
        newRequestInListWidget.setRequestEndpoint(requestEndpoint)
        return newRequestInListWidget

    def guiSaveRequest(self):
        requestName = self.requestWorkspaceWidget.requestName.text()
        requestType = str(
            self.requestWorkspaceWidget.requestType.currentText())
        requestEndpoint = self.requestWorkspaceWidget.requestEndpoint.text()
        requestHeaders = (self.requestWorkspaceWidget
                              .RequestAdvancedEditing.requestHeaders
                              .accessHeadersData())
        requestBody = (self.requestWorkspaceWidget
                           .RequestAdvancedEditing.requestBody.toPlainText())
        # Set object
        self.requestObj = {
            "name": requestName,
            "type": requestType,
            "endpoint": requestEndpoint,
            "headers": requestHeaders,
            "body": requestBody,
        }

        # Check if request has id (has been already in list)
        if self.requestWorkspaceWidget.requestId is None:
            requestItem = self.addRequestToRequestsList(
                requestName, requestType, requestEndpoint)
            # Add QListWidgetItem into QListWidget
            self.requestsListWidget.addItem(
                requestItem["RequestsQListWidgetItem"])
            self.requestsListWidget.setItemWidget(
                requestItem["RequestsQListWidgetItem"],
                requestItem["newRequestInListWidget"])

            requestId = saveRequest(self.requestObj)
            self.requestWorkspaceWidget.requestId = requestId
            self.requestWorkspaceWidget.requestLastModificationDate.setText(
                "Saved just a while ago")
            self._data = loadRequests()
            self.ROW_TO_DATA.append(requestId)
        else:
            selectedRow = self.currentSelectedRequest

            # Overwrite Request with same id
            self.requestObj["id"] = self._data[selectedRow]["id"]
            saveRequest(self.requestObj)

            # Delete currently selected item
            self.requestsListWidget.takeItem(selectedRow)

            # Create Request Item
            newRequestInListWidget = self.createRequestWidget(
                requestName, requestType, requestEndpoint)

            # Create QListWidgetItem
            RequestsQListWidgetItem = QListWidgetItem()

            # Set size hint
            RequestsQListWidgetItem.setSizeHint(
                newRequestInListWidget.sizeHint())

            self.requestsListWidget.insertItem(
                selectedRow, RequestsQListWidgetItem)

            self.requestsListWidget.setItemWidget(
                RequestsQListWidgetItem,
                newRequestInListWidget)

            # Update current request in workspace
            self.requestWorkspaceWidget.requestId = self.requestObj["id"]
            self._data = loadRequests()
            self.requestsListWidget.setCurrentRow(selectedRow)
            (self.requestWorkspaceWidget.requestLastModificationDate
                                        .setText("Saved just a while ago"))

    def addRequestToRequestsList(self, requestName, requestType,
                                 requestEndpoint):
        newRequestInListWidget = self.createRequestWidget(requestName,
                                                          requestType,
                                                          requestEndpoint)

        # Create QListWidgetItem
        RequestsQListWidgetItem = QListWidgetItem(
            self.requestsListWidget)

        # Set size hint
        RequestsQListWidgetItem.setSizeHint(
            newRequestInListWidget.sizeHint())

        return({"RequestsQListWidgetItem": RequestsQListWidgetItem,
                "newRequestInListWidget": newRequestInListWidget})

    def guiDeleteRequest(self):
        listItems = self.requestsListWidget.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.requestsListWidget.takeItem(self.requestsListWidget.row(item))
            removeRequest(self.ROW_TO_DATA[self.currentSelectedRequest-1])
            del self.ROW_TO_DATA[self.currentSelectedRequest-1]

    def removeCurrentSelection(self):
        # Clear all inputs
        self.clearWorkspaceInputs()
        self.requestWorkspaceWidget.requestId = None
        self.requestsListWidget.clearSelection()

    def fill_list(self, data=None):
        data = self._data if not data else data
        for index, request in enumerate(data):
            requestItem = self.addRequestToRequestsList(
                request["name"], request["type"], request["endpoint"])
            self.requestsListWidget.addItem(
                requestItem["RequestsQListWidgetItem"])
            self.requestsListWidget.setItemWidget(
                requestItem["RequestsQListWidgetItem"],
                requestItem["newRequestInListWidget"])
            self.ROW_TO_DATA.append(request["id"])

    def onRowChanged(self, current, previous):
        self.currentSelectedRequest = current.row()
        selectedRequestObj = next(request for request in self._data
                                  if request["id"] == self.ROW_TO_DATA[self.currentSelectedRequest])
        # Clear all inputs
        self.clearWorkspaceInputs()

        # Load data from request object
        self.requestWorkspaceWidget.requestName.setText(
            selectedRequestObj["name"])

        # Format data
        time = datetime.datetime.strptime(selectedRequestObj["lastModificationDate"], '%Y-%m-%dT%H:%M:%SZ')
        month = "0"+str(time.month) if time.month < 10 else time.month

        (self.requestWorkspaceWidget
             .requestLastModificationDate
             .setText(f'Saved:  {time.year}/{month}/{time.day} at {time.hour}:{time.minute}'))

        self.requestWorkspaceWidget.requestType.setCurrentText(
            selectedRequestObj["type"])
        self.requestWorkspaceWidget.requestEndpoint.setText(
            selectedRequestObj["endpoint"])

        # Check if body is json type
        try:
            parsedBody = json.loads(selectedRequestObj["body"])
            formatedBody = json.dumps(parsedBody, indent=4)
            self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText(formatedBody)
        except Exception as ex:
            self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText(selectedRequestObj["body"])

        (self.requestWorkspaceWidget
             .requestHeadersData) = selectedRequestObj["headers"]
        self.requestWorkspaceWidget.printRequestHeaders()
        self.requestWorkspaceWidget.requestId = selectedRequestObj["id"]

        self.requestWorkspaceWidget.saveRequestInList.setText("Update request")

    def clearWorkspaceInputs(self):
        self.requestWorkspaceWidget.requestName.setText("")
        self.requestWorkspaceWidget.requestLastModificationDate.setText("")
        self.requestWorkspaceWidget.requestType.setCurrentIndex(0)
        self.requestWorkspaceWidget.requestEndpoint.setText("")
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText("")
        self.requestWorkspaceWidget.RequestResponse.responseBody.setText("")
        self.requestWorkspaceWidget.RequestResponse.responseStatus.setText("")
        self.requestWorkspaceWidget.saveRequestInList.setText("Save request")

    def checkDisableSaveAndDelete(self, s):
        if (not self.requestWorkspaceWidget.requestName.text() or
                not self.requestWorkspaceWidget.requestEndpoint.text()):
            self.requestWorkspaceWidget.saveRequestInList.setEnabled(False)
            self.requestWorkspaceWidget.deleteRequestFromList.setEnabled(False)
        else:
            self.requestWorkspaceWidget.saveRequestInList.setEnabled(True)
            self.requestWorkspaceWidget.deleteRequestFromList.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("RequestsManager")
        self.setCentralWidget(widget)
        self.setMinimumSize(1200, 600)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    # QWidget
    widget = RequestsMainWidget()
    window = MainWindow(widget)
    window.show()

    # Execute application
    sys.exit(app.exec_())
