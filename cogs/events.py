import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Event Configuration
        self.events = [
            {"name": "Geyser", "minute": 5, "interval": 2},
            {"name": "Grandma", "minute": 35, "interval": 2},
            {"name": "Turtle", "minute": 50, "interval": 2},
            {"name": "Shard Event", "minute": 56, "interval": 4},
            {"name": "Sunset", "minute": 50, "interval": 2},
            {"name": "Fairy Ring", "minute": 50, "interval": 1},
            {"name": "Forest Rainbow", "hour": 5, "minute": 0, "interval": 12},
            {"name": "Daily Reset", "hour": 13, "minute": 30, "interval": None},
        ]

    def get_now(self):
        return datetime.now(IST)

    def get_next_occurrence(self, event):
        now = self.get_now()

        # Daily Reset (fixed time daily)
        if event["interval"] is None:
            next_time = now.replace(hour=event["hour"], minute=event["minute"], second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time

        # Special 12-hour rainbow event
        if event.get("hour") is not None:
            next_time = now.replace(hour=event["hour"], minute=event["minute"], second=0, microsecond=0)
            while next_time <= now:
                next_time += timedelta(hours=event["interval"])
            return next_time

        # Standard repeating event every X hours at specific minute
        next_time = now.replace(minute=event["minute"], second=0, microsecond=0)

        while next_time <= now:
            next_time += timedelta(hours=event["interval"])

        return next_time

    @app_commands.command(name="events", description="Shows upcoming event times (IST)")
    async def events(self, interaction: discord.Interaction):

        now = self.get_now()
        embed = discord.Embed(
            title="🌍 Upcoming Events (IST)",
            color=discord.Color.blue()
        )

        for event in self.events:
            next_time = self.get_next_occurrence(event)
            time_left = next_time - now

            total_seconds = int(time_left.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            embed.add_field(
                name=event["name"],
                value=(
                    f"🕒 Next: {next_time.strftime('%H:%M IST')}\n"
                    f"⏳ Time Left: {hours}h {minutes}m"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
