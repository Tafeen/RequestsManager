from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QCheckBox, QLabel, QPushButton, QGridLayout,
                               QDialog, QWidget, QComboBox, QTabWidget)


class integrationWikiWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(integrationWikiWidget, self).__init__(parent)
        # self._userData = self.parent._userData

        self.gitlabURLinput = QLineEdit()
        self.githubURLinput = QLineEdit()

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(QLabel("Gitlab access_token: "), 0, 0)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 0, 1)
        self.allQGridLayout.addWidget(QLabel("Github access_token: "), 1, 0)
        self.allQGridLayout.addWidget(self.githubURLinput, 1, 1)
        self.setLayout(self.allQGridLayout)

    # def integrationList(self):
    #     integrations = []
    #     if(self.gitlab is not None or len(self.gitlabURLinput.text()) > 0):
    #         gitlabIntegrationObj = {
    #             "provider": "gitlab",
    #             "projectUrl": self.gitlabURLinput.text()
    #         }
    #         integrations.append(gitlabIntegrationObj)

    #     if(self.github is not None or len(self.githubURLinput.text()) > 0):
    #         githubIntegrationObj = {
    #             "provider": "github",
    #             "projectUrl": self.githubURLinput.text()
    #         }
    #         integrations.append(githubIntegrationObj)
    #     return(integrations)


class userSettingsDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(userSettingsDialog, self).__init__(parent)
        self.setFixedSize(420, 200)
        self.setWindowTitle("User settings")

        self.integrationsWiki = integrationWikiWidget(self)

        self.saveBtn = QPushButton("Update settings")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(QLabel("Integrations: "), 0, 0)
        self.allQGridLayout.addWidget(QLabel("Wiki"), 1, 1)
        self.allQGridLayout.addWidget(self.integrationsWiki, 2, 1, 1, 5)
        self.allQGridLayout.addWidget(self.saveBtn, 3, 5)
        self.setLayout(self.allQGridLayout)

        # self.saveBtn.clicked.connect(self.parent.saveWorkspace)
        # Save user settings


class UserSettingsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(UserSettingsWidget, self).__init__(parent)

        # Workspace Details
        self.usertSettings = QPushButton("User settings")

        allQGridLayout = QGridLayout()
        allQGridLayout.addWidget(self.usertSettings, 0, 0)

        self.setLayout(allQGridLayout)

        self.usertSettings.clicked.connect(self.openUserSettingsDialog)

    def openUserSettingsDialog(self):
        self.userSettingsDialog = userSettingsDialog(self)
        self.userSettingsDialog.show()
        self.userSettingsDialog.activateWindow()
