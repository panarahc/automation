#!/usr/bin/python

from collections import defaultdict
from operation_registry import OperationRegistry
from StringIO import StringIO
import helpers
import re


registry = OperationRegistry()


@registry.device_operation('get_ospf_neighbors',family='ios')
def get_ospf_neighbors(context,target):
    '''
    IOS: show ip ospf neighbor 

    Returns:
	A list of dict with OSPF neighbors and state.        
    '''

    commands = ['show ip ospf neighbor']

    with context.get_connection("cli") as cli:
        output = cli.execute(commands)

    template = "ospf_neighbors_ios.tmpl"
    result = helpers.template_parser(template,output[0])

    neighbors = list()

    for elem in result:
        neighbors.append({'neighbor': elem[0],
			  'priority': elem[1],
			  'state': elem[2],
			  'neighbor_ip': elem[3],
			  'local_intf': elem[4]})
    return neighbors


