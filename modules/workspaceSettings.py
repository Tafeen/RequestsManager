from PySide2.QtWidgets import (QLineEdit, QRadioButton, QLabel, QPushButton, QGridLayout,
                               QDialog, QWidget, QComboBox)
from utils.fileOperations import saveWorkspaceDataToFile, removeWorkspaceFromFile
import logging


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
        self.gitlabRadioButton = QRadioButton("gitlab")
        self.gitlabURLinput = QLineEdit(gitlabUrl)
        self.github = next(
            (item for item in self.wikiDict["data"] if item["provider"] == "github"), None)
        githubUrl = self.github.get("projectUrl") if (
            self.github is not None) else ""
        self.githubRadioButton = QRadioButton("github")
        self.githubURLinput = QLineEdit(githubUrl)

        # Set Layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.githubRadioButton, 0, 0)
        self.allQGridLayout.addWidget(self.gitlabURLinput, 0, 1)
        self.allQGridLayout.addWidget(self.gitlabRadioButton, 1, 0)
        self.allQGridLayout.addWidget(self.githubURLinput, 1, 1)
        self.setLayout(self.allQGridLayout)

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


class WorksapceDropDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(WorksapceDropDialog, self).__init__(parent)
        self.mainParent = self.parent.parent.parent
        self.workspaceNameToRemove = self.mainParent._workspacesData[self.mainParent.workspaceId]["spaceName"]
        self.dropWorkspaceBtn = QPushButton("Drop workspace")
        self.dropWorkspaceConfirmation = QLineEdit()
        self.allQGridLayout = QGridLayout(self)
        self.allQGridLayout.addWidget(QLabel("Are you sure about dropping this workspace?"), 0, 0)
        self.allQGridLayout.addWidget(QLabel(f'If so, enter current workspace name "{self.workspaceNameToRemove}"'), 1, 0)
        self.allQGridLayout.addWidget(self.dropWorkspaceConfirmation, 2, 0)
        self.allQGridLayout.addWidget(self.dropWorkspaceBtn)
        self.setLayout(self.allQGridLayout)

        self.dropWorkspaceBtn.clicked.connect(self.removeWorkspace)

    def removeWorkspace(self):
        if(self.dropWorkspaceConfirmation.text() == self.workspaceNameToRemove):
            workspaceIdToRemove = self.mainParent._workspacesData[self.mainParent.workspaceId]["id"]
            logging.info(workspaceIdToRemove)
            # Remove workspace from list of workspaces
            self.mainParent._workspacesData = list(filter(lambda i: i['id'] != workspaceIdToRemove, self.mainParent._workspacesData))
            removeWorkspaceFromFile(workspaceIdToRemove)
            # Change current workspace to workspace with greatest id
            workspaceMaxId = max(workspace["id"] for workspace in self.mainParent._workspacesData)
            workspaceMaxIndex = next((i for i, item in enumerate(self.mainParent._workspacesData) if item["id"] == workspaceMaxId), None)
            self.mainParent.changeWorkspace(workspaceMaxIndex)
            # Update comboBox
            self.parent.parent.reloadAllWorkspaces()
            # Close all dialog windows
            self.parent.parent.workspaceSettingsDialog.close()
            self.close()


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

        self.selectedIntegration = "gitlab"
        self.integrationsWiki = integrationWikiWidget(self)

        self.dropWorkspaceBtn = QPushButton("Delete workspace")
        self.saveBtn = QPushButton("Update workspace")

        # Set layout
        self.allQGridLayout = QGridLayout()
        self.allQGridLayout.addWidget(self.workspaceName, 0, 0, 1, 6)
        self.allQGridLayout.addWidget(QLabel("Integrations: "), 1, 0)
        self.allQGridLayout.addWidget(QLabel("Wiki"), 2, 1)
        self.allQGridLayout.addWidget(self.integrationsWiki, 3, 1, 1, 5)
        self.allQGridLayout.addWidget(self.dropWorkspaceBtn, 4, 5)
        self.allQGridLayout.addWidget(self.saveBtn, 4, 6)
        self.setLayout(self.allQGridLayout)

        self.saveBtn.clicked.connect(
            lambda integrationsList: self.parent.saveWorkspace(self.integrationsWiki.integrationList()))
        self.dropWorkspaceBtn.clicked.connect(self.startDropingWorkspace)

    def closeEvent(self, event):
        print("Closed workspaceSettings")
        self.parent.checkWorkspaceIsCorrect()

    def startDropingWorkspace(self):
        self.WorksapceDropDialog = WorksapceDropDialog(self)
        self.WorksapceDropDialog.show()
        self.WorksapceDropDialog.activateWindow()


class WorkspaceSettingsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        self.addingNewWorkspace = False
        self.workspaceSavedToFile = False
        super(WorkspaceSettingsWidget, self).__init__(parent)

        # Workspace Space
        self.workspaceSpaces = QComboBox()
        self.reloadAllWorkspaces()

        # Workspace Details
        self.workspaceDetails = QPushButton("Workspace settings")

        allQGridLayout = QGridLayout()
        allQGridLayout.addWidget(self.workspaceSpaces, 0, 0)
        allQGridLayout.addWidget(self.workspaceDetails, 0, 1)

        self.setLayout(allQGridLayout)

        self.workspaceDetails.clicked.connect(self.openWorkspaceSettingsDialog)
        self.workspaceSpaces.currentIndexChanged.connect(self.changeWorkspace)

    def reloadAllWorkspaces(self):
        self.workspaceSpaces.clear()
        # Worskpaces
        WORKSPACES = [d["spaceName"] for d in self.parent._workspacesData]
        for option in WORKSPACES:
            self.workspaceSpaces.addItem(option)
        self.workspaceSpaces.addItem("Create new Workspace")

    def openWorkspaceSettingsDialog(self):
        self.workspaceSettingsDialog = WorkspaceSettingsDialog(self)
        self.workspaceSettingsDialog.show()
        self.workspaceSettingsDialog.activateWindow()

    def saveWorkspace(self, integrationsList):
        # Update integrations
        self.workspaceSavedToFile = True
        integrationsList = self.workspaceSettingsDialog.integrationsWiki.integrationList()
        for index, integrationObj in enumerate(integrationsList):
            key = next((i for i, item in enumerate(self.parent._workspacesData[self.workspaceSpaces.currentIndex(
            )]["integrations"]) if item["integrationType"] == "wiki"), None)
            self.parent._workspacesData[self.workspaceSpaces.currentIndex(
            )]["integrations"][key]["data"][index] = integrationObj

        # Update name
        self.parent._workspacesData[self.workspaceSpaces.currentIndex()]["spaceName"] = self.workspaceSettingsDialog.workspaceName.text()

        wasAtIndex = self.workspaceSpaces.currentIndex()
        self.updateWorkspaceNames(wasAtIndex)

        # Save workspace
        saveWorkspaceDataToFile(self.parent._workspacesData[wasAtIndex])

        # Check if wiki screen has loaded before
        if(hasattr(self.parent.RequestEditorWidget.RequestAdvancedEditing.RequestWiki, "wikiScreen")):
            # Update wiki layout
            self.parent.RequestEditorWidget.RequestAdvancedEditing.RequestWiki.wikiScreen.hide()
            self.parent.RequestEditorWidget.RequestAdvancedEditing.RequestWiki.setupLayout()
            self.parent.RequestEditorWidget.RequestAdvancedEditing.RequestWiki.wikiScreen.show()

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
