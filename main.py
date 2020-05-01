import requests
import LiveStreams
import APIKey
from time import sleep
import subprocess
import threading
import logging

TemplateArg = r'streamlink --hls-live-edge 1 "https://www.youtube.com/watch?v={}" "best" -O | ffmpeg -re -i pipe:0 -c copy -f flv rtmp://localhost/flv/{}'
workingdir = r'/web/hls'
rbcThreads = {}


def checkLive():
    for name in LiveStreams.streamID:
        id = LiveStreams.streamID[name]
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=%s&key=%s" % (id, APIKey.key))
        j = r.json()
        logging.debug('[%s,%s]liveBroadcastContent:%s' %
                      (name, id, j['items'][0]['snippet']['liveBroadcastContent']))
        if j['items'][0]['snippet']['liveBroadcastContent'] == 'live':
            if name in rbcThreads:
                logging.debug('[%s,%s]already start' % (name, id))
            else:
                rbcThreads[name] = RebroadcastThread(len(rbcThreads), name, id)
                rbcThreads[name].start()
        elif j['items'][0]['snippet']['liveBroadcastContent'] == 'none':
            logging.debug('[%s,%s]not a live stream' % (name, id))
            LiveStreams.streamID.pop(name)
        else:
            logging.error('[%s,%s]err:liveBroadcastContent' % (name, id))
        sleep(1)


class CheckLiveThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logging.debug('启动直播检测')
        while True:
            checkLive()
            sleep(1)


class RebroadcastThread (threading.Thread):
    def __init__(self, threadID, name, id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.id = id

    def run(self):
        arg = TemplateArg.format(self.id, self.name)
        logging.debug(self.id+":开始转播")
        ret = subprocess.run(arg, shell=True, encoding='utf-8', cwd=workingdir)
        if ret.returncode == 0:
            logging.debug(self.id+':转播完成')
        else:
            logging.error("err:startRebroadcast")
        # rbcThreads.pop(self.name)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s[%(levelname)s]%(threadName)s>%(message)s', level=logging.DEBUG)
    checkthread = CheckLiveThread().start()
    while True:
        cmd = input('rbc>').split(" ")
        if cmd[0] == 'add':
            LiveStreams.manualAdd(cmd[1], cmd[2])
        else:
            pass
