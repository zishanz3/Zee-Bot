import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class Shard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.land_offset = timedelta(minutes=8, seconds=40)
        self.end_offset = timedelta(hours=4)

        self.black_interval = timedelta(hours=8)
        self.red_interval = timedelta(hours=6)

        self.realms = ["Prairie", "Forest", "Valley", "Wasteland", "Vault"]

        self.shards_info = [
            {
                "no_shard_wkday": [6, 7],
                "interval": self.black_interval,
                "offset": timedelta(hours=1, minutes=50),
                "maps": ["Butterfly Field", "Forest Brook", "Ice Rink", "Broken Temple", "Starlight Desert"],
            },
            {
                "no_shard_wkday": [7, 1],
                "interval": self.black_interval,
                "offset": timedelta(hours=2, minutes=10),
                "maps": ["Village Islands", "Boneyard", "Ice Rink", "Battlefield", "Starlight Desert"],
            },
            {
                "no_shard_wkday": [1, 2],
                "interval": self.red_interval,
                "offset": timedelta(hours=7, minutes=40),
                "maps": ["Cave", "Forest Garden", "Village of Dreams", "Graveyard", "Jellyfish Cove"],
                "def_reward": 2,
            },
            {
                "no_shard_wkday": [2, 3],
                "interval": self.red_interval,
                "offset": timedelta(hours=2, minutes=20),
                "maps": ["Bird Nest", "Treehouse", "Village of Dreams", "Crabfield", "Jellyfish Cove"],
                "def_reward": 2.5,
            },
            {
                "no_shard_wkday": [3, 4],
                "interval": self.red_interval,
                "offset": timedelta(hours=3, minutes=30),
                "maps": ["Sanctuary Island", "Elevated Clearing", "Hermit Valley", "Forgotten Ark", "Jellyfish Cove"],
                "def_reward": 3.5,
            },
        ]

    def calculate_for_date(self, base_date):
        la = ZoneInfo("America/Los_Angeles")
        now = base_date.astimezone(la)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        day_of_month = today.day
        weekday = today.isoweekday()

        is_red = day_of_month % 2 == 1
        realm_idx = (day_of_month - 1) % 5

        if day_of_month % 2 == 1:
            info_index = int(((day_of_month - 1) / 2) % 3) + 2
        else:
            info_index = int((day_of_month / 2) % 2)

        info = self.shards_info[info_index]
        has_shard = weekday not in info["no_shard_wkday"]
        map_name = info["maps"][realm_idx]

        reward = info.get("def_reward") if is_red else None
        first_start = today + info["offset"]

        occurrences = []
        for i in range(3):
            start = first_start + (info["interval"] * i)
            land = start + self.land_offset
            end = start + self.end_offset
            occurrences.append((start, land, end))

        return {
            "now": now,
            "today": today,
            "is_red": is_red,
            "has_shard": has_shard,
            "realm": self.realms[realm_idx],
            "map": map_name,
            "reward": reward,
            "occurrences": occurrences,
        }

    def find_next_shard(self):
        la = ZoneInfo("America/Los_Angeles")
        check_date = datetime.now(la)

        for _ in range(10):  # search next 10 days max
            data = self.calculate_for_date(check_date)

            if data["has_shard"]:
                last_end = data["occurrences"][-1][2]
                if check_date < last_end:
                    return data

            check_date = (check_date + timedelta(days=1)).replace(
                hour=12, minute=0, second=0, microsecond=0
            )

        return None

    @app_commands.command(name="shard", description="Get Sky shard info")
    @app_commands.describe(mode="Choose: today or next")
    async def shard(self, interaction: discord.Interaction, mode: str = "today"):

        la = ZoneInfo("America/Los_Angeles")

        if mode.lower() == "next":
            data = self.find_next_shard()
            title_prefix = "🔮 Next Shard"
        else:
            data = self.calculate_for_date(datetime.now(la))
            title_prefix = "🔥 Today's Shard"

        if not data or not data["has_shard"]:
            await interaction.response.send_message("❌ No shard found.")
            return

        color = discord.Color.red() if data["is_red"] else discord.Color.dark_gray()

        embed = discord.Embed(
            title=title_prefix,
            color=color,
        )

        shard_type = "🔴 Red Shard" if data["is_red"] else "⚫ Black Shard"

        embed.add_field(name="Type", value=shard_type, inline=False)
        embed.add_field(name="Realm", value=data["realm"], inline=True)
        embed.add_field(name="Map", value=data["map"], inline=True)

        if data["reward"]:
            embed.add_field(name="Reward (AC)", value=str(data["reward"]), inline=True)

        times_text = ""
        for idx, (start, land, end) in enumerate(data["occurrences"], 1):
            times_text += (
                f"**Occurrence {idx}**\n"
                f"Start: <t:{int(start.timestamp())}:t>\n"
                f"Land: <t:{int(land.timestamp())}:t>\n"
                f"End: <t:{int(end.timestamp())}:t>\n\n"
            )

        embed.add_field(name="Times (Auto Localized)", value=times_text, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Shard(bot))
