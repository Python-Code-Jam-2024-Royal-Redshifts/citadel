import os
import sys

import discord
from discord import app_commands
from dotenv import load_dotenv

from citadel import commands
from citadel.globals import LOGGER

GUILD_ID = discord.Object(id=1262512524541296640)


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


def main() -> int:
    """Program entrypoint."""
    load_dotenv()
    token = os.environ.get("CITADEL_DISCORD_TOKEN")

    if not token:
        LOGGER.error(
            "No Discord client secret was detected. Set the [green]`CITADEL_DISCORD_TOKEN`[/green] environment"
            "variable to the secret's value.",
        )
        return os.EX_NOINPUT

    # Set up the client, add commands, and start.
    client = CitadelClient()
    client.tree.add_command(commands.hello)
    client.run(token)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
