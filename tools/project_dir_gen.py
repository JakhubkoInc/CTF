import os
import pickle
import shutil
from distutils.dir_util import copy_tree
from enum import Enum
from pathlib import Path

import testprog_common.conf.testing as tcfg
import testprog_common.lib.auxiliary as Auxiliary
from testprog_common.conf import Environment
from testprog_common.conf.projectdir import *

from .task_md import update_task_md
from testprog_common.lib.templating.progtest import ProgtestTaskGroupTemplate


class TodoItemAction(Enum):
    
    # accepts kwarg 'dst' - destination where to copy
    COPY_TREE = 1
    REMOVE = 2
    MOVE = 3 
    
class TodoItem:
    """
    Represents IO action to be done when updating project directory. 
     
    ---
    
    * COPY_TREE
       * copy source directory to <task dir>/data/
       * arguments:  
              * src[str]  ... source directory
    * REMOVE
       * removes directory
       * arguments:
              * path[str] ... path to directory
            
    """

    def __init__(self, action: TodoItemAction, *args, **kwargs):
        self.action = action
        self.args = args
        self.kwargs = kwargs
    
    def do(self, **kwargs):
        self.kwargs.update(kwargs)
        try:
            if self.action == TodoItemAction.COPY_TREE:
                if "dst" in self.kwargs and not os.path.exists(self.kwargs["dst"]):
                    os.makedirs(self.kwargs["dst"], exist_ok=True)
                copy_tree(*self.args, **self.kwargs)
            elif self.action == TodoItemAction.REMOVE:
                os.remove(*self.args, **self.kwargs)
            elif self.action == TodoItemAction.MOVE:
                shutil.move(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Project todoitem: Could not {self.action.name}:\n{e}")
    
    def __str__(self):
        return str(pickle.dumps(self))


def prepare_project_dir(path=os.getenv(Environment.TESTS_DIR_NAME), force_md_update=False, overwrite_templates=False):
    
    print(f" > Preparing project dir {path}")
    
    template_ids = [Path(file).stem for file in Auxiliary.list_file_paths(tcfg.TEMPLATES_DIR) if Path(file).suffix == ".json"]
    
    # copy markdown js assets to project dir
    try:
        assets_path = Path(path)/Files.PROJECT_DIR_ASSETS_DIR_NAME
        if os.path.exists(assets_path):
            shutil.rmtree(assets_path)
        shutil.copytree(Files.MARKDOWN_ASSETS_DIR_PATH,assets_path)
    except Exception as e:
        print(f"Could not copy assets. {e}")


    for template_id in template_ids:
        
        template_path = Path(tcfg.TEMPLATES_DIR) / f"{template_id}.json"
        group_template = ProgtestTaskGroupTemplate.from_json(template_path)
        project_dir_path = Path(path) / f"{template_id}_{Auxiliary.sanitize_str(group_template.title)}"
        optional_template_path:Path = project_dir_path / OPTIONAL_TEMPLATE_NAME
        

        if not os.path.exists(project_dir_path):
            os.mkdir(f"{project_dir_path}")
            
        if overwrite_templates or not optional_template_path.exists():
            shutil.copy2(template_path, optional_template_path)
        else:
            Auxiliary.update_json_file(optional_template_path, group_template)
        
        for task_id in group_template.tasks():
            task_dir_path = Path(project_dir_path) / f"{task_id}_{Auxiliary.sanitize_str(group_template.tasks()[task_id].title)}"
            md_path = task_dir_path / Files.MD_NAME
            task_program_path = task_dir_path / Files.PROGRAM_NAME

            # Setup task directory.
            if not task_dir_path.exists():
                os.mkdir(task_dir_path)

            # Create 'program.c' file. 
            if not task_program_path.exists():
                with open(task_program_path, 'w') as f:
                    f.write(Files.DEFAULT_PROG)
            else:
                print(f"{task_program_path} already exists.")

            # Create or update 'task.md' file.
            if not os.path.exists(md_path) or force_md_update:
                update_task_md(md_path, group_template.tasks()[task_id], task_dir_path)
            else:
                print(f"{md_path} already exists.")
            
            # Fulfil addition todolist.
            while len(group_template.tasks()[task_id].todolist) > 0:
                todo_args = group_template.tasks()[task_id].todolist.pop()
                try:
                    item:TodoItem = TodoItem(*todo_args)
                    item.do(dst=str(task_dir_path / Files.TASK_DIR_TEST_DATA_DIR_NAME))
                except Exception as e:
                    print(f"Prepare project dir: could not load TodoItem: {todo_args}\n{e}.")

                