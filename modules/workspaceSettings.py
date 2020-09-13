from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QHBoxLayout, QLineEdit, QTextEdit,
                               QCheckBox, QLabel, QPushButton, QGridLayout,
                               QDialog, QWidget, QComboBox, QTabWidget)
from utils.fileOperations import saveWorkspaceDataToFile, removeWorkspaceFromFile


class integrationWikiWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(integrationWikiWidget, self).__init__(parent)
        self._currentWorkspaceData = self.parent._currentWorkspaceData

        self.gitlab = next(
            (item for item in self._currentWorkspaceData["integrations"]["wiki"] if item["provider"] == "gitlab"), None)
        gitlabUrl = self.gitlab.get("projectUrl") if (
            self.gitlab is not None) else ""
        self.gitlabCheckBox = QCheckBox("Gitlab")
        self.gitlabURLinput = QLineEdit(gitlabUrl)

        self.github = next(
            (item for item in self._currentWorkspaceData["integrations"]["wiki"] if item["provider"] == "github"), None)
        githubUrl = self.github.get("projectUrl") if (
            self.github is not None) else ""
        self.githubCheckBox = QCheckBox("Github")
        self.githubURLinput = QLineEdit(githubUrl)

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.gitlabCheckBox, 0, 0)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 0, 1)
        self.allQGridLayout.addWidget(self.githubCheckBox, 1, 0)
        self.allQGridLayout.addWidget(self.githubURLinput, 1, 1)
        self.setLayout(self.allQGridLayout)

    def integrationList(self):
        integrations = []
        if(self.gitlab is not None or len(self.gitlabURLinput.text()) > 0):
            gitlabIntegrationObj = {
                "provider": "gitlab",
                "projectUrl": self.gitlabURLinput.text()
            }
            integrations.append(gitlabIntegrationObj)

        if(self.github is not None or len(self.githubURLinput.text()) > 0):
            githubIntegrationObj = {
                "provider": "github",
                "projectUrl": self.githubURLinput.text()
            }
            integrations.append(githubIntegrationObj)
        return(integrations)


class WorkspaceSettingsDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(WorkspaceSettingsDialog, self).__init__(parent)
        self._currentWorkspaceData = self.parent.parent._workspacesData[self.parent.workspaceSpaces.currentIndex(
        )]
        self.setMinimumSize(420, 120)

        self.workspaceName = QLineEdit(self._currentWorkspaceData["spaceName"])
        self.workspaceName.setPlaceholderText("Workspace name")

        self.integrationsWiki = integrationWikiWidget(self)

        self.saveBtn = QPushButton("Update workspace")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.workspaceName, 0, 0, 1, 6)
        self.allQGridLayout.addWidget(QLabel("Integrations: "), 1, 0)
        self.allQGridLayout.addWidget(QLabel("Wiki"), 2, 1)
        self.allQGridLayout.addWidget(self.integrationsWiki, 3, 1, 1, 5)
        self.allQGridLayout.addWidget(self.saveBtn, 4, 5)
        self.setLayout(self.allQGridLayout)

        self.saveBtn.clicked.connect(self.parent.saveWorkspace)


class WorkspaceSettingsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self.addingNewWorkspace = False
        super(WorkspaceSettingsWidget, self).__init__(parent)

        # Worskpaces
        WORKSPACES = [d["spaceName"] for d in self.parent._workspacesData]

        # Workspace Space
        self.workspaceSpaces = QComboBox()
        for option in WORKSPACES:
            self.workspaceSpaces.addItem(option)
        self.workspaceSpaces.addItem("Create new Workspace")

        # Workspace Details
        self.workspaceDetails = QPushButton("Settings")

        allQGridLayout = QGridLayout()
        allQGridLayout.addWidget(self.workspaceSpaces, 0, 0)
        allQGridLayout.addWidget(self.workspaceDetails, 0, 1)

        self.setLayout(allQGridLayout)

        self.workspaceDetails.clicked.connect(self.openWorkspaceSettingsDialog)
        self.workspaceSpaces.currentIndexChanged.connect(self.changeWorkspace)

    def openWorkspaceSettingsDialog(self):
        self.workspaceSettingsDialog = WorkspaceSettingsDialog(self)
        self.workspaceSettingsDialog.show()
        self.workspaceSettingsDialog.activateWindow()

    def saveWorkspace(self):
        # Update integrations
        integrationsList = self.workspaceSettingsDialog.integrationsWiki.integrationList()
        for integrationObj in enumerate(integrationsList):
            key = next((i for i, item in enumerate(self.parent._workspacesData[self.workspaceSpaces.currentIndex(
            )]["integrations"]["wiki"]) if item["provider"] == integrationObj[1]["provider"]), None)
            if(key is not None):
                self.parent._workspacesData[self.workspaceSpaces.currentIndex(
                )]["integrations"]["wiki"][key] = integrationObj[1]
            else:
                self.parent._workspacesData[self.workspaceSpaces.currentIndex(
                )]["integrations"]["wiki"].append(integrationObj[1])

        # Update name
        self.parent._workspacesData[self.workspaceSpaces.currentIndex(
        )]["spaceName"] = self.workspaceSettingsDialog.workspaceName.text()
        wasAtIndex = self.workspaceSpaces.currentIndex()
        self.updateWorkspaceNames(wasAtIndex)
        saveWorkspaceDataToFile(self.parent._workspacesData[wasAtIndex])

        if(self.addingNewWorkspace):
            if(len(self.workspaceSettingsDialog.workspaceName.text()) < 1):
                # Delete workspace
                removeWorkspaceFromFile(self.parent.workspaceId)

    def updateWorkspaceNames(self, index):
        self.workspaceSpaces.clear()
        WORKSPACES = [d["spaceName"] for d in self.parent._workspacesData]
        for option in WORKSPACES:
            self.workspaceSpaces.addItem(option)
        self.workspaceSpaces.addItem("Create new Workspace")
        self.workspaceSpaces.setCurrentIndex(index)

    def changeWorkspace(self):
        # Check if user want to add new workspace
        if (self.workspaceSpaces.currentIndex() == len(self.parent._workspacesData)):
            print("Creating new workspace")
            emptyWorkspace = {
                "spaceName": "",
                "integrations": {
                    "wiki": []
                },
                "requests": []
            }
            self.parent._workspacesData.append(emptyWorkspace)
            id = saveWorkspaceDataToFile(emptyWorkspace)
            self.parent.workspaceId = id
            self.openWorkspaceSettingsDialog()
            self.workspaceSettingsDialog.saveBtn.setText("Save workspace")
        else:
            self.parent.changeWorkspace(self.workspaceSpaces.currentIndex())
