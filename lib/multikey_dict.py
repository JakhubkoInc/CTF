
from typing import Union, Any

def cmp_tuple(a, b):
  assert len(a) == len(b), "Expected same length of both tuples"
  for i in range(len(a)):
    if b[i] != None and a[i] != b[i]:
      return False
  return True

class TupleKeyDict_Keys(list[tuple]):
  
  def __contains__(self, key:Union[tuple, Any]) -> bool:
    if isinstance(key, tuple):
      for t in self:
        if cmp_tuple(t, key):
          return True
      return False
    else:
      return key in [t[0] for t in self]
    

class TupleKeyDict(dict):
  
  def keys(self):
    return TupleKeyDict_Keys(super().keys())
  
  