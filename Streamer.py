import logging
import youtube_util
import asyncio
import Rebroadcast
import queue
import Discord
import config
import APIKey


class Streamer:
    state = {'status': 'None'}
    rbcThread = None
    queue = None
    discord = None
    config = {}

    def __init__(self, name, channelId, discord=None, conf=None):
        self.name = name
        self.channelId = channelId
        self.task = asyncio.ensure_future(self.autocheck())
        self.discord = discord
        if conf is None:
            self.setConfig('name', name)
            self.setConfig('channelId', channelId)
        else:
            self.config = conf

    def __str__(self):
        return f'[{self.name}]{self.channelId}：{self.getState()}'

    def __repr__(self):
        return (self.name, self.channelId)

    def cancel(self):
        self.task.cancel()

    def loadConfig(self, data):
        self.config = data

    def setConfig(self, key, data):
        self.config[key] = data

    def getConfig(self):
        return self.config

    async def check(self):
        # logging.debug('直播状态检测:'+self.name)
        state = await youtube_util.getLiveVideoId(self.channelId)
        # logging.debug(f'直播状态:[{self.name}]{state}')
        return state

    async def autocheck(self):
        try:
            while True:
                state = await self.check()
                logging.debug(f'[{self.name}]直播状态:{state}原状态:{self.state}')
                if state != self.state:
                    if state['status'] == 'LIVE_STREAM_OFFLINE':
                        await self.stopRbcCheck(state)
                        continue
                    elif state['status'] == 'OK':
                        await self.startRebroadcast(state['videoid'])
                    elif state['status'] == 'None':
                        await self.stopRbcCheck(state)
                        continue
                    else:
                        await self.sendError('Streamer.autocheck.state["status"]:未知状态')
                self.state = state
                await asyncio.sleep(15)
        except BaseException as e:
            logging.error('Streamer.autocheck.BaseException', exc_info=True)
            await self.sendMessage(f'[{self.name}]autocheck发生错误，请查看日志')

    async def stopRbcCheck(self, state):
        if(self.state['status'] != 'OK'):
            self.state = state
            await asyncio.sleep(15)
            return
        islive = await youtube_util.checkIsLive(self.state["videoid"])
        logging.warning(f'checkIsLive.status:{islive}')
        if islive['status'] == 'OK':
            logging.warning(f'youtube抽风了\n[{self.name}]直播状态:{state}原状态:{self.state}')
            await asyncio.sleep(15)
            return False
        else:
            if state['status'] == 'OK':
                logging.warning(f'不是youtube抽风，切换到新的<直播>页面\n[{self.name}]直播状态:{state}原状态:{self.state}')
                self.startRebroadcast(state['videoid'])
            else:
                logging.warning(f'不是youtube抽风，切换到新的<待机>页面\n[{self.name}]直播状态:{state}原状态:{self.state}')
                await self.stopRebroadcast()
            self.state = state
            await asyncio.sleep(15)
            return True

    async def startRebroadcast(self, videoid):
        logging.info(f'改变转播状态:[{self.name}]{videoid}')
        if not self.rbcThread is None:
            logging.warning(f'直播id更改，正在重启线程，原id{self.state}:，现id:{videoid}')
            self.queue.put('stop')
            self.rbcThread = None
            self.queue = None
        self.queue = queue.Queue()
        self.queue.put((self.name, videoid))
        self.rbcThread = Rebroadcast.RebroadcastThread(self.queue)
        self.rbcThread.start()
        await self.sendMessage(f'{self.name}{self.getState(state=videoid,type="detail")}')

    async def stopRebroadcast(self):
        logging.info(f'改变转播状态:[{self.name}]stop')
        if not self.rbcThread is None:
            self.queue.put('stop')
            self.rbcThread = None
            self.queue = None
        await self.sendMessage(f'{self.name}直播已结束')

    def getState(self, state='', type='simple'):
        if state == '':
            state = self.state
        if type == 'simple':
            if state is None:
                return '未直播'
            else:
                return f'正在直播中：{state}'
        elif type == 'detail':
            if state is None:
                return '未直播'
            else:
                return f'正在直播中：https://www.youtube.com/watch?v={state}\n转播链接：{APIKey.rebroadcast_prefix}{self.name}'

    async def sendMessage(self, msg):
        if self.discord is None:
            logging.warning('Streamer.discord is None')
            return
        if not self.discord.is_ready():
            logging.warning('Streamer.discord is not ready')
            return
        await self.discord.send_message(msg)

    async def sendWarning(self, msg):
        logging.warning(msg)
        await self.sendMessage(f'warning：{msg}')

    async def sendError(self, msg):
        logging.error(msg)
        await self.sendMessage(f'error：{msg}')
