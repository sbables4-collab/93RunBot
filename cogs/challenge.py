import discord
from discord.ext import commands

from cogs.views import ChallengeView


class Challenge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def challenge(self, ctx):

        embed = discord.Embed(
            title="🔥 93RUN July Grind",
            description=(
                "**July 18 – July 31**\n\n"
                "Click the button below to begin logging your workouts!"
            ),
            color=discord.Color.blue()
        )

        await ctx.send(
            embed=embed,
            view=ChallengeView(self.bot)
        )


async def setup(bot):
    print("🔥 Loading Challenge Cog...")
    await bot.add_cog(Challenge(bot))
    print("✅ Challenge Cog Loaded!")