import json
import datetime
import sys
import os
import logging


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath(""))

    # base_path = ""
    return os.path.join(base_path, relative_path)

# Workspaces


def loadWorkspaces():
    workspacesList = []
    initialWorkspace = {
        "id": 0,
        "spaceName": "InitialWorkspace",
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
    # Check if file exists and is array
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                if(len(workspacesList) == 0):
                    print(json.dumps(workspacesList, indent=4, sort_keys=True))
                    workspacesList.append(initialWorkspace)
                    saveWorkspaceDataToFile(initialWorkspace)
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
                workspacesList.append(initialWorkspace)
                saveWorkspaceDataToFile(initialWorkspace)
    except Exception as ex:
        logging.error(f'Could not open file, exception: {ex}')
        workspacesList.append(initialWorkspace)
        saveWorkspaceDataToFile(initialWorkspace)
    finally:
        return workspacesList


def saveWorkspaceDataToFile(workspace):
    lastId = 0
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            workspacesList = json.load(f)
            if(type(workspacesList) is list and len(workspacesList) > 0):
                if "id" in workspace:
                    workspace_index = next((index for (index, d) in enumerate(
                        workspacesList) if d["id"] == workspace["id"]), None)
                    workspacesList[workspace_index] = workspace
                else:
                    lastId = max(workspace["id"]
                                 for workspace in workspacesList)
                    workspace["id"] = lastId + 1
                    workspacesList.append(workspace)
            else:
                workspacesList = []
                workspacesList.append(workspace)
    except Exception as ex:
        logging.error(
            f'Could not open file, exception: {ex}')
        workspacesList = []
        workspacesList.append(workspace)
    finally:
        # Save to file
        with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return(workspace["id"])


def removeWorkspaceFromFile(workspaceId):
    workspacesList = []
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                workspacesList = list(
                    filter(lambda i: i['id'] != workspaceId, workspacesList))
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
    except Exception as ex:
        logging.error(
            f'Could not open file, exception: {ex}')
    finally:
        with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return workspacesList


# Requests

def saveRequestDataToFile(request, workspaceId):
    workspacesList = []
    requestsList = []
    request["lastModificationDate"] = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                if(type(workspacesList) is list and len(workspacesList) > 0):
                    requestsList = workspacesList[workspaceId]["requests"]
                    if(type(requestsList) is list and len(requestsList) > 0):
                        if("id" in request):
                            request_index = next((index for (index, d) in enumerate(
                                requestsList) if d["id"] == request["id"]), None)
                            requestsList[request_index] = request
                        else:
                            request["id"] = max(
                                request["id"] for request in workspacesList[workspaceId]["requests"]) + 1
                            requestsList.append(request)
                    else:
                        request["id"] = 0
                        requestsList.append(request)
                    workspacesList[workspaceId]["requests"] = requestsList
                else:
                    logging.error(
                        f'workspaces list is empty')
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
                print(
                    f'File is not correct json type, exception: {ex}')
    except Exception as ex:
        logging.error(
            f'Could not open file, exception: {ex}')
    finally:
        with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return(request["id"])


def removeRequestFromFile(requestId, workspaceId):
    workspacesList = []
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                requestsList = workspacesList[workspaceId]["requests"]
                requestsList = list(
                    filter(lambda i: i['id'] != requestId, requestsList))
                workspacesList[workspaceId]["requests"] = requestsList
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
    except Exception as ex:
        logging.error(
            f'Could not open file, exception: {ex}')
    finally:
        with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return requestsList


# User settings

def loadUserData():
    try:
        with open(resource_path("userSettings.json"), 'r', encoding='utf-8') as f:
            try:
                userData = json.load(f)
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
                saveInitialUserDataToFile()
                loadUserData()    
    except Exception as ex:
        logging.error(f'Could not open file, exception: {ex}')
        saveInitialUserDataToFile()
        loadUserData()
    finally:
        if userData:
            return userData


def saveInitialUserDataToFile():
    userData = {
        "integrations":
        [
            {
                "integrationType": "wiki",
                "data":
                [
                    {
                        "provider": "gitlab",
                        "token": "tokenGITLAB"
                    },
                    {
                        "provider": "github",
                        "token": "tokenGITHUB"
                    }
                ]
            }
        ],
        "workspaces":
        [
            {
                "id": 0,
                "integrations":
                [
                    {
                        "integrationType": "wiki",
                        "data": {
                            "selectedProvider": "gitlab"
                        }
                    }
                ]
            }
        ]
    }
    with open(resource_path("userSettings.json"), 'w', encoding='utf-8') as f:
        json.dump(userData, f, ensure_ascii=False, indent=4)


def saveUserIntegrationToFile(integration):
    try:
        with open(resource_path("userSettings.json"), 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                key = next((i for i, item in enumerate(
                    settings["integrations"]) if item["integrationType"] == integration['integrationType']), None)
                if(key is not None):
                    settings["integrations"][key] = integration
                else:
                    settings["integrations"].append(integration)
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
                saveInitialUserDataToFile()
    except Exception as ex:
        logging.error(
            f'File could not be open, exception: {ex}')
        saveInitialUserDataToFile()
    finally:
        if settings:
            with open(resource_path("userSettings.json"), 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        else:
            saveInitialUserDataToFile()


def saveUserWorkspaceToFile(workspace):
    settings = {}
    try:
        with open(resource_path("userSettings.json"), 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                if(type(settings) is dict and len(settings) > 0):
                    key = next((i for i, item in enumerate(
                        settings["workspaces"]) if item["id"] == workspace['id']), None)
                    if(key is not None):
                        settings["workspaces"][key] = workspace
                        print(workspace)
                    else:
                        settings["workspaces"].append(workspace)
                else:
                    settings = {}
                    settings["workspaces"] = []
                    settings["workspaces"].append(workspace)
            except Exception as ex:
                logging.error(
                    f'File is not correct json type, exception: {ex}')
    except Exception as ex:
        logging.error(
            f'File could not be open, exception: {ex}')
        settings["workspaces"] = []
        settings["workspaces"].append(workspace)
    finally:
        with open(resource_path("userSettings.json"), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        print(settings)
