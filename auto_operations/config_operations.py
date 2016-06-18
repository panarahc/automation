#!/usr/bin/python

from operation_registry import OperationRegistry
import re


registry = OperationRegistry()


@registry.device_operation('apply_config',family='ios,iosxe')
def apply_config(context,target,commands):
    """
    Returns:
	Error if any encountered or True if no errors are seen.
    """

    with context.get_connection("cli") as cli, cli.authorize():
        result = cli.configure(commands)

    return result


@registry.device_operation('config_replace',family='ios')
def config_replace(context,target,filename):
    """
    IOS: configure replace <filename> force revert trigger error

    Returns:
	True if no errors are seen.
    """

    commands = [ "configure replace {} force revert trigger error".format(filename) ]

    with context.get_connection("cli") as cli:
        result = cli.execute(commands)

    return True 


