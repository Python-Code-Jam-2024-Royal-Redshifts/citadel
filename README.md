<div align="center">
    <h1>Citadel</h1>
    <img src ="/assets/citadel.png" alt="Citadel profile image" height="200em">
    <br>
    <br>
    <p>Have you ever been overloaded by information you need to study? Do you need a method that's more interactive and enjoyable to use? Then Citadel is <em>the</em> Discord bot to use. It incorporates the best parts of services such as Quizlet and Kahoot, and combines them into a seamless interface that everyone can use (well, people that have Discord anyway).</p>
</div>

## Current features include:

#### Automatic test generation from chat history. No longer shall you manually type in your questions 🥳
<img src ="/assets/generate.gif" alt="Generate Command" height="250em">

#### Kahoot-styled quizzes. Challenge your friends to a game to see who really knows their stuff 🧑‍💻
<img src ="/assets/quiz.gif" alt="Quiz Command" height="250em">

## Running the bot
Setting up the bot is a fairly simple procedure, though it requires a few steps:

### 1. Download a copy of the Git repository
First, you'll need to clone the Git repository for the bot:

```bash
git clone 'https://github.com/Python-Code-Jam-2024-Royal-Redshifts/citadel'
```

### 2. Configuring the Guild ID
Next, you'll need to configure the guild ID for the bot in [`citadel/main.py`](https://github.com/Python-Code-Jam-2024-Royal-Redshifts/citadel/blob/cf42485bd8441b699d50c0b9489cc5466046b7b4/citadel/main.py#L15). Set it to the value of your server's Guild ID which can be found by:

- Right-clicking your server's icon in Discord
- Clicking on `Copy Server ID`

### 3. Creating a Discord bot
Next, you'll need to head to the [Discord Developer Portal](https://discord.com/developers/applications) and click `New Application` in the top right. Name the bot whatever you'd like; it won't change any future steps.

#### Installation
After creating the bot, go to the `Installation` tab and scroll down to `Default Install Settings`. Choose the `bot` scope and the `Manage Messages` permission.

Here, you'll also find the Install Link for the bot. Copy and paste the URL into a new browser tab, and add the bot to your server.

#### Bot Token
Next, go to the `Bot` tab and select the `Reset Token` button. **Make sure to copy the token down, as you'll need it later on**.

### 4. Setting up the bot environment
You're almost ready to run the bot. Make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed, and then run the following:

```python
poetry install --only main
```


### 5. Running the bot
There are a few environment variables needed to run the bot. Currently, those are:

- `CITADEL_DISCORD_TOKEN`: The Discord token you created above.
- `OPENAI_TOKEN` An [OpenAI API token](https://platform.openai.com/docs/api-reference/api-keys) to use in API requests.
- `OPENAI_MODEL`: The OpenAI model to use (defaults to GPT-4o).
- `OPENAI_BASE`: The OpenAI endpoint to use. Can be changed if you'd like to use an OpenAI-compatible service such as [Ollama](https://ollama.com/).
- `DB_PATH`: The path to the database Citadel should use (defaults to `./citadel.db`).
- `LOG_LEVEL` The amount of logging Citadel should show by default. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` (defaults to `INFO`).

These environment variables can be set when running Citadel, or in a file called `.env` in the root of the Git repository.

After setting up the environment variables, run the following and you'll be ready to go:

```bash
poetry run citadel
```

You can interact with the bot via slash commands, which can be seen by typing `/` into a Discord message box.

## Contributors
This project wouldn't be possible without the amazing work of the following individuals:

- [Joshtdbx](https://github.com/giplgwm): Development of test generation functionality
- [danman87](https://github.com/headlessdagger): Development of Docker functionality
- [hwittenborn](https://github.com/hwittenborn): Development of test generation/quiz/Docker functionality
- [juseraru](https://github.com/juseraru): Development of project outline, including implementations for test generation and Docker functionality
- [stephen](https://github.com/stuxf): Original idea for project, helped outline test generation and quiz functionality
