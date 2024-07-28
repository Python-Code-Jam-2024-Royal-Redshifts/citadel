import json
import math
from dataclasses import dataclass
from enum import StrEnum

import dacite
import discord
import sqlmodel
from discord import app_commands
from sqlmodel import Session

from citadel import globals, utils
from citadel.models import Question, Test

QUIZ_PROMPT = globals.JINJA.get_template("prompts/QUIZ.md")
QUIZ_PLAYERS = globals.JINJA.get_template("messages/QUIZ-PLAYERS.md")
QUIZ_QUESTION = globals.JINJA.get_template("messages/QUIZ-QUESTION.md")
QUIZ_OVERVIEW = globals.JINJA.get_template("messages/QUIZ-OVERVIEW.md")
QUIZ_RESULTS = globals.JINJA.get_template("messages/QUIZ-RESULTS.md")


LOBBY_STARTING_TIME = 2
QUESTION_TIME = 10
OVERVIEW_TIME = 5


class TestLauncherButtons(StrEnum):
    """Possible buttons when launching a test."""

    START = "Start"
    JOIN = "Join"
    LEAVE = "Leave"


@dataclass
class GameQuestion:
    """The format for game questions from ChatGPT."""

    question: str
    incorrect_answers: list[str]
    correct_answer: str


class PlayerStats:
    """The stastistics of a player during a quiz session."""

    points = 0
    correct = 0


def generate_leaderboard(
    game_players: dict[discord.User | discord.Member, PlayerStats],
) -> list[list[tuple[discord.User | discord.Member, PlayerStats]]]:
    """Generate the leaderboards from the list of game statistics."""
    leaderboard: list[list[tuple[discord.User | discord.Member, PlayerStats]]] = [[], [], [], [], []]
    player_placement = list(game_players.items())
    player_placement.sort(reverse=True, key=lambda player: player[1].points)

    for player in player_placement:
        for leaderboard_index in range(5):
            points = [player[1].points for player in leaderboard[leaderboard_index]]

            if len(leaderboard[leaderboard_index]) == 0 or player[1].points in points:
                leaderboard[leaderboard_index].append(player)
                break

    return leaderboard


def get_tests() -> list[Test]:
    """Get the list of tests in the database."""
    with Session(globals.SQL_ENGINE) as session:
        statement = sqlmodel.select(Test)
        tests = session.exec(statement)

    return list(tests)


































async def quiz_options(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:  # noqa: ARG001
    """Filter the autocompletions to any quizzes that start with the user's query."""
    return [
        app_commands.Choice(name=test.name, value=test.name) for test in get_tests() if test.name.startswith(current)
    ]


@app_commands.command()
@app_commands.autocomplete(name=quiz_options)
async def quiz(
    interaction: discord.Interaction,
    name: str,
) -> None:
    """Take a quiz with friends"""  # noqa: D400
    test = next((test for test in get_tests() if test.name == name), None)
    if test is None:
        await interaction.response.send_message(f'The test for "{name}" doesn\'t exist.')
        return
    await interaction.response.defer()

    with Session(globals.SQL_ENGINE) as session:
        statement = sqlmodel.select(Question).where(Question.test_id == test.id)
        db_questions = [
            {"question": question.question, "answer": question.answer} for question in session.exec(statement)
        ]

    completion = await utils.get_openai_resp(QUIZ_PROMPT.render(questions=json.dumps(db_questions)))
    test_questions = [dacite.from_dict(data_class=GameQuestion, data=question) for question in json.loads(completion)]

    test_title = f"Quiz Launcher: {name}"
    players = [interaction.user]
    def render_launcher_waiting() -> None:
        discord.Embed(
            title=test_title,
            description=QUIZ_PLAYERS.render(players=[player.display_name for player in players]),
        )
    def render_launcher_starting(countdown: int) -> None:
        discord.Embed(
            title=test_title,
            description="***Starting quiz in {countdown} {second}...***".format(
                countdown=countdown,
                second="seconds" if countdown != 1 else "second",
            ),
        )
    test_buttons = utils.Buttons(
        [
            (TestLauncherButtons.START.value, discord.ButtonStyle.primary),
            (TestLauncherButtons.JOIN.value, discord.ButtonStyle.green),
            (TestLauncherButtons.LEAVE.value, discord.ButtonStyle.red),
        ],
    )
    message = await interaction.followup.send(embed=render_launcher_waiting(), view=test_buttons, wait=True)

    quiz_confirmed = False
    countdown = LOBBY_STARTING_TIME

    while True:
        if quiz_confirmed:
            break
        await utils.sleep()

        for button, button_interaction in test_buttons.get_responses():
            match button:
                case TestLauncherButtons.START.value:
                    if button_interaction.user != players[0]:
                        await button_interaction.response.send_message(
                            f"Only {players[0].display_name} can start the quiz.",
                            ephemeral=True,
                        )
                    else:
                        await button_interaction.response.edit_message(
                            embed=render_launcher_starting(countdown),
                            view=None,
                        )
                        quiz_confirmed = True
                        break
                case TestLauncherButtons.JOIN.value:
                    if button_interaction.user in players:
                        await button_interaction.response.send_message(
                            content="You've already joined the quiz. Make sure you're ready to win!",
                            ephemeral=True,
                        )
                    else:
                        players.append(button_interaction.user)
                        await button_interaction.response.edit_message(embed=render_launcher_waiting())
                case TestLauncherButtons.LEAVE.value:
                    if button_interaction.user not in players:
                        await button_interaction.response.send_message(
                            content="You're not in the quiz right now.",
                            ephemeral=True,
                        )
                    else:
                        players.remove(button_interaction.user)
                        await button_interaction.response.edit_message(embed=render_launcher_waiting())

                        if len(players) == 0:
                            await utils.sleep(1)
                            await button_interaction.message.delete()
                            quiz_confirmed = True
                            break

    while countdown > 0:
        await utils.sleep(1)
        countdown -= 1
        await message.edit(embed=render_launcher_starting(countdown))

    # Start the game.
    game_players = {player: PlayerStats() for player in players}
    points = math.floor(1000 / len(players)) if len(players) != 1 else 1000

    for question_index, question in enumerate(test_questions):
        answers = question.incorrect_answers
        answers.append(question.correct_answer)

        question_buttons = utils.Buttons(answers)
        seconds_left = QUESTION_TIME
        answered: dict[discord.User | discord.Member, str] = {}
        def render_question() -> None:
            discord.Embed(
                description=QUIZ_QUESTION.render(
                    question=question.question,  # noqa: B023
                    seconds_left=seconds_left,  # noqa: B023
                    players_answered=len(answered),  # noqa: B023
                    players_total=len(players),
                ),
            )

        while seconds_left > 0 and len(answered) != len(game_players):
            for button, button_interaction in question_buttons.get_responses():
                if button_interaction.user in answered:
                    await button_interaction.response.send_message(
                        f'You already submitted your answer of "{answered[button_interaction.user]}".',
                        ephemeral=True,
                    )
                    continue

                if button == question.correct_answer:
                    game_players[button_interaction.user].points += points * (len(players) - len(answered))
                    game_players[button_interaction.user].correct += 1

                answered[button_interaction.user] = button
                await button_interaction.response.edit_message(embed=render_question())

            await utils.sleep(1)
            seconds_left -= 1
            await message.edit(embed=render_question(), view=question_buttons)

        leaderboard = generate_leaderboard(game_players)
        countdown = OVERVIEW_TIME

        question_number = question_index + 1
        if question_number == len(test_questions):
            await message.edit(
                embed=discord.Embed(
                    description=QUIZ_RESULTS.render(leaderboard=leaderboard, question_total=len(test_questions)),
                ),
                view=None,
            )
            break

        while countdown > 0:
            await message.edit(
                embed=discord.Embed(
                    description=QUIZ_OVERVIEW.render(
                        question_number=question_index + 1,
                        question_total=len(test_questions),
                        leaderboard=leaderboard,
                        seconds=countdown,
                    ),
                ),
                view=None,
            )
            await utils.sleep(1)
            countdown -= 1
