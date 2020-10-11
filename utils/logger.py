from PySide2.QtWidgets import (QPushButton, QPlainTextEdit)
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt, QObject, Signal

class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = Signal(str)


def __init__(self, parent):
    super().__init__()
    QObject.__init__(self)
    self.widget = QPlainTextEdit(parent)
    self.widget.setReadOnly(True)
    self.appendPlainText.connect(self.widget.appendPlainText)


def emit(self, record):
    msg = self.format(record)
    self.appendPlainText.emit(msg)
