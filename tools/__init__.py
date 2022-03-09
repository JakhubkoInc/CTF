# Quite the same as 'lib' module but have more robust implementation & use IO e.g. file generators

__ALL__ = ["project_dir", "task_md", "templating", "logger_gen"]

from .project_dir_gen import prepare_project_dir
from .task_md import update_task_md
