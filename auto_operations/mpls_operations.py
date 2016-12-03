#!/usr/bin/python

from operation_registry import OperationRegistry
import helpers


registry = OperationRegistry()


@registry.device_operation('get_mpls_table',family='ios,iosxe')
def get_mpls_table(context,target):
    '''
    IOS: show mpls forwarding-table 

    Returns:
	A list of dict with MPLS labels and interfaces.        
    '''

    commands = ['show mpls forwarding-table']

    with context.get_connection("cli") as cli:
        output = cli.execute(commands)

    template = "mpls_table_ios.tmpl"
    result = helpers.template_parser(template,output[0])

    labels = list()

    for elem in result:
        labels.append({'local_label': elem[0],
		       'remote_label': elem[1],
		       'prefix': elem[2],
		       'interface': helpers.interface_expand(elem[3]),
		       'nexthop': elem[4]})
    return labels



