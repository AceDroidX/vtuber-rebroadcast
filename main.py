import requests
import getLiveStreams
import APIKey
from time import sleep
import subprocess
import threading

TemplateArg = r'streamlink --hls-live-edge 1 "https://www.youtube.com/watch?v={}" "best" -O | ffmpeg -re -i pipe:0 -c copy -f flv rtmp://localhost/flv/{}'
workingdir = r'/web/hls'
threads = []

while True:
    checkLive()
    sleep(1)


def checkLive():
    for name, id in getLiveStreams.streamID.items():
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=%s&key=%s" % (id, APIKey.key))
        j = r.json()
        print('[%s,%s]liveBroadcastContent:%s' %
              (name, id, j['items']['snippet']['liveBroadcastContent']))
        if j['items']['snippet']['liveBroadcastContent'] == 'live':
            threads.append(RebroadcastThread(len(threads), name, id))
            threads[len(threads)-1].start()
        elif j['items']['snippet']['liveBroadcastContent'] == 'none':
            print('[%s,%s]not a live stream' % (name, id))
            getLiveStreams.streamID.pop(name)
        else:
            print('[%s,%s]err:liveBroadcastContent' % (name, id))
        sleep(1)


class RebroadcastThread (threading.Thread):
    def __init__(self, threadID, name, id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.id = id

    def run(self):
        arg = TemplateArg.format(self.id, self.name)
        print(self.id+":开始转播")
        ret = subprocess.run(arg, encoding='utf-8', cwd=workingdir)
        if ret.returncode == 0:
            print(self.id+':转播完成')
        else:
            print("err:startRebroadcast")
