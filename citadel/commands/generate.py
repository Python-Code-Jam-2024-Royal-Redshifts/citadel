import json
from enum import Enum

import discord
from discord import app_commands, ui

from citadel import globals, utils

NOTES_PROMPT = globals.JINJA.get_template("prompts/NOTES.md")
EDITOR_CONFIRM_PROMPT = globals.JINJA.get_template("prompts/EDITOR-CONFIRM.md")
NOTES_CONFIRMATION = globals.JINJA.get_template("messages/NOTES-CONFIRMATION.md")
NOTES_CONFIRMATION_EDITOR = globals.JINJA.get_template("messages/NOTES-CONFIRMATION-EDITOR.md")


class NotesButton(Enum):
    CREATE = 1
    EDIT = 2
    CANCEL = 3


class NotesView(ui.View):
    __button: NotesButton | None = None
    __interaction: discord.Interaction | None = None

    async def set_reactive(self, interaction: discord.Interaction, reactive: bool):
        for child in self.children:
            child.disabled = not reactive
            resp = await interaction.original_response()
            await resp.edit(view=self)

    @ui.button(label="Create Test", style=discord.ButtonStyle.green)
    async def create_callback(self, interaction: discord.Interaction, button: ui.Button):
        self.__interaction = interaction
        self.__button = NotesButton.CREATE

    @ui.button(label="Edit Questions", style=discord.ButtonStyle.red)
    async def edit_callback(self, interaction: discord.Interaction, button: ui.Button):
        self.__interaction = interaction
        self.__button = NotesButton.EDIT

    @ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, interaction: discord.Interaction, button: ui.Button):
        self.__interaction = interaction
        self.__button = NotesButton.CANCEL

    def resp_available(self) -> bool:
        return self.__button is not None

    def get_resp(self) -> tuple[NotesButton, discord.Interaction] | None:
        if self.__button is None:
            return None

        button = self.__button
        self.__button = None
        return (button, self.__interaction)


class NotesEditor(ui.Modal, title="Question Editor"):
    __done: bool = False
    __interaction: discord.Interaction | None = None

    def __init__(self, question_text):
        super().__init__()
        self.editor = ui.TextInput(
            label="Questions",
            style=discord.TextStyle.paragraph,
            default=question_text,
        )
        self.add_item(self.editor)

    async def on_submit(self, interaction: discord.Interaction):
        self.__done = True
        self.__interaction = interaction

    def get_resp(self) -> tuple[str, discord.Interaction] | None:
        if not self.__done:
            return None
        self.__done = False

        return (self.editor.value, self.__interaction)


@app_commands.command()
async def generate(
    interaction: discord.Interaction,
    msg_filter: str,
    test_name: str,
) -> None:
    """Generate test questions"""  # noqa: D400
    messages = []
    await interaction.response.defer()

    async for msg in interaction.channel.history():
        if not msg.content.startswith("/") and interaction.user != interaction.client.user:
            messages.append(msg.content)

    completion = globals.OPENAI_CLIENT.chat.completions.create(
        model=globals.OPENAI_MODEL,
        messages=[
            {"role": "user", "content": NOTES_PROMPT.render(messages=messages, msg_filter=msg_filter)},
        ],
    )

    try:
        output = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError as err:
        await interaction.followup.send("There was an error generating the notes. Please try again.")
        raise err

    buttons = NotesView()
    message = await interaction.followup.send(
        NOTES_CONFIRMATION.render(notes=output, test_name=test_name), view=buttons
    )

    while True:
        # Wait until we get a button click.
        buttons_resp = None
        while buttons_resp is None:
            await utils.sleep()
            buttons_resp = buttons.get_resp()

        # Parse buttons, blah blah we'll add better comments in a bit
        chosen_button, buttons_interaction = buttons_resp
        if chosen_button == NotesButton.CREATE:
            await message.edit(content=f'The test for "{test_name}" has been created :pencil:', view=None)

        elif chosen_button == NotesButton.EDIT:
            editor = NotesEditor(NOTES_CONFIRMATION_EDITOR.render(notes=output))
            await buttons_interaction.response.send_modal(editor)

            # Wait until the user clicks submit, or they click a different button (which would happen if they closed out of the model)
            editor_resp = None
            while editor_resp is None:
                await utils.sleep()
                buttons_resp = buttons.get_resp()

                # If a new button has been pressed, we need to break the loop so we can process it
                if buttons_resp is not None:
                    break
                editor_resp = editor.get_resp()

            # If a new button was pressed, we need to continue the main `while` loop so we can process it
            if buttons_resp is not None:
                continue

            editor_output, editor_interaction = editor_resp
            await buttons.set_reactive(buttons_interaction, False)
            await message.edit(content="Processing question list...")
            await editor_interaction.response.defer()

            completion = globals.OPENAI_CLIENT.chat.completions.create(
                model=globals.OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": EDITOR_CONFIRM_PROMPT.render(question_data=editor_output)},
                ],
            )

            try:
                output = json.loads(completion.choices[0].message.content)
                await message.edit(content=NOTES_CONFIRMATION.render(notes=output, test_name=test_name))
                await buttons.set_reactive(buttons_interaction, True)
            except json.JSONDecodeError as err:
                await interaction.followup.send("There was an error generating the notes. Please try again.")
                raise err

        elif chosen_button == NotesButton.CANCEL:
            await message.delete()
            break
