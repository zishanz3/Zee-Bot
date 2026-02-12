import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def now_ist(self):
        return datetime.now(IST)

    def next_interval_event(self, minute, interval, hour_offset=0):
        now = self.now_ist()

        # Anchor from midnight with optional hour offset
        base = now.replace(hour=hour_offset, minute=minute, second=0, microsecond=0)

        while base <= now:
            base += timedelta(hours=interval)

        return base

    @app_commands.command(name="events", description="Shows upcoming event times")
    async def events(self, interaction: discord.Interaction):

        now = self.now_ist()

        # ✅ Correct schedules
        turtle = self.next_interval_event(minute=20, interval=2, hour_offset=0)
        grandma = self.next_interval_event(minute=5, interval=2, hour_offset=0)
        geyser = self.next_interval_event(minute=35, interval=2, hour_offset=1)

        # 🔥 Daily Reset at 13:30 IST
        reset = now.replace(hour=13, minute=30, second=0, microsecond=0)
        if reset <= now:
            reset += timedelta(days=1)

        events = [
            ("Turtle", turtle),
            ("Grandma", grandma),
            ("Geyser", geyser),
            ("Daily Reset", reset)
        ]

        events.sort(key=lambda x: x[1])

        embed = discord.Embed(
            title="🌍 Upcoming Events",
            description="Times shown in your local timezone.",
            color=discord.Color.blue()
        )

        for name, time in events:
            unix = int(time.timestamp())
            embed.add_field(
                name=name,
                value=f"🕒 Next: <t:{unix}:F>\n⏳ Starts: <t:{unix}:R>",
                inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
