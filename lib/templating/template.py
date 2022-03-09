from email.policy import default
import json
import os
from pathlib import Path
from types import NoneType
from typing import (Any, Callable, Generic, Iterable, Iterator, Mapping, Type,
                    TypeVar, Union)

import testprog_common.lib.auxiliary as auxiliary
from testprog_common.lib.multikey_dict import TupleKeyDict
from testprog_common.lib.logging.static_log import STATIC_LOGGER as log

# ISSUE: [BT-11] Templating


JSON_TYPES = Union[int,float,str,bool,Iterable,Mapping, NoneType] # json compatible type structures
templateFieldDescriptorType = TypeVar("templateFieldDescriptorType", bound=JSON_TYPES)

class TemplateDictFieldDescriptor(Generic[templateFieldDescriptorType]):
    """
    Emulates python `@property` 
    - `getter` returns template dict value within which the decorator is defined and default 
    - `setter` calls `Template.update({<passed key>:<decorated function>(value)})`
    """
    
    def __init__(self,
                 key_name:str,
                 default_value,
                 formatter:Callable=None,
                 getter:Callable=None):
        self._name = None
        self._owner = None         
        self._key_name = key_name
        self._default_val = default_value 
        self._owner_instance = None
        self._formatter = formatter
        
        
        if self._default_val != None:
          assert isinstance(self._default_val, JSON_TYPES), "Default value must be json-compatible."
          self._type:templateFieldDescriptorType = type(self._default_val)
        if self._formatter != None:
          # case: secondary instance of payload created
          # as in functools.wraps - mask as wrapped object (formatter method)
          self.__doc__ = self._formatter.__doc__
          self.__name__ = "payload"
          
        if getter != None:
          self._fget = getter
          #self.__doc__ = self._fget.__doc__
          
        else:
          def default_getter(self, value):
            return value
          self._fget = default_getter
        
    def __set_name__(self, owner:'Template', name:str):
      self._name = name
      self._owner = owner
    
    def __repr__(self) -> str:
        return f"TemplateFieldDescriptor({self.__dict__})"

    def __call__(self, *args, **kwargs):
      if self._formatter == None:
        assert args[0] is not None, "Function argument cannot be `None` in case of first call (owner class constructor)."
        return TemplateDictFieldDescriptor[templateFieldDescriptorType](self._key_name, self._default_val, *args)
      else:
        # case: secondary instance of payload
        # support when linked value is Callable
        return self._getter(*args, **kwargs)
    
    def __getattribute__(self, __name: str) -> Any:
      if super(TemplateDictFieldDescriptor, self).__getattribute__("_formatter") == None:
        # case: instance of payload in template class object -> no changes needed
        return super(TemplateDictFieldDescriptor, self).__getattribute__(__name)
      
      # case: secondary instance of payload (attr of template instance)
      # only few private attributes are supported, otherwise public attributes from linked value are offered  
      elif __name[0] == "_" or __name == "getter":
        return super().__getattribute__(__name)
      else:
        return getattr(self._getter(), __name)
      
    def __get__(self, instance:'Template', owner:type):
      if instance != None and self._formatter != None:
        if self._owner_instance == None:
          self._owner_instance = instance
      return self
    
    def __set__(self, instance:'Template', value):
      if instance == None:
        super().__set__(instance, value)
      else:
        if self._owner_instance == None:
          self._owner_instance = instance
        return self._setter(value)
        
    def __iter__(self) -> Iterator[templateFieldDescriptorType]:
      value = self._getter()
      if isinstance(value, dict):
        return value.items()
      elif isinstance(value, list):
        return value.__iter__()
      else:
        return [value].__iter__()
    
    def getter(self, fget):
      return type(self)(self._key_name, self._default_val, self._formatter, fget)
    
    def setter(self, fset):
      return type(self)(self._key_name, self._default_val, fset, self._fget)
      
    def _getter(self, format_get=True):
      assert self._owner_instance is not None, "Owner instance cannot be None"
      if format_get:
        return self._fget(self, self._owner_instance[self._key_name])
      else:
        return self._owner_instance[self._key_name]
    
    def _setter(self, value, format_value=True):
      assert self._owner_instance is not None, "Owner instance cannot be None" 
      if format_value:
        self._owner_instance.update({self._key_name:self._formatter(self, value)}, update_as_attrs=False)
      else:
        self._owner_instance.update({self._key_name:value}, update_as_attrs=False)
      return self

# kind of more memorable name
def payload(key_name:str,
            default_value,
            formatter:Callable=None,
            getter:Callable=None):
  return TemplateDictFieldDescriptor(key_name, default_value, formatter, getter)

def _list_template_links(cls:Union['Template', Type['Template']]) -> dict[str, 'TemplateDictFieldDescriptor']:
    links = {}
    for name in [n for n in dir(cls) if not n.startswith('__')]:
      
      # unfortunate implementation -> skip because of recursion
      if name == "_links_":
        continue
      
      cls_attr = getattr(cls, name)
      if callable(cls_attr) and issubclass(type(cls_attr), TemplateDictFieldDescriptor) and isinstance(cls_attr, TemplateDictFieldDescriptor):
        links[name] = cls_attr
        
    return links
class TemplateMeta(type):
  """
  Template metaclass. Attributes `_links_` and `_defaults_` are created in template class object.
  """
  
  def __new__(self, class_name, bases, attrs:dict):
    cls = type(class_name, bases, attrs)
    links:dict[str, 'TemplateDictFieldDescriptor'] = _list_template_links(cls)
    cls._defaults_ = TupleKeyDict({(attr_name, link._key_name):link._default_val for attr_name, link in links.items()})
    cls._cls_links_ = links
    return cls

# [abstract class]
class Template(dict):
  """
  When using `Template` as base you must include metaclass `TemplateMeta`, which provides needed:
  
  * `_defaults_` attribute containing default values of each of `payload` defined within class.
  * `_cls_links_` attribute containing list of linked payloads to the `Template` class.
  
  ---
  
  ### Motivation / 'rules'
  
  - Template should be easely converted to json format without need to create specific converter hooks for every class you want format, that's why it extends `dict`.  
  - Use `@payload` decorator to set dict key names and default values (those should always be json convertable / instance of `Template`).
    - see :func:`payload` for more details
  - It is also to be easely used in `str.format(**template)` statement.
  - It should store only the most important data inside its `dict` structure.
  - Also if possible be able to extrapolate additional information via `@property`. 
  - Both stored and extrapolated data should be accessible only via `@payload` and `@property` respectively as it minimalizes chances of poorly written key names and provides name/return types hints to pylance.
  - Logic should be implemented only in static builders/converters and when extrapolating.
  - At the end template should compress its internal data as much as possible yet provide just as much additional data and metadata. 
  """
  
  def __new__(cls:Type['Template'], payload:Mapping={}, update_as_attrs:bool=False, format_payload:bool=True):
    obj = super().__new__(cls)
    obj.update({keys[1]:value for keys, value in cls._defaults_.items()}, update_as_attrs=False)
    print("Template __new__ done")
    return obj
  
  def __init__(self:'Template', payload:Mapping={}, update_as_attrs:bool=False, format_payload:bool=True):
    
    # ISSUE: [BT-12] format initial payload with payload._formatter now that payloads are instantiated with passed decorated functions
    formatted_payload = payload
    if format_payload:
      for link in self._cls_links_.values():
        if link._key_name in formatted_payload:
          formatted_payload[link._key_name] = link._formatter(self, payload[link._key_name])
    self.update(formatted_payload, update_as_attrs=update_as_attrs)
  
  def __repr__(self):
    return self.json
  
  def update(self:Union[Mapping, 'Template'], payload:Mapping[str,'Template.TYPES'], update_as_attrs:bool=True):
    """
    Recursively updates self and all vars instantiated as `Template`
    """
    for k,v in payload.items():
      if k in self and isinstance(self[k], Template):
        Template.update(self[k], v, update_as_attrs=update_as_attrs)
      else:
        if not update_as_attrs and (None,k) in self._defaults_.keys():
          self[k] = v
          continue
        if (k, None) in self._defaults_.keys():
          setattr(self, k, v)
          continue
        log.warn(f"Could not update template as {'attr' if update_as_attrs else 'dict'} with {repr(k)}:{repr(v)}")
  
  @classmethod
  def from_json(cls, path:Union[str,Path], format_payload:bool=False):
    """
    Loads a Template from JSON file without formatting the data.
    """
    with open(path, 'r', encoding="utf-8") as file:
      data = json.load(file)
    return cls(payload=data, format_payload=format_payload)

  @property
  def json(self):
    return json.dumps(dict(self.items()), ensure_ascii=False, indent=4)
  
  def json_flush(self, path:Union[str,Path]):
    if not isinstance(path, Path):
      path = Path(path)
    os.makedirs(path.parent, exist_ok=True)
    data = dict(self.items())
    with open(Path(path).absolute(), "w", encoding="utf-8") as file:
      json.dump(data, file, indent=4, ensure_ascii=False)

 
# dont use, builder suggests much more robust structure in contrast with template which should be lightweight
#   (actually pretty extesive on RAM as whole python is)
# left 4 better understandment of how python attributes and typing are handled internally
templateBuilderType = TypeVar("templateBuilderType", bound=Template)
class _TemplateBuilder(Generic[templateBuilderType]):
  
  class BuilderFieldSetter:
    
    def __init__(self, builder:'_TemplateBuilder', key_name:str):
      self.key_name = key_name
      # back-progation of builder instance could be done via __get__ method
      #   when argument instance is not None
      self.builder = builder
    
    def __call__(self, value) -> '_TemplateBuilder[templateBuilderType]':
      self.builder._payload.update({self.key_name:value})
      return self.builder
  
  def __init__(self, type_cls:Type[templateBuilderType], payload:Mapping={}):
    self._payload = payload
    self._type_cls = type_cls
    for link in type_cls._links_:
      ret = type(link._default_val)
      key = link._key_name
      # whole BuilderFieldSetter could be replaced by a lambda, 
      #   but a class serves as a 'sturdy' base
      setattr(self, auxiliary.sanitize_str(key), _TemplateBuilder.BuilderFieldSetter(self, key))
  
  def build(self) -> templateBuilderType:
    self._obj = self._type_cls(self._payload)
    return self._obj
    