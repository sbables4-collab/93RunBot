import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ======================================================
# LOAD ENVIRONMENT
# ======================================================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ======================================================
# CONFIGURATION
# ======================================================

INTRO_CHANNEL_ID = 1519579729303179264
MEMBER_ROLE_ID = 1525288952574115962

# ======================================================
# DATABASE
# ======================================================

conn = sqlite3.connect("93run.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS introductions (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# ======================================================
# INTENTS
# ======================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ======================================================
# READY
# ======================================================

@bot.event
async def on_ready():

    print("-----------------------------------------")
    print("93RUN BOT IS ONLINE")
    print(f"Logged in as {bot.user}")
    print("-----------------------------------------")

# ======================================================
# MEMBER JOIN
# ======================================================

@bot.event
async def on_member_join(member):

    try:

        await member.send(
f"""
# 👋 Welcome to 93Run!

We're excited to have you join our community.

Before jumping in, please head over to:

<#1519579729303179264>

and introduce yourself!

### We'd love to know:

👤 **Name**

🏃 **Current run goal**

❤️ **What brought you to 93Run**

Once you've posted your introduction,
you'll automatically receive your **Member** role
and unlock the rest of the community.

See you in the server!

🖤 93Run
"""
        )

        print(f"Sent welcome DM to {member}")

    except Exception as e:

        print(f"Couldn't DM {member}")
        print(e)

# ======================================================
# MESSAGE EVENT
# ======================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    await bot.process_commands(message)

    # Only watch introductions

    if message.channel.id != INTRO_CHANNEL_ID:
        return

    cursor.execute(
        "SELECT user_id FROM introductions WHERE user_id=?",
        (message.author.id,)
    )

    existing = cursor.fetchone()

    # ===========================================
    # ALREADY INTRODUCED
    # ===========================================

    if existing:

        try:
            await message.delete()
        except:
            pass

        try:
            await message.author.send(
"""
You have already posted your introduction.

If you need to update it,
please contact a staff member.

🏃🖤
"""
            )
        except:
            pass

        return

    # ===========================================
    # FIRST INTRODUCTION
    # ===========================================

    cursor.execute(
        "INSERT INTO introductions(user_id) VALUES(?)",
        (message.author.id,)
    )

    conn.commit()

    print(f"Saved introduction for {message.author}")

    # React

    try:
        await message.add_reaction("👋")
    except:
        pass

    # Member Role

    role = message.guild.get_role(MEMBER_ROLE_ID)

    if role:

        try:

            await message.author.add_roles(role)

            print(f"Member role added to {message.author}")

        except Exception as e:

            print(e)

    # ===========================================
    # Confirmation DM
    # ===========================================

    try:

        await message.author.send(
"""
🎉 Thanks for introducing yourself!

You're officially a **93Run Member**.

Welcome to the community!

See you at the next run! 🏃🖤
"""
        )

    except Exception as e:

        print(f"Couldn't send confirmation DM: {e}")

    # ===========================================
    # Lock this member from posting again
    # ===========================================

    try:

        overwrite = message.channel.overwrites_for(message.author)

        overwrite.send_messages = False
        overwrite.add_reactions = True
        overwrite.view_channel = True
        overwrite.read_message_history = True

        await message.channel.set_permissions(
            message.author,
            overwrite=overwrite,
            reason="Completed member introduction"
        )

        print(f"Locked {message.author} from posting again.")

    except Exception as e:

        print(f"Permission error: {e}")

# ======================================================
# START BOT
# ======================================================

try:

    bot.run(TOKEN)

finally:

    conn.close()