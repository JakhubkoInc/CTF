from pathlib import Path

from colour import Color

TASK_DIR_ID_NAME_DELIMETER = "_"
GROUP_DIR_ID_NAME_DELIMETER = "_"
# Can be found in task-group directory.
OPTIONAL_TEMPLATE_NAME = "template.json"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class Files:
    MARKDOWN_ASSETS_DIR_PATH = Path("assets\\markdown")
    PROJECT_DIR_ASSETS_DIR_NAME = "assets"
    TASK_DIR_TEST_DATA_DIR_NAME = "data"
    PROGRAM_NAME = "program.c"
    MD_NAME = "task.md"
    PASSED_LOCK_FILE_NAME = "passed.lock"
    DEFAULT_PROG = """#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define ERR_INPUT "Nespravny vstup.\\n"

int main(int argc, char** argv){

    return 0;
}
"""

    DEFAULT_MD = """
# {title}

## Deadline: {deadline}

### Points: {gotPoints}/{maxPoints} [{percentPoints}%]

---

{headerExtra}

---

{description}

---

{footer}

{scripts}

"""

class Scripts:
    DEADLINE_TIMEOUT = f'<script src=\"..\\..\\{Files.PROJECT_DIR_ASSETS_DIR_NAME}\\deadline_timeout.js"></script>  \n'
    FONTAWESOME = f'<script src=\"..\\..\\{Files.PROJECT_DIR_ASSETS_DIR_NAME}\\fontawesome.js"></script>  \n'
    AS_SRC = '<script src="{src}"></script>  \n'
    AS_JS = '<script>  \n{js}  \n</script> \n'
    
class Colors:
    NICE_RED = Color("#cc4d4d")
    NICE_GREEN = Color("#50c878")
    WHITE_SMOKE = Color("#d7dbd7")
    ORANGE = Color("#f59721")
    YELLOW = Color("#f7e800")
    
class Extras:
    SHOW_TEMPLATE_BUTTON = '[<i class="far fa-sticky-note"></i> show template](../template.json)'
    NORMALIZED_TESTING_DATA_NOT_FOUND = "Could not find normalized IO testing data. Downloaded resources have been copied to `data/`."
    LAST_UPDATE = f"Last update: {{lastUpdateDate:{DATETIME_FORMAT}}}"
    TESTS_OK = 'Tests OK'
    NL = "  \n"
    TESTS_SKIP = 'Tests SKIPPED'
    NO_TEST_DATA = 'No test data'
    FOUND_TESTING_SETS = "Found {setsLen} testing sets: {sets}"
    LINE = "  \n  \n---  \n  \n"
    RIGHTS = "© {year} Testprog, Kuba"
    DEADLINE_TIMEOUT_PLACEHOLDER = '<span id="timeout-placeholder"></span>'
    
class Style:
    FONT_BOLD = "font-weight:bold;"
    ALING_RIGHT = "text-align:right;"
