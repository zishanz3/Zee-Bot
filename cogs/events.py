import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Added +30 minutes to every event
        self.events = [
            {"name": "Geyser", "minute": 35, "interval": 2},
            {"name": "Grandma", "minute": 5, "interval": 2},
            {"name": "Turtle", "minute": 20, "interval": 2},
            {"name": "Shard Event", "minute": 26, "interval": 4},
            {"name": "Sunset", "minute": 20, "interval": 2},
            {"name": "Fairy Ring", "minute": 20, "interval": 1},
            {"name": "Forest Rainbow", "hour": 5, "minute": 30, "interval": 12},
            {"name": "Daily Reset", "hour": 14, "minute": 0, "interval": None},  # 13:30 + 30 = 14:00
        ]

    def get_now(self):
        return datetime.now(IST)

    def get_next_occurrence(self, event):
        now = self.get_now()

        # Daily fixed time event
        if event["interval"] is None:
            next_time = now.replace(
                hour=event["hour"],
                minute=event["minute"],
                second=0,
                microsecond=0
            )
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time

        # Event with specific starting hour (like rainbow)
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

        # Standard repeating events
        next_time = now.replace(
            minute=event["minute"],
            second=0,
            microsecond=0
        )

        while next_time <= now:
            next_time += timedelta(hours=event["interval"])

        return next_time

    @app_commands.command(name="events", description="Shows upcoming event times")
    async def events(self, interaction: discord.Interaction):

        now = self.get_now()
        embed = discord.Embed(
            title="🌍 Upcoming Events",
            description="Times are shown in **your local timezone** automatically.",
            color=discord.Color.blue()
        )

        event_list = []

        for event in self.events:
            next_time = self.get_next_occurrence(event)
            unix_timestamp = int(next_time.timestamp())

            event_list.append((event["name"], next_time, unix_timestamp))

        # Sort by soonest event
        event_list.sort(key=lambda x: x[1])

        for name, next_time, unix in event_list:
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
