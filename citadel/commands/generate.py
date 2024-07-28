import json
from enum import Enum

import discord
from discord import app_commands, ui
from sqlmodel import Session

from citadel import globals, utils
from citadel.models import Question, Test

NOTES_PROMPT = globals.JINJA.get_template("prompts/NOTES.md")
EDITOR_CONFIRM_PROMPT = globals.JINJA.get_template("prompts/EDITOR-CONFIRM.md")
NOTES_CONFIRMATION = globals.JINJA.get_template("messages/NOTES-CONFIRMATION.md")
NOTES_CONFIRMATION_EDITOR = globals.JINJA.get_template("messages/NOTES-CONFIRMATION-EDITOR.md")


class ButtonChoice(Enum):
    """The clicked button in `Buttons`."""

    CREATE = 1
    EDIT = 2
    CANCEL = 3


class Buttons(ui.View):
    """The buttons we show in the test generation message."""

    __button: ButtonChoice | None = None
    __interaction: discord.Interaction | None = None

    async def set_reactive(self, interaction: discord.Interaction, reactive: bool) -> None:  # noqa: FBT001
        """Set if the buttons should be reactive (i.e. they can be clicked."""
        for child in self.children:
            if not isinstance(child, ui.Button):
                raise TypeError("Unexpected child in button")  # noqa: TRY003,EM101
            child.disabled = not reactive
            resp = await interaction.original_response()
            await resp.edit(view=self)

    @ui.button(label="Create Test", style=discord.ButtonStyle.green)
    async def create_callback(
        self,
        interaction: discord.Interaction,
        button: ui.Button,  # type: ignore[type-arg]  # noqa: ARG002
    ) -> None:
        """Handle clicking of the create test button."""
        self.__interaction = interaction
        self.__button = ButtonChoice.CREATE

    @ui.button(label="Edit Questions", style=discord.ButtonStyle.red)
    async def edit_callback(
        self,
        interaction: discord.Interaction,
        button: ui.Button,  # type: ignore[type-arg]  # noqa: ARG002
    ) -> None:
        """Handle clicking of the edit questions button."""
        self.__interaction = interaction
        self.__button = ButtonChoice.EDIT

    @ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(
        self,
        interaction: discord.Interaction,
        button: ui.Button,  # type: ignore[type-arg]  # noqa: ARG002
    ) -> None:
        """Handle clicking of the cancel button."""
        self.__interaction = interaction
        self.__button = ButtonChoice.CANCEL

    def get_resp(self) -> tuple[ButtonChoice, discord.Interaction] | None:
        """Get the clicked button and it's related interaction. Returns `None` if no button has been clicked."""
        if self.__button is None or self.__interaction is None:
            return None

        button = self.__button
        interaction = self.__interaction
        self.__button = None
        self.__interaction = None
        return (button, interaction)


class QuestionEditor(ui.Modal, title="Question Editor"):
    """Editor for the AI-generated questions."""

    __done: bool = False
    __interaction: discord.Interaction | None = None

    def __init__(self, question_text: str) -> None:
        """Create the editor UI, pre-filling it with the specified question list."""
        super().__init__()
        self.editor = ui.TextInput(
            label="Questions",
            style=discord.TextStyle.paragraph,
            default=question_text,
        )  # type: ignore[var-annotated]
        self.add_item(self.editor)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle the editor form being submitted."""
        self.__done = True
        self.__interaction = interaction

    def get_resp(self) -> tuple[str, discord.Interaction] | None:
        """Get the submitted text from the editor form. Returns `None` if it hasn't been submitted yet."""
        if not self.__done or self.__interaction is None:
            return None
        interaction = self.__interaction
        self.__done = False
        self.__interaction = None

        return (self.editor.value, interaction)


@app_commands.command()
@app_commands.describe(
    msg_filter="A query that describes the kind of messages you want to include from this channel "
    '(e.g. "Shakespeare Texts")',
    test_name='The name you want to assign the generated test (e.g. "The Renaissance")',
)
async def generate(  # noqa: C901
    interaction: discord.Interaction,
    msg_filter: str,
    test_name: str,
) -> None:
    """Generate test questions"""  # noqa: D400
    await interaction.response.defer()

    if type(interaction.channel) is not discord.TextChannel:
        raise RuntimeError("Unexpected channel type")  # noqa: TRY003,EM101
    messages = [
        msg.content
        async for msg in interaction.channel.history()
        if not msg.content.startswith("/") and interaction.user != interaction.client.user
    ]

    completion = await utils.get_openai_resp(NOTES_PROMPT.render(messages=messages, msg_filter=msg_filter))
    output = json.loads(completion)

    buttons = Buttons()
    message = await interaction.followup.send(
        NOTES_CONFIRMATION.render(notes=output, test_name=test_name),
        view=buttons,
        wait=True,
    )

    buttons_resp = None
    while True:
        # Wait until we get a button click.
        while buttons_resp is None:
            await utils.sleep()
            buttons_resp = buttons.get_resp()

        # Parse buttons, blah blah we'll add better comments in a bit
        chosen_button, buttons_interaction = buttons_resp
        buttons_resp = None
        if chosen_button == ButtonChoice.CREATE:
            with Session(globals.get_sql_engine()) as session:
                test = Test(name=test_name)
                session.add(test)
                session.commit()

                for item in output:
                    question = Question(question=item["question"], answer=item["answer"], test_id=test.id)
                    session.add(question)
                session.commit()

            await message.edit(content=f'The test for "{test_name}" has been created :pencil:', view=None)

        elif chosen_button == ButtonChoice.EDIT:
            editor = QuestionEditor(NOTES_CONFIRMATION_EDITOR.render(notes=output))
            await buttons_interaction.response.send_modal(editor)

            # Wait until the user clicks submit, or they click a different button (which would happen if they closed
            # out of the model)
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
            await buttons.set_reactive(buttons_interaction, False)  # noqa: FBT003
            await message.edit(content="Processing question list...")
            await editor_interaction.response.defer()

            completion = await utils.get_openai_resp(EDITOR_CONFIRM_PROMPT.render(question_data=editor_output))
            output = json.loads(completion)
            await message.edit(content=NOTES_CONFIRMATION.render(notes=output, test_name=test_name))
            await buttons.set_reactive(buttons_interaction, True)  # noqa: FBT003

        elif chosen_button == ButtonChoice.CANCEL:
            await message.delete()
            break
