from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLabel,
                               QGridLayout, QWidget)


class RequestInListWidget(QWidget):
    def __init__(self, parent=None):
        super(RequestInListWidget, self).__init__(parent)
        self.requestName = QLabel()
        self.requestName.setAlignment(Qt.AlignHCenter)

        self.requestType = QLabel()
        self.requestType.setMaximumWidth(50)

        self.requestEndpoint = QLabel()
        self.requestEndpoint.setAlignment(Qt.AlignLeft)

        self.requestQGridLayout = QGridLayout()
        self.requestQGridLayout.setVerticalSpacing(20)
        self.requestQGridLayout.addWidget(self.requestName, 0, 0, 0, 2)
        self.requestQGridLayout.addWidget(self.requestType, 1, 0)
        self.requestQGridLayout.addWidget(self.requestEndpoint, 1, 1)

        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.addLayout(self.requestQGridLayout)
        self.setLayout(self.allQHBoxLayout)

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
