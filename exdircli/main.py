#!/usr/bin/env python
from __future__ import print_function
import argparse
import sys
import exdir
import yaml
import os
import os.path
try:
    from termcolor import colored, cprint
except ImportError:
    def colored(value, **attrs):
        return value
        
    def cprint(value, **attrs):
        return value
try:
    import colorama
    colorama.init()
except ImportError:
    pass


def verify_inside(directory):
    try:
        exdir.core.assert_inside_exdir(directory)
    except FileNotFoundError:
        print("ERROR:", os.path.abspath(directory), "is not inside a exdir repository.")
        sys.exit(1)


def list_(args):
    directory = args.group or '.'
    verify_inside(directory)
    obj = exdir.core.open_object(directory)
    if isinstance(obj, exdir.core.Group):
        for sub in obj.values():
            if isinstance(sub, exdir.core.Group):
                cprint(sub.object_name, 'blue', attrs=['bold'])
            else:
                print(sub.object_name)
    elif isinstance(obj, exdir.core.Dataset):
        print(obj.object_name)
    else:
        print("Cannot list object of this type:", obj)
        return 1
        

def info(args):
    directory = args.object or '.'
    verify_inside(directory)
    obj = exdir.core.open_object(directory)
    if isinstance(obj, exdir.core.Group):
        print("Group:", obj.object_name)
        print("Item count:", len(list(obj.keys())))
        return 0
    if isinstance(obj, exdir.core.Dataset):
        print("Dataset:", obj.object_name)
        return 0


def show(args):
    directory = args.object or '.'
    verify_inside(directory)
    obj = exdir.core.open_object(directory)
    
    if args.all:
        import numpy as np
        np.set_printoptions(threshold=np.inf)        
    
    if isinstance(obj, exdir.core.File):
        print("__root__")
        print("Type: File")
        print("Item count:", len(list(obj.keys())))
        return 0
    if isinstance(obj, exdir.core.Group):
        print(obj.object_name)
        print("Type: Group")
        print("Name:", obj.name)
        print("Item count:", len(list(obj.keys())))
        return 0
    if isinstance(obj, exdir.core.Dataset):
        print(obj.object_name)
        print("Type: Dataset")
        print("Name:", obj.name)
        print("Shape:", obj.shape)
        print("Data:")
        print(obj.data)
        return 0


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser('list', aliases=['ls'])
    list_parser.add_argument('group', help="directory to list", default=None, nargs='?')
    list_parser.set_defaults(func=list_)

    view_parser = subparsers.add_parser('show')
    view_parser.add_argument('object', help="object to show", default=None, nargs='?')
    view_parser.add_argument('--all', '-a', action='store_true', help="show all data in datasets")
    view_parser.set_defaults(func=show)

    info_parser = subparsers.add_parser('info')
    info_parser.add_argument('object', help="object to list info about", default=None, nargs='?')
    info_parser.set_defaults(func=info)

    args = parser.parse_args()

    try:
        args.func
    except AttributeError:
        print("ERROR: Unknown command")
        return 1

    return args.func(args)
if __name__ == "__main__":
    sys.exit(main())
