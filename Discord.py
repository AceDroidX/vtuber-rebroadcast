import APIKey
import logging
import discord
import asyncio


class DiscordClient(discord.Client):
    channel = None

    def __init__(self, manage=None):
        super().__init__()
        self.manage = manage

    def set_manage(self, manage):
        self.manage = manage

    async def on_ready(self):
        print(f'Discord:We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        logging.debug(
            'DiscordClient.on_message.message.content:'+message.content)
        if message.content.startswith('/vtblive hello'):
            await message.channel.send('Hello!')
        elif message.content.startswith('/vtblive init'):
            self.channel = message.channel
            await message.channel.send('初始化成功channel.name:'+self.channel.name)
        elif message.content.startswith('/vtblive add'):
            cmd = message.content.split(" ")
            await message.channel.send(self.manage.Add(cmd[2], cmd[3]))
        elif message.content.startswith('/vtblive del'):
            cmd = message.content.split(" ")
            await message.channel.send(self.manage.Del(cmd[2]))

    async def send_message(self, msg):
        if self.channel is None:
            logging.warn('self.channel is None')
            return
        await self.channel.send(msg)
