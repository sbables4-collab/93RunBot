import discord

from challenge_db import (
    add_submission,
    save_submission_message
)

# ======================================================
# CONFIG
# ======================================================

GUILD_ID = 1519576931220062270

SUBMISSIONS_CHANNEL_ID = 1526769880374710302


# ======================================================
# ACTIVITY MODAL
# ======================================================

class ActivityModal(discord.ui.Modal):

    def __init__(self, bot, activity):

        super().__init__(title=f"{activity} Activity")

        self.bot = bot
        self.activity = activity

        self.hours = discord.ui.TextInput(
            label="Hours",
            placeholder="0",
            required=True,
            max_length=2
        )

        self.minutes = discord.ui.TextInput(
            label="Minutes",
            placeholder="30",
            required=True,
            max_length=2
        )

        self.notes = discord.ui.TextInput(
            label="Notes (Optional)",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=300
        )

        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.notes)

    # ==================================================
    # SUBMIT
    # ==================================================

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        submission_id = add_submission(

            interaction.user.id,

            str(interaction.user),

            self.activity,

            int(self.hours.value),

            int(self.minutes.value),

            self.notes.value

        )

        guild = self.bot.get_guild(GUILD_ID)

        if guild is None:

            await interaction.response.send_message(
                "Unable to locate server.",
                ephemeral=True
            )

            return

        submissions_channel = guild.get_channel(
            SUBMISSIONS_CHANNEL_ID
        )

        if submissions_channel is None:

            await interaction.response.send_message(
                "Challenge submissions channel not found.",
                ephemeral=True
            )

            return

        embed = discord.Embed(

            title="📸 Pending Workout Submission",

            color=discord.Color.orange()

        )

        embed.add_field(
            name="Member",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Activity",
            value=self.activity,
            inline=True
        )

        embed.add_field(
            name="Duration",
            value=f"{self.hours.value}h {self.minutes.value}m",
            inline=True
        )

        if self.notes.value:

            embed.add_field(
                name="Notes",
                value=self.notes.value,
                inline=False
            )

        embed.add_field(
            name="Status",
            value="🟡 Waiting for Screenshot",
            inline=False
        )

        embed.set_footer(
            text=f"Submission #{submission_id}"
        )

        submission_message = await submissions_channel.send(
            embed=embed
        )
                # Save the Discord message ID
        save_submission_message(
            submission_id,
            submission_message.id
        )

        # Create a link to the submission message
        submission_link = (
            f"https://discord.com/channels/"
            f"{GUILD_ID}/"
            f"{SUBMISSIONS_CHANNEL_ID}/"
            f"{submission_message.id}"
        )

        # Confirmation embed shown only to the member
        confirmation = discord.Embed(
            title="📸 Step 2 of 2",
            description=(
                "Your workout has been recorded as a **pending submission**.\n\n"
                "**One more step is required.**\n\n"
                "Click the button below to open your submission and upload "
                "**ONE screenshot** from your fitness app.\n\n"
                "Accepted apps include:\n"
                "• Strava\n"
                "• Garmin\n"
                "• Apple Fitness\n"
                "• Nike Run Club\n"
                "• Fitbit\n"
                "• Samsung Health\n\n"
                "⏳ You have **5 minutes** to upload your screenshot."
            ),
            color=discord.Color.green()
        )

        confirmation.add_field(
            name="Activity",
            value=self.activity,
            inline=True
        )

        confirmation.add_field(
            name="Duration",
            value=f"{self.hours.value}h {self.minutes.value}m",
            inline=True
        )

        confirmation.set_footer(
            text=f"Submission #{submission_id}"
        )

        class SubmissionView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)

                self.add_item(
                    discord.ui.Button(
                        label="📸 Go To My Submission",
                        url=submission_link
                    )
                )

        await interaction.response.send_message(
            embed=confirmation,
            view=SubmissionView(),
            ephemeral=True
        )