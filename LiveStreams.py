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

    def Del(self, string):
        for name, streamer in list(self.streamers.items()):
            if streamer.channelId == string or name == string:
                streamer.cancel()
                self.streamers.pop(name)
                print('成功删除'+string)
                return
        print('找不到'+string)


class Streamer:
    def __init__(self, name, channelId):
        self.name = name
        self.channelId = channelId
        self.task = asyncio.ensure_future(self.autocheck())

    def cancel(self):
        self.task.cancel()

    async def autocheck(self):
        while True:
            state = await self.check()
            if state != self.state:
                self.changeRebroadcast(state)
                self.state = state
            await asyncio.sleep(15)

    def changeRebroadcast(self, state):
        logging.debug(f'改变转播状态:[{self.name}]{state}')
        if not state is None:  # 正在直播中
            if self.rbcThread is None:
                self.queue = queue.Queue()
                self.rbcThread = Rebroadcast.RebroadcastThread(self.queue)
            self.queue.put(self.name, self.channelId)
            self.rbcThread.start()
        else:  # 不在直播中
            if not self.rbcThread is None:
                self.queue.put('stop')

    async def check(self):
        logging.debug('直播状态检测:'+self.name)
        state = await youtube_util.getLiveVideoId(self.channelId)
        logging.debug(f'直播状态:[{self.name}]{state}')
        return state

    def getState(self):
        return self.state
