import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Base Schedule (original times BEFORE +30 shift)
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

    def now_ist(self):
        return datetime.now(IST)

    def get_next_occurrence(self, event):
        now = self.now_ist()

        # 🟣 DAILY RESET (fixed time)
        if event["interval"] is None:
            next_time = now.replace(
                hour=event["hour"],
                minute=event["minute"],
                second=0,
                microsecond=0
            )
            if next_time <= now:
                next_time += timedelta(days=1)

        # 🟡 EVENTS WITH FIXED START HOUR (e.g., Rainbow)
        elif event.get("hour") is not None:
            base_hour = event["hour"]
            interval = event["interval"]

            next_time = now.replace(
                hour=base_hour,
                minute=event["minute"],
                second=0,
                microsecond=0
            )

            while next_time <= now:
                next_time += timedelta(hours=interval)

        # 🔵 STANDARD INTERVAL EVENTS (every X hours at specific minute)
        else:
            interval = event["interval"]
            minute = event["minute"]

            current_hour = now.hour

            # Find next aligned interval hour
            if current_hour % interval == 0 and now.minute < minute:
                next_hour = current_hour
            else:
                next_hour = ((current_hour // interval) + 1) * interval

            # Handle 24-hour overflow
            next_day = False
            if next_hour >= 24:
                next_hour -= 24
                next_day = True

            next_time = now.replace(
                hour=next_hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            if next_day:
                next_time += timedelta(days=1)

        # ✅ ADD +30 MINUTES TO EVERYTHING
        next_time += timedelta(minutes=30)

        return next_time

    @app_commands.command(name="events", description="Shows upcoming event times")
    async def events(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🌍 Upcoming Events",
            description="Times are shown in your local timezone automatically.",
            color=discord.Color.blue()
        )

        event_list = []

        for event in self.events:
            next_time = self.get_next_occurrence(event)
            unix = int(next_time.timestamp())
            event_list.append((event["name"], next_time, unix))

        # Sort by soonest event
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
