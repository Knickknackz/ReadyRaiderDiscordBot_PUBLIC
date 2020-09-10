from discord.ext import commands
from .utils.globalfunctions import search_format
import requests


class APImanage(commands.Cog, name='RR_API'):
    def __init__(self, bot):
        self.bot = bot

    """
    Contains Many of the functions that control API Management
    """

    async def guild_data(self, guild_id):
        """
        returns the ReadyRaider Data for a specific Server's Discord ID
        :param guild_id:
            the Discord ID of a server
        :return resutls:
            returns either the expected data or nothing
        """
        guild_api = self.bot.guildAPI
        s = '[' + search_format('GuildDiscordID', 'equals', str(guild_id)) + ']'
        r = requests.get(guild_api + '?constraints=' + str(s))
        res = r.json()['response']['results']
        if res:
            return res[0]
        return None

    async def raid_data(self, messageID):
        """
            obtains the data for a specific discord message(only called on known raids)
        :param messageID:
            the Discord messageID of a specific raid
        :return:
            returns the data for a raid attatched to a specific message
        """
        raid_api = self.bot.raidAPI

        s = '[' + search_format('discordID', 'equals', str(messageID)) + ']'
        r = requests.get(raid_api + '?constraints=' + str(s))
        return r.json()['response']['results']

    async def get_channel_info(self, serverID):
        """
        Finds the Channel ID's for a specific Discord Server
        :param serverID:
            Discord Server ID
        :return:
            either returns nothing or a dictionary of channel IDs
        """
        s = '[' + search_format('GuildDiscordID', 'equals', str(serverID)) + ']'
        r = requests.get(self.bot.guildAPI + '?constraints=' + str(s))
        guild_data = r.json()['response']['results']
        if guild_data:
            guild_data = guild_data[0]
        else:
            print('GUILD DATA NOT FOUND FOR SERVER: ' + str(serverID))
            return None

        channelinfo = {}
        if 'pastchannelID' in guild_data:
            channelinfo['pastchannelid'] = guild_data['pastchannelID']
        else:
            channelinfo['pastchannelid'] = None

        if 'futurechannelID' in guild_data:
            channelinfo['futurechannelid'] = guild_data['futurechannelID']
        else:
            channelinfo['futurechannelid'] = None

        if 'lootchannelID' in guild_data:
            channelinfo['lootchannelid'] = guild_data['lootchannelID']
        else:
            channelinfo['lootchannelid'] = None

        if 'categoryID' in guild_data:
            channelinfo['categoryid'] = guild_data['categoryID']
        else:
            channelinfo['categoryid'] = None

        if 'commandsid' in guild_data:
            channelinfo['commandschannelid'] = guild_data['commandsid']
        else:
            channelinfo['commandschannelid'] = None

        return channelinfo


def setup(bot):
    bot.add_cog(APImanage(bot))
