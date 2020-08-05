from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox, QMenuBar)


class RequestAdvancedEditingWidget(QWidget):
    def __init__(self, parent):
        super(RequestAdvancedEditingWidget, self).__init__(parent)
        self.requestBody = QTextEdit()

        self.requestMenuHeaders = QLabel("Headers")
        self.requestMenuBody = QLabel("Body")

        self.switchQHBoxLayout = QHBoxLayout()
        self.switchQHBoxLayout.addWidget(self.requestMenuHeaders)
        self.switchQHBoxLayout.addWidget(self.requestMenuBody)

        allQGridLayout = QGridLayout()
        allQGridLayout.addLayout(self.switchQHBoxLayout, 0, 0)
        allQGridLayout.addWidget(self.requestBody, 1, 0)

        self.setLayout(allQGridLayout)


class RequestWorkspaceWidget(QWidget):
    def __init__(self, parent):
        super(RequestWorkspaceWidget, self).__init__(parent)

        # Request name
        self.requestName = QLineEdit()
        self.requestName.setPlaceholderText("Request name")

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

        # Request 'request button' with disabling until filled inputs
        self.addRequestToList = QPushButton("Save request")
        self.sendRequest = QPushButton("Send Request")
        self.addRequestToList.setEnabled(False)

        # Set request editing widget
        self.RequestAdvancedEditing = RequestAdvancedEditingWidget(self)

        self.endpointQVBoxLayout = QHBoxLayout()
        self.endpointQVBoxLayout.addWidget(self.requestType)
        self.endpointQVBoxLayout.addWidget(self.requestEndpoint)

        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.requestName, 0, 0, 1, 0)
        self.allQGridLayout.addLayout(self.endpointQVBoxLayout, 1, 0, 1, 0)
        self.allQGridLayout.addWidget(self.RequestAdvancedEditing, 2, 0, 1, 0)
        self.allQGridLayout.addWidget(
            self.addRequestToList, 3, 2, Qt.AlignBottom)
        self.allQGridLayout.addWidget(
            self.sendRequest, 3, 1, Qt.AlignBottom)

        self.setLayout(self.allQGridLayout)

        self.requestName.textChanged[str].connect(parent.check_disable)
        self.requestEndpoint.textChanged[str].connect(parent.check_disable)
        self.addRequestToList.clicked.connect(parent.add_request)
