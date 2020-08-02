import requests
import LiveStreams
import APIKey
from time import sleep
import subprocess
import threading
import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s[%(levelname)s]%(threadName)s>%(message)s', level=logging.DEBUG)
    manager = LiveStreams.StreamerManager()
    manager.start()
    while True:
        cmd = input('rbc>').split(" ")
        if cmd[0]=='':
            continue
        elif cmd[0] == 'add':
            LiveStreams.manualAdd(cmd[1], cmd[2])
        elif cmd[0] == 'del':
            LiveStreams.manualDel(cmd[1])
        elif cmd[0]=='quit' or cmd[0]=='exit' or cmd[0]=='q':
            sys.exit()
        else:
            print('未知的控制台命令')
