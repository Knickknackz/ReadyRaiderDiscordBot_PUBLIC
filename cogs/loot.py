import discord
import datetime
import requests
from datetime import datetime, timedelta

from cogs.utils.globalfunctions import search_format
from discord.ext import commands
from cogs.utils import customcommand


class Loot(commands.Cog):
    """
    This contains the control of listening for the loot call and embeding it
    """

    def __init__(self, bot):
        self.bot = bot

    async def loot_helper(self, guild, days):
        """
        posts the loot to the lootchannel
        :param guild:
            instance of Discord Server
        :param days:
            which day should we target?
        """
        loot_api = self.bot.lootAPI
        API_cog = self.bot.get_cog('RR_API')

        guildData = await API_cog.guild_data(guild.id)

        if not guildData:
            return

        lootChannel = self.bot.get_channel(int(guildData['lootchannelID']))

        if not lootChannel:
            raid_cog = self.bot.get_cog('Raid')
            await raid_cog.run_add_bot_channels(guild)
            return

        t = datetime.today()

        dt = datetime.combine(t, datetime.min.time())
        greater = (dt - timedelta(days=days))
        lesser = (greater + timedelta(days=1))
        s = '[' + search_format('Guild Delivered', 'equals', guildData['_id']) + ","
        s += search_format("Created Date", "greater%20than", greater.isoformat()) + ","
        s += search_format("Created Date", "less%20than", lesser.isoformat()) + ']'
        s = "".join(str(s).split())

        r = requests.get(loot_api + '?constraints=' + s)
        lootData = r.json()['response']['results']

        # Functionality if we want Today/Yesterday instead of the date all the time
        """
        if days == 0:
            dt_out = 'Today'
        elif days == 1:
            dt_out = 'Yesterday'
        else:
            dt_out = 'on ' + greater.strftime("%A, %B %d")
        """
        dt_out = 'on ' + greater.strftime("%A, %B %d")

        embed = discord.Embed(
            title=guildData['Guild Name'] + "'s Loot " + dt_out,
            colour=discord.Colour.from_rgb(25, 145, 235),
            timestamp=datetime.utcnow()
        )

        # Probably want a better image
        embed.set_thumbnail(url='https://img.icons8.com/fluent/48/000000/armored-breastplate.png')
        c = 0
        part = 1
        if lootData:
            for l in lootData:
                if c == 18:
                    embed.set_footer(text='**Part ' + str(part) + '**')
                    await lootChannel.send(embed=embed)
                    part += 1
                    c = 0
                    embed = discord.Embed(
                        title=guildData['Guild Name'] + "'s Loot " + dt_out,
                        colour=discord.Colour.from_rgb(25, 145, 235),
                        timestamp=datetime.utcnow()
                    )
                if 'RecipientText' in l:
                    recipient = l['RecipientText']
                else:
                    recipient = 'NoNameFound'
                embed.add_field(name=l['Loot Name'],
                                value=recipient + ' for ' + str(l['Loot Item Worth']) + ' Pts',
                                inline=True)
                c += 1
            # Adds Empty Fields for formatting
            if c % 3 != 0:
                for i in range(3 - (c % 3)):
                    embed.add_field(name='\u200b',
                                    value='\u200b',
                                    inline=True)
        else:
            embed.description = 'Sorry, No Loot Found in this Window!'

        if part == 1:
            await lootChannel.send(embed=embed)
        else:
            embed.set_footer(text='**Part ' + str(part) + '**')
            await lootChannel.send(embed=embed)

    @commands.cooldown(3, 600, commands.BucketType.guild)
    @customcommand.c_command(description="Displays all loot from the day that was X days ago, default = 0(Today).",
                             examples=["loot", "loot 3 (3 days ago)", "loot 1  (Yesterday)"])
    @commands.Cog.listener()
    async def loot(self, ctx, *, days=0):
        """
        $loot command
        :param ctx:
            discord context
        :param days:
            which day to target
        """
        guild = ctx.guild
        if type(days) == int:
            await self.loot_helper(guild, days)

    # optional cooldown
    # @commands.cooldown(2, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['priority', 'Prio', 'Priority'],
                             description="Displays Recommended Class Priority for an Item\n *Case Sensative!*",
                             examples=["prio Chromatically Tempered Sword", "Priority Azuresong Mageblade"])
    @commands.Cog.listener()
    async def prio(self, ctx, *, item=None):
        """
        displays item prio info for a chosen item
        :param ctx:
            discord context
        :param item:
            the targetted item
        """
        if not item:
            await ctx.send("Please enter an item!")
            return

        s = "[" + search_format("Item Name", "equals", item) + "]"
        r = requests.get(self.bot.wowheadAPI + "?constraints=" + s)
        itemData = r.json()['response']['results']

        if not itemData:
            await ctx.send("Sorry, item Not Found")
            return
        itemData = itemData[0]

        priotext = ''
        if "Prio 1" in itemData:
            priotext += 'Prio 1: ' + itemData['Prio 1']
        if "Prio 2" in itemData:
            priotext += '\nPrio 2: ' + itemData['Prio 2']
        if "Prio 3" in itemData:
            priotext += '\nPrio 3: ' + itemData['Prio 3']

        embed = discord.Embed(title='Prio Info on ' + item,
                              colour=discord.Colour.from_rgb(25, 145, 235),
                              )

        if "Drop Location" in itemData:
            embed.add_field(name='Drop Location: ', value=itemData['Drop Location'], inline=False)
        if "Item Type" in itemData:
            embed.add_field(name='Item Type: ', value=itemData['Item Type'], inline=True)
        if "Item Slot" in itemData:
            embed.add_field(name='Item Slot: ', value=itemData['Item Slot'], inline=True)
        embed.add_field(name='Recommended Class Priority', value=priotext, inline=False)
        embed.add_field(name='\u200b', value="\U0001F440 [See Item Details Here](" + itemData["Item URL"] + ")",
                        inline=False)
        embed.set_thumbnail(url='https://img.icons8.com/fluent/48/000000/low-priority.png')
        embed.set_footer(text='For Complete Item Priority Lists, Go to ReadyRaider.com')
        await ctx.send(embed=embed)

    # Optional cooldown for command
    # @commands.cooldown(2, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['wish', 'Wish', 'Wishlist'],
                             description="Displays Wishlist for Target Character\n *Case Sensative!*",
                             examples=["wish Asmongold", "Wishlist Jokerd"])
    @commands.Cog.listener()
    async def wishlist(self, ctx, *, name=None):
        """
        displays the wishlist for a target character
        :param ctx:
            discord context
        :param name:
            name of target
        """
        if not name:
            await ctx.send("Please Enter a Character Name!")
            return

        s = "[" + search_format("WoWChar", "equals", name) + "]"
        r = requests.get(self.bot.discordAPI + "?constraints=" + s)
        characterData = r.json()['response']['results']

        if not characterData:
            await ctx.send("Sorry, Target User Isn't Linked to Discord! (Also check spelling, it's case sensetive)")
            return

        characterData = characterData[0]
        id = characterData['UserID']

        s = "[" + search_format("List Owner", "equals", str(id)) + "]"
        r = requests.get(self.bot.wishlistAPI + "?constraints=" + s)
        wishData = r.json()['response']['results']

        if not wishData:
            await ctx.send("Sorry, Wishlist Not Found!")
            return
        wishData = wishData[0]

        wishtext = ''
        if "Item 1" in wishData:
            wishtext += '1: ' + wishData['Item 1']
        if "item 2" in wishData:
            wishtext += '\n2: ' + wishData['item 2']
        if "item 3" in wishData:
            wishtext += '\n3: ' + wishData['item 3']
        if "item 4" in wishData:
            wishtext += '\n4: ' + wishData['item 4']
        if "item 5" in wishData:
            wishtext += '\n5: ' + wishData['item 5']

        embed = discord.Embed(title=name + "'s Wishlist",
                              description=wishtext,
                              colour=discord.Colour.from_rgb(25, 145, 235),
                              )
        embed.set_thumbnail(url='https://img.icons8.com/fluent/96/000000/wish-list.png')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Loot(bot))
