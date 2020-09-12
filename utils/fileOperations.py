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


def saveRequestToFile(request):
    requestsList = []
    requestsList.append(request)
    isFileCorrupted = False
    request["lastModificationDate"] = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    lastId = 0

    # Check if file exists and is array
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                requestsList = json.load(f)
                if(type(requestsList) is list and len(requestsList) > 0):
                    # print(requestsList)
                    # Check if request with this id exists
                    if "id" in request:
                        request_index = next((index for (index, d) in enumerate(
                            requestsList) if d["id"] == request["id"]), None)
                        requestsList[request_index] = request
                    else:
                        lastId = max(request["id"] for request in requestsList)
                        request["id"] = lastId + 1
                        requestsList.append(request)
                else:
                    request["id"] = 0
                    requestsList.append(request)
            except Exception as ex:
                print(ex)
                print("It was not json file")
                request["id"] = 0
                requestsList = []
                requestsList.append(request)
    except Exception as ex:
        print(ex)
        request["id"] = 0
        pass
    finally:
        if(not isFileCorrupted):
            with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
                json.dump(requestsList, f, ensure_ascii=False, indent=4)
        return(request["id"])


def removeRequestFromFile(requestId):
    requestsList = []
    try:
        with open(resource_path("requests.json"), 'r', encoding='utf-8') as f:
            try:
                requestsList = json.load(f)
                requestsList = list(
                    filter(lambda i: i['id'] != requestId, requestsList))
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        with open(resource_path("requests.json"), 'w', encoding='utf-8') as f:
            json.dump(requestsList, f, ensure_ascii=False, indent=4)
        return requestsList


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


def saveIntegrations(integration):
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
        settings["integrations"] = []
        settings["integrations"].append(integration)
    finally:
        with open(resource_path("settings.json"), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
