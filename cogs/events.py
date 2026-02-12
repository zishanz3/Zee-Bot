import discord
from discord.ext import commands
from discord import app_commands
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import subprocess
import os


IST = ZoneInfo("Asia/Kolkata")


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.browser_ready = False

    async def ensure_browser(self):
        """
        Installs Chromium at runtime if not already installed.
        This fixes Railway cache issues permanently.
        """
        if not self.browser_ready:
            subprocess.run(["playwright", "install", "chromium"])
            self.browser_ready = True

    async def fetch_events(self):
        await self.ensure_browser()

        url = "https://sky-clock.netlify.app/"
        results = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )

                page = await browser.new_page()
                await page.goto(url, timeout=60000)

                await page.wait_for_selector("tr.event", timeout=15000)

                rows = await page.query_selector_all("tr.event")

                for row in rows:
                    cols = await row.query_selector_all("td")
                    if len(cols) < 4:
                        continue

                    name = (await cols[1].inner_text()).strip()
                    next_time = (await cols[2].inner_text()).strip()
                    remaining = (await cols[3].inner_text()).strip()

                    results.append((name, next_time, remaining))

                await browser.close()

        except Exception as e:
            print("Playwright error:", e)

        return results

    def to_discord_timestamp(self, time_str: str):
        try:
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
        except Exception:
            return time_str

    @app_commands.command(
        name="events",
        description="Show upcoming Sky events"
    )
    async def events(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

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

        embed.set_footer(text="Times auto convert to your local timezone")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
