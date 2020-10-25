from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDialog, QLabel, QTabWidget, QLayout, QVBoxLayout,
                               QGridLayout, QLineEdit, QPushButton, QTextEdit)
import requests
import json
from modules.integrations.wiki import wikiInitialSetup


class Integration(QDialog):
    def __init__(self, parent, data):
        self.parent = parent
        super(Integration, self).__init__(parent)
        self.setWindowTitle(f'Connect with {data["provider"]} repository wiki')
        self.setMinimumSize(600, 350)

        # Set layout
        self.allQGridLayout = QHBoxLayout()
        self.allQGridLayout.addWidget(wikiInitialSetup(self, data))
        self.setLayout(self.allQGridLayout)


class wikiPages(QWidget):
    def __init__(self, parent, integrationProvider, integrationURL, integrationKEY):
        self.parent = parent
        super(wikiPages, self).__init__(parent)
        self.setupLayout(integrationProvider, integrationURL, integrationKEY)

    def reloadLayout(self, tf):
        print("Layout reloaded Wiki page")
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


class RequestWiki(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self.mainParent = self.parent.parent.parent
        super(RequestWiki, self).__init__(parent)
        self.requestWikiLayout = QGridLayout()
        self.setupLayout()
        self.setLayout(self.requestWikiLayout)

    def setupLayout(self):
        if(hasattr(self, "wikiScreen")):
            print("Wikiscreen", self.wikiScreen.isVisible())
        if(hasattr(self, "gitlabBtn")):
            print("gitlab", self.gitlabBtn.isVisible())
        # Get selected wiki provider from user settings
        wikiIntegrationUserIndex = next((i for i, item in enumerate(
            self.mainParent._userData["workspaces"]) if item["id"] == self.mainParent.workspaceId), None)
        wikiIntegrationUserWikiData = next(
            (item for item in self.mainParent._userData["workspaces"][wikiIntegrationUserIndex]["integrations"]if item["integrationType"] == "wiki"), None)
        wikiIntegrationSelectedProvider = wikiIntegrationUserWikiData["data"]["selectedProvider"]

        # Get selected wiki token from user settings
        wikiIntegrationUserIndex = next((i for i, item in enumerate(
            self.mainParent._userData["integrations"]) if item["integrationType"] == "wiki"), None)
        wikiIntegrationUserItem = next(
            (item for item in self.mainParent._userData["integrations"][wikiIntegrationUserIndex]["data"] if item["provider"] == wikiIntegrationSelectedProvider), None)
        wikiIntegrationSelectedToken = wikiIntegrationUserItem["token"]

        # Get selected wiki project url from workspace
        wikiIntegrationWorkspaceData = next((i for i, item in enumerate(
            self.mainParent._workspacesData[self.mainParent.workspaceId]["integrations"]) if item["integrationType"] == "wiki"), None)
        wikiIntegrationWorkspaceProviderData = next((item for item in self.mainParent._workspacesData[self.mainParent.workspaceId][
                                                    "integrations"][wikiIntegrationWorkspaceData]["data"] if item["provider"] == wikiIntegrationSelectedProvider), None)
        wikiIntegrationSelectedProjectUrl = wikiIntegrationWorkspaceProviderData["projectUrl"]
        if (len(wikiIntegrationSelectedProjectUrl) > 0 and len(wikiIntegrationSelectedToken) > 0):
            # check if already added
            if(hasattr(self, "wikiScreen")):
                self.wikiScreen.hide()
                self.layout().removeWidget(self.wikiScreen)
            self.wikiScreen = wikiPages(self, wikiIntegrationSelectedProvider,
                                        wikiIntegrationSelectedProjectUrl, wikiIntegrationSelectedToken)
            self.requestWikiLayout.addWidget(self.wikiScreen)
            if(hasattr(self, "gitlabBtn")):
                self.githubBtn.hide()
                self.gitlabBtn.hide()
        else:
            # check if already added
            if(hasattr(self, "wikiScreen")):
                self.wikiScreen.hide()
            if(hasattr(self, "gitlabBtn")):
                self.gitlabBtn.show()
                self.githubBtn.show()
            else:
                self.gitlabBtn = QPushButton("Connect with gitlab wiki's")
                self.githubBtn = QPushButton("Connect with github wiki's")
                self.requestWikiLayout.addWidget(self.gitlabBtn, 0, 0)
                self.requestWikiLayout.addWidget(self.githubBtn, 0, 1)
            gitlabToken = next(
            (item for item in self.mainParent._userData["integrations"][wikiIntegrationUserIndex]["data"] if item["provider"] == "gitlab"), None)
            gitlabUrl = next(
            (item for item in self.mainParent._workspacesData[self.mainParent.workspaceId]["integrations"][wikiIntegrationWorkspaceData]["data"] if item["provider"] == "gitlab"), None)
            self.gitlabBtn.clicked.connect(
                lambda: self.Integration({"provider": "gitlab", "url": gitlabUrl["projectUrl"], "token": gitlabToken["token"]})
            )
            githubToken = next(
            (item for item in self.mainParent._userData["integrations"][wikiIntegrationUserIndex]["data"] if item["provider"] == "github"), None)
            githubUrl = next(
            (item for item in self.mainParent._workspacesData[self.mainParent.workspaceId]["integrations"][wikiIntegrationWorkspaceData]["data"] if item["provider"] == "github"), None)
            self.githubBtn.clicked.connect(
                lambda: self.Integration({"provider": "github", "url": githubUrl["projectUrl"], "token": githubToken["token"]})
            )

        self.requestWikiLayout.setSizeConstraint(QLayout.SetMinimumSize)

    def closeIntegrationSetup(self):
        self.integrationDialog.close()

    @Slot()
    def Integration(self, data):
        # Create linking with gitlab wiki's window per each user
        self.integrationDialog = Integration(self, data)
        self.integrationDialog.show()
        self.integrationDialog.activateWindow()
