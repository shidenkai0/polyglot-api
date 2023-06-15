from glob import glob

import pytest
from pytest_asyncio.plugin import event_loop

# Load all fixtures from all files in any fixtures directory in the tests directory
pytest_plugins = [
    fixture_file.replace("/", ".").replace(".py", "")
    for fixture_file in glob("tests/**/fixtures/[!__]*.py", recursive=True)
]
