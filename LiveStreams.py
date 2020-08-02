import subprocess
import threading
import logging
import sys
from time import sleep
import requests
import main
import APIKey

#streamID = {}
#streaming = {}
streamers = {}
rbcThreads = {}
threadLock = threading.Lock()


class StreamerManager (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logging.debug('启动直播流管理')
        while True:
            for name, streamer in list(streamers.items):
                if streamer.check():
                    pass
                else:
                    pass

    def Add(self, name, id):
        threadLock.acquire()
        streamers[name] = Streamer(name, id)
        threadLock.release()
        print('成功添加'+name+'  '+id)

    def Del(self, string):
        threadLock.acquire()
        if string in streamers:
            streamers.pop(string)
            threadLock.release()
            print('成功删除'+string)
        else:
            for name, streamer in list(streamers.items()):
                if streamer.id == string:
                    streamers.pop(name)
                    print('成功删除'+string)
                    threadLock.release()
                    return
            threadLock.release()
            print('找不到'+string)


class Streamer(threading.Thread):
    def __init__(self, name, id):
        threading.Thread.__init__(self)
        self.name = name
        self.id = id
        self.state = False

    def run(self):
        while True:
            tempState = self.check()
            if self.state!='开始' and tempState=="开始":
                self.state = tempState
            sleep(15)

    def check(self):
        self.log('直播状态检测')
        return getyoutubevideostatus(self.id)

    def start(self):
        pass
    def stop(self):
        pass

    def log(self, string):
        logging.debug('[%s,%s]%s' % (self.name, self.id, string))

# 此处参考：https://github.com/lovezzzxxx/livemonitor/blob/73e616cd4fc3972701cb57d0cd56b75bca0dbb57/spider.py#L1417


def getyoutubevideostatus(video_id):
    try:
        url = 'https://www.youtube.com/heartbeat?video_id=%s' % video_id
        response = requests.get(url, stream=True, timeout=(3, 7))
        if response.status_code == 200:
            try:
                if response.json()["stop_heartbeat"] == "1":
                    video_status = "上传"
                    return video_status
                else:
                    # 测试中stop_heartbeat只在类型为视频的情况下出现且值为1
                    return False
            except:
                if response.json()["status"] == "stop":
                    video_status = "删除"
                elif response.json()["status"] == "ok":
                    video_status = "开始"
                elif "liveStreamability" not in response.json() or "displayEndscreen" in response.json()["liveStreamability"]["liveStreamabilityRenderer"]:
                    video_status = "结束"
                else:
                    video_status = "等待"
                # 不可能为空 不可以为空
                return video_status
        else:
            return False
    except:
        return False


# def checkLiveV3Api():  # 已弃用
#     for name, id in list(streamID.items()):
#         #id = LiveStreams.streamID[name]
#         r = requests.get(
#             "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=%s&key=%s" % (id, APIKey.key))
#         j = r.json()
#         logging.debug('[%s,%s]liveBroadcastContent:%s' %
#                       (name, id, j['items'][0]['snippet']['liveBroadcastContent']))
#         if j['items'][0]['snippet']['liveBroadcastContent'] == 'live':
#             if name in rbcThreads:
#                 logging.debug('[%s,%s]already start' % (name, id))
#             else:
#                 rbcThreads[name] = main.RebroadcastThread(
#                     len(rbcThreads), name, id)
#                 rbcThreads[name].start()
#         elif j['items'][0]['snippet']['liveBroadcastContent'] == 'none':
#             logging.debug('[%s,%s]not a live stream' % (name, id))
#             streamID.pop(name)
#         else:
#             logging.error('[%s,%s]err:liveBroadcastContent' % (name, id))
#         sleep(2)
