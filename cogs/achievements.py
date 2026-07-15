import discord
from discord.ext import commands

from challenge_db import (
    get_user_stats,
    give_achievement,
    get_achievements
)


class AchievementEngine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def check_achievements(self, user):

        stats = get_user_stats(user.id)

        if not stats:
            return

        workouts = stats[0] or 0
        runs = stats[1] or 0
        walks = stats[2] or 0
        hikes = stats[3] or 0
        total_minutes = stats[4] or 0

        unlocked = []

        # ==========================================
        # WORKOUT ACHIEVEMENTS
        # ==========================================

        if workouts >= 1:
            if give_achievement(user.id, "🥇 First Workout"):
                unlocked.append("🥇 First Workout")

        # ==========================================
        # RUN ACHIEVEMENTS
        # ==========================================

        if runs >= 5:
            if give_achievement(user.id, "🏃 5 Runs"):
                unlocked.append("🏃 5 Runs")

        if runs >= 10:
            if give_achievement(user.id, "🏃 10 Runs"):
                unlocked.append("🏃 10 Runs")

        if runs >= 25:
            if give_achievement(user.id, "🏃 25 Runs"):
                unlocked.append("🏃 25 Runs")

        # ==========================================
        # WALK ACHIEVEMENTS
        # ==========================================

        if walks >= 1:
            if give_achievement(user.id, "🚶 First Walk"):
                unlocked.append("🚶 First Walk")

        # ==========================================
        # HIKE ACHIEVEMENTS
        # ==========================================

        if hikes >= 1:
            if give_achievement(user.id, "🥾 First Hike"):
                unlocked.append("🥾 First Hike")

        # ==========================================
        # TIME ACHIEVEMENTS
        # ==========================================

        hours = total_minutes / 60

        if hours >= 5:
            if give_achievement(user.id, "⏱ 5 Hours Logged"):
                unlocked.append("⏱ 5 Hours Logged")

        if hours >= 10:
            if give_achievement(user.id, "⏱ 10 Hours Logged"):
                unlocked.append("⏱ 10 Hours Logged")

        # ==========================================
        # SEND DM
        # ==========================================

        if unlocked:

            embed = discord.Embed(
                title="🏅 Achievement Unlocked!",
                description="\n".join(unlocked),
                color=discord.Color.gold()
            )

            embed.set_footer(
                text="Keep Grinding 🖤 • 93RUN"
            )

            try:
                await user.send(embed=embed)
            except:
                pass


async def setup(bot):
    await bot.add_cog(AchievementEngine(bot))