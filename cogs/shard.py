import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


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

    # ======================
    # CORE CALCULATION
    # ======================
    def calculate_for_date(self, dt):
        la = ZoneInfo("America/Los_Angeles")
        now = dt.astimezone(la)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        day = today.day
        weekday = today.isoweekday()

        is_red = day % 2 == 1
        realm_index = (day - 1) % 5

        if is_red:
            info_index = ((day - 1) // 2) % 3 + 2
        else:
            info_index = (day // 2) % 2

        config = self.shards_info[info_index]
        has_shard = weekday not in config["no_shard_wkday"]

        map_name = config["maps"][realm_index]
        reward = config.get("def_reward") if is_red else None

        first_start = today + config["offset"]

        occurrences = []
        for i in range(3):
            start = first_start + config["interval"] * i
            land = start + self.land_offset
            end = start + self.end_offset
            occurrences.append((start, land, end))

        return {
            "now": now,
            "is_red": is_red,
            "has_shard": has_shard,
            "realm": self.realms[realm_index],
            "map": map_name,
            "reward": reward,
            "occurrences": occurrences,
        }

    # ======================
    # NEXT SHARD (STABLE VERSION)
    # ======================
    def find_next_shard(self, color_filter=None):
        la = ZoneInfo("America/Los_Angeles")
        now = datetime.now(la)

        for days_ahead in range(15):
            check_time = now + timedelta(days=days_ahead)
            data = self.calculate_for_date(check_time)

            if not data["has_shard"]:
                continue

            if color_filter == "red" and not data["is_red"]:
                continue

            if color_filter == "black" and data["is_red"]:
                continue

            # If checking today, ensure it hasn't ended
            if days_ahead == 0:
                last_end = data["occurrences"][-1][2]
                if now >= last_end:
                    continue

            return data

        return None

    # ======================
    # EMBED BUILDER
    # ======================
    async def send_embed(self, interaction, data, title):
        if not data:
            await interaction.response.send_message("❌ No shard found.")
            return

        embed_color = discord.Color.red() if data["is_red"] else discord.Color.dark_gray()
        embed = discord.Embed(title=title, color=embed_color)

        shard_type = "🔴 Red Shard" if data["is_red"] else "⚫ Black Shard"

        embed.add_field(name="Type", value=shard_type, inline=False)
        embed.add_field(name="Realm", value=data["realm"], inline=True)
        embed.add_field(name="Map", value=data["map"], inline=True)

        if data["reward"]:
            embed.add_field(name="Reward (AC)", value=str(data["reward"]), inline=True)

        now = data["now"]
        status = "Not active"
        countdown = ""

        for idx, (start, _, end) in enumerate(data["occurrences"], 1):
            if start <= now <= end:
                status = f"🔥 Occurrence {idx} is ACTIVE!"
                remaining = end - now
                countdown = f"⏳ Ends in: `{str(remaining).split('.')[0]}`"
                break
            elif now < start:
                remaining = start - now
                countdown = f"⏳ Starts in: `{str(remaining).split('.')[0]}`"
                break

        embed.add_field(name="Status", value=status, inline=False)

        if countdown:
            embed.add_field(name="Countdown", value=countdown, inline=False)

        time_text = ""
        for i, (start, land, end) in enumerate(data["occurrences"], 1):
            time_text += (
                f"**Occurrence {i}**\n"
                f"Start: <t:{int(start.timestamp())}:t>\n"
                f"Land: <t:{int(land.timestamp())}:t>\n"
                f"End: <t:{int(end.timestamp())}:t>\n\n"
            )

        embed.add_field(name="Times", value=time_text, inline=False)

        await interaction.response.send_message(embed=embed)

    # ======================
    # SUBCOMMANDS
    # ======================

    @app_commands.command(name="today", description="Show today's shard")
    async def today(self, interaction: discord.Interaction):
        la = ZoneInfo("America/Los_Angeles")
        data = self.calculate_for_date(datetime.now(la))
        await self.send_embed(interaction, data, "🔥 Today's Shard")

    @app_commands.command(name="next", description="Show next shard")
    async def next(self, interaction: discord.Interaction):
        data = self.find_next_shard()
        await self.send_embed(interaction, data, "🔮 Next Shard")

    @app_commands.command(name="red", description="Show next red shard")
    async def red(self, interaction: discord.Interaction):
        data = self.find_next_shard("red")
        await self.send_embed(interaction, data, "🔴 Next Red Shard")

    @app_commands.command(name="black", description="Show next black shard")
    async def black(self, interaction: discord.Interaction):
        data = self.find_next_shard("black")
        await self.send_embed(interaction, data, "⚫ Next Black Shard")


async def setup(bot: commands.Bot):
    await bot.add_cog(Shard(bot))
