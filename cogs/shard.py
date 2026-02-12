import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class Shard(commands.GroupCog, name="shard"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.la = ZoneInfo("America/Los_Angeles")

        # 🔥 Anchor = TODAY (confirmed BLACK)
        self.anchor_date = datetime.now(self.la).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self.land_offset = timedelta(minutes=8, seconds=40)
        self.end_offset = timedelta(hours=4)

        self.black_interval = timedelta(hours=8)
        self.red_interval = timedelta(hours=6)

        self.realms = ["Prairie", "Forest", "Valley", "Wasteland", "Vault"]

        # 5 rotating shard offset groups
        self.offsets = [
            timedelta(hours=1, minutes=50),
            timedelta(hours=2, minutes=10),
            timedelta(hours=7, minutes=40),
            timedelta(hours=2, minutes=20),
            timedelta(hours=3, minutes=30),
        ]

    # =========================
    # BUILD SHARD FOR DATE
    # =========================
    def build_shard(self, current_time, filter_color=None):
        now = current_time.astimezone(self.la)

        for days_ahead in range(15):
            check_time = now + timedelta(days=days_ahead)
            today = check_time.replace(hour=0, minute=0, second=0, microsecond=0)

            cycle_day = (today.date() - self.anchor_date.date()).days

            # Alternate daily
            is_red = (cycle_day % 2) == 1

            # Filter color if requested
            if filter_color == "red" and not is_red:
                continue
            if filter_color == "black" and is_red:
                continue

            # 5-day rotation
            group_index = cycle_day % 5

            interval = self.red_interval if is_red else self.black_interval
            first_start = today + self.offsets[group_index]

            occurrences = []
            for i in range(3):
                start = first_start + (interval * i)
                end = start + self.end_offset
                occurrences.append((start, end))

            # If today, skip if finished
            if days_ahead == 0:
                if now >= occurrences[-1][1]:
                    continue

            realm_index = cycle_day % 5

            return {
                "now": now,
                "isRed": is_red,
                "realm": self.realms[realm_index],
                "occurrences": occurrences,
            }

        return None

    # =========================
    # EMBED
    # =========================
    async def send_embed(self, interaction, data, title):
        if not data:
            await interaction.response.send_message("No shard found.")
            return

        embed = discord.Embed(
            title=title,
            color=discord.Color.red() if data["isRed"] else discord.Color.dark_gray()
        )

        embed.add_field(
            name="Type",
            value="🔴 Red Shard" if data["isRed"] else "⚫ Black Shard"
        )
        embed.add_field(name="Realm", value=data["realm"])

        now = data["now"]
        status = "Not active"
        countdown = ""

        for i, (start, end) in enumerate(data["occurrences"], 1):
            if start <= now <= end:
                status = f"🔥 Occurrence {i} ACTIVE"
                countdown = f"⏳ Ends in `{str(end - now).split('.')[0]}`"
                break
            elif now < start:
                countdown = f"⏳ Starts in `{str(start - now).split('.')[0]}`"
                break

        embed.add_field(name="Status", value=status, inline=False)

        if countdown:
            embed.add_field(name="Countdown", value=countdown, inline=False)

        await interaction.response.send_message(embed=embed)

    # =========================
    # COMMANDS
    # =========================

    @app_commands.command(name="today")
    async def today(self, interaction: discord.Interaction):
        data = self.build_shard(datetime.now(self.la))
        await self.send_embed(interaction, data, "Today's Shard")

    @app_commands.command(name="next")
    async def next(self, interaction: discord.Interaction):
        data = self.build_shard(datetime.now(self.la))
        await self.send_embed(interaction, data, "Next Shard")

    @app_commands.command(name="red")
    async def red(self, interaction: discord.Interaction):
        data = self.build_shard(datetime.now(self.la), "red")
        await self.send_embed(interaction, data, "Next Red Shard")

    @app_commands.command(name="black")
    async def black(self, interaction: discord.Interaction):
        data = self.build_shard(datetime.now(self.la), "black")
        await self.send_embed(interaction, data, "Next Black Shard")


async def setup(bot):
    await bot.add_cog(Shard(bot))
