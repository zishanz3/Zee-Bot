import os
import aiohttp
import random
import discord
from discord.ext import commands
from discord import app_commands

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
GIPHY_URL = "https://api.giphy.com/v1/gifs/search"

if not GIPHY_API_KEY:
    raise RuntimeError("GIPHY_API_KEY missing from .env")


class hug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="hug",
        description="hug someone (anime style)"
    )
    @app_commands.describe(user="Who do you want to hug?")
    async def hug(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        sender = interaction.user.display_name
        target = user.display_name

        params = {
            "api_key": GIPHY_API_KEY,
            "q": "Anime hug",
            "limit": 10,
            "rating": ""
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(GIPHY_URL, params=params) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(
                        "❌ Couldn't fetch a hug GIF 😔",
                        ephemeral=True
                    )
                    return

                data = await resp.json()

        if not data["data"]:
            await interaction.response.send_message(
                "❌ No hug GIFs found!",
                ephemeral=True
            )
            return

        gif = random.choice(data["data"])
        gif_url = gif["images"]["original"]["url"]

        embed = discord.Embed(
            description=f"💥 **{sender} hugged {target}!**",
            color=discord.Color.red()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(hug(bot))
