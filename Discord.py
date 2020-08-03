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
        await self.send_message('vtuber转播助手已启动\n'+self.manage.List())

    async def on_message(self, message):
        if message.author == self.user:
            return
        logging.debug(
            'DiscordClient.on_message.message.content:'+message.content)
        if message.content.startswith('/vtblive hello'):
            await message.channel.send('Hello!')
        elif message.content.startswith('/vtblive init'):
            self.set_config('channel', message.channel.id)
            await message.channel.send('初始化成功channel.name:'+message.channel.name)
        elif message.content.startswith('/vtblive add'):
            cmd = message.content.split(" ")
            await message.channel.send(self.manage.Add(cmd[2], cmd[3]))
        elif message.content.startswith('/vtblive del'):
            cmd = message.content.split(" ")
            await message.channel.send(self.manage.Del(cmd[2]))
        elif message.content.startswith('/vtblive list'):
            await message.channel.send(self.manage.List())
        elif message.content.startswith('/vtblive help'):
            await message.channel.send(self.manage.List())
        elif message.content.startswith('/vtblive'):
            await message.channel.send('未知命令 输入/vtblive help查看帮助')

    async def send_message(self, msg):
        channel = self.get_channel(self.get_config('channel'))
        if channel is None:
            logging.warn('channel is None')
            return
        await channel.send(msg)

    def get_config(self, key):
        return config.get_config('discord', key)

    def set_config(self, key, value):
        return config.set_config('discord', key, value)
