import threading

TemplateArg = r'streamlink --hls-live-edge 1 "https://www.youtube.com/watch?v={}" "best" -O | ffmpeg -re -i pipe:0 -c copy -f flv rtmp://localhost/flv/{}'
workingdir = r'/web/hls'

class RebroadcastThread (threading.Thread):
    def __init__(self, threadID, name, id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.id = id

    def run(self):
        arg = TemplateArg.format(self.id, self.name)
        logging.debug(self.id+":开始转播")
        pp = subprocess.Popen(
            arg, shell=True, encoding='utf-8', cwd=workingdir)
        while True:
            if not self.name in LiveStreams.streamID:
                pp.terminate()
                break
            if pp.returncode == None:
                continue
            elif pp.returncode == 0:
                logging.debug(self.id+':转播完成')
                break
            else:
                logging.error("err:startRebroadcast")
                break
            # rbcThreads.pop(self.name)