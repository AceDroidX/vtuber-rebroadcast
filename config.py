import json
import asyncio
import os
import logging
import logging.config

configpath = 'config.json'


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        if not os.path.exists('./log'):
            os.makedirs('./log')
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


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
