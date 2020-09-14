import json
import datetime
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath(""))

    # base_path = ""
    return os.path.join(base_path, relative_path)


def loadWorkspaces():
    workspacesList = []
    # Check if file exists and is array
    try:
        with open(resource_path("nexgenRequests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        if type(workspacesList) is list:
            return workspacesList
        else:
            return []


def saveWorkspaceDataToFile(workspace):
    lastId = 0
    try:
        with open(resource_path("nexgenRequests.json"), 'r', encoding='utf-8') as f:
            workspacesList = json.load(f)
            if(type(workspacesList) is list and len(workspacesList) > 0):
                if "id" in workspace:
                    workspace_index = next((index for (index, d) in enumerate(
                        workspacesList) if d["id"] == workspace["id"]), None)
                    workspacesList[workspace_index] = workspace
                else:
                    lastId = max(workspace["id"] for workspace in workspacesList)
                    workspace["id"] = lastId + 1
                    workspacesList.append(workspace)
            else:
                # Workspace is invalid or is empty
                workspacesList = []
    except Exception as ex:
        print("Could not open file")
        print(ex)
    finally:
        # Save to file
        with open(resource_path("nexgenRequests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return(workspace["id"])


def saveRequestDataToFile(request, workspaceId):
    requestsList = []
    requestsList.append(request)
    request["lastModificationDate"] = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    lastId = 0
    try:
        with open(resource_path("nexgenRequests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                if(type(workspacesList) is list and len(workspacesList) > 0):
                    requestsList = workspacesList[workspaceId]["requests"]         
                    if(type(requestsList) is list and len(requestsList) > 0):
                        if "id" in request:
                            request_index = next((index for (index, d) in enumerate(
                            requestsList) if d["id"] == request["id"]), None)
                            requestsList[request_index] = request
                        else:
                            print("there was no id in request obj")
                            lastId = max(request["id"]
                                         for request in requestsList)
                            request["id"] = lastId + 1
                            requestsList.append(request)
                            workspacesList[workspaceId]["requests"] = requestsList
                    else:
                        # RequestsList is invalid or is empty
                        requestsList = []
                        request["id"] = lastId
                        requestsList.append(request)
                        workspacesList[workspaceId]["requests"] = requestsList
                else:
                    # Workspace is invalid or is empty
                    workspacesList = []
                    workspace = {
                        "id": 0,
                        "name": "My first workspace"
                    }
                    workspace["requests"] = [request]
                    workspacesList.append(workspace)
            except Exception as ex:
                # file is not json
                print("File is not correct json type")
                print(ex)
    except Exception as ex:
        print("Could not open file")
        print(ex)
    finally:
        # Save to file
        print(request)
        with open(resource_path("nexgenRequests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return(request["id"])


def removeRequestFromFile(requestId, workspaceId):
    workspacesList = []
    try:
        with open(resource_path("nexgenRequests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)
                requestsList = workspacesList[workspaceId]["requests"]         
                requestsList = list(filter(lambda i: i['id'] != requestId, requestsList))
                workspacesList[workspaceId]["requests"] = requestsList
            except Exception as ex:
                # file is not json
                print("File is not correct json type")
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        with open(resource_path("nexgenRequests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return requestsList


def removeWorkspaceFromFile(workspaceId):
    workspacesList = []
    try:
        with open(resource_path("nexgenRequests.json"), 'r', encoding='utf-8') as f:
            try:
                workspacesList = json.load(f)      
                workspacesList = list(filter(lambda i: i['id'] != workspaceId, workspacesList))
            except Exception as ex:
                # file is not json
                print("File is not correct json type")
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        with open(resource_path("nexgenRequests.json"), 'w', encoding='utf-8') as f:
            json.dump(workspacesList, f, ensure_ascii=False, indent=4)
        return workspacesList


def loadUserData():
    userData = {}
    # Check if file exists and is array
    try:
        with open(resource_path("settings.json"), 'r', encoding='utf-8') as f:
            try:
                userData = json.load(f)
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        if type(userData) is dict:
            return userData
        else:
            return {}


def saveUserIntegration(integration):
    settings = {}
    try:
        with open(resource_path("settings.json"), 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                if(type(settings) is dict and len(settings) > 0):
                    key = next((i for i, item in enumerate(settings["integrations"]) if item["provider"] == integration['provider']), None)
                    if(key is not None):
                        settings["integrations"][key] = integration
                    else:
                        settings["integrations"].append(integration)
                else:
                    settings = {}
                    settings["integrations"] = []
                    settings["integrations"].append(integration)
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print("File could not be open" + ex)
        settings["integrations"] = []
        settings["integrations"].append(integration)
    finally:
        with open(resource_path("settings.json"), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
