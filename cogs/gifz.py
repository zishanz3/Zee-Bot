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
    raise RuntimeError("GIPHY_API_KEY not found in .env file")


class Gifz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="gifz",
        description="Search for a GIF on Giphy"
    )
    @app_commands.describe(query="What kind of GIF do you want?")
    async def gifz(
        self,
        interaction: discord.Interaction,
        query: str
    ):
        params = {
            "api_key": GIPHY_API_KEY,
            "q": query,
            "limit": 10,
            "rating": "pg-13"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(GIPHY_URL, params=params) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(
                        "❌ Failed to contact Giphy.",
                        ephemeral=True
                    )
                    return

                data = await resp.json()

        if not data["data"]:
            await interaction.response.send_message(
                f"No GIFs found for **{query}** 😔",
                ephemeral=True
            )
            return

        gif = random.choice(data["data"])
        gif_url = gif["images"]["original"]["url"]

        embed = discord.Embed(
            title=f"GIF result for: {query}",
            color=discord.Color.blurple()
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Gifz(bot))
