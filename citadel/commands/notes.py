import discord
from discord import app_commands
from citadel.globals import OPENAI_CLIENT


@app_commands.command()
async def notes(interaction: discord.Interaction) -> None:
    """Generate notes from the current channel manually"""  # noqa: D400
    messages = []
    await interaction.response.send_message("Generating...")
    async for msg in interaction.channel.history():
        if msg.content.startswith("/"):
            continue
        if msg.author.name == "Citadel - joshdtbx":
            continue
        messages.append(msg)
    message_prompt_string = ""
    for msg in messages:
        message_prompt_string += msg.content + f" -{msg.author.name},"
    completion = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a study-bot who generates quizlet-like questions."},
            {
                "role": "user",
                "content": "Turn the following comma-delimited list into a plaintext JSON list with the 3 keys: "
                           "Question, Answer, Author. The Question key will be the main text of the string"
                           "with 1 term identified as the 'answer' and extracted from the text, replaced with a _. The Answer "
                           "key will be the extracted term from the question. The Author key will be the "
                           "username at the end of the string, denoted with a -. If the message does not contain a "
                           "fact or statement that we can use to create a meaningful study question,"
                           f"then skip that statement and move on to the next one.\n{message_prompt_string}",
            },
        ],
    )
    # print(completion.choices[0].message)
