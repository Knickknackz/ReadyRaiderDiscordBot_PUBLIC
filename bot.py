import requests
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import os
import json
import datetime
import logging

from collections import Counter
from discord.ext import commands
from cogs.utils import customhelp

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_cfg():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with open('config.json') as json_data_file:
        cfg = json.load(json_data_file)
    return cfg


class ReadyRaider(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cmd_prefixes = ", ".join(kwargs['command_prefix'])
        self.mod_cmds = kwargs['mod_cmds']
        self.cd = commands.CooldownMapping.from_cooldown(8, 12, commands.BucketType.user)
        self.cd_counter = Counter()
        self.log = logger
        self.api_key = kwargs['api_key']
        self.warcraftLogs_api_key = kwargs['warcraftLogs_api_key']
        self.raidAPI = kwargs['raidAPI']
        self.guildAPI = kwargs['guildAPI']
        self.lootAPI = kwargs['lootAPI']
        self.discordAPI = kwargs['discordAPI']
        self.signAPI = kwargs['signAPI']
        self.declineAPI = kwargs['declineAPI']
        self.benchAPI = kwargs['benchAPI']
        self.messageAPI = kwargs['messageAPI']
        self.channelAPI = kwargs['channelAPI']
        self.initAPI = kwargs['initAPI']
        self.wowheadAPI = kwargs['wowheadAPI']
        self.wishlistAPI = kwargs['wishlistAPI']
        self.inviteAPI = kwargs['inviteAPI']
        self.signupAPI = kwargs['signupAPI']
        self.nexusHubAPI = kwargs['nexusHubAPI']

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                name = filename[:-3]
                # Comment to enable errorhandler module
                if name == 'errorhandler':
                    continue
                self.load_extension(f"cogs.{name}")

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        author_id = message.author.id

        if ctx.command is None:
            return

        # Allow admin commands through DMs
        if ctx.command.cog_name == 'Admin' and author_id == self.owner_id:
            await self.invoke(ctx)
            return

        if ctx.guild is None:
            return

        bucket = self.cd.get_bucket(message)
        current = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
        retry_after = bucket.update_rate_limit(current)

        if retry_after and author_id != self.owner_id:
            self.cd_counter[author_id] += 1
        else:
            self.cd_counter.pop(author_id, None)

        await self.invoke(ctx)


def run_bot():
    cfg = get_cfg()

    bot = ReadyRaider(api_key=cfg['api_key'], warcraftLogs_api_key=cfg['warcraftLogs_api_key'],command_prefix=cfg['prefix'], mod_cmds=cfg['mod_cmds'], raidAPI=cfg['raidAPI'], lootAPI=cfg['lootAPI'], discordAPI=cfg['discordAPI'],
                      guildAPI=cfg['guildAPI'], signAPI=cfg['signAPI'], declineAPI=cfg['declineAPI'],benchAPI=cfg['benchAPI'],
                      messageAPI=cfg['messageAPI'], channelAPI=cfg['channelAPI'], initAPI=cfg['initAPI'], inviteAPI=cfg['inviteAPI'], signupAPI=cfg['signupAPI'],
                      wishlistAPI=cfg['wishlistAPI'], wowheadAPI=cfg['wowheadAPI'], nexusHubAPI=cfg['nexusHubAPI'],
                      help_command=customhelp.CustomHelpCommand(mod_cmds=cfg['mod_cmds'], prefixes=cfg['prefix']))
    bot.run(cfg['token'])


run_bot()