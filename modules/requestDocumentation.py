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


class SuccessAfterConnection(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(SuccessAfterConnection, self).__init__(parent)
        self.setWindowTitle("Successfully connected")
        self.setMinimumSize(420, 120)

        accepted = QLabel("Successfully connected to provider - now you can view wiki from requests manager")
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
        print(self.integrationProvider)

        # repository link
        self.repositoryUrl = QLineEdit()
        self.repositoryUrl.setPlaceholderText("Repository url")

        # user access token
        self.accessToken = QLineEdit()
        self.accessToken.setPlaceholderText("User access token with permission read_api")

        # connect button
        self.connectWithRepositoryBtn = QPushButton("Link with wiki")

        # Set layout
        self.allQGridLayout = QGridLayout()

        # Set final layout
        self.allQGridLayout.addWidget(self.repositoryUrl, 0, 0)
        self.allQGridLayout.addWidget(self.accessToken, 1, 0)
        self.allQGridLayout.addWidget(self.connectWithRepositoryBtn, 2, 0, Qt.AlignRight)

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
                spaceName = self.repositoryUrl.text().rsplit("/",2)[1]
                project = self.repositoryUrl.text().rsplit("/",2)[2]
                projectPath = spaceName + "%2F" + project
                url = "https://gitlab.com/api/v4/projects/" + projectPath + "/wikis"
                connection = requests.get(url, headers={"User-Agent": "RequestsManager.0.2020.0.2", "PRIVATE-TOKEN": self.accessToken.text()})
                if(connection.status_code == 200):
                    # Connected
                    parsedBody = json.loads(str(connection.text))
                    integrationObj = {
                        "provider": self.integrationProvider,
                        "access_token": self.accessToken.text()
                    }
                    # Save connection
                    saveIntegrations(integrationObj)
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


class RequestDocumentation(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self._requestDocumentationData = None
        super(RequestDocumentation, self).__init__(parent)
       
        self.connectWithGitlabBtn = QPushButton("Connect with gitlab wiki's")

        # Set layout
        self.requestDocumentationLayout = QHBoxLayout()
        self.requestDocumentationLayout.addWidget(self.connectWithGitlabBtn)
        self.setLayout(self.requestDocumentationLayout)

        self.connectWithGitlabBtn.clicked.connect(lambda provider: self.Integration("gitlab"))
        

    def closeIntegrationSetup(self):
        self.integrationDialog.close()

    @Slot()
    def Integration(self, provider="gitlab"):
        # Create linking with gitlab wiki's window per each user
        self.integrationDialog = Integration(self, provider)
        self.integrationDialog.show()
        self.integrationDialog.activateWindow()
