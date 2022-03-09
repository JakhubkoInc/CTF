from pathlib import Path
from typing import Union, Mapping

from .template import Template, TemplateMeta, payload


class TextTemplate(Template, metaclass=TemplateMeta):
  
  @payload("layout", "")
  def layout(self, text:str):
    return str(text)
  
  @property
  def text(self):
    return self.layout.format(**dict(self))


class FileTemplate(TextTemplate, metaclass=TemplateMeta):
  
  @payload("filename", "a.txt")
  def filename(self, name:str):
    return str(name)
  
  def flush(self, path:Union[str, Path]):
    path = Path(path)
    filepath = (path / self.filename).absolute()
    with open(filepath, 'w') as file:
      file.write(self.text)
  