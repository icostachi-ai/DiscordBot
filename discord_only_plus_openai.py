# discord_only_plus_openai.py
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# --- OpenAI client (SDK v1) ---
# pip install openai>=1.40
from openai import OpenAI
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN (or TOKEN) in your environment/.env")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your environment/.env")

client_oa = OpenAI(api_key=OPENAI_API_KEY)

# --- Discord setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = (
    "You are a concise, friendly assistant helping in a Discord server. "
    "Keep answers short unless the user asks for details."
)

async def ask_openai(prompt: str) -> str:
    """Call OpenAI and return the assistant's text."""
    try:
        resp = client_oa.chat.completions.create(
            model="gpt-4o-mini",  # pick a model you have access to
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Log and return a friendly message
        print(f"[OpenAI error] {e}")
        return "Sorry—I'm having trouble reaching the AI service right now."

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id: {bot.user.id})")
    # Sync slash commands globally
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# --- Slash command: /ask ---
from discord import app_commands

@bot.tree.command(name="ask", description="Ask the AI a question")
@app_commands.describe(prompt="Your question or prompt")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)  # typing indicator
    reply = await ask_openai(prompt)
    # Discord message limit ~2000 chars
    if len(reply) > 1900:
        reply = reply[:1900] + "…"
    await interaction.followup.send(reply)

# --- Text command: !ask <prompt> ---
@bot.command(name="ask")
async def ask_cmd(ctx: commands.Context, *, prompt: str):
    async with ctx.typing():
        reply = await ask_openai(prompt)
    if len(reply) > 1900:
        reply = reply[:1900] + "…"
    await ctx.reply(reply, mention_author=False)

# --- Simple ping ---
@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send("pong 🏓")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
