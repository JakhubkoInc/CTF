from datetime import timedelta
from pathlib import Path

TMP_DIR = Path("bin\\tmp")
TEMPLATES_DIR = Path("bin\\templates")
LANGS = ["CZE", "ENG"]

TEST_LIST_PARAM_FORMAT = "{gid}/{tid}/{taskName}"

# single files must have format: */<group id>.<task id>.*
# TODO: remove this (check for dependencies)
TEST_LIST = [
]

RUN_TIMEOUT = timedelta(seconds=5)

class Compilation:
    ARGS = ["-D__PROGTEST__", "-Wall", "-pedantic", "-fpermissive"]
    COMMAND = "g++"
    OUTPUT_FILE_ARG_NAME = "-o"
    PROGRAM_NAME = "program.exe"
