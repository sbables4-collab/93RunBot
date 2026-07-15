import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

# ======================================================
# CONFIG
# ======================================================

DATABASE = "93run.db"

LEADERBOARD_CHANNEL_ID = 1527178145805897758

# ======================================================
# LEADERBOARD COG
# ======================================================

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # DATABASE
    # ==================================================

    def get_leaderboard(self):

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT

                user_id,
                SUM(hours * 60 + minutes) AS total_minutes

            FROM challenge_submissions

            WHERE status='verified'

            GROUP BY user_id

            ORDER BY total_minutes DESC
        """)

        results = cursor.fetchall()

        conn.close()

        return results

    # ==================================================
    # BUILD EMBED
    # ==================================================

    async def build_embed(self):

        leaderboard = self.get_leaderboard()

        embed = discord.Embed(

            title="🏆 93RUN July Grind Leaderboard",

            description=(
                "Top verified workout time.\n"
                "Updated automatically after every verified workout."
            ),

            color=discord.Color.gold()

        )

        if len(leaderboard) == 0:

            embed.add_field(
                name="No workouts yet",
                value="Be the first to log one! 💪",
                inline=False
            )

            embed.set_footer(
                text="93RUN"
            )

            return embed

        medals = [
            "🥇",
            "🥈",
            "🥉",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟"
        ]

        for index, row in enumerate(leaderboard[:10]):

            user_id = row[0]
            total_minutes = row[1]

            hours = total_minutes // 60
            minutes = total_minutes % 60

            embed.add_field(

                name=f"{medals[index]}  <@{user_id}>",

                value=f"⏱ **{hours}h {minutes}m**",

                inline=False

            )

        embed.set_footer(

            text=f"Last Updated • {datetime.now().strftime('%I:%M %p')}"

        )

        return embed
            # ==================================================
    # POST OR UPDATE LEADERBOARD
    # ==================================================

    async def update_leaderboard(self):

        channel = self.bot.get_channel(LEADERBOARD_CHANNEL_ID)

        if channel is None:
            return

        embed = await self.build_embed()

        try:

            # Look for the existing leaderboard message
            async for message in channel.history(limit=25):

                if (
                    message.author == self.bot.user
                    and len(message.embeds) > 0
                    and message.embeds[0].title == "🏆 93RUN July Grind Leaderboard"
                ):

                    await message.edit(embed=embed)
                    return

            # No leaderboard found, create one
            await channel.send(embed=embed)

        except Exception as e:
            print(f"Leaderboard update failed: {e}")

    # ==================================================
    # ADMIN COMMAND
    # ==================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leaderboard(self, ctx):

        await self.update_leaderboard()

        await ctx.send(
            "✅ Leaderboard has been created/updated.",
            delete_after=5
        )

    # ==================================================
    # READY
    # ==================================================

    @commands.Cog.listener()
    async def on_ready(self):

        print("-----------------------------------------")
        print("Leaderboard Cog Loaded")
        print("-----------------------------------------")


# ======================================================
# SETUP
# ======================================================

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))