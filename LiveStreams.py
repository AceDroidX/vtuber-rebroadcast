import logging
import sys
from time import sleep
import datetime
import requests
import main
import youtube_util
import APIKey
import asyncio
import Rebroadcast
import queue
import Discord


class StreamerManager:
    discord = None
    streamers = {}

    def __init__(self, discord=None):
        self.discord = discord

    def Add(self, name, channelId):
        for streamername, streamer in list(self.streamers.items()):
            if streamer.channelId == channelId or streamername == name:
                print(f'已经添加过了[{name}]{streamer.channelId}')
                return f'已经添加过了[{name}]{streamer.channelId}'
        self.streamers[name] = Streamer(name, channelId, self.discord)
        print('成功添加:['+name+']'+channelId)
        return '成功添加:['+name+']'+channelId

    def Del(self, string):
        for name, streamer in list(self.streamers.items()):
            if streamer.channelId == string or name == string:
                streamer.cancel()
                self.streamers.pop(name)
                print('成功删除'+string)
                return '成功删除'+string
        print('找不到'+string)
        return '找不到'+string


class Streamer:
    state = None
    rbcThread = None
    queue = None
    discord = None

    def __init__(self, name, channelId, discord=None):
        self.name = name
        self.channelId = channelId
        self.task = asyncio.ensure_future(self.autocheck())
        self.discord = discord

    def cancel(self):
        self.task.cancel()

    async def autocheck(self):
        while True:
            state = await self.check()
            logging.debug(f'state:{state}--self.state:{self.state}')
            if state != self.state:
                await self.changeRebroadcast(state)
                self.state = state
            await asyncio.sleep(15)

    async def changeRebroadcast(self, state):
        logging.debug(f'改变转播状态:[{self.name}]{state}')
        if not state is None:  # 正在直播中
            if not self.rbcThread is None:
                self.queue.put('stop')
                self.rbcThread = None
                self.queue = None
            self.queue = queue.Queue()
            self.queue.put((self.name, state))
            self.rbcThread = Rebroadcast.RebroadcastThread(self.queue)
            self.rbcThread.start()
            await self.sendMessage(
                f'{self.name}正在直播中:https://www.youtube.com/watch?v={state}\n转播链接:https://live.acedroidx.top/?stream={self.name}')
        else:  # 不在直播中
            if not self.rbcThread is None:
                self.queue.put('stop')
                self.rbcThread = None
                self.queue = None
            await self.sendMessage(f'{self.name}直播已结束')

    async def check(self):
        logging.debug('直播状态检测:'+self.name)
        state = await youtube_util.getLiveVideoId(self.channelId)
        logging.debug(f'直播状态:[{self.name}]{state}')
        return state

    def getState(self):
        return self.state

    async def sendMessage(self, msg):
        if self.discord is None:
            logging.warning('Streamer.discord is None')
            return
        await self.discord.send_message(msg)
