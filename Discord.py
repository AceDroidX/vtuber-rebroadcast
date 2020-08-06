import APIKey
import logging
import discord
import asyncio
import config


class DiscordClient(discord.Client):
    channel = None

    def __init__(self, manage=None):
        super().__init__()
        self.manage = manage
        self.config = config.configjson['discord']

    def set_manage(self, manage):
        self.manage = manage

    async def on_ready(self):
        print(f'Discord:We have logged in as {self.user}')
        #await self.send_message('vtuber转播助手已启动\n'+self.manage.List())

    async def on_message(self, message):
        try:
            if message.author == self.user:
                return
            logging.debug(
                'DiscordClient.on_message.message.content:'+message.content)
            if message.content.startswith('/vtblive hello'):
                await self.send_message('Hello!',message.channel)
            elif message.content.startswith('/vtblive init'):
                self.set_config('channel', message.channel.id)
                await self.send_message(f'初始化成功channel.name:{message.channel.name}',message.channel)
            elif message.content.startswith('/vtblive add'):
                cmd = message.content.split(" ")
                await self.send_message(self.manage.Add(cmd[2], cmd[3]),message.channel)
            elif message.content.startswith('/vtblive del'):
                cmd = message.content.split(" ")
                await self.send_message(self.manage.Del(cmd[2]),message.channel)
            elif message.content.startswith('/vtblive set'):
                cmd = message.content.split(" ")
                await self.send_message(self.manage.Set(cmd[2], cmd[3], cmd[4]),message.channel)
            elif message.content.startswith('/vtblive get'):
                cmd = message.content.split(" ")
                await self.send_message(self.manage.Get(cmd[2], cmd[3]),message.channel)
            elif message.content.startswith('/vtblive list'):
                await self.send_message(self.manage.List(),message.channel)
            elif message.content.startswith('/vtblive help'):
                await self.send_message(self.help())
            elif message.content.startswith('/vtblive'):
                await self.send_message('未知命令 输入/vtblive help查看帮助',message.channel)
        except IndexError as e:
            logging.error('DiscordClient.on_message.IndexError', exc_info=True)
            await self.send_message('参数错误 输入/vtblive help查看帮助',message.channel)
        except BaseException as e:
            logging.error('DiscordClient.on_message.BaseException', exc_info=True)
            await self.send_message(f'未知错误：\n{str(sys.exc_info())}',message.channel)
        

    async def send_message(self, msg, channel=None):
        if channel is None:
            channel = self.get_channel(self.get_config('channel'))
        if channel is None:
            logging.warn('channel is None')
            return
        logging.info(f'DiscordClient.send_message[{channel.id}]{msg}')
        await channel.send(msg)

    def get_config(self, key):
        return config.get_config('discord', key)

    def set_config(self, key, value):
        return config.set_config('discord', key, value)

    def help(self):
        return '''/vtblive add <name> <channelId>：添加一个vtuber到监控列表
/vtblive del <name>：删除一个vtuber
/vtblive list：显示当前监控的vtuber的状态'''
