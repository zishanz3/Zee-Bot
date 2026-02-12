import os
import discord
import asyncio
from discord.ext import commands


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
#DEV_GUILD_ID = 729007907131359322  # <-- your server ID
DEV_GUILD_ID = 942018727174619186 
intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        print("⚡ setup_hook CALLED")

        # Load cogs
        await self.load_extension("cogs.greet")
        print("✅ greet loaded")

        await self.load_extension("cogs.gifz")
        print("✅ gifz loaded")

        await self.load_extension("cogs.events")
        print("✅ events loaded")

        await self.load_extension("cogs.slap")
        print("✅ events loaded")

        await self.load_extension("cogs.hug")
        print("✅ events loaded")

        await self.load_extension("cogs.yeet")
        print("✅ events loaded")

        await self.load_extension("cogs.pat")
        print("✅ events loaded")

        await self.load_extension("cogs.ask_zee")
        print("✅ events loaded")

        await self.load_extension("cogs.shard")
        print("✅ events loaded")

        guild = discord.Object(id=DEV_GUILD_ID)

        # DEV MODE: instant commands
        print("🧹 Clearing guild commands")
        self.tree.clear_commands(guild=guild)

        print("📋 Copying global commands to guild")
        self.tree.copy_global_to(guild=guild)

        print("🔄 Syncing guild commands")
        synced = await self.tree.sync(guild=guild)

        print("📌 Synced commands:")
        for cmd in synced:
            print(" -", cmd.name)

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")


bot = MyBot()


# ---------- SLASH COMMAND ----------

@bot.tree.command(
    name="ping",
    description="Check if the bot is alive"
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong 🏓")


# ---------- PREFIX COMMAND ----------

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.display_name} 👋")


async def main():
    await bot.start(DISCORD_TOKEN)


asyncio.run(main())
