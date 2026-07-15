import discord
from discord.ext import commands
from cogs.utils.verifier import verify_workout

from cogs.challenge_config import (
    CHALLENGE_NAME,
    CHALLENGE_START,
    CHALLENGE_END,
)

from cogs.badges import check_badges
from challenge_db import (
    get_pending_submission,
    verify_submission
)

# ======================================================
# CONFIG
# ======================================================

SUBMISSIONS_CHANNEL_ID = 1526769880374710302

# ======================================================
# SUBMISSION COG
# ======================================================

class SubmissionListener(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # IMAGE CHECK
    # ==================================================

    def is_image(self, attachment):

        filename = attachment.filename.lower()

        return (
            filename.endswith(".png")
            or filename.endswith(".jpg")
            or filename.endswith(".jpeg")
            or filename.endswith(".webp")
        )

    # ==================================================
    # MESSAGE LISTENER
    # ==================================================

    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignore bots
        if message.author.bot:
            return

        # Wrong channel
        if message.channel.id != SUBMISSIONS_CHANNEL_ID:
            return

        # No attachment
        if len(message.attachments) == 0:
            return

        attachment = message.attachments[0]

        # Not an image
        if not self.is_image(attachment):

            await message.reply(
                "❌ Only image screenshots are accepted."
            )

            return

        # ==================================================
        # FIND PENDING SUBMISSION
        # ==================================================

        submission = get_pending_submission(message.author.id)

        if submission is None:

            await message.reply(
                "❌ You don't have any pending workout submissions."
            )

            return

        submission_id = submission[0]
        activity = submission[3]
        hours = submission[4]
        minutes = submission[5]
        notes = submission[6]
        submission_message_id = submission[7]

        # ==================================================
        # FIND ORIGINAL SUBMISSION MESSAGE
        # ==================================================

        try:

            submission_message = await message.channel.fetch_message(
                submission_message_id
            )

        except discord.NotFound:

            await message.reply(
                "❌ Original submission not found."
            )

            return

        # ==================================================
        # OCR VERIFICATION
        # ==================================================

        ocr = await verify_workout(attachment.url)

        if not ocr["success"]:

            await message.reply(
                "❌ I couldn't read the workout duration from your screenshot.\n\nPlease upload a clearer screenshot."
            )

            return

        difference = abs(ocr["minutes"] - minutes)

        if difference > 1:

            await message.reply(
                f"❌ Verification Failed\n\n"
                f"You entered **{minutes} minutes**.\n"
                f"Screenshot shows **{ocr['minutes']} minutes**."
            )

            return

            # ==================================================
            # DATE VERIFICATION
            # ==================================================

            if ocr["workout_date"] is None:

                await message.reply(
                    "❌ I couldn't read the workout date from your screenshot.\n\n"
                    "Please upload a screenshot that clearly shows the workout date."
                )

                return

            if (
                ocr["workout_date"] < CHALLENGE_START
                or
                ocr["workout_date"] > CHALLENGE_END
            ):

                await message.reply(

                    f"❌ Verification Failed\n\n"

                    f"Workout Date: **{ocr['workout_date'].strftime('%B %d, %Y')}**\n\n"

                    f"This workout is outside the **{CHALLENGE_NAME}** window.\n\n"

                    f"Accepted Dates:\n"
                    f"**{CHALLENGE_START.strftime('%B %d')}** "
                    f"through "
                    f"**{CHALLENGE_END.strftime('%B %d')}**"

                )

                return


        # ==================================================
        # SAVE VERIFICATION
        # ==================================================

        verify_submission(
            submission_id,
            message.id,
            attachment.url
        )

        # ==================================================
        # VERIFIED EMBED
        # ==================================================

        verified_embed = discord.Embed(
            title="✅ Workout Submission Verified",
            color=discord.Color.green()
        )

        verified_embed.add_field(
            name="Member",
            value=message.author.mention,
            inline=False
        )

        verified_embed.add_field(
            name="Activity",
            value=f"🏃 {activity}",
            inline=True
        )

        verified_embed.add_field(
            name="Duration",
            value=f"{hours}h {minutes}m",
            inline=True
        )

        if notes:

            verified_embed.add_field(
                name="Notes",
                value=notes,
                inline=False
            )

        verified_embed.add_field(
            name="Screenshot",
            value=f"[View Screenshot]({attachment.url})",
            inline=False
        )

        verified_embed.add_field(
            name="Status",
            value="🟢 VERIFIED",
            inline=False
        )

        verified_embed.set_footer(
            text=f"Submission #{submission_id}"
        )

        # ==================================================
        # UPDATE ORIGINAL MESSAGE
        # ==================================================

        await submission_message.edit(
            embed=verified_embed
        )

                # ==================================================
        # UPDATE LEADERBOARD
        # ==================================================

        leaderboard = self.bot.get_cog("Leaderboard")

        if leaderboard is not None:
            await leaderboard.update_leaderboard()

        # ==================================================
        # CHECK BADGES
        # ==================================================

        new_badges = check_badges(message.author.id)

        if new_badges:

            embed = discord.Embed(
                title="🏅 Badge Unlocked!",
                description="\n".join(new_badges),
                color=discord.Color.gold()
            )

            embed.set_footer(
                text="Keep Grinding 🖤"
            )

            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                pass

        # ==================================================
        # CONFIRM MEMBER
        # ==================================================

        await message.reply(
            "✅ Your workout has been verified and recorded!"
        )

        try:
            await message.add_reaction("✅")
        except Exception:
            pass

    # ==================================================
    # READY
    # ==================================================

    @commands.Cog.listener()
    async def on_ready(self):

        print("-----------------------------------------")
        print("Submission Listener Loaded")
        print("-----------------------------------------")
# ======================================================
# SETUP
# ======================================================

async def setup(bot):
    await bot.add_cog(SubmissionListener(bot))