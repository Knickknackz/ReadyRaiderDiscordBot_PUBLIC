import discord
import requests
from discord.ext import commands
from cogs.utils import customcommand
from urllib.parse import quote


class Nexushub(commands.Cog):
    """
    This class implements bot's Nexushub Commands
    """

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def convertCurrency(num):
        """
        converts a number to Warcraft Currency
        :param num:
            the raw number
        :return:
            a string that represents to currency
        <:Gold:740110014164762644>
        <:Silver:740110030430273537>
        <:Copper:740110042627571754>
        """
        num = int(num)
        copper = num % 100
        num = num // 100
        silver = num % 100
        gold = num // 100
        result = ''
        if gold != 0:
            result += str(gold) + '<:Gold:740110014164762644> \u200b '
        if silver != 0:
            result += str(silver) + '<:Silver:740110030430273537> \u200b '
        if copper != 0:
            result += str(copper) + '<:Copper:740110042627571754>'

        return result

    @customcommand.c_command(aliases=['CraftingDeals', 'Craftingdeals', 'craftingdeals'],
                             description="Displays useful data about an item.",
                             examples=['craftingDeals', 'CraftingDeals'])
    @commands.Cog.listener()
    async def craftingDeals(self, ctx):
        """
        posts NexusHub's Crafting Deals to Discord
        :param ctx:
            discord context
        """

        s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
        r = requests.get(self.bot.guildAPI + s)
        guild = r.json()['response']['results']

        if not guild:
            print('WarcraftLogs Error, guildLogs')
            return

        guild = guild[0]

        server_data = guild['Guild Server']
        server_data = server_data.split()
        serverName = server_data[0].lower()
        faction = guild['Guild Faction'].lower()
        if not serverName or not faction:
            await ctx.send("Error! Either faction or server is corrupt in database")
            return

        fullServerName = serverName + '-' + faction

        s = 'crafting/' + fullServerName + '/deals'
        r = requests.get(self.bot.nexusHubAPI + s)
        deals = r.json()

        embed = discord.Embed(
            title="Today's Crafting Deals",
            description='**Server:** ' + serverName.capitalize() + '\n**Faction:** ' + faction.capitalize(),
            colour=discord.Colour.from_rgb(25, 145, 235)
        )
        embed.add_field(name="\u200b",
                        value="Data pulled from [NexusHub](https://nexushub.co/).",
                        inline=False)

        await ctx.send(embed=embed)
        count = 0
        iconURL = 'https://wow.zamimg.com/images/wow/icons/large/'
        for deal in deals:
            count += 1
            name = deal['name']
            category = deal['category']
            requiredSkill = deal['requiredSkill']
            icon = deal['icon']
            profit = deal['profit']
            itemProfit = deal['itemProfit']
            createdByCosts = deal['createdByCosts']
            embed = discord.Embed(
                title='`' + str(count) + '`: ' + name,
                description='**Requires:** ' + str(requiredSkill) + '/300 ' + category +
                            '\n**Estimated Mats Cost:** ' + self.convertCurrency(createdByCosts) +
                            '\n**Estimated Sale:** ' + self.convertCurrency(itemProfit) +
                            '\n**Estimated Profit:** ' + self.convertCurrency(profit),
                colour=discord.Colour.from_rgb(25, 145, 235))
            embed.set_thumbnail(url=iconURL + icon + '.jpg')
            await ctx.send(embed=embed)

    @customcommand.c_command(aliases=['Deals'],
                             description="Displays useful data about an item.",
                             examples=['deals', 'Deals'])
    @commands.Cog.listener()
    async def deals(self, ctx):
        """
        Posts NexusHub's Auction Deals to Discord
        :param ctx:
            discord context
        """
        s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
        r = requests.get(self.bot.guildAPI + s)
        guild = r.json()['response']['results']

        if not guild:
            print('WarcraftLogs Error, guildLogs')
            return

        guild = guild[0]

        server_data = guild['Guild Server']
        server_data = server_data.split()
        serverName = server_data[0].lower()
        faction = guild['Guild Faction'].lower()
        if not serverName or not faction:
            await ctx.send("Error! Either faction or server is corrupt in database")
            return

        fullServerName = serverName + '-' + faction

        s = 'items/' + fullServerName + '/deals'
        r = requests.get(self.bot.nexusHubAPI + s)
        deals = r.json()

        embed = discord.Embed(
            title="Today's Deals",
            description='**Server:** ' + serverName.capitalize() + '\n**Faction:** ' + faction.capitalize(),
            colour=discord.Colour.from_rgb(25, 145, 235)
        )
        embed.add_field(name="\u200b",
                        value="Data pulled from [NexusHub](https://nexushub.co/). This data reflect their most recent "
                              "market values.",
                        inline=False)
        await ctx.send(embed=embed)
        count = 0
        iconURL = 'https://wow.zamimg.com/images/wow/icons/large/'
        for deal in deals:
            count += 1
            marketValue = deal['marketValue']
            minBuyout = deal['minBuyout']
            name = deal['name']
            icon = deal['icon']
            dealDiff = deal['dealDiff']
            dealPercent = round(deal['dealPercentage'] * 100, 1)
            embed = discord.Embed(
                title='`' + str(count) + '`: ' + name,
                description='**Market Value:** ' + self.convertCurrency(marketValue) +
                            '\n**Min Buyout:** ' + self.convertCurrency(minBuyout) +
                            '\n**Deal Diff:** ' + self.convertCurrency(dealDiff) + ' / ' + str(dealPercent) + '%\n ',
                colour=discord.Colour.from_rgb(25, 145, 235))
            embed.set_thumbnail(url=iconURL + icon + '.jpg')
            await ctx.send(embed=embed)

    @customcommand.c_command(aliases=['Item'],
                             description="Displays useful data about an item.",
                             examples=['item black lotus', 'Item Dark Edge of Insanity'])
    @commands.Cog.listener()
    async def item(self, ctx, *, item):
        """
        Shows Data for a given Warcraft Item
        :param ctx:
            discord context
        :param item:
            item name
        """
        itemName = item.lower()
        itemName = quote(itemName)

        s = 'search?query=' + itemName
        r = requests.get(self.bot.nexusHubAPI + s)
        searchData = r.json()
        if searchData:
            itemId = str(searchData[0]['itemId'])
        else:
            await ctx.send('Item Not Found')
            return

        s = 'item/' + itemId
        r = requests.get(self.bot.nexusHubAPI + s)
        itemData = r.json()
        iconURL = itemData['icon']

        description = ''
        title = itemData['name']
        for row in itemData['tooltip']:
            label = row['label']
            if label == title:
                continue
            elif label == 'Sell Price:':
                description += 'Vendor Price: ' + self.convertCurrency(itemData['sellPrice']) + '\n'
            else:
                description += label + '\n'

        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.from_rgb(25, 145, 235)
        )
        embed.set_thumbnail(url=iconURL)
        embed.add_field(name="\u200b",
                        value="Data pulled from [NexusHub](https://nexushub.co/).",
                        inline=False)
        await ctx.send(embed=embed)

    # Optional addition of cooldown for the command
    # @commands.cooldown(10, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['Price', 'auction', 'Auction'],
                             description="searches for the current price of an item",
                             examples=['price black lotus', 'Auction Runecloth'])
    @commands.Cog.listener()
    async def price(self, ctx, *, item):
        """
        Auction data for an item
        :param ctx:
            discord context
        :param item:
            item name
        """
        itemName = item.lower()
        itemName = quote(itemName)

        s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
        r = requests.get(self.bot.guildAPI + s)
        guild = r.json()['response']['results']

        if not guild:
            print('WarcraftLogs Error, guildLogs')
            return

        guild = guild[0]

        server_data = guild['Guild Server']
        server_data = server_data.split()
        serverName = server_data[0].lower()
        faction = guild['Guild Faction'].lower()
        if not serverName or not faction:
            await ctx.send("Error! Either faction or server is corrupt in database")
            return

        fullServerName = serverName + '-' + faction

        s = 'search?query=' + itemName
        r = requests.get(self.bot.nexusHubAPI + s)
        searchData = r.json()
        if searchData:
            itemId = str(searchData[0]['itemId'])
        else:
            await ctx.send('Item Not Found')
            return

        s = 'item/' + itemId
        r = requests.get(self.bot.nexusHubAPI + s)
        itemData = r.json()
        iconURL = itemData['icon']

        s = 'items/' + fullServerName + '/' + itemId
        r = requests.get(self.bot.nexusHubAPI + s)
        itemsData = r.json()
        stats = itemsData['stats']

        if not stats['current']:
            await ctx.send('No Auction Data Found on ' + itemsData['name'])
            return
        else:
            marketValue = int(stats['current']['marketValue'])
            minBuyout = int(stats['current']['minBuyout'])
            historicalValue = int(stats['current']['historicalValue'])
            quantity = int(stats['current']['quantity'])

            if minBuyout != 0:
                ratio = marketValue / minBuyout
                percent = int(100 * (ratio - 1))
                if percent >= 0:
                    profit_percent = '+' + str(percent) + '%'
                else:
                    profit_percent = str(percent) + '%'
            diff = marketValue - minBuyout

            embed = discord.Embed(
                title='Auction Data for ' + itemData['name'],
                description='**Server:** ' + serverName.capitalize() + '\n**Faction:** ' + faction.capitalize() + '\n**Quantity:** ' + str(
                    quantity),
                colour=discord.Colour.from_rgb(25, 145, 235)
            )

            embed.add_field(
                name='Current Market Value',
                value=self.convertCurrency(marketValue),
                inline=True)

            if minBuyout != 0:
                embed.add_field(
                    name='Current Min Buyout',
                    value=self.convertCurrency(minBuyout),
                    inline=True)

            embed.add_field(
                name='Historical Market Value',
                value=self.convertCurrency(historicalValue),
                inline=True)
            if minBuyout != 0:
                diff_str = self.convertCurrency(diff)
                if diff_str[0] != '-':
                    diff_str = '+' + diff_str
                embed.add_field(
                    name='Potential Profit (Current Market vs Current Min Buyout)',
                    value=diff_str + ' / ' + profit_percent,
                    inline=False)

            embed.set_thumbnail(url=iconURL)
            embed.add_field(name="\u200b",
                            value="Data pulled from [NexusHub](https://nexushub.co/). This data reflect their most recent market values.",
                            inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Nexushub(bot))


"""
Some personal Notes about the NexusHub API

Step 2)

<API> item/13468
- Info
- Tooltip
- etc.

Step 3)
<API> blaumeux-horde/13468/prices

"""
