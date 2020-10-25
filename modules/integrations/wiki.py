from PySide2.QtWidgets import (QLineEdit, QRadioButton, QLabel, QPushButton, QGridLayout,
                               QDialog, QWidget, QComboBox)
from PySide2.QtCore import Qt
from utils.fileOperations import (saveInitialUserDataToFile,
                                  saveUserIntegrationToFile)
import requests
import json

# user settings
class wikiUserSettingsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self.mainParent = self.parent.parent.parent
        super(wikiUserSettingsWidget, self).__init__(parent)

        self._userData = self.mainParent._userData
        self.gitlabURLinput = QLineEdit()
        self.githubURLinput = QLineEdit()

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(QLabel("Wiki"), 0, 0)
        self.allQGridLayout.addWidget(QLabel("Gitlab access_token: "), 1, 1)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 1, 2, 1, 1)
        self.allQGridLayout.addWidget(QLabel("Github access_token: "), 2, 1)
        self.allQGridLayout.addWidget(self.githubURLinput, 2, 2, 1, 1)
        self.setLayout(self.allQGridLayout)

        wikiIntegrationIndex = next((i for i, item in enumerate(
            self._userData["integrations"]) if item["integrationType"] == "wiki"), None)
        for integration in self._userData["integrations"][wikiIntegrationIndex]["data"]:
            provider = getattr(self, integration["provider"]+"URLinput")
            provider.setText(integration["token"])


# workspace settings
class wikiWorkspaceWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(wikiWorkspaceWidget, self).__init__(parent)
        self._currentWorkspaceData = self.parent._currentWorkspaceData
        self.selectedIntegrationName = None

        workspaceData = next((item for item in self.parent.parent.parent._userData["workspaces"] if item["id"] == self.parent.parent.parent.workspaceId), None)
        if workspaceData is not None:
            wikiIntegration = next((item for item in workspaceData["integrations"] if item["integrationType"] == "wiki"), None)
            self.selectedIntegrationName = wikiIntegration["data"]["selectedProvider"]

        self.wikiDict = next(
            (item for item in self._currentWorkspaceData["integrations"] if item["integrationType"] == "wiki"), None)

        self.gitlab = next(
            (item for item in self.wikiDict["data"] if item["provider"] == "gitlab"), None)
        gitlabUrl = self.gitlab.get("projectUrl") if (
            self.gitlab is not None) else ""
        self.gitlabRadioButton = QRadioButton("gitlab")
        self.gitlabURLinput = QLineEdit(gitlabUrl)
        self.gitlabURLinput.setPlaceholderText(
            "https://gitlab.com/project/repo")
        self.github = next(
            (item for item in self.wikiDict["data"] if item["provider"] == "github"), None)
        githubUrl = self.github.get("projectUrl") if (
            self.github is not None) else ""
        self.githubRadioButton = QRadioButton("github")
        self.githubURLinput = QLineEdit(githubUrl)
        self.githubURLinput.setPlaceholderText(
            "https://github.com/project/repo")

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(QLabel("Wiki"), 0, 0)
        self.allQGridLayout.addWidget(self.githubRadioButton, 1, 1)
        self.allQGridLayout.addWidget(self.githubURLinput, 1, 2, 1, 1)
        self.allQGridLayout.addWidget(self.gitlabRadioButton, 2, 1)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 2, 2, 1, 1)
        self.setLayout(self.allQGridLayout)

        self.gitlabRadioButton.setChecked(
            self.selectedIntegrationName == "gitlab")
        self.githubRadioButton.setChecked(
            self.selectedIntegrationName == "github")

        self.githubRadioButton.toggled.connect(self.onRadioBtn)
        self.gitlabRadioButton.toggled.connect(self.onRadioBtn)

    def integrationList(self):
        gitlabIntegrationObj = {
            "provider": "gitlab",
            "projectUrl": self.gitlabURLinput.text()
        }
        githubIntegrationObj = {
            "provider": "github",
            "projectUrl": self.githubURLinput.text()
        }
        integrations = [gitlabIntegrationObj, githubIntegrationObj]
        return(integrations)

    def onRadioBtn(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.selectedIntegrationName = radioBtn.text()


# initial setup
class wikiInitialSetup(QWidget):
    def __init__(self, parent, connection):
        self.parent = parent
        self.integrationProvider = connection["provider"]
        super(wikiInitialSetup, self).__init__(parent)
        self.ErrorDuringConnection = ErrorDuringConnection(self)
        self.SuccessAfterConnection = SuccessAfterConnection(self)

        print(connection)
        # repository link
        # check if present already
        self.repositoryUrl = QLineEdit()
        self.repositoryUrl.setPlaceholderText("Repository url")
        self.repositoryUrl.setText(connection["url"])

        # user access token
        # check if present already
        self.accessToken = QLineEdit()
        self.accessToken.setPlaceholderText(
            "User access token with permission read_api")
        self.accessToken.setText(connection["token"])

        # connect button
        self.connectWithRepositoryBtn = QPushButton("Link with wiki")

        # Set layout
        self.allQGridLayout = QGridLayout()

        # Set final layout
        self.allQGridLayout.addWidget(QLabel("Repository url:"), 0, 0)
        self.allQGridLayout.addWidget(self.repositoryUrl, 1, 0)
        self.allQGridLayout.addWidget(QLabel("User access token:"), 2, 0)
        self.allQGridLayout.addWidget(self.accessToken, 3, 0)
        self.allQGridLayout.addWidget(
            self.connectWithRepositoryBtn, 4, 0, Qt.AlignRight)

        self.setLayout(self.allQGridLayout)

        self.repositoryUrl.setFocus()
        self.connectWithRepositoryBtn.clicked.connect(self.linkToRepository)

    def closeError(self):
        self.ErrorDuringConnection.close()

    def closeSuccess(self):
        self.SuccessAfterConnection.close()
        self.parent.parent.closeIntegrationSetup()

    def linkToRepository(self):
        if(self.integrationProvider == "gitlab"):
            try:
                spaceName = self.repositoryUrl.text().rsplit("/", 2)[1]
                project = self.repositoryUrl.text().rsplit("/", 2)[2]
                projectPath = spaceName + "%2F" + project
                url = "https://gitlab.com/api/v4/projects/" + projectPath + "/wikis"
                connection = requests.get(url, headers={
                                          "User-Agent": "RequestsManager.0.2020.0.2", "PRIVATE-TOKEN": self.accessToken.text()})
                if(connection.status_code == 200):
                    # Connected
                    print("connected with wiki successfully")
                    json.loads(str(connection.text))
                    integrationObj = {
                        "provider": self.integrationProvider,
                        "access_token": self.accessToken.text()
                    }
                    # Save connection to user settings
                    saveUserIntegrationToFile(integrationObj)
                    # Save workspace integration to workspace settings
                    integrations = []
                    gitlabIntegrationObj = {
                        "provider": self.integrationProvider,
                        "projectUrl": self.repositoryUrl.text()
                    }
                    integrations.append(gitlabIntegrationObj)

                    self.parent.parent.parent.parent.parent.workspaceSettingsWidget.saveWorkspace(
                        integrations, self.integrationProvider)
                    self.parent.parent.setupLayout()
                    # TODO: Save connection to workspace
                    self.SuccessAfterConnection.show()
                    self.SuccessAfterConnection.activateWindow()
                else:
                    self.ErrorDuringConnection.show()
                    self.ErrorDuringConnection.activateWindow()
            except Exception as ex:
                print("error during connection")
                print(ex)
                self.ErrorDuringConnection.show()
                self.ErrorDuringConnection.activateWindow()
        else:
            print("This provider is not available yet")


class SuccessAfterConnection(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(SuccessAfterConnection, self).__init__(parent)
        self.setWindowTitle("Successfully connected")
        self.setMinimumSize(420, 120)

        accepted = QLabel(
            "Successfully connected to provider - now you can view wiki from requests manager")
        self.acceptBtn = QPushButton("Ok")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(accepted)
        self.allQGridLayout.addWidget(self.acceptBtn)
        self.setLayout(self.allQGridLayout)

        self.acceptBtn.clicked.connect(self.parent.closeSuccess)


class ErrorDuringConnection(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(ErrorDuringConnection, self).__init__(parent)
        self.setWindowTitle("Couldn't connect")
        self.setMinimumSize(420, 120)

        notConnnected = QLabel(
            "Couldn't connect to provider - check if url and token are correct")
        self.acceptBtn = QPushButton("Ok")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(notConnnected)
        self.allQGridLayout.addWidget(self.acceptBtn)
        self.setLayout(self.allQGridLayout)

        self.acceptBtn.clicked.connect(self.parent.closeError)
