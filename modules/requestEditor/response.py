from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QTextEdit, QLabel, QGridLayout,
                               QWidget)


class RequestsResponseWidget(QWidget):
    def __init__(self, parent):
        super(RequestsResponseWidget, self).__init__(parent)

        wholeResponseLayout = QGridLayout()
        responseTitle = QLabel("Response:")
        self.responseStatus = QLabel()
        self.responseStatus.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.responseBody = QTextEdit()
        self.responseBody.setTextInteractionFlags(Qt.TextSelectableByMouse)

        wholeResponseLayout.addWidget(responseTitle, 0, 0)
        wholeResponseLayout.addWidget(self.responseStatus, 0, 0, Qt.AlignRight)
        wholeResponseLayout.addWidget(self.responseBody, 1, 0)

        self.setLayout(wholeResponseLayout)
