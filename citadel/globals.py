"""Global values that can be used throughout the program."""

import logging
from pathlib import Path

import inflect
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from openai import OpenAI
from rich.logging import RichHandler
from sqlalchemy import Engine

_all_ = ["LOGGER", "INFLECT", "JINJA", "get_openai_client", "get_openai_model", "get_sql_engine"]

# Logger
logging.basicConfig(
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
LOGGER = logging.getLogger("rich")

# OpenAI client
#
# The API key and model name get set in `main::main`
OPENAI_CLIENT: OpenAI | None = None
OPENAI_MODEL: str | None = None
UNINITIALIZED_ERR = "Variable hasn't been initalized yet"


def get_openai_client() -> OpenAI:
    """Get the global OpenAI client."""
    if OPENAI_CLIENT is None:
        raise NameError(UNINITIALIZED_ERR)
    return OPENAI_CLIENT


def get_openai_model() -> str:
    """Get the global OpenAI model."""
    if OPENAI_MODEL is None:
        raise NameError(UNINITIALIZED_ERR)
    return OPENAI_MODEL


# SQLModel engine
#
# The engine gets set in `main::main`
SQL_ENGINE: Engine | None = None


def get_sql_engine() -> Engine:
    """Get the global SQLAlchemy engine."""
    if SQL_ENGINE is None:
        raise NameError(UNINITIALIZED_ERR)
    return SQL_ENGINE


# Jinja2
TEMPLATE_PATH = Path(__file__).parent / "templates"
JINJA = Environment(loader=FileSystemLoader(TEMPLATE_PATH), undefined=StrictUndefined)  # noqa: S701

# Inflect
INFLECT = inflect.engine()
