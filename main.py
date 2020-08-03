import LiveStreams
import APIKey
import logging
import sys
import asyncio
import traceback
import aioconsole
import Discord
import config


async def mainConsole(manager, discord):
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
        elif cmd[0] == 'list':
            manager.List()
        elif cmd[0] == 'send':
            await discord.send_message(cmd[1])
        elif cmd[0] == 'quit' or cmd[0] == 'exit' or cmd[0] == 'q':
            config.writeConfig()
            sys.exit()
        else:
            print('未知的控制台命令')


def exception_handler(loop, context):
    logging.error('Exception handler called')
    traceback.print_exc()


# https://github.com/klen/muffin/issues/18#issuecomment-182138773
# avoid frustrating INFO messages about timeout caused by sleep(1)
class SkipTimeouts(logging.Filter):
    def filter(self, rec):
        if(rec.levelno == logging.INFO and
           rec.msg.startswith('poll') and
           rec.msg.endswith(': timeout') and
           990 < rec.args[0] < 1000 and
           1000 < rec.args[1] < 1010):
            return False  # hide this record
        return True


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s[%(levelname)s]%(threadName)s>%(message)s', level=logging.DEBUG)
    logging.getLogger('discord').setLevel(logging.INFO)
    logging.info('eventloop已启动')
    asyncio.get_event_loop().set_debug(True)
    asyncio.get_event_loop().set_exception_handler(exception_handler)
    logging.getLogger('asyncio').addFilter(SkipTimeouts())
    ########
    discord = Discord.DiscordClient()
    manager = LiveStreams.StreamerManager(discord)
    discord.set_manage(manager)
    # manager.Add('tamaki','UC8NZiqKx6fsDT3AVcMiVFyA')
    # add matsuri UCQ0UDLQCjY0rmuxCDE38FGg
    # add kizunaai UC4YaOt1yT-ZeyB0OmxHgolA
    asyncio.ensure_future(discord.start(APIKey.dc_bot_token))
    asyncio.ensure_future(mainConsole(manager, discord))
    asyncio.ensure_future(config.autoSave())
    ########
    asyncio.get_event_loop().run_forever()
