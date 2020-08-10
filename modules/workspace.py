from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox)


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

        self.requestName.textChanged[str].connect(parent.checkDisableSaveAndDelete)
        self.requestEndpoint.textChanged[str].connect(parent.checkDisableSaveAndDelete)
        self.saveRequestInList.clicked.connect(parent.guiSaveRequest)
        self.deleteRequestFromList.clicked.connect(parent.guiDeleteRequest)
