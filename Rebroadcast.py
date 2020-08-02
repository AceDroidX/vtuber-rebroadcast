import threading
import time
import queue
import logging

TemplateArg = r'streamlink --hls-live-edge 1 "https://www.youtube.com/watch?v={}" "best" -O | ffmpeg -re -i pipe:0 -c copy -f flv rtmp://localhost/flv/{}'
workingdir = r'/web/hls'


class RebroadcastThread (threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        # self.threadID = threadID
        self.queue = queue
        self.name, self.id = queue.get()

    def run(self):
        arg = TemplateArg.format(self.id, self.name)
        logging.debug(self.id+":开始转播")
        pp = subprocess.Popen(
            arg, shell=True, encoding='utf-8', cwd=workingdir)
        while True:
            time.sleep(0.01)
            if not self.queue.empty():
                item = self.queue.get()
                if item == 'stop':
                    pp.terminate()
                    logging.info(name+'转播已停止')
                    break
                else:
                    logging.warn('RebroadcastThread.queue:未知命令')
            if pp.returncode == None:
                continue
            elif pp.returncode == 0:
                logging.debug(self.id+':转播完成')
                break
            else:
                logging.error("err:startRebroadcast")
                break
