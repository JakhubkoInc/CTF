
import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Union

from testprog_common.lib import auxiliary

from .pytest import TaskTemplate
from .template import Template, TemplateMeta, payload


class ProgtestTaskGroupTemplate(Template, metaclass=TemplateMeta): 
  
  DEADLINE_FORMAT = '%d.%m.%Y %H:%M:%S'
  
  @payload("title", None)
  def title(self, title) -> str:
    "Taskgroup title"
    assert isinstance(title, str), "The title argument must be of type str."
    return title
  
  @payload("id", -1)
  def ID(self, id:str):
    "Taskgroup id"
    assert isinstance(id, str), "The id argument must be of type str."
    return id
  
  @payload("deadline", None)
  def deadline(self, deadline:Union[str, datetime]):
    """Taskgroup deadline

    :param deadline: deadline date, if passed as a str it will be formatted to datetime in format `{ProgtestTaskGroupTemplate.DEADLINE_FORMAT}`
    :type deadline: Union[str, datetime]
    :return: [description]
    :rtype: str
    """
    
    if isinstance(deadline, datetime):
      return str(datetime)
    return str(datetime.strptime(deadline, ProgtestTaskGroupTemplate.DEADLINE_FORMAT))
  
  @payload("tasks", {})
  def tasks(self, tasks:dict[str, Union['TaskTemplate', dict]]) -> dict[str,'TaskTemplate']:
    "Dict of `ProgtestTaskTemplate` indexed by task id."
    task_templates = {}
    for id, task in tasks.items():
      if isinstance(task, TaskTemplate):
        task_templates[id] = task
      else:
        task_templates[id] = TaskTemplate(task)
    return task_templates

  def add_task_template(self, task:Union['TaskTemplate', dict]) -> None:
    if isinstance(task, TaskTemplate):
      self.tasks()[task.id] = task
    else:
      self.tasks()[task.id] = TaskTemplate(task)
  
  
  def dump(self, dirpath, update_if_exists=False):
    self.update({
      "_last_update": str(time.time())
      })
    path = Path(dirpath) / f"{self.ID}.json"
    if update_if_exists and path.exists():
      with open(path, "rw", encoding="utf-8") as write_file:
        olddata=type(self)(json.load(write_file))
        olddata.update(dict(self.items()))
        write_file.write(olddata.json)
    else:
      self.json_flush(path)
    return path

class ProgtestTestingDataTemplate(Template, metaclass=TemplateMeta):
  
  @payload("input","")
  def input(self, inp) -> str:
    "Input"
    return str(inp)
    
  @payload("output","")
  def output(self, outp) -> str:
    "Output"
    return str(outp)
    
  @payload("outputWin","")
  def output_win(self, outp_win) -> str:
    "Output window"
    return str(outp_win)
    
class ProgtestTestingSetsTemplate(Template, metaclass=TemplateMeta):
  
  @classmethod
  def from_progtest_files(cls, files:list[Union[str,Path]]):
    data = {}
    for file in files:
      path = Path(file)
      text = path.read_text()
      index = int(path.stem.split("_")[0])
      if not index in data:
          data[index] = {}
      if path.stem.endswith("_out_win"):
          data[index]["output_win"] = text
      elif path.stem.endswith("_out"):
          data[index]["output"] = text
      elif path.stem.endswith("_in"):
          data[index]["input"] = text
    for index in data:
      data[index] = ProgtestTestingDataTemplate(data[index])
    return cls(data)
