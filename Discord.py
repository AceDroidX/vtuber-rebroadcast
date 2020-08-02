import APIKey
import logging
import discord


class DiscordClient(discord.Client):
    self.channel = None

    def __init__(self, manage):
        self.manage = manage
        self.client = discord.Client()

    async def start(self):
        await client.start(APIKey.dc_bot_token)

    async def on_ready(self):
        print('Discord:We have logged in as {0.user}'.format(client))

    async def on_message(self, message):
        if message.author == client.user:
            return
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
