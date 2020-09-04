import logging
import youtube_util
import asyncio
import Rebroadcast
import queue
import Discord
import config
import APIKey
from datetime import datetime


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

    def getConfig(self, key):
        if not key in self.config:
            return None
        return self.config[key]

    async def check(self):
        # logging.debug('直播状态检测:'+self.name)
        state = await youtube_util.getLiveVideoId(self.channelId)
        # logging.debug(f'直播状态:[{self.name}]{state}')
        return state

    async def autocheck(self):
        try:
            while True:
                state = await self.check()
                if state['status'] == 'Error':
                    await asyncio.sleep(30)
                    state = await self.check()
                    if state['status'] == 'Error':
                        await self.sendMessage(f'[{self.name}]autocheck获取状态失败，请查看日志')
                        return
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
                        await self.sendError(f'[{self.name}]Streamer.autocheck.state["status"]:未知状态')
                self.state = state
                await asyncio.sleep(15)
        except BaseException as e:
            logging.error('Streamer.autocheck.BaseException', exc_info=True)
            await self.sendMessage(f'[{self.name}]autocheck发生未知错误，请查看日志')

    async def stopRbcCheck(self, state):  # 用于检查是否真的是直播结束
        if(self.state['status'] != 'OK'):
            if self.getConfig('checkOffline') == 'true' and state['status'] == 'LIVE_STREAM_OFFLINE':
                await self.sendMessage(f'{self.name}{self.getState(state=state,type="detail")}')
            self.state = state
            await asyncio.sleep(15)
            return
        islive = await youtube_util.checkIsLive(self.state["videoid"])
        logging.warning(f'checkIsLive.status:{islive}')
        if islive['status'] == 'OK':
            logging.warning(
                f'youtube抽风了\n[{self.name}]直播状态:{state}原状态:{self.state}')
            await asyncio.sleep(15)
            return False
        else:
            if state['status'] == 'OK':
                logging.warning(
                    f'不是youtube抽风，切换到新的<直播>页面\n[{self.name}]直播状态:{state}原状态:{self.state}')
                self.startRebroadcast(state['videoid'])
            else:
                logging.warning(
                    f'不是youtube抽风，切换到新的<待机>页面\n[{self.name}]直播状态:{state}原状态:{self.state}')
                await self.stopRebroadcast()
            self.state = state
            await asyncio.sleep(15)
            return True

    async def startRebroadcast(self, videoid):
        if self.getConfig('rbc') != 'true' and config.get_config('LiveStreams','rbc') != 'true':
            await self.sendMessage(f'{self.name}{self.getState(state={"videoid":videoid,"status":"OK"},type="detail")}')
            return
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
        await self.sendMessage(f'{self.name}{self.getState(state={"videoid":videoid,"status":"OK"},type="detail")}')

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
            if state['status'] == 'OK':
                return f'正在直播中：{state["videoid"]}'
            elif state['status'] == 'LIVE_STREAM_OFFLINE':
                if self.getConfig('checkOffline') == 'true':
                    return f'待机界面：{state["videoid"]}'
            return '未直播'
        elif type == 'detail':
            if state['status'] == 'OK':
                detailstate = f'正在直播中：https://www.youtube.com/watch?v={state["videoid"]}'
                if self.getConfig('biliroomid') != None:
                    detailstate += f'\nB站直播间：https://live.bilibili.com/{self.getConfig("biliroomid")}'
                if self.getConfig('rbc') == 'true' and config.get_config('LiveStreams','rbc') == 'true':
                    detailstate += f'\n转播链接：{APIKey.rebroadcast_prefix}{self.name}'
                return detailstate
            elif state['status'] == 'LIVE_STREAM_OFFLINE':
                if state['scheduledStartTime'] != 'None':
                    startTime = datetime.fromtimestamp(
                        state['scheduledStartTime'])
                    remainTime = startTime-datetime.now()
                    if remainTime.days > 0:
                        remainTime = strfdelta(
                            remainTime, "{days}天{hours}:{minutes}:{seconds}")
                    else:
                        remainTime = strfdelta(
                            remainTime, "{hours}:{minutes}:{seconds}")
                else:
                    startTime = 'None'
                    remainTime = 'None'
                if self.getConfig('checkOffline') == 'true':
                    return f'添加了新的待机界面：https://www.youtube.com/watch?v={state["videoid"]}\n开始时间：{startTime}剩余时间：{remainTime}'
            return '未直播'

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


# https://stackoverflow.com/questions/8906926/formatting-timedelta-objects
# >>> print strfdelta(delta_obj, "{days} days {hours}:{minutes}:{seconds}")
# 1 days 20:18:12
# >>> print strfdelta(delta_obj, "{hours} hours and {minutes} to go")
# 20 hours and 18 to go
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)
