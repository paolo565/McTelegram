import requests
import json


def check_mojang_status():
    response = requests.request("GET", "https://status.mojang.com/check")
    if response.status_code != 200:
        return False

    statuses = {}
    for data in response.json():
        key = list(data.keys())[0]
        statuses[key] = data[key]
    return True, statuses


def get_uid_from_username(username):
    response = requests.request("POST", "https://api.mojang.com/profiles/minecraft", data=json.dumps([
        username
    ]), headers={
        'content-type': "application/json"
    })

    if response.status_code != 200:
        return False

    data = response.json()
    if len(data):
        username = data[0]['name']
        uid = data[0]['id']
        return True, True, username, uid

    return True, False, username, None


def get_name_history_from_uid(uid):
    response = requests.request("GET", "https://api.mojang.com/user/profiles/" + uid + "/names")

    if response.status_code == 204:
        return True, None

    if response.status_code != 200:
        return False

    names = response.json()
    return True, names
