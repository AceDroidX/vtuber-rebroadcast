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
    streamers = {}

    async def run(self):
        logging.debug('启动直播流管理')
        # while True:
        #     for name, streamer in list(self.streamers.items()):
        #         state = streamer.getState()

    def Add(self, name, channelId):
        self.streamers[name] = Streamer(name, channelId)
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
                self.changeRebroadcast(state)
                self.state = state
            await asyncio.sleep(15)

    def changeRebroadcast(self, state):
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
            self.sendMessage(f'{self.name}正在直播中:https://www.youtube.com/watch?v={state}')
        else:  # 不在直播中
            if not self.rbcThread is None:
                self.queue.put('stop')
                self.rbcThread = None
                self.queue = None
            self.sendMessage(f'{self.name}直播已结束')

    async def check(self):
        logging.debug('直播状态检测:'+self.name)
        state = await youtube_util.getLiveVideoId(self.channelId)
        logging.debug(f'直播状态:[{self.name}]{state}')
        return state

    def getState(self):
        return self.state

    def sendMessage(self,msg):
        self.discord.send_message(msg)
