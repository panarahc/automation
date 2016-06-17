#!/usr/bin/python

from operation_registry import OperationRegistry


registry = OperationRegistry()


@registry.device_operation('get_config_diff', family='ios')
def get_config_diff(context, target, file1, file2):
    """
    IOS: show archive config differences <file1> <file2> 

    Returns:
	A list of diff.
    """

    commands = [ "show archive config difference {} {}".format(file1,file2) ]

    with context.get_connection("cli") as cli:
        output = cli.execute(commands)

    # Ignore first 4 lines
    diffs = output[0].splitlines()[4:]
    return diffs 


