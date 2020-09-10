import discord
import datetime
import requests
from datetime import datetime

from discord.ext import commands
from cogs.utils import customcommand
from cogs.utils import timezones
from urllib.parse import quote


class WarcraftLogs(commands.Cog):
    """
    This contains the calls related to the website WarcraftLogs
    """

    def __init__(self, bot):
        self.bot = bot

    # Option to add a cooldown to the command
    # @commands.cooldown(2, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['Logs', 'warcraftlogs', 'Warcraftlogs'],
                             description="Displays Rankings for a character\n"
                                         "Regions are in the format: US, EU, KR, TW, CN.",
                             examples=["logs Esfand Faerlina US", "warcraftlogs asmon faerlina us"])
    @commands.Cog.listener()
    async def logs(self, ctx, characterName=None, serverName=None):
        """
        Posts logs from a given character
        :param ctx:
            discord context
        :param characterName:
            Warcraft name of a character, required
        :param serverName:
            either defaults to your Wow Guild's server or the inputted one
        """
        if not characterName:
            await ctx.send('Please Input a Character Name:\n'
                           '$logs "Character Name"')
            return

        if not serverName:
            s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
            r = requests.get(self.bot.guildAPI + s)
            guild = r.json()['response']['results']

            if not guild:
                print('WarcraftLogs Error, guildLogs')
                return

            guild = guild[0]

            server_data = guild['Guild Server']
            server_data = server_data.split()
            serverName = server_data[0]

        if serverName.lower() == "sul'thraze":
            serverName = 'sulthraze'
        elif serverName.lower() == "rhok'delar":
            serverName = 'rhokdelar'
        elif serverName.lower() == "dragon's call":
            serverName = "dragons call"

        if serverName.lower() in timezones.servers:
            serverRegion = timezones.servers[serverName.lower()]
        else:
            await ctx.send('Error! Please Check Server Spelling!')
            print('WarcraftLogs Error, guildLogs')
            return

        if not characterName or not serverName or not serverRegion:
            await ctx.send('Error! One or More Variables were empty!')
            return

        r = requests.get("https://classic.warcraftlogs.com:443/v1/rankings/character/{}/{}/{}"
                         .format(characterName, "-".join(serverName.split()), serverRegion) + '?api_key=' +
                         self.bot.warcraftLogs_api_key)
        if r.status_code != 200:
            await ctx.send('Error! Data could not be found')
            return

        rankData = r.json()
        if not rankData:
            await ctx.send('Error! No Data for this Character')
            return

        embed = discord.Embed(
            title=characterName + "'s Best Rankings",
            description='Server: ' + serverName,
            colour=discord.Colour.from_rgb(25, 145, 235),
            timestamp=datetime.utcnow()
        )
        for boss in rankData:
            if boss['spec'] == 'Healer':
                embed.add_field(
                    name=boss['encounterName'],
                    value="Rank: " + str(boss['rank']) + '/' + str(boss['outOf']) + "\n" + boss[
                        'spec'] + " Percentile: " + str(round(boss['percentile'], 1)) + "%"
                )
            else:
                embed.add_field(
                    name=boss['encounterName'],
                    value="Rank: " + str(boss['rank']) + '/' + str(boss['outOf']) + "\n" + boss[
                        'spec'] + " Percentile: " + str(round(boss['percentile'], 1)) + "%\n" + "DPS: " + str(
                        boss['total'])
                )

        embed.set_thumbnail(url="https://img.icons8.com/fluent/48/000000/define-location.png")
        embed.set_footer(
            text="Rankings pulled from Warcraftlogs. These rankings reflect this player's best parses compared to "
                 "today's best performances")
        await ctx.send(embed=embed)

    # @commands.cooldown(2, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['Gear'],
                             description="Displays Gear for a Character",
                             examples=["gear Mcconnell faerlina", "Gear Madseason faerlina"])
    @commands.Cog.listener()
    async def gear(self, ctx, characterName=None, serverName=None):
        """
        posts Gear the targetted character uses
        :param ctx:
            discord context
        :param characterName:
            Warcraft Character Name
        :param serverName:
            Warcraft Server Name, Defaults to Guild's Server if Empty
        """

        if not characterName:
            await ctx.send('Please Input a Character Name:\n'
                           '"$gear [character name]"')
            return

        if not serverName:
            s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
            r = requests.get(self.bot.guildAPI + s)
            guild = r.json()['response']['results']

            if not guild:
                print('WarcraftLogs Error, guildLogs')
                return

            guild = guild[0]

            server_data = guild['Guild Server']
            server_data = server_data.split()
            serverName = server_data[0]

        if serverName.lower() == "sul'thraze":
            serverName = 'sulthraze'
        elif serverName.lower() == "rhok'delar":
            serverName = 'rhokdelar'
        elif serverName.lower() == "dragon's call":
            serverName = "dragons call"

        if serverName.lower() in timezones.servers:
            serverRegion = timezones.servers[serverName.lower()]
        else:
            await ctx.send('Error! Please Check Server Spelling!')
            print('WarcraftLogs Error, guildLogs')
            return

        r = requests.get("https://classic.warcraftlogs.com:443/v1/rankings/character/{}/{}/{}"
                         .format(characterName, '-'.join(serverName.split()), serverRegion) + '?api_key=' +
                         self.bot.warcraftLogs_api_key)
        if r.status_code != 200:
            await ctx.send('Error! Data Could not be Found, Please Check Spelling')
            return
        rankData = r.json()
        if not rankData:
            await ctx.send('Error! No Data for This Character')
            return

        gear = [[] for _ in range(18)]

        slots = ['Helm ', 'Neck', 'Shoulders', 'Shirt', 'Chest', 'Waist', 'Legs', 'Feet', 'Wrists', 'Hands', 'Rings',
                 'Trinkets', 'Back', 'MainHand', 'OffHand', 'Ranged']

        slotemojis = ['<:head:728346680407097375>', '<:neck:728346750850433036>', '<:shoulder:728346856387641505>',
                      '<:shirtslot:728346835718111402>', '<:chest:728346572647301223>', '<:waist:728346896837640202>',
                      '<:legs:728346701173096518>', '<:boots:728346594109423747>', '<:wrists:728346919495270492>',
                      '<:hands:728346656579256330>', '<:finger:728346613881241606>', '<:trinket:728346877548036217>',
                      '<:cloak:728346519706533929>', '<:mainhand:728346727568113755>', '<:offhand:728346794907402351>',
                      '<:ranged:728346776049811466>']

        for boss in rankData:
            slot = 0
            for item in boss['gear']:
                if item["name"] != "Unknown Item":
                    if item['name'] not in gear[slot]:
                        gear[slot].append(item['name'])
                slot += 1
        # gearURL = 'https://wow.zamimg.com/images/wow/icons/large/'
        embed = discord.Embed(title=characterName + "'s Gear",
                              description="A List of Gear Used in the Best Parses From " + characterName,
                              timestamp=datetime.utcnow())

        in_first = set(gear[10])
        in_second = set(gear[11])
        in_second_but_not_in_first = in_second - in_first
        gear[10] = gear[10] + list(in_second_but_not_in_first)

        in_first = set(gear[12])
        in_second = set(gear[13])
        in_second_but_not_in_first = in_second - in_first
        gear[12] = gear[12] + list(in_second_but_not_in_first)

        del gear[13]
        del gear[11]

        for slot, items in enumerate(gear):
            if items:
                itemstring = ''
                for item in items:
                    itemstring += item + '\n'
                embed.add_field(name=slotemojis[slot] + slots[slot], value=itemstring + '\u200b', inline=True)

        embed.set_thumbnail(url="https://img.icons8.com/fluent/48/000000/armored-breastplate.png")
        embed.set_footer(
            text="Gear is Pulled From Warcraftlogs. This is the Gear Used During " + characterName +
                 "'s Best Parses, Not Necessarily Current Gear")
        await ctx.send(embed=embed)

    @customcommand.c_command(aliases=['Guildlogs'],
                             description='Displays Recent Logs From a Guild\n *If guilds are longer then one word, '
                                         'please use quotation marks:* "Guild Name"',
                             examples=['Guildlogs ONSLAUGHT Skeram", "guildlogs "SALAD BAKERS" gehennes'])
    @commands.Cog.listener()
    async def guildlogs(self, ctx, guildName=None, serverName=None):
        """
        Posts links to the guild's WarcraftLogs
        :param ctx:
            Discord Context
        :param guildName:
            Target Guilds Name, Defaults to Current Guild if Empty
        :param serverName:
            Target Servers Name, Defaults to Current Guild's Server if Empty
        """
        if not serverName and not guildName:
            s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
            r = requests.get(self.bot.guildAPI + s)
            guild = r.json()['response']['results']

            if not guild:
                print('WarcraftLogs Error, guildLogs')
                return

            guild = guild[0]

            guildName = guild['Guild Name']
            server_data = guild['Guild Server']
            server_data = server_data.split()
            serverName = server_data[0]

        elif not serverName:
            s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
            r = requests.get(self.bot.guildAPI + s)
            guild = r.json()['response']['results']

            if not guild:
                print('WarcraftLogs Error, guildLogs')
                return

            guild = guild[0]

            server_data = guild['Guild Server']
            server_data = server_data.split()
            serverName = server_data[0]

        if serverName.lower() == "sul'thraze":
            serverName = 'sulthraze'
        elif serverName.lower() == "rhok'delar":
            serverName = 'rhokdelar'
        elif serverName.lower() == "dragon's call":
            serverName = "dragons call"

        if serverName.lower() in timezones.servers:
            serverRegion = timezones.servers[serverName.lower()]
        else:
            await ctx.send('Server Error')
            print('WarcraftLogs Error, guildLogs')
            return

        r = requests.get("https://classic.warcraftlogs.com:443/v1/reports/guild/{}/{}/{}".format(guildName, '-'.join(
            serverName.split()), serverRegion) + '?api_key=' + self.bot.warcraftLogs_api_key)

        if r.status_code != 200:
            await ctx.send('Error! Data Could not be Found, Please Check Spelling')
            return

        guildlogData = r.json()
        if not guildlogData:
            await ctx.send('Error! No Data for This Guild')
            return

        l = min(len(guildlogData), 5)
        guildlogData = guildlogData[:l]

        embed = discord.Embed(title=guildName + "'s Last " + str(l) + " Logs",
                              description="For a Look at All Raids From " + guildName +
                                          " [Click Here](https://classic.warcraftlogs.com/guild/{}/{}/{}".format(
                                           serverRegion, '-'.join(serverName.split()), quote(guildName)) + ')',
                              timestamp=datetime.utcnow())
        for log in guildlogData:
            timestamp = datetime.fromtimestamp(log['start'] / 1000)
            timestamp = timestamp.strftime('%m/%d/%Y')
            embed.add_field(name=log['owner'] + "'s " + log['title'],
                            value='[' + timestamp + '](https://classic.warcraftlogs.com/reports/' + log['id'] + ')',
                            inline=False)

        embed.set_thumbnail(url="https://img.icons8.com/fluent/48/000000/today.png")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(WarcraftLogs(bot))
