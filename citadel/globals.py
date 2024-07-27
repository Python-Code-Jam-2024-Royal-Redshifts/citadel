"""Global values that can be used throughout the program."""

import logging
import os

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from openai import OpenAI
from rich.logging import RichHandler

_all_ = ["LOGGER", "OPENAI_CLIENT", "OPENAI_MODEL", "JINJA"]

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
OPENAI_CLIENT: OpenAI = OpenAI(api_key="XYZ")
OPENAI_MODEL: str = ""

# Jinja2
TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "templates",
)
JINJA = Environment(loader=FileSystemLoader(TEMPLATE_PATH), undefined=StrictUndefined)
