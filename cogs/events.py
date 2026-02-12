import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # FINAL CORRECT TIMES (already shifted +30 minutes)
        self.events = [
            {"name": "Turtle", "minute": 20, "interval": 2},
            {"name": "Geyser", "minute": 35, "interval": 2},
            {"name": "Grandma", "minute": 5, "interval": 2},
            {"name": "Shard Event", "minute": 26, "interval": 4},
            {"name": "Forest Rainbow", "hour": 5, "minute": 30, "interval": 12},
            {"name": "Daily Reset", "hour": 14, "minute": 0, "interval": 24},
        ]

    def now_ist(self):
        return datetime.now(IST)

    def get_next_occurrence(self, event):
        now = self.now_ist()

        # Events with fixed hour (Rainbow & Reset)
        if event.get("hour") is not None:
            next_time = now.replace(
                hour=event["hour"],
                minute=event["minute"],
                second=0,
                microsecond=0
            )

            while next_time <= now:
                next_time += timedelta(hours=event["interval"])

            return next_time

        # Standard repeating events (every X hours at fixed minute)
        interval = event["interval"]
        minute = event["minute"]

        # Anchor from midnight
        base = now.replace(hour=0, minute=minute, second=0, microsecond=0)

        while base <= now:
            base += timedelta(hours=interval)

        return base

    @app_commands.command(name="events", description="Shows upcoming event times")
    async def events(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🌍 Upcoming Events",
            description="Times shown in your local timezone.",
            color=discord.Color.blue()
        )

        event_list = []

        for event in self.events:
            next_time = self.get_next_occurrence(event)
            unix = int(next_time.timestamp())
            event_list.append((event["name"], next_time, unix))

        event_list.sort(key=lambda x: x[1])

        for name, _, unix in event_list:
            embed.add_field(
                name=name,
                value=(
                    f"🕒 Next: <t:{unix}:F>\n"
                    f"⏳ Starts: <t:{unix}:R>"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
