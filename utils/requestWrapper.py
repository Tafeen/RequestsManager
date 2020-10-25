import requests


def requestWrapper(requestType, endpoint, headers, body=None):
    if(requestType == "GET"):
        response = requests.get(endpoint, headers=headers)
        return response
    if(requestType == "POST"):
        response = requests.post(endpoint, headers=headers, data=body)
        return response
    if(requestType == "DELETE"):
        response = requests.delete(endpoint, headers=headers)
        return response
    if(requestType == "PATCH"):
        response = requests.patch(endpoint, headers=headers, data=body)
        return response
