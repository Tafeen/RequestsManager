from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLabel,
                               QGridLayout, QWidget)


class RequestInListWidget(QWidget):
    def __init__(self, parent=None):
        super(RequestInListWidget, self).__init__(parent)
        self.requestQGridLayout = QGridLayout()
        self.requestQGridLayout.setColumnStretch(0, 0)
        self.requestQGridLayout.setColumnStretch(1, 4)
        self.requestName = QLabel()
        self.requestType = QLabel()
        self.requestEndpoint = QLabel()
        self.requestQGridLayout.addWidget(self.requestName, 0, 0, 0, 2)
        self.requestQGridLayout.addWidget(self.requestType, 1, 0)
        self.requestQGridLayout.addWidget(self.requestEndpoint, 1, 1)

        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.addLayout(self.requestQGridLayout)
        self.setLayout(self.allQHBoxLayout)

        self.requestName.setAlignment(Qt.AlignHCenter)
        self.requestEndpoint.setAlignment(Qt.AlignLeft)

    def setRequestName(self, text):
        self.requestName.setText(text)

    def setRequestType(self, text):
        requestTypeColor = {
            "POST": "orange",
            "GET": "green",
            "DELETE": "red",
            "PATCH": "silver"
        }

        self.requestType.setText(text)
        self.requestType.setStyleSheet(
            f'color: {requestTypeColor[text]};')

    def setRequestEndpoint(self, text):
        self.requestEndpoint.setText(text)
        self.requestEndpoint.setStyleSheet('color: gray')
