#!/usr/bin/python

from collections import defaultdict
from ncclient import manager
from operation_registry import OperationRegistry
from StringIO import StringIO
from lxml import etree
import helpers
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



