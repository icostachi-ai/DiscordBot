# bot.py
import os
import discord
from discord.ext import commands

# Read token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN env var (see README).")

# Enable intents (must match the toggles you set in the Developer Portal)
intents = discord.Intents.default()
intents.message_content = True  # required if you want to read message text

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id: {bot.user.id})")

# Classic text command: !ping
@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")

# Slash commands use app_commands in discord.py v2+
from discord import app_commands

@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}! 👋")

@bot.event
async def on_guild_join(guild):
    # Re-sync slash commands if the bot joins a new server
    await bot.tree.sync(guild=guild)

@bot.event
async def setup_hook():
    # Sync slash commands globally on startup (can take up to an hour to propagate)
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

bot.run(TOKEN)
