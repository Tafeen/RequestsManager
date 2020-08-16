from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QPushButton, QGridLayout,
                               QWidget, QComboBox,
                               QTableWidget, QHeaderView, QTableWidgetItem,
                               QTabWidget)


class RequestsResponseWidget(QWidget):
    def __init__(self, parent):
        super(RequestsResponseWidget, self).__init__(parent)

        wholeResponseLayout = QGridLayout()
        responseTitle = QLabel("Response:")
        self.responseStatus = QLabel()
        self.responseStatus.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.responseBody = QLabel()
        self.responseBody.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.responseBody.setFixedWidth = 2
        self.responseBody.setFixedHeight = 1

        wholeResponseLayout.addWidget(responseTitle, 0, 0)
        wholeResponseLayout.addWidget(self.responseStatus, 1, 0)
        wholeResponseLayout.addWidget(self.responseBody, 2, 0)

        self.setLayout(wholeResponseLayout)
