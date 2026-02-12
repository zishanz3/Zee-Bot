import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_events(self):
        url = "https://sky-clock.netlify.app/"
        results = []

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()

        # Extract event rows directly from the HTML table
        pattern = re.findall(
            r'<tr class="event">.*?<td.*?</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>',
            html,
            re.DOTALL
        )

        for name, next_time, time_to_next in pattern:
            results.append((
                name.strip(),
                next_time.strip(),
                time_to_next.strip()
            ))

        return results

    def to_discord_timestamp(self, time_str: str):
        now_ist = datetime.now(IST)

        hour, minute = map(int, time_str.split(":"))
        event_time = now_ist.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        if event_time < now_ist:
            event_time += timedelta(days=1)

        unix_ts = int(event_time.timestamp())

        return f"<t:{unix_ts}:t>"

    @app_commands.command(
        name="events",
        description="Show upcoming Sky events (auto local time)"
    )
    async def events(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            data = await self.fetch_events()

            if not data:
                await interaction.followup.send("❌ Failed to fetch events.")
                return

            embed = discord.Embed(
                title="✨ Upcoming Events (Wax)",
                color=discord.Color.blurple()
            )

            for name, next_time, remaining in data:

                if ":" in next_time:
                    local_time = self.to_discord_timestamp(next_time)
                else:
                    local_time = next_time

                embed.add_field(
                    name=name,
                    value=(
                        f"🕒 **Next:** {local_time}\n"
                        f"⏳ **In:** `{remaining}`"
                    ),
                    inline=True
                )

            embed.set_footer(
                text="Times automatically convert to your local timezone"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print("Events error:", e)
            await interaction.followup.send("❌ Error fetching events.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
