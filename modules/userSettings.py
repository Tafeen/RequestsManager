from PySide2.QtWidgets import (QLineEdit, QLabel, QPushButton,
                               QGridLayout, QDialog, QWidget)
from utils.fileOperations import saveUserIntegration


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

        integrations = self.parent.parent.parent._userData["integrations"]
        for integration in integrations:
            provider = getattr(self, integration["provider"]+"URLinput")
            provider.setText(integration["access_token"])


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

        self.saveBtn.clicked.connect(self.saveIntegrations)

    def saveIntegrations(self):
        integrationProviders = (
            "gitlab",
            "github"
        )
        for provider in integrationProviders:
            ac_tkn = getattr(self.integrationsWiki, provider+"URLinput")
            # Save user settings
            integrationObj = {
                "provider": provider,
                "access_token": ac_tkn.text()
            }
            key = next((i for i, item in enumerate(
                self.parent.parent._userData["integrations"]) if item["provider"] == provider), None)
            if(key is not None):
                self.parent.parent._userData["integrations"][key] = integrationObj
            else:
                self.parent.parent._userData["integrations"].append(integrationObj)

            saveUserIntegration(integrationObj)
        self.parent.parent.requestWorkspaceWidget.RequestAdvancedEditing.requestDocumentation.reloadDocumentation()


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
