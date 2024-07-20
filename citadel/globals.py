"""Global values that can be used throughout the program."""

import logging

from rich.logging import RichHandler

_all_ = ["LOGGER"]

# Logger
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
LOGGER = logging.getLogger("rich")
