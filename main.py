import LiveStreams
import APIKey
from time import sleep
import logging
import sys
import asyncio
import traceback
import aioconsole
import Discord
import config


async def mainConsole(manager):
    stdin, stdout = await aioconsole.get_standard_streams()
    while True:
        await asyncio.sleep(0.1)
        byte = await stdin.readline()
        cmd = byte.decode().strip('\n').split(" ")
        if cmd[0] == '':
            continue
        elif cmd[0] == 'add':
            manager.Add(cmd[1], cmd[2])
        elif cmd[0] == 'del':
            manager.Del(cmd[1])
        elif cmd[0] == 'quit' or cmd[0] == 'exit' or cmd[0] == 'q':
            sys.exit()
        else:
            print('未知的控制台命令')

def exception_handler(loop, context):
    logging.error('Exception handler called')
    traceback.print_exc()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s[%(levelname)s]%(threadName)s>%(message)s', level=logging.DEBUG)
    logging.getLogger('discord').setLevel(logging.INFO)
    logging.info('eventloop已启动')
    asyncio.get_event_loop().set_debug(True)
    asyncio.get_event_loop().set_exception_handler(exception_handler)
    ########
    discord = Discord.DiscordClient()
    manager = LiveStreams.StreamerManager(discord)
    discord.set_manage(manager)
    # manager.Add('tamaki','UC8NZiqKx6fsDT3AVcMiVFyA')
    # add matsuri UCQ0UDLQCjY0rmuxCDE38FGg
    # add kizunaai UC4YaOt1yT-ZeyB0OmxHgolA
    asyncio.ensure_future(discord.start(APIKey.dc_bot_token))
    asyncio.ensure_future(mainConsole(manager))
    asyncio.ensure_future(config.autoSave())
    ########
    asyncio.get_event_loop().run_forever()
