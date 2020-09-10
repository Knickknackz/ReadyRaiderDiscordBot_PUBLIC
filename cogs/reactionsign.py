from discord.ext import commands
from .utils.globalfunctions import search_format
import requests
from urllib.parse import quote


class React(commands.Cog):
    """
    class that contains much of the reaction singing functions
    """
    def __init__(self, bot):
        self.bot = bot

    async def raidUpdate(self, raidData, channel_id, guild_id):
        """
        updates a given posted raid
        :param raidData:
        :param channel_id:
        :param guild_id:
        """
        channel = self.bot.get_channel(int(channel_id))
        message = await channel.fetch_message(int(raidData['messageID']))
        raid_cog = self.bot.get_cog('Raid')
        api_cog = self.bot.get_cog('RR_API')

        guildData = await api_cog.guild_data(guild_id)

        if 'Guild Server' in guildData:
            wowServer = guildData['Guild Server']
            wowServer = wowServer.split('(')[1][:-1]
        else:
            wowServer = None

        await raid_cog.postupcomingraid(raidData, channel, wowServer, message, True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Event triggered when user reacts to a message. Signs player to raid with data based emoji

        Parameters
        ----------
        payload
            discord's instance of where the reaction occured.
        """

        # Don't accept DMs
        if not payload.guild_id:
            return

        # Ignore Bot
        if payload.user_id == self.bot.user.id:
            return

        if payload.emoji.name not in {'\U00002705', '\U0000274C', '\U0001FA91'}:  # Green Check, X, Chair
            return

        user = await self.bot.fetch_user(payload.user_id)
        if user.bot:
            return

        # U+2705 (:white_check_mark: ), U+2611(:ballot_box_with_check:) ,U+1FA91(:chair:),
        # U+1F1FD(:regional_indicator_x:), U+1F1E7(:regional_indicator_b:),  U+274C(:x:)

        # Is this ID attached to a raid message? (Also technically checks if this is the right channel)
        message_id = payload.message_id
        s = search_format('messageID', 'equals', str(message_id))
        s = "".join(str(s).split())
        r = requests.get(self.bot.raidAPI + '?constraints=[' + s + ']')
        raidData = r.json()['response']['results']

        if raidData:
            raid_id = raidData[0]['_id']
        else:
            print("User liked a post that isn't a raid" + payload.member.name + '#' + str(payload.member.discriminator))
            return  # Returns if messageID isn't attached to a Raid in DB

        # UserName Checks
        discord_name = payload.member.name
        discord_suffix = payload.member.discriminator
        discord_full = quote(discord_name + ' #' + discord_suffix)

        s = search_format('DiscordID', 'equals', discord_full)
        s = "".join(str(s).split())
        r = requests.get(self.bot.discordAPI + '?constraints=[' + s + ']')
        userData = r.json()['response']['results']

        if userData:
            RR_id = userData[0]['UserID']
        else:
            # DMs User to update RR account
            dmchannel = await payload.member.create_dm()
            print("This user liked a post and was told he wasn't signed up:" + discord_name + '%20%23' + str(
                discord_suffix) + ', Full:' + discord_full)
            await dmchannel.send(
                "Error! Please Link Your Discord Account to ReadyRaider Here: https://www.readyraider.com/profile2")

            # Removes Wrong Reaction
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(message_id)
            user = await self.bot.fetch_user(payload.user_id)
            await msg.remove_reaction(payload.emoji.name, user)
            return

        if payload.emoji.name == '\U00002705':  # GREEN CHECK
            signAPI = self.bot.signAPI

        elif payload.emoji.name == '\U0000274C':  # 'X'
            signAPI = self.bot.declineAPI

        elif payload.emoji.name == '\U0001FA91':  # CHAIR
            signAPI = self.bot.benchAPI
        else:
            signAPI = self.bot.declineAPI

        headers = {"Authorization": "Bearer " + self.bot.api_key}
        body = {"rid": str(raid_id), "raider": str(RR_id)}
        requests.post(signAPI, data=body, headers=headers)

        s = search_format('messageID', 'equals', str(message_id))
        s = "".join(str(s).split())
        r = requests.get(self.bot.raidAPI + '?constraints=[' + s + ']')
        raidData = r.json()['response']['results']
        await self.raidUpdate(raidData[0], payload.channel_id, payload.guild_id)


def setup(bot):
    bot.add_cog(React(bot))
