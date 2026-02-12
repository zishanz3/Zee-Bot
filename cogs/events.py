import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Base event definitions (BEFORE +30)
        self.events = [
            {"name": "Turtle", "base_hour": 0, "minute": 50, "interval": 2},
            {"name": "Geyser", "base_hour": 0, "minute": 5, "interval": 2},
            {"name": "Grandma", "base_hour": 0, "minute": 35, "interval": 2},
            {"name": "Shard Event", "base_hour": 0, "minute": 56, "interval": 4},
            {"name": "Forest Rainbow", "base_hour": 5, "minute": 0, "interval": 12},
            {"name": "Daily Reset", "base_hour": 13, "minute": 30, "interval": 24},
        ]

    def now_ist(self):
        return datetime.now(IST)

    def next_event_time(self, event):
        now = self.now_ist()

        # Anchor to today's base time
        base = now.replace(
            hour=event["base_hour"],
            minute=event["minute"],
            second=0,
            microsecond=0
        )

        # Move forward in interval blocks until future
        while base <= now:
            base += timedelta(hours=event["interval"])

        # ✅ Apply +30 shift globally
        base += timedelta(minutes=30)

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
            next_time = self.next_event_time(event)
            unix = int(next_time.timestamp())
            event_list.append((event["name"], next_time, unix))

        # Sort by soonest
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
