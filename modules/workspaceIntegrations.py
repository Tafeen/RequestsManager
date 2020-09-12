from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDialog, QLabel,
                               QGridLayout, QLineEdit, QPushButton)
import requests
import json
from utils.fileOperations import saveIntegrations


class ErrorDuringConnection(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(ErrorDuringConnection, self).__init__(parent)
        self.setWindowTitle("Couldn't connect")
        self.setMinimumSize(420, 120)

        notConnnected = QLabel("Couldn't connect to provider - check if url and token are correct")
        self.acceptBtn = QPushButton("Ok")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(notConnnected)
        self.allQGridLayout.addWidget(self.acceptBtn)
        self.setLayout(self.allQGridLayout)

        self.acceptBtn.clicked.connect(self.parent.closeError)