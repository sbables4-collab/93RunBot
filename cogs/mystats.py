import discord
from discord.ext import commands

from challenge_db import (
    get_user_stats,
    get_user_rank,
    get_last_workout,
    get_user_streak,
    get_achievements
)


class MyStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mystats")
    async def my_stats(self, ctx):

        stats = get_user_stats(ctx.author.id)

        if stats is None:
            await ctx.send("No stats found.")
            return

        workouts = stats[0] or 0
        runs = stats[1] or 0
        walks = stats[2] or 0
        hikes = stats[3] or 0
        total_minutes = stats[4] or 0

        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        rank = get_user_rank(ctx.author.id)
        last = get_last_workout(ctx.author.id)
        streak = get_user_streak(ctx.author.id)
        badges = len(get_achievements(ctx.author.id))

        embed = discord.Embed(
            title="🏃 93RUN July Grind Stats",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        embed.add_field(
            name="🏃 Runs",
            value=str(runs),
            inline=True
        )

        embed.add_field(
            name="🚶 Walks",
            value=str(walks),
            inline=True
        )

        embed.add_field(
            name="🥾 Hikes",
            value=str(hikes),
            inline=True
        )

        embed.add_field(
            name="📸 Verified Workouts",
            value=str(workouts),
            inline=True
        )

        embed.add_field(
            name="⏱ Total Time",
            value=f"{total_hours}h {remaining_minutes}m",
            inline=True
        )

        embed.add_field(
            name="🏆 Rank",
            value=f"#{rank}" if rank else "Unranked",
            inline=True
        )

        if last:

            activity = last[0]
            hours = last[1]
            minutes = last[2]

            embed.add_field(
                name="🔥 Last Workout",
                value=f"{activity}\n{hours}h {minutes}m",
                inline=False
            )

        embed.add_field(
            name="🏅 Badges",
            value=str(badges),
            inline=True
        )

        if streak == 0:
            streak_text = "Start your streak! 💪"
        elif streak == 1:
            streak_text = "1 Day 🔥"
        else:
            streak_text = f"{streak} Days 🔥"

        embed.add_field(
            name="🔥 Current Streak",
            value=streak_text,
            inline=True
        )

        embed.set_footer(
            text="Keep Grinding 🖤 • 93RUN"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MyStats(bot))