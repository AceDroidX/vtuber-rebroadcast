import json
import asyncio
import os

configpath = 'config.json'


def initConfig():
    global configjson
    configjson = {'discord': {}, 'LiveStreams': {}}
    writeConfig()


def checkConfig():
    global configjson
    if configjson['discord'] is None:
        configjson['discord'] = {}
    if configjson['LiveStreams'] is None:
        configjson['LiveStreams'] = {}


def readConfig():
    global configjson
    if not os.path.exists(configpath):
        initConfig()
        return
    with open(configpath, 'r') as f:
        configjson = json.load(f)


def writeConfig():
    global configjson
    with open(configpath, 'w') as f:
        json.dump(configjson, f, ensure_ascii=False)


async def autoSave():
    while True:
        writeConfig()
        await asyncio.sleep(1)


def get_config(zone, key):
    global configjson
    if key in configjson[zone]:
        return configjson[zone][key]
    else:
        return None


def set_config(zone, key, value):
    global configjson
    configjson[zone][key] = value


readConfig()
checkConfig()