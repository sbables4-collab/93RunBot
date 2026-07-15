import discord

from cogs.modals import ActivityModal
from challenge_db import (
    get_user_stats,
    get_user_rank,
    get_achievements,
    get_user_streak
)


# ======================================================
# ACTIVITY SELECT
# ======================================================

class ActivitySelect(discord.ui.Select):

    def __init__(self, bot):

        self.bot = bot

        options = [

            discord.SelectOption(
                label="Run",
                emoji="🏃",
                description="Log a run"
            ),

            discord.SelectOption(
                label="Walk",
                emoji="🚶",
                description="Log a walk"
            ),

            discord.SelectOption(
                label="Hike",
                emoji="🥾",
                description="Log a hike"
            )

        ]

        super().__init__(
            placeholder="Choose your activity...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        activity = self.values[0]

        await interaction.response.send_modal(
            ActivityModal(
                self.bot,
                activity
            )
        )


# ======================================================
# ACTIVITY VIEW
# ======================================================

class ActivitySelectView(discord.ui.View):

    def __init__(self, bot):

        super().__init__(timeout=120)

        self.add_item(
            ActivitySelect(bot)
        )


# ======================================================
# CHALLENGE HUB
# ======================================================

class ChallengeView(discord.ui.View):

    def __init__(self, bot):

        super().__init__(timeout=None)

        self.bot = bot
            # ======================================================
    # LOG ACTIVITY
    # ======================================================

    @discord.ui.button(
        label="🏃 Log Activity",
        style=discord.ButtonStyle.green,
        row=0
    )
    async def log_activity(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "## 🏃 Select your activity",
            view=ActivitySelectView(self.bot),
            ephemeral=True
        )

    # ======================================================
    # MY STATS
    # ======================================================

    @discord.ui.button(
        label="📊 My Stats",
        style=discord.ButtonStyle.blurple,
        row=0
    )
    async def my_stats(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        stats = get_user_stats(interaction.user.id)

        workouts = stats[0] or 0
        runs = stats[1] or 0
        walks = stats[2] or 0
        hikes = stats[3] or 0
        total_minutes = stats[4] or 0

        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        rank = get_user_rank(interaction.user.id)

        embed = discord.Embed(
            title="📊 My July Grind Stats",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.add_field(
            name="🏆 Rank",
            value=f"#{rank}" if rank else "Unranked",
            inline=False
        )

        embed.add_field(
            name="⏱ Total Time",
            value=f"{total_hours}h {remaining_minutes}m",
            inline=True
        )

        embed.add_field(
            name="📸 Verified Workouts",
            value=str(workouts),
            inline=True
        )

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

        earned = len(get_achievements(interaction.user.id))

        embed.add_field(
            name="🏅 Badges",
            value=f"{earned} Earned",
            inline=False
        )

        embed.set_footer(
            text="Keep Grinding 🖤"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ======================================================
    # LEADERBOARD
    # ======================================================

    @discord.ui.button(
        label="🏆 Leaderboard",
        style=discord.ButtonStyle.gray,
        row=1
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        leaderboard = self.bot.get_cog("Leaderboard")

        if leaderboard is None:

            await interaction.response.send_message(
                "❌ Leaderboard unavailable.",
                ephemeral=True
            )

            return

        embed = await leaderboard.build_embed()

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
            # ======================================================
    # MY BADGES
    # ======================================================

    @discord.ui.button(
        label="🏅 My Badges",
        style=discord.ButtonStyle.gray,
        row=1
    )
    async def my_badges(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        stats = get_user_stats(interaction.user.id)

        runs = stats[1] or 0
        walks = stats[2] or 0
        hikes = stats[3] or 0
        total_minutes = stats[4] or 0
        hours = total_minutes // 60

        earned = {
            badge[0]
            for badge in get_achievements(interaction.user.id)
        }

        embed = discord.Embed(
            title="🏅 My Badges",
            color=discord.Color.gold()
        )

        badge_list = [

            ("🥇 First Workout", "🥇 First Workout", "Complete your first verified workout"),

            ("🏃 5 Runs", "🏃 5 Runs", f"{runs}/5 Runs"),

            ("🏃 10 Runs", "🏃 10 Runs", f"{runs}/10 Runs"),

            ("🏃 25 Runs", "🏃 25 Runs", f"{runs}/25 Runs"),

            ("🚶 First Walk", "🚶 First Walk", f"{walks}/1 Walk"),

            ("🚶 10 Walks", "🚶 10 Walks", f"{walks}/10 Walks"),

            ("🥾 First Hike", "🥾 First Hike", f"{hikes}/1 Hike"),

            ("⏱ 5 Hours Logged", "⏱ 5 Hours Logged", f"{hours}/5 Hours"),

            ("⏱ 10 Hours Logged", "⏱ 10 Hours Logged", f"{hours}/10 Hours"),
        ]

        unlocked = 0

        for display_name, achievement_name, progress in badge_list:

            if achievement_name in earned:

                unlocked += 1

                embed.add_field(
                    name=f"✅ {display_name}",
                    value="Unlocked",
                    inline=False
                )

            else:

                embed.add_field(
                    name=f"🔒 {display_name}",
                    value=f"Progress: {progress}",
                    inline=False
                )

        embed.set_footer(
            text=f"{unlocked} / {len(badge_list)} Badges Unlocked"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ======================================================
    # RULES
    # ======================================================

    @discord.ui.button(
        label="📜 Rules",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def rules(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="📜 July Grind Rules",
            color=discord.Color.orange()
        )

        embed.description = (
            "🏃 **Allowed Activities**\n"
            "• Run\n"
            "• Walk\n"
            "• Hike\n\n"
            "📸 Every workout requires one screenshot from a fitness app.\n\n"
            "✅ Only verified workouts count toward the leaderboard.\n\n"
            "🖤 Keep it honest. Keep grinding."
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ======================================================
    # HELP
    # ======================================================

    @discord.ui.button(
        label="❓ Help",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def help_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="❓ Challenge Help",
            color=discord.Color.green()
        )

        embed.description = (
            "**1️⃣ Click Log Activity**\n"
            "Choose Run, Walk, or Hike.\n\n"
            "**2️⃣ Enter your workout details**\n\n"
            "**3️⃣ Upload ONE screenshot in the submissions channel.**\n\n"
            "Once verified, your workout is automatically added to the leaderboard."
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )