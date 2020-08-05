import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QApplication, QMainWindow, QListWidget,
                               QListWidgetItem, QGridLayout,
                               QWidget)
from modules.workspace import RequestWorkspaceWidget
from modules.requestItem import RequestInListWidget


class RequestsMainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self._data = [
            {
                "name": "Example GET request",
                "type": "GET",
                "endpoint": "https://example.com",
                "headers": {
                    "User-Agent": "",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Example POST request",
                "type": "POST",
                "endpoint": "https://example.com",
                "headers": {
                    "User-Agent": "",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Example DELETE request",
                "type": "DELETE",
                "endpoint": "https://example.com",
                "headers": {
                    "User-Agent": "",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Example PATCH request",
                "type": "PATCH",
                "endpoint": "https://example.com",
                "headers": {
                    "User-Agent": "",
                    "Content-Type": "application/json"
                }
            }
        ]

        # LEFT - LIST LAYOUT
        self.requestsListWidget = QListWidget()
        self.requestsListWidget.setMaximumWidth(320)

        # RIGHT - WORKSPACE LAYOUT
        self.requestWorkspaceWidget = RequestWorkspaceWidget(self)

        # Set general layout
        allQGridLayout = QGridLayout()
        allQGridLayout.setColumnStretch(0, 2)
        allQGridLayout.setColumnStretch(1, 5)
        allQGridLayout.addWidget(self.requestsListWidget, 0, 0)
        allQGridLayout.addWidget(self.requestWorkspaceWidget, 0, 1)
        self.setLayout(allQGridLayout)

        # Signals and Slots
        self.requestsListWidget.selectionModel().currentChanged.connect(
            self.on_row_changed)

        # Fill Requests List
        self.fill_list()

    @Slot()
    def add_request(self):
        requestName = self.requestWorkspaceWidget.requestName.text()
        requestType = str(
            self.requestWorkspaceWidget.requestType.currentText())
        requestEndpoint = self.requestWorkspaceWidget.requestEndpoint.text()

        # Insert to list
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
    def fill_list(self, data=None):
        data = self._data if not data else data
        for index, request in enumerate(data):
            # Create QCustomQWidget
            myRequestInListWidget = RequestInListWidget()
            myRequestInListWidget.setRequestName(request["name"])
            myRequestInListWidget.setRequestType(request["type"])
            myRequestInListWidget.setRequestEndpoint(request["endpoint"])

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
    def on_row_changed(self, current, previous):
        print('Row %d selected' % current.row())

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
