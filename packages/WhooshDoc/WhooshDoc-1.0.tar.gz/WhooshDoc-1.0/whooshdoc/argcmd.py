""" A class-based approach for constructing command-line programs with multiple
sub-commands using argparse.
"""

import argparse


class ArgDecorator(object):
    """ Base class for decorators to add ArgumentParser information to a method.
    """

    def __call__(self, func):
        if not getattr(func, 'has_arguments', False):
            func.argcmd_args = []
            func.argcmd_kwds = []
            func.has_arguments = True
        return func

# Mark the method as a command, but don't add any arguments.
noarguments = ArgDecorator()

class argument(ArgDecorator):
    """ Store arguments and keywords to pass to add_argument().

    Instances also serve to decorate command methods.
    """
    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds

    def __call__(self, func):
        """ Decorate the method.
        """
        func = super(argument, self).__call__(func)
        func.argcmd_args.append(self.args)
        func.argcmd_kwds.append(self.kwds)
        return func

class rename(ArgDecorator):
    """ Store an alternate name for a sub-command for decorating command
    methods.
    """
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        func = super(rename, self).__call__(func)
        func.argcmd_name = self.name
        return func

class kwds(ArgDecorator):
    """ Provide other keywords to the sub-parser constructor.
    """
    def __init__(self, **kwds):
        self.kwds = kwds

    def __call__(self, func):
        func = super(kwds, self).__call__(func)
        func.argcmd_subparser_kwds = self.kwds
        return func


class ArgCmd(object):
    """ Base class for constructing command-line programs with multiple
    sub-commands.
    """

    # Extra keyword arguments to pass to ArgumentParser.
    kwds = {}

    # A list of the main arguments as specified by argument() instances.
    main_args = []

    # The help text that goes with the list of sub-commands.
    subparsers_help = "Available commands."

    def __init__(self, *args, **kwds):
        self.parser = self._assemble_parser()
        self.args = None

    def run(self, args=None, namespace=None):
        """ Parse arguments to the self.args attribute and run the command with
        the parsed arguments.
        """
        self.args = self.postprocess_args(self.parser.parse_args(args, namespace))
        method = getattr(self, self.args._command)
        method(self.args)

    def postprocess_args(self, args):
        """ Postprocess the arguments, if necessary.
        """
        return args

    def _assemble_parser(self):
        """ Assemble an ArgumentParser from the decorated methods.
        """
        kwds = self.kwds.copy()
        if 'description' not in kwds:
            kwds['description'] = self.__doc__
        parser = argparse.ArgumentParser(**kwds)
        for arg in self.main_args:
            parser.add_argument(*arg.args, **arg.kwds)

        subparsers = parser.add_subparsers(help=self.subparsers_help)
        for name in dir(self):
            value = getattr(self, name, None)
            if getattr(value, 'has_arguments', False):
                kwds = getattr(value, 'argcmd_subparser_kwds', {})
                if 'help' not in kwds:
                    kwds['help'] = getattr(value, '__doc__', None)
                if 'description' not in kwds:
                    kwds['description'] = getattr(value, '__doc__', None)
                arg_name = getattr(value, 'argcmd_name', value.__name__)
                cmd_parser = subparsers.add_parser(arg_name, **kwds)
                for args, kwds in zip(value.argcmd_args, value.argcmd_kwds):
                    cmd_parser.add_argument(*args, **kwds)
                cmd_parser.set_defaults(_command=name)
        return parser



