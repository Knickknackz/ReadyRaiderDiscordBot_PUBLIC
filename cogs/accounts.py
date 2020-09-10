import discord
import requests

from urllib.parse import quote
from discord.ext import commands
from cogs.utils import customcommand
from cogs.utils.globalfunctions import search_format


class Account(commands.Cog):
    """
    This contains the control of listening for Account Management
    """

    def __init__(self, bot):
        self.bot = bot

    # @commands.cooldown(2, 600, commands.BucketType.guild)
    @customcommand.c_command(aliases=['Invite'],
                             description="Invites a User to Join ReadyRaider",
                             examples=["Invite [email] [wowName]", "invite examplemail@gmail.com Sodapoppin"])
    @commands.Cog.listener()
    async def invite(self, ctx, email=None, wowName=None):
        """
        emails target with instructions on how to set up their account
        immediately deletes the message to hide the email address
        :param ctx:
            context
        :type email: str
            email of target user
        :type wowName: str
            Warcraft Character Name of target user
        """
        if not email or not wowName:
            await ctx.message.delete()
            await ctx.send("Error! Missing Variables")
            return
        print(email + ',' + wowName)
        guild_id = ctx.guild.id
        headers = {"Authorization": "Bearer " + self.bot.api_key}
        body = {"name": str(wowName), "discordid": str(guild_id), "email": email}
        requests.post(self.bot.inviteAPI, data=body, headers=headers)

        await ctx.message.delete()

        embed = discord.Embed(title="Success!",
                              description=wowName + "has been invited to join your guild. If this user already exists "
                                                    "in our database they will need to join manually on our web app.")
        embed.set_thumbnail(url='https://img.icons8.com/fluent/48/000000/new-contact.png')
        await ctx.send(embed=embed)

    @customcommand.c_command(aliases=['Register'],
                             description="Register _Yourself_ for ReadyRaider. Auto-Deletes the Post to Hide Emails.",
                             examples=["register [email] [wowName] [wowClass]",
                                       "Register myemail@gmail.com Barrymanalow Mage"])
    @commands.Cog.listener()
    async def register(self, ctx, email=None, wowName=None, wowClass=None):
        """
        registers yourself for ReadyRaider. Uses Discord ID of the user that posts this.
        :param ctx:
            context of action
        :param email:
            your own email address
        :param wowName:
            Your Warcraft Character Name
        :param wowClass:
            Your Class in Wow
        :return:
        """
        if not email or not wowName or not wowClass:
            await ctx.message.delete()
            await ctx.send("Error! Missing Variables")
            return

        classes = {"Druid", "Hunter", "Mage",
                   "Paladin", "Priest", "Rogue",
                   "Shaman", "Warlock", "Warrior"}

        if wowClass not in classes:
            await ctx.message.delete()
            await ctx.send("Error! Wow Classic Class Not Valid:\n (Spelling or Capitalization) ie. Rogue")
            return
        discord_full = quote(ctx.author.name + ' #' + ctx.author.discriminator)

        s = search_format('DiscordID', 'equals', discord_full)
        s = "".join(str(s).split())
        r = requests.get(self.bot.discordAPI + '?constraints=[' + s + ']')
        userData = r.json()['response']['results']

        if userData:
            await ctx.send('Error! User Already Has an Account!')
            return

        discordname = ctx.author.name + ' #' + str(ctx.author.discriminator)
        guild_id = ctx.guild.id
        headers = {"Authorization": "Bearer " + self.bot.api_key}
        body = {
            "discordname": discordname,
            "discordid": str(guild_id),
            "email": email,
            "name": wowName,
            "class": wowClass
        }
        requests.post(self.bot.signupAPI, data=body, headers=headers)

        await ctx.message.delete()

        # https://img.icons8.com/fluent/48/000000/new-contact.png   <-NEW CONTACT LINK
        embed = discord.Embed(title="Success!",
                              description=wowName + " has been invited to join your guild. \nPlease Tell Them to Check Their Email.\nIf this user already exists in our database they will need to join manually on our web app.")
        embed.set_thumbnail(url='https://img.icons8.com/fluent/48/000000/new-contact.png')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Account(bot))
