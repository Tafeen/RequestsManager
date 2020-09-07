#!/usr/bin/env python3.8.3
import sys
from datetime import datetime, timezone

from PySide2.QtWidgets import (QApplication, QMainWindow, QListWidget,
                               QListWidgetItem, QGridLayout,
                               QWidget, QPushButton)
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt

from modules.workspace import RequestWorkspaceWidget
from modules.requestsList import RequestsList

from utils.fileOperations import (loadRequests, saveRequestToFile,
                                  removeRequestFromFile)


class RequestsMainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._requestsData = loadRequests()
        self.selectedRequest = None

        if(len(self._requestsData) > 0):
            self.selectedRequest = len(self._requestsData)-1

        # LEFT - LIST LAYOUT
        self.requestsListLayout = QGridLayout()

        self.requestsListWidget = RequestsList(self)
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

        # On row changed set inputs
        (self.requestsListWidget.requestsList.
         selectionModel().currentChanged.connect(self.onRowChanged))

        # Creating new Request - remove selection
        # self.createNewRequest.clicked.connect(self.removeCurrentSelection)

    def checkDisableSaveAndDelete(self, s):
        if (not self.requestWorkspaceWidget.requestName.text() or
                not self.requestWorkspaceWidget.requestEndpoint.text()):
            self.requestWorkspaceWidget.saveRequestInList.setEnabled(False)
            self.requestWorkspaceWidget.deleteRequestFromList.setEnabled(False)
        else:
            self.requestWorkspaceWidget.saveRequestInList.setEnabled(True)
            self.requestWorkspaceWidget.deleteRequestFromList.setEnabled(True)

    def onRowChanged(self, current, previous):
        self.selectedRequest = current.row()
        self.requestWorkspaceWidget.saveRequestInList.setText("Update request")
        # Update data in workspace
        requestId = self._requestsData[self.selectedRequest]["id"]
        requestName = self._requestsData[self.selectedRequest]["name"]
        requestType = self._requestsData[self.selectedRequest]["type"]
        requestEndpoint = self._requestsData[self.selectedRequest]["endpoint"]
        requestHeaders = self._requestsData[self.selectedRequest]["headers"]
        requestBody = self._requestsData[self.selectedRequest]["body"]

        self.requestWorkspaceWidget.requestId = requestId
        self.requestWorkspaceWidget.requestName.setText(requestName)
        self.requestWorkspaceWidget.requestType.setCurrentText(requestType)
        self.requestWorkspaceWidget.requestEndpoint.setText(requestEndpoint)
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestHeadersTable.requestHeadersModel.load_data(requestHeaders)
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setPlainText(requestBody)


    def saveRequest(self):
        # Current data
        requestId = self.requestWorkspaceWidget.requestId
        requestName = self.requestWorkspaceWidget.requestName.text()
        requestType = self.requestWorkspaceWidget.requestType.currentText()
        requestEndpoint = self.requestWorkspaceWidget.requestEndpoint.text()
        requestHeaders = self.requestWorkspaceWidget.RequestAdvancedEditing._headersData
        requestBody = (self.requestWorkspaceWidget.
                       RequestAdvancedEditing.requestBody.toPlainText())

        self.requestDict = {
            "name": requestName,
            "type": requestType,
            "endpoint": requestEndpoint,
            "headers": requestHeaders,
            "body": requestBody,
        }

        if self.requestWorkspaceWidget.requestId is None:
            requestId = saveRequestToFile(self.requestDict)
            self.requestDict["id"] = requestId
            self._requestsData.append(self.requestDict)
            # TODO: Select last row
            print(f'saved request with id: {requestId}')
        else:
            self.requestDict["id"] = requestId
            saveRequestToFile(self.requestDict)
            self._requestsData[self.selectedRequest] = self.requestDict
            print(f'updated request with id: {requestId}')

        self.requestsListWidget.requestsListModel.load_data(self._requestsData)

    def deleteRequest(self):
        removeRequestFromFile(self.requestWorkspaceWidget.requestId)
        self._requestsData.pop(self.selectedRequest)
        self.requestsListWidget.requestsListModel.load_data(self._requestsData)
        print("Deleted request")


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("RequestsManager")
        self.setCentralWidget(widget)
        self.setMinimumSize(1200, 600)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(41, 41, 41))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(23, 23, 23))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(41, 41, 41))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Link, QColor(66, 165, 227))
    palette.setColor(QPalette.Highlight, QColor(0, 76, 117))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)

    # QWidget
    widget = RequestsMainWidget()
    window = MainWindow(widget)
    window.show()

    # Execute application
    sys.exit(app.exec_())
