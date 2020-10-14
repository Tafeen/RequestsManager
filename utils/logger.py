from PySide2.QtWidgets import (QPlainTextEdit, QDialog, QWidget,
                               QGridLayout, QPushButton, QVBoxLayout)
import logging


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QDialog, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logs")
        self.setMinimumSize(500, 1000)

        self.logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self._button = QPushButton(self)
        self._button.setText('Clear')

        layout = QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(self.logTextBox.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)

        # Connect signal to slot
        self._button.clicked.connect(self.clearBox)

    # def test(self):
    #     logging.debug('damn, a bug')
    #     logging.info('something to remember')
    #     logging.warning('that\'s not right')
    #     logging.error('foobar')

    def clearBox(self):
        self.logTextBox.widget.setPlainText('')


class logWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(logWidget, self).__init__(parent)
        self.openLogBtn = QPushButton("Logs")
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.openLogBtn, 0, 0)
        self.setLayout(self.allQGridLayout)

        self.openLogBtn.clicked.connect(self.openLogDialog)

    def openLogDialog(self):
        self.logDialog = MyDialog(self)
        self.logDialog.show()
        self.logDialog.activateWindow()
