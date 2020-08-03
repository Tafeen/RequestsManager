import sys
from PySide2.QtWidgets import (QApplication, QGridLayout, QFrame)
from screens.RequestsListView import RequestListFrame
from screens.RequestWorkspace import RequestWorkspaceFrame


class MainWindow(QFrame):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # Set the title
        title = "RequestsManager"
        self.setWindowTitle(title)
        # Create RequestListFrame
        self.RequestList = RequestListFrame()
        self.RequestList.setMaximumWidth(320)
        # Create WorkspaceFrame
        self.RequestWorkspace = RequestWorkspaceFrame()
        # Create layout and add Frames
        allQGridLayout = QGridLayout()
        allQGridLayout.setColumnStretch(0, 2)
        allQGridLayout.setColumnStretch(1, 5)
        allQGridLayout.addWidget(self.RequestList, 0, 0)
        allQGridLayout.addWidget(self.RequestWorkspace, 0, 1)
        # Set dialog layout
        self.setLayout(allQGridLayout)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Set minimum size of window
    window = MainWindow()
    window.setMinimumSize(900, 600)
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
