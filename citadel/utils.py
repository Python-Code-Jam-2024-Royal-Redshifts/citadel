__all__ = ["sleep"]

import asyncio
from typing import ClassVar

import discord
from discord import ui

from citadel import globals


class Buttons(ui.View):
    __output: ClassVar[list[tuple[str, discord.Interaction]]] = []

    def create_callback(self, button: str) -> int:
        async def callback(interaction: discord.Interaction) -> None:
            self.__output.append((button, interaction))

        return callback

    def __init__(self, buttons: list[str | tuple[str, discord.ButtonStyle]]) -> None:
        super().__init__()

        for button in buttons:
            if type(button) is str:
                label = button
                style = discord.ButtonStyle.primary
            else:
                label = button[0]
                style = button[1]

            ui_button = ui.Button(label=label, style=style)
            ui_button.callback = self.create_callback(label)
            self.add_item(ui_button)

    def get_responses(self) -> list[tuple[str, discord.Interaction]]:
        output = []
        while len(self.__output) > 0:
            output.append(self.__output.pop(0))
        return output


async def get_openai_resp(msg: str) -> str:
    completion = globals.get_openai_client().chat.completions.create(
        model=globals.get_openai_model(),
        messages=[{"role": "user", "content": msg}],
    )
    return completion.choices[0].message.content


async def sleep(time: float = 0.5) -> None:
    """Sleep for a bit of time."""
    await asyncio.sleep(time)
