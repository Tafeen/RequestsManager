#!/usr/bin/env python3.8.3
import sys
from datetime import datetime, timezone

from PySide2.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                               QWidget, QPushButton)
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt

from modules.workspace import RequestWorkspaceWidget
from modules.requestsList import RequestsList
from modules.workspaceSettings import WorkspaceSettingsWidget
from modules.userSettings import UserSettingsWidget

from utils.fileOperations import (saveRequestDataToFile, loadWorkspaces,
                                  removeRequestFromFile, loadUserData)


class RequestsMainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._workspacesData = loadWorkspaces()
        self.workspaceId = 0
        self._userData = loadUserData()
        self._requestsData = self._workspacesData[self.workspaceId]["requests"]
        self.selectedRequest = None

        if(len(self._requestsData) > 0):
            self.selectedRequest = len(self._requestsData)-1

        # TOP LEFT - workspace settings
        self.workspaceSettingsWidget = WorkspaceSettingsWidget(self)
        self.workspaceSettingsWidget.setMaximumWidth(320)
        self.workspaceSettingsWidget.setMaximumHeight(50)

        # TOP RIGHT - user settings
        self.userSettingsWidget = UserSettingsWidget(self)
        self.userSettingsWidget.setMaximumWidth(320)
        self.userSettingsWidget.setMaximumHeight(50)

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
        allQGridLayout.addWidget(self.workspaceSettingsWidget, 0, 0)
        allQGridLayout.addWidget(self.userSettingsWidget, 0, 1, Qt.AlignRight)
        allQGridLayout.addLayout(self.requestsListLayout, 1, 0)
        allQGridLayout.addWidget(self.requestWorkspaceWidget, 1, 1)
        self.setLayout(allQGridLayout)

        # Connections
        # On row changed set inputs
        (self.requestsListWidget.requestsList.
         selectionModel().currentChanged.connect(self.onRowChanged))

        # Creating new Request - remove selection
        self.createNewRequest.clicked.connect(self.clearWorkspace)

        # Select last item in list
        self.requestsListWidget.selectRow(len(self._requestsData)-1)

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
        if(self.selectedRequest != -1):
            self.requestWorkspaceWidget.saveRequestInList.setText(
                "Update request")

            # Update data in workspace
            requestId = self._requestsData[self.selectedRequest]["id"]
            requestName = self._requestsData[self.selectedRequest]["name"]
            requestType = self._requestsData[self.selectedRequest]["type"]
            requestEndpoint = self._requestsData[self.selectedRequest]["endpoint"]
            requestHeaders = self._requestsData[self.selectedRequest]["headers"]
            requestBody = self._requestsData[self.selectedRequest]["body"]

            # Format UTC data to locale
            timeUTC = datetime.strptime(
                self._requestsData[self.selectedRequest]["lastModificationDate"], '%Y-%m-%dT%H:%M:%SZ')
            time = timeUTC.replace(tzinfo=timezone.utc).astimezone(tz=None)

            month = "0"+str(time.month) if time.month < 10 else time.month
            day = "0"+str(time.day) if time.day < 10 else time.day
            hour = "0"+str(time.hour) if time.hour < 10 else time.hour
            minute = "0"+str(time.minute) if time.minute < 10 else time.minute

            (self.requestWorkspaceWidget
                .requestLastModificationDate
                .setText(f'Saved:  {time.year}/{month}/{day} at {hour}:{minute}'))

            self.requestWorkspaceWidget.requestId = requestId
            self.requestWorkspaceWidget.requestName.setText(requestName)
            self.requestWorkspaceWidget.requestType.setCurrentText(requestType)
            self.requestWorkspaceWidget.requestEndpoint.setText(
                requestEndpoint)
            self.requestWorkspaceWidget.RequestAdvancedEditing.requestHeadersTable.requestHeadersModel.load_data(
                requestHeaders)
            self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setPlainText(
                requestBody)        

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
            requestId = saveRequestDataToFile(self.requestDict, self.workspaceId)
            self.requestDict["id"] = requestId
            self._requestsData.append(self.requestDict)
            # Select last item in list
            self.requestsListWidget.selectRow(len(self._requestsData)-1)
            print(f'Saved request with id: {requestId}')
        else:
            self.requestDict["id"] = requestId
            saveRequestDataToFile(self.requestDict, self.workspaceId)
            self._requestsData[self.selectedRequest] = self.requestDict
            (self.requestWorkspaceWidget
             .requestLastModificationDate
             .setText("Just updated"))
            print(f'Updated request with id: {requestId}')

        self.requestsListWidget.requestsListModel.load_data(self._requestsData)

    def deleteRequest(self):
        removeRequestFromFile(self.requestWorkspaceWidget.requestId, self.workspaceId)
        self._requestsData.pop(self.selectedRequest)
        self.requestsListWidget.requestsListModel.load_data(self._requestsData)
        print("Deleted request")
        self.requestsListWidget.selectRow(len(self._requestsData)-1)

    def clearWorkspace(self):
        print("Cleared workspace")
        self.requestsListWidget.clearSelection()
        self.requestWorkspaceWidget.requestId = None
        self.requestWorkspaceWidget.requestName.setText("")
        self.requestWorkspaceWidget.requestLastModificationDate.setText("")
        self.requestWorkspaceWidget.requestType.setCurrentIndex(0)
        self.requestWorkspaceWidget.requestEndpoint.setText("")
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText(
            "")
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestHeadersTable.requestHeadersModel.load_data(
            self.requestWorkspaceWidget.defaultRequestHeadersData)
        self.requestWorkspaceWidget.RequestResponse.responseBody.setText("")
        self.requestWorkspaceWidget.RequestResponse.responseStatus.setText("")
        self.requestWorkspaceWidget.saveRequestInList.setText("Save request")

    def changeWorkspace(self, workspaceId):
        self.workspaceId = workspaceId
        self._requestsData = self._workspacesData[workspaceId]["requests"]
        if(len(self._requestsData) > 0):
            self.requestsListWidget.requestsListModel._requestsData = self._requestsData
            self.requestsListWidget.requestsListModel.load_data(self._requestsData)
            self.requestsListWidget.selectRow(len(self._requestsData)-1)
        else:
            self.requestsListWidget.requestsListModel.load_data([])
            self.clearWorkspace()
        print(workspaceId)
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestDocumentation.reloadDocumentation()   


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
