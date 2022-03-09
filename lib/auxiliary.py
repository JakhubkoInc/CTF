import hashlib
import json
import os
import tarfile
import unicodedata
from os import listdir
from os.path import isdir, isfile, join
from pathlib import Path
from typing import Iterable, Union
from urllib.parse import parse_qs, urlparse


def get_file_md5_checksum(filename) -> str:
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def load_json_file(path):
    with open(path, "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    print(f"Loaded json object from '{path}'")
    return data

def save_json_file(path, data):
    dir = Path(path).parent.absolute()
    os.makedirs(dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as write_file:
        json.dump(data, write_file,ensure_ascii=False,indent=4, default=str)

def update_json_file(path, data):
    if Path(path).exists():
        olddata:dict = load_json_file(path)
        olddata.update(data)
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file,ensure_ascii=False,indent=4, default=str)
    else:
        raise FileNotFoundError(path)

def extract_tgz(tar_url, extract_dir='.'):
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(tar_url, 'r') as tar:
        for item in tar:
            tar.extract(item, extract_dir, set_attrs=False)
            if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
                extract_tgz(item.name, "./" + item.name[:item.name.rfind('/')])   

def sanitize_str(s):
    noaccents = ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')
    return noaccents.replace(" ", "_").replace("/", "_").replace("'","").lower()

def format_locator(locator, **kargs):
    formated = (locator[0], locator[1].format(**kargs))
    print(f"formated locator: {locator} -> {formated}")
    return formated

def json_print(object) -> None:
    opt = {
        "indent": 4,
        "ensure_ascii": False
    }
    if type(object) != dict:
        print(object.__class__.__name__ + ": " + json.dumps(object.__dict__,**opt))
    else:
        print(f"Dict:\n{json.dumps(object,**opt)}")

def get_url_param(url, name) -> str:
    return parse_qs(urlparse(url).query)[name][0]

def get_url_params(url) -> list[str]:
    return parse_qs(urlparse(url).query)

def read_file(filename, encoding="utf-8") -> str:
    with open(filename, 'r', encoding) as f:
        data = f.read()
    return data

def transform(iter:Iterable,transformation):
    for val in iter:
        yield transformation(val)

# TODO: create Generator -> utilize methods select,where,transform,etc. to chain themselves
def select(self:Iterable,transformation, default=None):
    """
    maps iterable to list of transformed values, if val is None returns default(=None)
    """
    for val in self:
        if val != None:
            yield transformation(val)
        else: 
            yield default

def where(iter:Iterable, statement):
    """
    returns a list of all the values from given list if statement is true
    """
    out = []
    for val in iter:
        if statement(val):
            out.append(val)
    return out

def get_dirs(path):
    return [ Path(join(path, f)) for f in listdir(path) if isdir(join(path, f))]

def list_dir_names(path) -> list[str]:
    return [ f for f in listdir(path) if isdir(join(path, f))]

def list_file_paths(path) -> list[Path]:
    """returns list of filepaths from specified directory"""
    return [ Path(join(path, f)) for f in listdir(path) if isfile(join(path, f))]

def list_file_names(path):
    """returns list of filenames, including suffix, from specified directory"""
    return [ f for f in listdir(path) if isfile(join(path, f))]

def any_common(a:Union[set,list], b:Union[set,list]):
    """Finds out whether two sets have any common element.

    Args:
        a (Union[set,list]): first set
        b (Union[set,list]): second set

    Returns:
        bool: -
    """
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True
    else:
        return False

def strip_accents(s:str):
    """
    removes all accents from string
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

   
def flatten(t):
    """
    flattens specified list
    """
    return [item for sublist in t for item in sublist]
