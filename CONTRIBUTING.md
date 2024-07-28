# Contributing
This document contains information for those wanting to contribute to Citadel. Read on to find out how you can help!

## Issues
There aren't many rules for creating issues at the moment. Feel free to create them as appropriate, and a team member will help you out.

## Code
This section outlines some helpful information for working with Citadel's codebase. This section is a work-in-progress (feel free to contribute!), though it should still be beneficial to get you going.

### Setup
Citadel uses Poetry for dependency management, which will likewise be crucial to your work on the codebase. You don't need to know the ins and outs of Poetry, and most relevant information is discussed below.

#### Setting up Poetry
See [Poetry's documentation](https://python-poetry.org/docs/#installation) for installation instructions. After you're done with that, you can set up Citadel's development environment:

```sh
poetry install
```

#### Running Citadel
After installing the project, you can run Citadel via the following command:

```sh
poetry run citadel
```

#### Running code linters
Citadel uses [Ruff](https://github.com/astral-sh/ruff) to format and check for issues in the codebase. This tool is automatically installed when you set up Poetry. To run the linters, run the following:

```sh
# Check the code for issues
poetry run ruff check

# Format the code according to Citadel's styling guidelines
poetry run ruff format
```

#### Setting up `pre-commit`
The `pre-commit` tool is used to ensure quality commits are made in the codebase and is also automatically installed when you set up Poetry. It runs the above code linters and ensures commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. To set it up, run the following:

```sh
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
```

The `pre-commit` tool will now check all changes automatically before committing them.
