import discord
from discord.ext import commands
from discord import app_commands
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "huihui_ai/deepseek-r1-abliterated:7b"

SYSTEM_PROMPT = (
    "Your name is Zee. "
    "You are friendly, slightly witty, and helpful. "
    "You speak like a human, not like an AI."
)

class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ask",
        description="Ask Zee anything ✨"
    )
    async def ask(
        self,
        interaction: discord.Interaction,
        question: str
    ):
        # Prevent 'interaction failed'
        await interaction.response.defer(thinking=True)

        try:
            payload = {
                "model": MODEL,
                "prompt": f"{SYSTEM_PROMPT}\n\nUser: {question}\nZee:",
                "stream": False
            }

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=300  # DeepSeek can be slow
            )
            response.raise_for_status()

            data = response.json()
            reply = data.get("response", "").strip()

            if not reply:
                reply = "🤔 I didn’t get a clear response. Try again?"

            # Discord hard limit
            if len(reply) > 2000:
                reply = reply[:1990] + "..."

            await interaction.followup.send(reply)

        except requests.exceptions.Timeout:
            await interaction.followup.send(
                "⏳ I’m still thinking… that model is a bit heavy. Try again in a moment."
            )

        except Exception as e:
            print("Ollama error:", e)
            await interaction.followup.send(
                "⚠️ Zee couldn’t reach her brain right now. Is Ollama running?"
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
