import os
import aiohttp
import random
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
GIPHY_URL = "https://api.giphy.com/v1/gifs/search"

if not GIPHY_API_KEY:
    raise RuntimeError("GIPHY_API_KEY missing from .env")


class yeet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="yeet",
        description="yeet someone (anime style)"
    )
    @app_commands.describe(user="Who do you want to yeet?")
    async def yeet(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        sender = interaction.user.display_name
        target = user.display_name

        params = {
            "api_key": GIPHY_API_KEY,
            "q": "Throwing a person",
            "limit": 10,
            "rating": ""
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(GIPHY_URL, params=params) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(
                        "❌ Couldn't fetch a yeet GIF 😔",
                        ephemeral=True
                    )
                    return

                data = await resp.json()

        if not data["data"]:
            await interaction.response.send_message(
                "❌ No yeet GIFs found!",
                ephemeral=True
            )
            return

        gif = random.choice(data["data"])
        gif_url = gif["images"]["original"]["url"]

        embed = discord.Embed(
            description=f"💥 **{sender} yeeted {target}!**",
            color=discord.Color.red()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(yeet(bot))
