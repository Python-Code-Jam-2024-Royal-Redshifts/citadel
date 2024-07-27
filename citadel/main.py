import logging
from enum import Enum
from typing import Annotated

import discord
import typer
from discord import app_commands
from dotenv import load_dotenv

from citadel import commands, globals

APP = typer.Typer()
GUILD_ID = discord.Object(id=1262512524541296640)


class LogLevel(str, Enum):
    """The log level used for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CitadelClient(discord.Client):
    """The Citadel Discord Client."""

    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """Ensure the slash commands have been synced to our guild.

        Without specifying our guild, it can take up to an hour for slash commands to sync.
        """
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)


@APP.command()
def main(
    discord_token: Annotated[str, typer.Argument(envvar="CITADEL_DISCORD_TOKEN")],
    openai_token: Annotated[str, typer.Argument(envvar="OPENAI_TOKEN")],
    openai_model: Annotated[str, typer.Argument(envvar="OPENAI_MODEL")] = "gpt-4o",
    log_level: Annotated[LogLevel, typer.Argument(case_sensitive=False, envvar="LOG_LEVEL")] = LogLevel.INFO,
) -> None:
    """Citadel Discord bot.

    Environment variables can be set via the command-line, or in a file named `.env`.
    """
    globals.LOGGER.setLevel(logging.getLevelName(log_level.value))
    globals.OPENAI_CLIENT.api_key = openai_token
    globals.OPENAI_MODEL = openai_model

    # Set up the client, add commands, and start.
    client = CitadelClient()
    client.tree.add_command(commands.hello)
    client.tree.add_command(commands.generate)

    client.run(discord_token)


def entrypoint() -> None:
    """Entrypoint of the application, used when running `./main.py` and for the Poetry config."""
    load_dotenv()
    APP()


if __name__ == "__main__":
    entrypoint()
