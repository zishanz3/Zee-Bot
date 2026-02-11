import discord
from discord.ext import commands
from discord import app_commands

GREET_GIF = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXo2NmJtZmp4YXd2YXl4ang5eDByOHVjOG1qajd3OWt4eHIyZTl2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RTN53gaKnw3OqbAb8L/giphy.gif"


class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="greet",
        description="Greet a server member with a GIF"
    )
    @app_commands.describe(user="Select a server member")
    async def greet(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        embed = discord.Embed(
            description=f"✨ Hello **{user.display_name}** ✨",
            color=discord.Color.pink()
        )

        embed.set_image(url=GREET_GIF)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Greet(bot))
