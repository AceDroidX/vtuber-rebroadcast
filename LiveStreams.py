import logging
import Discord
import config
import Streamer


class StreamerManager:
    discord = None
    streamers = {}
    confstreamers = []

    def __init__(self, discord=None):
        self.discord = discord
        self.loadConfig()

    def Add(self, name, channelId):
        for streamername, streamer in list(self.streamers.items()):
            if streamer.channelId == channelId or streamername == name:
                print(f'已经添加过了[{name}]{streamer.channelId}')
                return f'已经添加过了[{name}]{streamer.channelId}'
        self.streamers[name] = Streamer.Streamer(name, channelId, self.discord)
        self.addToConfig(name, channelId)
        print('成功添加:['+name+']'+channelId)
        return '成功添加:['+name+']'+channelId

    def Del(self, string):
        for name, streamer in list(self.streamers.items()):
            if streamer.channelId == string or name == string:
                streamer.cancel()
                self.streamers.pop(name)
                self.delToConfig(name)
                print('成功删除'+string)
                return '成功删除'+string
        print('找不到'+string)
        return '找不到'+string

    def List(self):
        tmp = []
        for name, streamer in list(self.streamers.items()):
            tmp.append(str(streamer))
        if tmp == []:
            print('监控列表：\n没有正在监控的vtb')
            return '监控列表：\n没有正在监控的vtb'
        print('监控列表：\n'+'\n'.join(tmp))
        return '监控列表：\n'+'\n'.join(tmp)

    def get_config(self, key):
        return config.get_config('LiveStreams', key)

    def set_config(self, key, value):
        return config.set_config('LiveStreams', key, value)

    def addToConfig(self, name, channelId):
        self.confstreamers.append({'name': name, 'channelId': channelId})
        self.set_config('streamers', self.confstreamers)

    def delToConfig(self, name):
        for streamer in list(self.confstreamers):
            if streamer['name'] == name:
                self.confstreamers.remove(streamer)
                self.set_config('streamers', self.confstreamers)

    def loadConfig(self):
        self.confstreamers = self.get_config('streamers')
        if self.confstreamers is None:
            self.confstreamers = []
            self.set_config('streamers', self.confstreamers)
        if self.streamers == {}:
            for streamer in list(self.confstreamers):
                self.Add(streamer['name'], streamer['channelId'])
        else:
            logging.warning('重新加载设置功能还没测试（')
            # self.unload()

    def unload(self):  # 未测试
        for name, streamer in list(self.streamers.items()):
            streamer.cancel()
