from PySide2.QtWidgets import (QLabel, QPushButton,
                               QGridLayout, QDialog, QWidget)
from utils.fileOperations import saveUserIntegrationToFile
from modules.integrations.wiki import wikiUserSettingsWidget


class userSettingsDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        self.mainParent = self.parent.parent
        super(userSettingsDialog, self).__init__(parent)
        self.setFixedSize(420, 200)
        self.setWindowTitle("User settings")
        
        self.integrationsWiki = wikiUserSettingsWidget(self)
        self.saveBtn = QPushButton("Update settings")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(QLabel("Integrations: "), 0, 0, 1, 4)
        self.allQGridLayout.addWidget(self.integrationsWiki, 1, 0, 1, 6)
        self.allQGridLayout.addWidget(self.saveBtn, 3, 5)
        self.setLayout(self.allQGridLayout)

        self.saveBtn.clicked.connect(self.saveIntegrations)

    # Integrations
    def saveIntegrations(self):
        # Wiki integration
        wikiIntegrationIndex = next((i for i, item in enumerate(self.mainParent._userData["integrations"]) if item["integrationType"] == "wiki"), None)
        integrationProviders = (
            "gitlab",
            "github"
        )
        for provider in integrationProviders:
            ac_tkn = getattr(self.integrationsWiki, provider+"URLinput")
            # Save user settings
            wikiIntegrationObj = {
                "provider": provider,
                "token": ac_tkn.text()
            }
            key = next((i for i, item in enumerate(
                self.mainParent._userData["integrations"][wikiIntegrationIndex]["data"]) if item["provider"] == provider), None)
            self.mainParent._userData["integrations"][wikiIntegrationIndex]["data"][key] = wikiIntegrationObj

        saveUserIntegrationToFile(self.mainParent._userData["integrations"][wikiIntegrationIndex])
        print(self.mainParent._userData["integrations"][wikiIntegrationIndex])
        # self.mainParent.requestWorkspaceWidget.RequestAdvancedEditing.requestDocumentation.reloadDocumentation()


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
