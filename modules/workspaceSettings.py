from PySide2.QtWidgets import (QLineEdit, QRadioButton, QLabel, QPushButton, QGridLayout,
                               QDialog, QWidget, QComboBox)
from utils.fileOperations import saveWorkspaceDataToFile, removeWorkspaceFromFile
import json


class integrationWikiWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(integrationWikiWidget, self).__init__(parent)
        self._currentWorkspaceData = self.parent._currentWorkspaceData

        self.wikiDict = next(
            (item for item in self._currentWorkspaceData["integrations"] if item["integrationType"] == "wiki"), None)

        self.gitlab = next(
            (item for item in self.wikiDict["data"] if item["provider"] == "gitlab"), None)
        gitlabUrl = self.gitlab.get("projectUrl") if (
            self.gitlab is not None) else ""
        self.gitlabCheckBox = QRadioButton("Gitlab")
        self.gitlabURLinput = QLineEdit(gitlabUrl)

        self.github = next(
            (item for item in self.wikiDict["data"] if item["provider"] == "github"), None)
        githubUrl = self.github.get("projectUrl") if (
            self.github is not None) else ""
        self.githubCheckBox = QRadioButton("Github")
        self.githubURLinput = QLineEdit(githubUrl)

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.gitlabCheckBox, 0, 0)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 0, 1)
        self.allQGridLayout.addWidget(self.githubCheckBox, 1, 0)
        self.allQGridLayout.addWidget(self.githubURLinput, 1, 1)
        self.setLayout(self.allQGridLayout)

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


class WorkspaceSettingsDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(WorkspaceSettingsDialog, self).__init__(parent)
        self._currentWorkspaceData = self.parent.parent._workspacesData[self.parent.workspaceSpaces.currentIndex(
        )]
        self.setFixedSize(420, 200)
        self.setWindowTitle("Workspace settings")
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

    def closeEvent(self, event):
        print("Closed workspaceSettings")
        self.parent.checkWorkspaceIsCorrect()


class WorkspaceSettingsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self.addingNewWorkspace = False
        self.workspaceSavedToFile = False
        super(WorkspaceSettingsWidget, self).__init__(parent)

        # Worskpaces
        WORKSPACES = [d["spaceName"] for d in self.parent._workspacesData]

        # Workspace Space
        self.workspaceSpaces = QComboBox()
        for option in WORKSPACES:
            self.workspaceSpaces.addItem(option)
        self.workspaceSpaces.addItem("Create new Workspace")

        # Workspace Details
        self.workspaceDetails = QPushButton("Workspace settings")

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
        self.workspaceSavedToFile = True
        integrationsList = self.workspaceSettingsDialog.integrationsWiki.integrationList()
        for index, integrationObj in enumerate(integrationsList):
            key = next((i for i, item in enumerate(self.parent._workspacesData[self.workspaceSpaces.currentIndex(
            )]["integrations"]) if item["integrationType"] == "wiki"), None)
            self.parent._workspacesData[self.workspaceSpaces.currentIndex(
            )]["integrations"][key]["data"][index] = integrationObj

        # Update name
        self.parent._workspacesData[self.workspaceSpaces.currentIndex(
        )]["spaceName"] = self.workspaceSettingsDialog.workspaceName.text()
        wasAtIndex = self.workspaceSpaces.currentIndex()
        self.updateWorkspaceNames(wasAtIndex)
        saveWorkspaceDataToFile(self.parent._workspacesData[wasAtIndex])

        # Check if documentation screen has loaded before
        if(hasattr(self.parent.RequestEditorWidget.RequestAdvancedEditing.requestDocumentation, "documentationScreen")):
            # Update documentation layout
            self.parent.RequestEditorWidget.RequestAdvancedEditing.requestDocumentation.documentationScreen.hide()
            self.parent.RequestEditorWidget.RequestAdvancedEditing.requestDocumentation.setupLayout()
            self.parent.RequestEditorWidget.RequestAdvancedEditing.requestDocumentation.documentationScreen.show()

        if(self.addingNewWorkspace):
            self.workspaceSettingsDialog.close()

    def checkWorkspaceIsCorrect(self):
        if(self.addingNewWorkspace):
            if(len(self.workspaceSettingsDialog.workspaceName.text()) < 1):
                print("Workspace name was blank -> deleting this empty workspace")
                # Delete from file
                removeWorkspaceFromFile(self.parent.workspaceId)
                if(self.workspaceSavedToFile):
                    print("Dialog closed with save button")
                    self.parent._workspacesData.pop(
                        len(self.parent._workspacesData)-1)
                    self.updateWorkspaceNames(0)
                    self.workspaceSavedToFile = False
                else:
                    # Delete last element from parent list of workspaces
                    self.parent._workspacesData.pop(
                        len(self.parent._workspacesData)-1)
                    # Reload data in requests list and reload data in workspace comboBox
                    self.parent.changeWorkspace(
                        len(self.parent._workspacesData)-1)
                # Go back to last
                self.workspaceSpaces.setCurrentIndex(
                    len(self.parent._workspacesData)-1)
                # Close adding dialog
                self.addingNewWorkspace = False

    def updateWorkspaceNames(self, index):
        self.workspaceSpaces.clear()
        WORKSPACES = [d["spaceName"] for d in self.parent._workspacesData]
        # Dev print
        # print("current workspaces:")
        # for item in WORKSPACES:
        #     print(f'name - {item}')
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
                "integrations": [
                    {
                        "integrationType": "wiki",
                        "data": [
                            {
                                "provider": "gitlab",
                                "projectUrl": ""
                            },
                            {
                                "provider": "github",
                                "projectUrl": ""
                            }
                        ]
                    }
                ],
                "requests": []
            }
            self.parent._workspacesData.append(emptyWorkspace)
            id = saveWorkspaceDataToFile(emptyWorkspace)
            self.parent.workspaceId = id
            self.openWorkspaceSettingsDialog()
            self.addingNewWorkspace = True
            self.workspaceSettingsDialog.saveBtn.setText("Save workspace")
        else:
            self.parent.changeWorkspace(self.workspaceSpaces.currentIndex())
