#!/usr/bin/python

import re
from operation_registry import OperationRegistry


registry = OperationRegistry()

@registry.device_operation('get_interfaces',family='junos')
def get_interfaces_junos(context,target,interfaces='all'):
    '''
    Executes 'show interfaces <interface>' command and returns a dict of interfaces with all its attributes.

    Arguments:
 	target: Target device
	interfaces: (Optional) A comma-separated list of interfaces. If not specified, all interfaces are collected.
    '''

    intf_list = list()

    if interfaces:
        intf_list = interfaces.split(',')
        commands = [ 'show interfaces {}'.format(intf) for intf in intf_list ] 
    else:
	commands = ['show interfaces']

    with context.get_connection('netconf') as nc:
        output = nc.execute(commands)

    print output
    return None

 
