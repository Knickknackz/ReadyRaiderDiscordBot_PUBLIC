import discord
import datetime
import requests

from discord.ext import commands
from .utils import customcommand, emojis, timezones
from .utils.globalfunctions import search_format
from datetime import datetime, timedelta


class Raid(commands.Cog):
    """
    This category includes adding, deleting, editing, clearing raids and etc.
    All raid comps are updated every 60 minutes and posted on the proper channel.
    """

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def add_emojis(msg):
        """
        Adds emojis to message

        Parameters
        ----------
        msg
            Instance of Message
        """
        await msg.add_reaction('\U00002705')  # Check
        await msg.add_reaction('\U0000274C')  # X
        await msg.add_reaction('\U0001FA91')  # Chair

    async def run_add_bot_channels(self, guild):
        """
        See add_bot_channels in guild.py

        Parameters
        ----------
        guild
            Instance of Guild
        """

        guild_cog = self.bot.get_cog('Server')
        await guild_cog.add_bot_channels(guild)

    async def get_raid_data(self, days, wowguildID):
        """
        finds raids in a given window of days.
        :param days:
            how far to look for raids.
        :param wowguildID:
            ReadyRaider ID for a guild
        :return:
            a list of json data for raids.
        """
        n = datetime.utcnow()
        c = '[' + search_format("Guild Hosting", "equals", wowguildID)
        if days >= 0:
            # if upcoming
            c += "," + search_format("Start Date", "less%20than", (n + timedelta(days=days)).isoformat())
            c += "," + search_format("Start Date", "greater%20than",
                                     (n - timedelta(days=days)).isoformat())  # (n - timedelta(days=1))
            c += "," + '{"key":"showedlist","constraint_type":"empty"}'
        else:
            # if completed
            c += "," + search_format("Start Date", "greater%20than", (n + timedelta(days=days)).isoformat())
            c += "," + search_format("Start Date", "less%20than", (n - timedelta(days=days)).isoformat())
            c += "," + '{"key":"showedlist","constraint_type":"not%20empty"}'
        c = "".join(str(c).split())
        r = requests.get(self.bot.raidAPI + '?constraints=' + c + ']')
        raidData = r.json()['response']['results']
        return raidData

    async def postupcomingraid(self, raid, channel, zone, message='0', edit=False):
        """
        posts a raid
        :param raid:
            json data for a raid
        :param channel:
            the future channel
        :param zone:
            timezone
        :param message:
            if there is already a messageID for the raid
        :param edit:
            is this an edit or a raw post
        :return:
        """
        if raid is None:
            return

        if 'Number of Players' in raid:
            raidSize = str(raid['Number of Players'])
        else:
            raidSize = None

        if 'Player Signed Up' in raid:
            attending = str(len(raid["Player Signed Up"]))
        else:
            attending = '0'

        benchString = ''
        if 'BenchList' in raid:
            if len(raid['BenchList']) > 0:
                bench = '(' + str(len(raid['BenchList'])) + ')'
                for raider in raid['BenchList']:
                    benchString += raider + ', '
                benchString = benchString[:-2]
            else:
                bench = '(0)'
                benchString = 'No Raiders on the Bench'
        else:
            bench = '(0)'
            benchString = 'No Raiders on the Bench'

        declinedString = ''
        if 'DeclinedList' in raid:
            if len(raid['DeclinedList']) > 0:
                declined = '(' + str(len(raid['DeclinedList'])) + ')'
                for raider in raid['DeclinedList']:
                    declinedString += raider + ', '
                declinedString = declinedString[:-2]
            else:
                declined = '(0)'
                declinedString = 'No Raiders Declined'
        else:
            declined = '(0)'
            declinedString = 'No Raiders Declined'

        if 'Raid Location' in raid:
            title = 'Sign-up is Live for ' + raid['Raid Location']
        else:
            title = 'Sign-up is Live'

        desc = 'Raid Team: '
        if 'RaidTeam' in raid:
            desc += raid['RaidTeam']
        else:
            desc += 'Not Selected'

        if 'Special Requirements' in raid:
            desc += '\n\nRaid Notes: ' + raid['Special Requirements']

        embed = discord.Embed(
            title=title,
            description=desc,
            colour=discord.Colour.from_rgb(25, 145, 235),
            timestamp=datetime.utcnow()
        )

        if zone in timezones.zones:
            offset = timedelta(hours=timezones.zones[zone])
        else:
            offset = timedelta(hours=0)

        sraw = datetime.fromisoformat(raid['Start Date'][:-1])
        sraw = sraw + offset
        sdate = sraw.strftime("%A, %B %d")
        stime = sraw.strftime("%I:%M(%p)")

        # Calendar \U0001F4C5"\u200b, Spiral Calendar \U0001F5D3
        embed.add_field(name="\u200b", value=' \U0001F5D3 **' + sdate + '**\n \u200b', inline=True)

        # Clock (3pm) \U0001F552
        embed.add_field(name="\u200b", value='\U0001F552 **' + stime + '**\n \u200b \u200b (Server Time)', inline=True)

        # Dollar \U0001F4B5, \U00002694 Crossed Swords
        if 'Raid Worth' in raid:
            embed.add_field(name="\u200b", value='\U00002694 **' + str(raid['Raid Worth']) + ' R.A.P/DKP**\n \u200b',
                            inline=True)
        else:
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        attend_f = '\U00002705 Attending: (' + attending
        if raidSize:
            attend_f += '/' + raidSize
        attend_f += ')'
        decline_f = '\U0000274C Declined: ' + declined + '             \u200b'
        bench_f = '\U0001FA91 Benched: ' + bench + '    \u200b'

        embed.add_field(name=attend_f, value="\u200b", inline=True)
        embed.add_field(name=decline_f, value="\u200b")
        embed.add_field(name=bench_f, value="\u200b")

        attendingList = {}

        if 'SignedUpList' in raid:
            sign_up_order = 0
            for pair in raid['SignedUpList']:
                sign_up_order += 1
                pair = pair[1:-1].split(',')  # ASSUMES FORMATTING: '[*Name*,*Class*]'
                name = "`" + str(sign_up_order) + "` " + pair[0]
                if pair[1] in attendingList:
                    attendingList[pair[1]].append(name)
                elif pair[1] in emojis.spec_emojis:
                    attendingList[pair[1]] = [name]

        for c in attendingList.keys():
            emo = emojis.spec_emojis[c]
            value = ''
            for player in attendingList[c]:
                value += player + '\n'
            embed.add_field(name=emo + '`' + c + 's(' + str(len(attendingList[c])) + ')`', value=value + '\n \u200b')

        decline_f = '\U0000274C __Declined' + declined + ':__'
        embed.add_field(name=decline_f, value=declinedString + '\n', inline=False)

        bench_f = '\U0001FA91 __Benched' + bench + ':__'
        embed.add_field(name=bench_f, value=benchString, inline=False)

        raidUrl = 'https://www.readyraider.com/dashboard?view=raids'
        embed.add_field(name="\u200b",
                        value='\U0001F440 [View Full Raid Details](' + raidUrl + ')' +
                              '\n[Dashboard](https://www.readyraider.com/dashboard) - [Support]('
                              'https://discord.gg/GByncpz) - ' +
                              '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium]('
                              'https://www.readyraider.com/premium)',
                        inline=False)

        if edit:
            await message.edit(embed=embed)
        else:
            msg = await channel.send(embed=embed)
            await self.add_emojis(msg)
            body = {"raid": str(raid['_id']), "messageid": str(msg.id)}
            headers = {"Authorization": "Bearer " + self.bot.api_key}
            requests.post(self.bot.messageAPI, data=body, headers=headers)

        return str(msg.id)

    async def upcoming_raids_helper(self, guild_id):
        """
        Prepares the needed variables for posting raids
        :param guild_id:
            discord ID for a server
        """
        days = 7
        api_cog = self.bot.get_cog('RR_API')
        guildData = await api_cog.guild_data(guild_id)

        if not guildData:
            return

        if 'Guild Server' in guildData:
            wowServer = guildData['Guild Server']
            zone = wowServer.split('(')[1][:-1]
        else:
            zone = None

        wowguildID = guildData['_id']
        raidData = await self.get_raid_data(days, wowguildID)  # gets all raids starting in the next 7 days

        if 'futurechannelID' in guildData:
            futurechannelid = guildData['futurechannelID']
        else:
            print('No Future Channel found for: ' + guildData['Guild Name'])
            return

        if not futurechannelid:
            print('FutureChannelID is None in the DB for guild: ' + guildData['Guild Name'])
            # await self.run_add_bot_channels(guild)
            return

        futurechannel = self.bot.get_channel(int(futurechannelid))

        if not futurechannel:
            # guild = self.bot.get_guild(guild_id)
            # await self.run_add_bot_channels(guild)
            print('FutureChannelID is in DB, but, Channel is not in ' + guildData['Guild Name'] + "'s server")
            return

        if not raidData:
            return

        embed = discord.Embed(
            title='__Upcoming Raids__',
            description='Raids +/- 1 Week from Today',
            colour=discord.Colour.from_rgb(25, 145, 235),
            timestamp=datetime.utcnow()
        )

        for raid in raidData:
            if 'messageID' in raid:
                try:
                    await futurechannel.fetch_message(int(raid['messageID']))
                    msg = str(raid['messageID'])
                except:
                    msg = await self.postupcomingraid(raid, futurechannel, zone)
            else:
                msg = await self.postupcomingraid(raid, futurechannel, zone)

            field_name = ''
            if 'RaidTeam' in raid:
                field_name += raid['RaidTeam'] + "'s "
            else:
                field_name += guildData['Guild Name']

            if 'Raid Location' in raid:
                field_name += raid['Raid Location']
            else:
                field_name += 'Raid'

            if zone in timezones.zones:
                offset = timedelta(hours=timezones.zones[zone])
            else:
                offset = timedelta(hours=0)

            sraw = datetime.fromisoformat(raid['Start Date'][:-1])
            sraw = sraw + offset
            sdate = sraw.strftime("%A, %B %d")
            stime = sraw.strftime("%I:%M(%p)")
            url = 'https://discordapp.com/channels/' + str(guild_id) + '/' + str(futurechannelid) + '/' + msg
            field_value = '**' + sdate + '**, **' + stime +'**\n [Click Here](' + url + ') to See Message'

            embed.add_field(name= field_name,
                            value =field_value,
                            inline = True)

        await futurechannel.send(embed=embed)

    @commands.cooldown(4, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['Upcoming', 'upcoming', 'update'],
                             description="Updates and displays information about all raids in the upcoming week.",
                             examples=["upcoming", "upcoming_raids"])
    async def upcoming_raids(self, ctx):
        """
        command for updating upcoming raids
        :param ctx:
            discord context
        """
        await self.upcoming_raids_helper(ctx.guild.id)

    @staticmethod
    async def postpastraid(raid, channel, zone):
        """
        posts a raid to the past channel
        Parameters
        ----------
        raid
            dictionary of raid info
        channel
            pastraid channel
        zone
            timezone
        """
        if raid is None:
            return

        if 'showedlist' in raid:
            confirmed = str(len(raid["showedlist"]))
            confirmedList = []
            for raider in raid['showedlist']:
                confirmedList.append(raider)
            confirmedList.sort(key=str.lower)
            confirmedString = ', '.join(confirmedList)
            del confirmedList
        else:
            confirmed = '0'
            confirmedString = 'None Confirmed Yet'

        benchString = ''
        if 'BenchList' in raid:
            if len(raid['BenchList']) > 0:
                bench = str(len(raid['BenchList']))
                for raider in raid['BenchList']:
                    benchString += raider + ', '
                benchString = benchString[:-2]
            else:
                bench = '0'
                benchString = 'None Benched'
        else:
            bench = '0'
            benchString = 'None Benched'

        declinedString = ''
        if 'DeclinedList' in raid:
            if len(raid['DeclinedList']) > 0:
                declined = str(len(raid['DeclinedList']))
                for raider in raid['DeclinedList']:
                    declinedString += raider + ', '
                declinedString = declinedString[:-2]
            else:
                declined = '0'
                declinedString = 'None Declined'
        else:
            declined = '0'
            declinedString = 'None Declined'

        if 'Raid Location' in raid:
            title = raid['Raid Location'] + ' Attendance'
        else:
            title = 'Raid Attendance'

        desc = 'Raid Team: '
        if 'RaidTeam' in raid:
            desc += raid['RaidTeam']
        else:
            desc += 'Not Selected'

        if 'Special Requirements' in raid:
            desc += '\n\nRaid Notes: ' + raid['Special Requirements']

        embed = discord.Embed(
            title=title,
            description=desc,
            colour=discord.Colour.from_rgb(25, 145, 235),
            timestamp=datetime.utcnow()
        )

        if zone in timezones.zones:
            offset = timedelta(hours=timezones.zones[zone])
        else:
            offset = timedelta(hours=0)

        sraw = datetime.fromisoformat(raid['Start Date'][:-1])
        sraw = sraw + offset
        sdate = sraw.strftime("%A, %B %d")
        stime = sraw.strftime("%I:%M(%p)")

        # Calendar \U0001F4C5"\u200b, Spiral Calendar  \U0001F5D3"
        embed.add_field(name="\u200b", value='** \U0001F5D3 ' + sdate + '\n \u200b**', inline=True)
        # Clock (3pm) \U0001F552
        embed.add_field(name="\u200b", value='**\U0001F552 ' + stime + '**\n \u200b \u200b (Server Time)', inline=True)
        # Dollar \U0001F4B5, \U00002694 Crossed Swords
        if 'Raid Worth' in raid:
            embed.add_field(name="\u200b", value='**\U00002694 ' + str(raid['Raid Worth']) + ' R.A.P/DKP**\n \u200b',
                            inline=True)
        else:
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        confirmed_f = '\U00002705 __Confirmed(' + confirmed + '):__'
        decline_f = '\U0000274C __Declined(' + declined + '):__'
        bench_f = '\U0001FA91 __Benched(' + bench + '):__'

        embed.add_field(name=confirmed_f, value=confirmedString, inline=False)
        embed.add_field(name=decline_f, value=declinedString)
        embed.add_field(name=bench_f, value=benchString, inline=False)

        if 'rapreductiontext' in raid:
            reductionString = ''
            for raider in raid['rapreductiontext']:
                reductionString += raider + ', '
            embed.add_field(name='\U000026A0__RAP Deductions(' + str(len(raid['rapreductiontext'])) + ')__:',
                            value=reductionString[:-2])
        # Eyes \U0001F440
        # raidUrl= 'https://readyraider.com/dashboard?raid=' + str(raid['_id'])
        raidUrl = 'https://www.readyraider.com/dashboard?view=raids'
        embed.add_field(name="\u200b",
                        value='\U0001F440 [View Full Raid Details](' + raidUrl + ')' +
                              '\n[Dashboard](https://www.readyraider.com/dashboard) - [Support]('
                              'https://discord.gg/GByncpz) - ' +
                              '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium]('
                              'https://www.readyraider.com/premium)',
                        inline=False)

        await channel.send(embed=embed)

        """
        OutDated // Used to post message Id's, No longer used
        body = {"raid": str(raid['_id']), "messageid": str(msg.id)}
        headers = {"Authorization": "Bearer " + self.bot.api_key}
        requests.post(self.bot.messageAPI, data=body, headers=headers)
        """

    async def past_raids_helper(self, guild_id):
        """
        sets up variables to post raids
        :param guild_id:
            discord guild id
        """
        days = -7
        api_cog = self.bot.get_cog('RR_API')
        guildData = await api_cog.guild_data(guild_id)

        if not guildData:
            return

        if 'Guild Server' in guildData:
            wowServer = guildData['Guild Server']
            wowServer = wowServer.split('(')[1][:-1]
        else:
            wowServer = None

        wowguildID = guildData['_id']
        raidData = await self.get_raid_data(days, wowguildID)  # gets all raids starting in the next 7 days

        if 'futurechannelID' in guildData:
            futurechannelid = guildData['futurechannelID']
        else:
            print('No Future Channel found for: ' + guildData['Guild Name'])
            return

        if 'pastchannelID' in guildData:
            pastchannelid = guildData['pastchannelID']
        else:
            print('No Past Channel found for: ' + guildData['Guild Name'])
            return

        pastchannel = self.bot.get_channel(int(pastchannelid))
        futurechannel = self.bot.get_channel(int(futurechannelid))
        if not pastchannel or not futurechannel:
            # guild = self.bot.get_guild(guild_id)
            # await self.run_add_bot_channels(guild)
            print('Channels not in ' + guildData['Guild Name'] + "'s server")
            return

        g = self.bot.get_guild(guild_id)
        bot_member = g.get_member(self.bot.user.id)

        if (bot_member.permissions_in(pastchannel).manage_messages and bot_member.permissions_in(
                pastchannel).read_message_history) or bot_member.permissions_in(pastchannel).administrator:
            try:
                await pastchannel.purge(bulk=False)
            except:
                print('Could not Purge Channel for guild: ' + guildData['Guild Name'])
                return
        else:
            print('Could not Purge Channel for guild: ' + guildData['Guild Name'])
            return

        embed = discord.Embed(
            title="For Information About Older Raids",
            # \U0001F448 POINT LEFT, \U0001F449 POINT RIGHT
            description='\U0001F449 [Click Here](https://www.readyraider.com/dashboard?view=raids) \U0001F448',
            colour=discord.Colour.from_rgb(25, 145, 235)
        )

        if 'Guild Banner' in guildData:
            embed.set_image(url='http:' + guildData['Guild Banner'])

        if not raidData:
            embed.title = "No Confirmed Raids in the Last Week!\n For Information About Older Raids"
            await pastchannel.send(embed=embed)
            return
        await pastchannel.send(embed=embed)
        for raid in reversed(raidData):
            if 'messageID' in raid:
                try:
                    # if the message just moved from future raids to past raids, delete the old message
                    msg = await futurechannel.fetch_message(int(raid['messageID']))
                    await msg.delete()
                    break
                finally:
                    await self.postpastraid(raid, pastchannel, wowServer)
            else:
                await self.postpastraid(raid, pastchannel, wowServer)

    @commands.cooldown(4, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['completed', 'Completed'],
                             description="Displays all raids from the last week and the confirmed attendance.",
                             examples=["completed", "past_raids", "Completed"])
    async def past_raids(self, ctx):
        """
        completed raids commands
        :param ctx:
            discord context
        """
        await self.past_raids_helper(ctx.guild.id)

    @commands.cooldown(2, 600, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @customcommand.c_command(description="Deletes all Raids in the upcoming raids channel from the last X days.",
                             examples=["cleanRaidChannel", "cleanRaidChannel 45"],
                             hidden=True)
    async def cleanRaidChannel(self, ctx, days=30):
        """
        deletes all raids in the upcoming channel to repost them
        :param ctx:
            discord context
        :param days:
            how many days to clear out.
        """

        guild_id = ctx.guild.id
        api_cog = self.bot.get_cog('RR_API')
        guildData = await api_cog.guild_data(guild_id)
        if not guildData:
            return

        wowguildID = guildData['_id']
        futurechannelid = guildData['futurechannelID']

        raidData = await self.get_raid_data(days, wowguildID)
        futurechannel = self.bot.get_channel(int(futurechannelid))

        for raid in raidData:
            if 'messageID' in raid:
                try:
                    # if the message just moved from future raids to past raids, delete the old message
                    msg = await futurechannel.fetch_message(int(raid['messageID']))
                    await msg.delete()
                    break
                except:
                    True

def setup(bot):
    bot.add_cog(Raid(bot))
