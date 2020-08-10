import json
import datetime

fileName = 'requests.json'


def saveRequest(request):
    requestsList = []
    requestsList.append(request)
    isFileCorrupted = False
    request["lastModificationDate"] = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    lastId = 0
    # Check if file exists and is array
    try:
        with open(fileName, 'r', encoding='utf-8') as f:
            try:
                requestsList = json.load(f)
                # Check if request with this id exists
                if "id" in request:
                    request_index = next((index for (index, d) in enumerate(
                        requestsList) if d["id"] == request["id"]), None)
                    requestsList[request_index] = request
                else:
                    lastId = max(request["id"] for request in requestsList)
                    request["id"] = lastId + 1
                    requestsList.append(request)
            except Exception as ex:
                print(ex)
                isFileCorrupted = True
                request["id"] = 0
    except Exception as ex:
        print(ex)
        request["id"] = 0
        pass
    finally:
        if(not isFileCorrupted):
            with open(fileName, 'w+', encoding='utf-8') as f:
                json.dump(requestsList, f, ensure_ascii=False, indent=4)
        return(request["id"])


def removeRequest(requestId):
    requestsList = []
    try:
        with open(fileName, 'r', encoding='utf-8') as f:
            try:
                requestsList = json.load(f)
                requestsList = list(
                    filter(lambda i: i['id'] != requestId, requestsList))
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(requestsList, f, ensure_ascii=False, indent=4)
        return requestsList


def loadRequests():
    requestsList = []

    # Check if file exists and is array
    try:
        with open(fileName, 'r', encoding='utf-8') as f:
            try:
                requestsList = json.load(f)
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
    finally:
        return requestsList
