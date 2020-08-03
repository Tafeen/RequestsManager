from PySide2.QtWidgets import (
    QGridLayout, QLabel, QFrame, QComboBox, QTextEdit, QLineEdit)


class RequestEditorFrame(QFrame):
    def __init__(self, parent=None):
        super(RequestEditorFrame, self).__init__(parent)
        self.allQGridLayout = QGridLayout()
        # Request body
        self.requestBodyText = ""
        self.requestBody = QTextEdit(self.requestBodyText)
        self.allQGridLayout.addWidget(self.requestBody, 0, 0)
        self.setLayout(self.allQGridLayout)


class RequestBasicInfoFrame(QFrame):
    def __init__(self, parent=None):
        super(RequestBasicInfoFrame, self).__init__(parent)
        self.allQGridLayout = QGridLayout()
        # Request name
        self.requestName = QLabel("Request name")
        # Request type
        TYPE_OPTIONS = [
            "GET",
            "POST",
            "DELETE",
            "PATCH"
        ]
        self.requestType = QComboBox()
        for option in TYPE_OPTIONS:
            self.requestType.addItem(option)
        # Request endpoint
        self.requestEnpointText = ""
        self.requestEnpoint = QLineEdit(self.requestEnpointText)

        self.allQGridLayout.addWidget(self.requestName, 0, 0)
        self.allQGridLayout.addWidget(self.requestType, 1, 0)
        self.allQGridLayout.addWidget(self.requestEnpoint, 1, 1)
        self.setLayout(self.allQGridLayout)


class RequestWorkspaceFrame(QFrame):
    def __init__(self, parent=None):
        super(RequestWorkspaceFrame, self).__init__(parent)
        self.allQGridLayout = QGridLayout()
        self.RequestBasicInfo = RequestBasicInfoFrame()
        self.RequestEditor = RequestEditorFrame()
        self.allQGridLayout.addWidget(self.RequestBasicInfo, 0, 0)
        self.allQGridLayout.addWidget(self.RequestEditor, 1, 0)
        self.setLayout(self.allQGridLayout)
