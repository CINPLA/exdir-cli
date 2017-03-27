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
    def colored(value, *args, **kwargs):
        return value
        
    def cprint(value, *args, **kwargs):
        print(value)
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


class ListCommand:
    def command(args):
        directory = args.object or "."
        verify_inside(directory)
        try:
            obj = exdir.core.open_object(directory)
        except KeyError:
            return 0
        if isinstance(obj, exdir.core.Group):
            for sub in obj.values():
                if isinstance(sub, exdir.core.Group):
                    cprint(sub.object_name, "blue", attrs=["bold"])
                elif isinstance(sub, exdir.core.Raw):
                    cprint(sub.object_name, "yellow", attrs=["bold"])
                else:
                    print(sub.object_name)
            return 0
        elif isinstance(obj, exdir.core.Dataset):
            print(obj.object_name)
            return 0
        else:
            print("Cannot list object of this type:", obj)
            return 1
            
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            "list", 
            aliases=["ls"],
            description="List contents",
            help="list contents of object"
        )
        parser.add_argument(
            "object", 
            help="name of object to list contents of, should be File or Group", 
            default=None, 
            nargs="?"
        )
        return parser
    
        
class InfoCommand:
    def command(args):
        directory = args.object or "."
        verify_inside(directory)
        obj = exdir.core.open_object(directory)
        if isinstance(obj, exdir.core.Group):
            print("Group:", obj.object_name)
            print("Item count:", len(list(obj.keys())))
            return 0
        if isinstance(obj, exdir.core.Dataset):
            print("Dataset:", obj.object_name)
            return 0
        if isinstance(obj, exdir.core.Raw):
            print("Raw:", obj.object_name)
            return 0
            
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            "info",
            description="Show info about object",
            help="show short info about object"
        )
        parser.add_argument("object", help="object to list info about", default=None, nargs="?")
        return parser


class ShowCommand:
    def command(args):
        directory = args.object or "."
        verify_inside(directory)
        obj = exdir.core.open_object(directory)
        
        if args.all:
            import numpy as np
            np.set_printoptions(threshold=np.inf)        
        
        if isinstance(obj, exdir.core.File):
            print("__root__")
            print("Type: File")
            print("Item count:", len(list(obj.keys())))
            print("Items:")
            ListCommand.command(args)
            return 0
        if isinstance(obj, exdir.core.Group):
            print(obj.object_name)
            print("Type: Group")
            print("Name:", obj.name)
            print("Item count:", len(list(obj.keys())))
            print("Items:")
            ListCommand.command(args)
            return 0
        if isinstance(obj, exdir.core.Dataset):
            print(obj.object_name)
            print("Type: Dataset")
            print("Name:", obj.name)
            print("Shape:", obj.shape)
            print("Data:")
            print(obj.data)
            return 0
        if isinstance(obj, exdir.core.Raw):
            print(obj.object_name)
            print("Type: Raw")
            print("Name:", obj.name)
            return 0
            
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            "show",
            description="Show object contents",
            help="show object contents"
        )
        parser.add_argument("object", help="object to show", default=None, nargs="?")
        parser.add_argument("--all", "-a", action="store_true", help="show all data in datasets")
        return parser


class CreateGroupCommand:
    def command(args):
        exdir.create_group(args.name)
        
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            "create",
            aliases=["mkgrp"],
            description="Create group",
            help="create group"
        )
        parser.add_argument(
            "name", 
            help="name(s) of the group(s) to create",
            default=None,
            nargs="+"
        )
        return parser


class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._subparsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        print("\nThese are available exdir commands:\n")
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                print("\t{}\t\t{}".format(choice, subparser.description))
                # print(subparser.format_help())

        parser.exit()
        

def main():
    # parser = argparse.ArgumentParser(add_help=False)
    # parser.add_argument("--help", action=_HelpAction, help="show this help message and exit")
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(metavar="command", dest="cmd")
    subparsers.required = True

    commands = [
        ListCommand,
        ShowCommand,
        InfoCommand,
        CreateGroupCommand
    ]
    
    for command in commands:
        subparser = command.add_parser(subparsers)
        subparser.set_defaults(func=command.command)
    
    def completer(prefix, **kwargs):
        return [i for i in list(subparsers.choices) + find_commands() if i.startswith(prefix)]
    
    subparsers.completer = completer

    args = parser.parse_args()

    return args.func(args)
    
if __name__ == "__main__":
    sys.exit(main())
