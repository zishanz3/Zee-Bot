import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import math


class Shard(commands.GroupCog, name="shard"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.land_offset = timedelta(minutes=8, seconds=40)
        self.end_offset = timedelta(hours=4)

        self.black_interval = timedelta(hours=8)
        self.red_interval = timedelta(hours=6)

        self.realms = ["Prairie", "Forest", "Valley", "Wasteland", "Vault"]

        self.shards_info = [
            {
                "noShardWkDay": [6, 7],
                "interval": self.black_interval,
                "offset": timedelta(hours=1, minutes=50),
                "maps": ["Butterfly Field", "Forest Brook", "Ice Rink", "Broken Temple", "Starlight Desert"],
            },
            {
                "noShardWkDay": [7, 1],
                "interval": self.black_interval,
                "offset": timedelta(hours=2, minutes=10),
                "maps": ["Village Islands", "Boneyard", "Ice Rink", "Battlefield", "Starlight Desert"],
            },
            {
                "noShardWkDay": [1, 2],
                "interval": self.red_interval,
                "offset": timedelta(hours=7, minutes=40),
                "maps": ["Cave", "Forest Garden", "Village of Dreams", "Graveyard", "Jellyfish Cove"],
                "defRewardAC": 2,
            },
            {
                "noShardWkDay": [2, 3],
                "interval": self.red_interval,
                "offset": timedelta(hours=2, minutes=20),
                "maps": ["Bird Nest", "Treehouse", "Village of Dreams", "Crabfield", "Jellyfish Cove"],
                "defRewardAC": 2.5,
            },
            {
                "noShardWkDay": [3, 4],
                "interval": self.red_interval,
                "offset": timedelta(hours=3, minutes=30),
                "maps": ["Sanctuary Island", "Elevated Clearing", "Hermit Valley", "Forgotten Ark", "Jellyfish Cove"],
                "defRewardAC": 3.5,
            },
        ]

    # =========================
    # DIRECT PORT OF getShardInfo(date)
    # =========================
    def get_shard_info(self, date):
        la = ZoneInfo("America/Los_Angeles")
        date = date.astimezone(la)

        today = date.replace(hour=0, minute=0, second=0, microsecond=0)

        day_of_month = today.day
        weekday = today.isoweekday()

        is_red = day_of_month % 2 == 1
        realm_idx = (day_of_month - 1) % 5

        if is_red:
            info_index = int((((day_of_month - 1) / 2) % 3) + 2)
        else:
            info_index = int((day_of_month / 2) % 2)

        config = self.shards_info[info_index]

        has_shard = weekday not in config["noShardWkDay"]

        first_start = today + config["offset"]

        occurrences = []
        for i in range(3):
            start = first_start + (config["interval"] * i)
            land = start + self.land_offset
            end = start + self.end_offset
            occurrences.append((start, land, end))

        return {
            "date": date,
            "isRed": is_red,
            "hasShard": has_shard,
            "lastEnd": occurrences[2][2],
            "realm": self.realms[realm_idx],
            "map": config["maps"][realm_idx],
            "rewardAC": config.get("defRewardAC") if is_red else None,
            "occurrences": occurrences,
        }

    # =========================
    # DIRECT PORT OF findNextShard
    # =========================
    def find_next_shard(self, from_dt, only=None):
        la = ZoneInfo("America/Los_Angeles")
        current = from_dt.astimezone(la)

        while True:
            info = self.get_shard_info(current)

            condition = (
                info["hasShard"]
                and current < info["lastEnd"]
                and (not only or ((only == "red") == info["isRed"]))
            )

            if condition:
                return info

            current = current + timedelta(days=1)

    # =========================
    # EMBED
    # =========================
    async def send_embed(self, interaction, info, title):
        embed_color = discord.Color.red() if info["isRed"] else discord.Color.dark_gray()
        embed = discord.Embed(title=title, color=embed_color)

        embed.add_field(name="Realm", value=info["realm"])
        embed.add_field(name="Map", value=info["map"])

        if info["rewardAC"]:
            embed.add_field(name="Reward AC", value=str(info["rewardAC"]))

        now = info["date"]

        status = "Not active"
        countdown = ""

        for idx, (start, _, end) in enumerate(info["occurrences"], 1):
            if start <= now <= end:
                status = f"🔥 Occurrence {idx} ACTIVE"
                countdown = f"Ends in `{str(end - now).split('.')[0]}`"
                break
            elif now < start:
                countdown = f"Starts in `{str(start - now).split('.')[0]}`"
                break

        embed.add_field(name="Status", value=status, inline=False)

        if countdown:
            embed.add_field(name="Countdown", value=countdown, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="red")
    async def red(self, interaction: discord.Interaction):
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        info = self.find_next_shard(now, "red")
        await self.send_embed(interaction, info, "Next Red Shard")

    @app_commands.command(name="black")
    async def black(self, interaction: discord.Interaction):
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        info = self.find_next_shard(now, "black")
        await self.send_embed(interaction, info, "Next Black Shard")

    @app_commands.command(name="next")
    async def next(self, interaction: discord.Interaction):
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        info = self.find_next_shard(now)
        await self.send_embed(interaction, info, "Next Shard")

    @app_commands.command(name="today")
    async def today(self, interaction: discord.Interaction):
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        info = self.get_shard_info(now)
        await self.send_embed(interaction, info, "Today's Shard")


async def setup(bot):
    await bot.add_cog(Shard(bot))
