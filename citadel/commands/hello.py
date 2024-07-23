import discord
from discord import app_commands


@app_commands.command()
async def hello(interaction: discord.Interaction) -> None:
    """Say hello to the bot!"""  # noqa: D400
    await interaction.response.send_message(
        f"Hello {interaction.user.name}! The bot is online, and ready to serve :saluting_face:",
    )
