from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDialog, QLabel, QTabWidget, QLayout, QVBoxLayout,
                               QGridLayout, QLineEdit, QPushButton, QTextEdit)
import requests
import json
from utils.fileOperations import saveUserIntegration


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


class IntegrationDetails(QWidget):
    def __init__(self, parent, provider):
        self.parent = parent
        self.integrationProvider = provider
        super(IntegrationDetails, self).__init__(parent)
        self.ErrorDuringConnection = ErrorDuringConnection(self)
        self.SuccessAfterConnection = SuccessAfterConnection(self)

        # repository link
        self.repositoryUrl = QLineEdit()
        self.repositoryUrl.setPlaceholderText("Repository url")

        # user access token
        self.accessToken = QLineEdit()
        self.accessToken.setPlaceholderText(
            "User access token with permission read_api")

        # connect button
        self.connectWithRepositoryBtn = QPushButton("Link with wiki")

        # Set layout
        self.allQGridLayout = QGridLayout()

        # Set final layout
        self.allQGridLayout.addWidget(self.repositoryUrl, 0, 0)
        self.allQGridLayout.addWidget(self.accessToken, 1, 0)
        self.allQGridLayout.addWidget(
            self.connectWithRepositoryBtn, 2, 0, Qt.AlignRight)

        self.setLayout(self.allQGridLayout)

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
                    json.loads(str(connection.text))
                    integrationObj = {
                        "provider": self.integrationProvider,
                        "access_token": self.accessToken.text()
                    }
                    # Save connection to user settings
                    saveUserIntegration(integrationObj)
                    # Save workspace integration to workspace settings
                    integrations = []
                    gitlabIntegrationObj = {
                        "provider": "gitlab",
                        "projectUrl": self.repositoryUrl.text()
                    }
                    integrations.append(gitlabIntegrationObj)
                    print("Integration provider =" + self.integrationProvider)
                    self.parent.parent.parent.parent.parent.workspaceSettingsWidget.saveWorkspace(integrations, self.integrationProvider)
                    self.parent.parent.reloadDocumentation()
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


class Integration(QDialog):
    def __init__(self, parent, provider):
        self.parent = parent
        super(Integration, self).__init__(parent)
        self.setWindowTitle(f'Connect with {provider} repository wiki')
        self.setMinimumSize(600, 350)

        # Set layout
        self.allQGridLayout = QHBoxLayout()
        self.allQGridLayout.addWidget(IntegrationDetails(self, provider))
        self.setLayout(self.allQGridLayout)


class DocumentationPages(QWidget):
    def __init__(self, parent, integrationProvider, integrationURL, integrationKEY):
        self.parent = parent
        super(DocumentationPages, self).__init__(parent)
        self.setupLayout(integrationProvider, integrationURL, integrationKEY)

    def reloadLayout(self, tf):
        print("Layout reloaded documentation page")
        if(tf):
            self.lay = QHBoxLayout()
            self.lab = QLabel("Yes")
            self.lay.addWidget(self.lab)
            self.setLayout(self.lay)
        else:
            self.lay = QHBoxLayout()
            self.lab = QLabel("No")
            self.lay.addWidget(self.lab)
            self.setLayout(self.lay)

    def setupLayout(self, integrationProvider, integrationURL, integrationKEY):
        pages = self.linkToRepository(
            integrationProvider, integrationURL, integrationKEY)
        allQGridLayout = QGridLayout()
        if(pages):
            print("Got Wiki")
            tabWidget = QTabWidget()
            for index, page in enumerate(pages):
                formatedPage = QTextEdit()
                formatedPage.setMarkdown(page["content"])
                formatedPage.setReadOnly(True)
                tabWidget.addTab(formatedPage, page["title"])

            # Set layout
            allQGridLayout.addWidget(tabWidget)
        else:
            print("Didnt get Wiki")
            # Set layout
            allQGridLayout.addWidget(QLabel(
                "Couldn't get wiki for this workspace - check if project url and token for selected provider are correct"))
        self.setLayout(allQGridLayout)

    def linkToRepository(self, integrationProvider, repositoryUrl, accessToken):
        if(integrationProvider == "gitlab"):
            try:
                spaceName = repositoryUrl.rsplit("/", 2)[1]
                project = repositoryUrl.rsplit("/", 2)[2]
                projectPath = spaceName + "%2F" + project
                url = "https://gitlab.com/api/v4/projects/" + projectPath + "/wikis"
                connection = requests.get(url, headers={
                                          "User-Agent": "RequestsManager.0.2020.0.2", "PRIVATE-TOKEN": accessToken})
                if(connection.status_code == 200):
                    # Connected
                    parsedBody = json.loads(str(connection.text))
                    pages = []
                    for page in parsedBody:
                        url = "https://gitlab.com/api/v4/projects/" + \
                            projectPath + "/wikis/" + page["slug"]
                        connection = requests.get(url, headers={
                            "User-Agent": "RequestsManager.0.2020.0.2", "PRIVATE-TOKEN": accessToken})
                        if(connection.status_code == 200):
                            parsedBody = json.loads(str(connection.text))
                            pages.append(parsedBody)
                    return(pages)
                else:
                    print("network error: " + connection.status_code)
            except Exception as ex:
                print("error during connection")
                print(ex)
        else:
            print("This provider is not available yet")


class RequestDocumentation(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(RequestDocumentation, self).__init__(parent)
        self.requestDocumentationLayout = QVBoxLayout()
        self.setupLayout()

    def setupLayout(self):
        if(hasattr(self, 'gitlabConnect')):
            self.gitlabConnect.setHidden(True)
        if(hasattr(self, 'documentationScreen')):
            self.documentationScreen.setHidden(True)

        # Workspace id
        workspace_id = self.parent.parent.parent.workspaceId

        wikis = self.parent.parent.parent._workspacesData[
            self.parent.parent.parent.workspaceId]["integrations"]["wiki"]
        user_data = self.parent.parent.parent._userData

        integration_url = None
        integration_workspace_key = None
        # Selected provider from user settings
        selected_provider_id = next((i for i, item in enumerate(
            user_data["workspaces"]) if item["id"] == workspace_id), None)
        if(selected_provider_id is not None):
            selected_provider_name = user_data["workspaces"][selected_provider_id]["integration_provider"]
            # Get project URL from workspace
            selected_workspace_provider_id = next((i for i, item in enumerate(
                wikis) if item["provider"] == selected_provider_name), None)
            if(selected_workspace_provider_id is not None):
                integration_url = wikis[selected_workspace_provider_id]["projectUrl"]
                # Get user Access token from user settings
                selected_provider_id_user_data = next((i for i, item in enumerate(
                    user_data["integrations"]) if item["provider"] == selected_provider_name), None)
                if(selected_provider_id_user_data is not None):
                    integration_workspace_key = user_data["integrations"][
                        selected_provider_id_user_data]["access_token"]

        print("Integration url:" + str(integration_url) +
              " key: " + str(integration_workspace_key))
        if(integration_url is not None and integration_workspace_key is not None):
            self.documentationScreen = DocumentationPages(
                self, selected_provider_name, integration_url, integration_workspace_key)
            self.requestDocumentationLayout.addWidget(self.documentationScreen)
        else:
            providers = ("gitlab", "github")
            self.gitlabConnect = QPushButton("Connect with gitlab wiki's")
            self.gitlabConnect.clicked.connect(
                lambda provider: self.Integration("gitlab"))
            self.requestDocumentationLayout.addWidget(self.gitlabConnect)
        self.setLayout(self.requestDocumentationLayout)
        # Update size of layout - specially needed after rebuilding widget
        self.requestDocumentationLayout.setSizeConstraint(
            QLayout.SetMinimumSize)

    def reloadDocumentation(self):
        self.setupLayout()

    def closeIntegrationSetup(self):
        self.integrationDialog.close()

    @Slot()
    def Integration(self, provider="gitlab"):
        # Create linking with gitlab wiki's window per each user
        self.integrationDialog = Integration(self, provider)
        self.integrationDialog.show()
        self.integrationDialog.activateWindow()
