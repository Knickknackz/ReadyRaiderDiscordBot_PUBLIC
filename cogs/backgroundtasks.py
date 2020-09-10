import asyncio
import asyncpg
from datetime import datetime

from discord.ext import commands, tasks


class Background(commands.Cog):
    """
    This class impelements tasks that are run periodically on the background

    Attributes
    ----------
    bot
    last_clear
        The last time when events were autocleared.
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_clear = self.get_time()
        self.back_tasks.start()
        self.back_tasks.add_exception_type(asyncpg.PostgresConnectionError)

    @tasks.loop(minutes=60)
    async def back_tasks(self):
        """
        A task every 60 minutes that updates Discord Servers
        """
        raid_cog = self.bot.get_cog('Raid')
        print('Upcoming_Raid UPDATE STARTED at ' + str(datetime.utcnow()))

        # ADDS NEW UPCOMING RAIDS.
        upcoming_list = []
        c = 0
        for guild in self.bot.guilds:
            c += 1
            upcoming_list.append(raid_cog.upcoming_raids_helper(guild.id))
        print('Bot is in ' + str(c) + ' Servers')
        await asyncio.gather(*upcoming_list)
        print('Upcoming_Raid UPDATE COMPLETE at ' + str(datetime.utcnow()))

        # Updates Completed Raids at 1:30 every day (Once a Day)
        h = int(datetime.utcnow().hour)
        m = int(datetime.utcnow().minute)
        if h == 1 and m == 30:
            print('Completed_Raid UPDATE STARTED at ' + str(datetime.utcnow()))
            upcoming_list = []
            for guild in self.bot.guilds:
                upcoming_list.append(raid_cog.past_raids_helper(guild.id))
            await asyncio.gather(*upcoming_list)
            print('Completed_Raid UPDATE COMPLETE at ' + str(datetime.utcnow()))

    #            CODE FOR LOOT UPDATES
    #            loot_cog = self.bot.get_cog('Loot')
    #            for guild in self.bot.guilds:
    #                loot_list.append(loot_cog.loot_helper(guild, 1))
    #            await asyncio.gather(*loot_list)

    @back_tasks.before_loop
    async def before_tasks(self):
        """
        Waits decorated tasks to from starting before bot is ready
        """
        print('Starting...')
        await self.bot.wait_until_ready()

    @staticmethod
    def get_time():
        """
        Gets current week day and hour in hours

        Returns
        -------
        Time in hours
        """

        weekday = datetime.utcnow().weekday()
        hour = datetime.utcnow().hour

        time_hours = weekday * 24 + hour

        return time_hours


def setup(bot):
    bot.add_cog(Background(bot))
