import os
import importlib


def instantiate_class(arguments):
    from importlib import import_module

    d = dict(arguments)
    classname = d["classname"]
    del d["classname"]
    module_path, class_name = classname.rsplit(".", 1)
    module = import_module(module_path)
    class_name = class_name.replace(":", ".")
    c = getattr(module, class_name)
    return c(**d)

def get_class(arguments):
    from importlib import import_module

    if isinstance(arguments, dict):
        classname = arguments["classname"]
        module_path, class_name = classname.rsplit(".", 1)
        module = import_module(module_path)
        c = getattr(module, class_name)
        return c
    else:
        classname = arguments.classname
        module_path, class_name = classname.rsplit(".", 1)
        module = import_module(module_path)
        c = getattr(module, class_name)
        return c

def get_arguments(arguments):
    from importlib import import_module

    d = dict(arguments)
    if "classname" in d:
        del d["classname"]
    return d
def fullname_classname_from_object(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def classname_from_object(o):
    return o.__class__.__name__

def fullname_classname_from_class(klass):
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def classname_from_class(klass):
    return klass.__name__

def dir_fields(c):
    return [m for m in dir(c) if not m.startswith("_")]

from .component import Component
from .entity import Entity
from .world import World
from .worldapi import WorldAPI,LocalWorldAPI
from .system import System,LocalSystem
from .game import Game
