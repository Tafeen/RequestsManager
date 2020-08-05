import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QApplication, QMainWindow, QListWidget,
                               QListWidgetItem, QGridLayout,
                               QWidget, QPushButton)
from modules.workspace import RequestWorkspaceWidget
from modules.requestItem import RequestInListWidget
from utils.fileOperations import loadRequests, saveRequest


class RequestsMainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._data = loadRequests()

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

        # Signals and Slots
        self.requestsListWidget.selectionModel().currentChanged.connect(
            self.on_row_changed)
        self.createNewRequest.clicked.connect(self.removeSelection)

        # Fill Requests List
        self.fill_list()

    @Slot()
    def add_request(self):
        requestName = self.requestWorkspaceWidget.requestName.text()
        requestType = str(
            self.requestWorkspaceWidget.requestType.currentText())
        requestEndpoint = self.requestWorkspaceWidget.requestEndpoint.text()
        requestBody = self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.toPlainText()

        # Set object
        self.requestObj = {
            "name": requestName,
            "type": requestType,
            "endpoint": requestEndpoint,
            "headers": {
                "User-Agent": "",
                "Content-Type": "application/json"
            },
            "body": requestBody,
        }

        # Check if request has id (has been already in list)
        if self.requestWorkspaceWidget.requestId is None:
            self.addRequestToRequestsList(
                requestName, requestType, requestEndpoint)
            requestId = saveRequest(self.requestObj)
            self.requestWorkspaceWidget.requestId = requestId
            self.requestWorkspaceWidget.requestLastModificationDate.setText(
                "Just a while ago")
            self._data = loadRequests()

        # TODO: If else - update already added item in list

    @Slot()
    def removeSelection(self):
        # Clear all inputs
        self.clearWorkspaceInputs()
        self.requestWorkspaceWidget.requestId = None
        self.requestsListWidget.clearSelection()

    @Slot()
    def addRequestToRequestsList(self, requestName, requestType,
                                 requestEndpoint):
        # Create QCustomQWidget
        myRequestInListWidget = RequestInListWidget()
        myRequestInListWidget.setRequestName(requestName)
        myRequestInListWidget.setRequestType(requestType)
        myRequestInListWidget.setRequestEndpoint(requestEndpoint)

        # Create QListWidgetItem
        RequestsQListWidgetItem = QListWidgetItem(
            self.requestsListWidget)

        # Set size hint
        RequestsQListWidgetItem.setSizeHint(
            myRequestInListWidget.sizeHint())

        # Add QListWidgetItem into QListWidget
        self.requestsListWidget.addItem(RequestsQListWidgetItem)
        self.requestsListWidget.setItemWidget(
            RequestsQListWidgetItem, myRequestInListWidget)

    @Slot()
    def removeSelectedRequests(self):
        listItems = self.requestsListWidget.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.requestsListWidget.takeItem(self.requestsListWidget.row(item))

    @Slot()
    def fill_list(self, data=None):
        data = self._data if not data else data
        for index, request in enumerate(data):
            self.addRequestToRequestsList(
                request["name"], request["type"], request["endpoint"])

    @Slot()
    def on_row_changed(self, current, previous):
        print(f'Row {current.row()} selected')
        selectedRequestObj = self._data[current.row()]

        # Clear all inputs
        self.clearWorkspaceInputs()

        self.requestWorkspaceWidget.requestName.setText(
            selectedRequestObj["name"])
        self.requestWorkspaceWidget.requestLastModificationDate.setText(
            selectedRequestObj["lastModificationDate"])
        self.requestWorkspaceWidget.requestType.setCurrentText(
            selectedRequestObj["type"])
        self.requestWorkspaceWidget.requestEndpoint.setText(
            selectedRequestObj["endpoint"])
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText(
            selectedRequestObj["body"])
        self.requestWorkspaceWidget.requestId = self._data[current.row()]["id"]

        self.requestWorkspaceWidget.addRequestToList.setText("Update request")

    @Slot()
    def clearWorkspaceInputs(self):
        self.requestWorkspaceWidget.requestName.setText("")
        self.requestWorkspaceWidget.requestLastModificationDate.setText("")
        self.requestWorkspaceWidget.requestType.setCurrentIndex(0)
        self.requestWorkspaceWidget.requestEndpoint.setText("")
        self.requestWorkspaceWidget.RequestAdvancedEditing.requestBody.setText(
            "")
        self.requestWorkspaceWidget.addRequestToList.setText("Save request")

    @Slot()
    def check_disable(self, s):
        if (not self.requestWorkspaceWidget.requestName.text() or
                not self.requestWorkspaceWidget.requestEndpoint.text()):
            self.requestWorkspaceWidget.addRequestToList.setEnabled(False)
        else:
            self.requestWorkspaceWidget.addRequestToList.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("RequestsManager")
        self.setCentralWidget(widget)
        self.setMinimumSize(900, 600)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    # QWidget
    widget = RequestsMainWidget()
    window = MainWindow(widget)
    window.show()

    # Execute application
    sys.exit(app.exec_())
