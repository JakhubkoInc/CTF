from .template import Template, TemplateMeta, payload
from pathlib import Path
from typing import Union
from .. import auxiliary
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ...tools.project_dir_gen import TodoItem



class PytestReportTemplate(Template, metaclass=TemplateMeta):
  
  @payload("testsRan", 0)
  def tests_ran(self, count) -> int:
    "Number of tests ran."
    return int(count)
  
  @payload("reportPath","")
  def report_path(self, path:Union[str,Path]) -> Path:
    "Path to pytest xml report."
    return str(path)

  @payload("passedVersions", [])
  def passed_versions(self, versions:Union[str, list[str]]) -> list[str]:
    "String hashes of passed versions of tested source code."
    if isinstance(versions, list):
      return versions
    elif isinstance(versions, str):
      return [versions]
    else:
      raise TypeError("Value can be only string or list of strings.")


class MarkdownTemplate(Template, metaclass=TemplateMeta):
  
  @payload("headerExtra",[])
  def header(self, header:Union[str, list[str]]) -> list[str]:
    "Extra header markdown to be inserted into task.md file."
    if isinstance(header, list):
      return header
    else:
      return [header]
  
  @payload("footer",[])
  def footer(self, footer) -> list[str]:
    "Footer markdown to be inserted into task.md file."
    if isinstance(footer, list):
      return footer
    else:
      return [footer]
  
  
class TaskTemplate(Template, metaclass=TemplateMeta):
  
  id = ""

  @payload("points", (0,-1))
  def points(self, tuple:tuple[int,int]) -> tuple[int,int]:
    "`Tuple` containing gained points / max points"
    assert tuple[1] >= 0, "Max possible points should be at least zero or bigger." 
    return tuple
  
  @payload("md", MarkdownTemplate())
  def markdown(self, template:'MarkdownTemplate') -> 'MarkdownTemplate':
    "Markdown template"
    return template
  
  @payload("pytest", PytestReportTemplate())
  def pytest(self, template:'PytestReportTemplate') -> 'PytestReportTemplate':
    "Pytest report"
    return template
  
  @payload("todo", [])
  def todolist(self, todo:Union[tuple, list[tuple]]) -> list[tuple]:
    "List of todo items metadata."
    if isinstance(todo, list):
      return todo
    else:
      return [todo]
  
  @payload("data", {})
  def testing_sets(self, sets) -> dict[str,list[dict[str,str]]]:
    "Dictionary of testing sets"
    assert isinstance(sets, dict), "Testing sets should have a specific format."
    return sets
  
  @payload("title","")
  def title(self, title) -> str:
    "Title of the task"
    return str(title)
  
  @payload("deadline","")
  def deadline(self, date) -> str:
    "Deadline"
    return str(date)
  
  @payload("description","")
  def description(self, desc) -> str:
    "Description of the task"
    return str(desc)

  def add_todo(self, item:'TodoItem'):
    self.todolist().append((str(item.action), item.args, item.kwargs))
  


  