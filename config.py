import json
import asyncio
import os

configpath = 'config.json'


def initConfig():
    global configjson
    configjson = {'discord': {}, 'streamers': []}
    writeConfig()


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

readConfig()
