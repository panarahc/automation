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

@registry.device_operation('get_interfaces_traffic',family='ios')
def get_interfaces_traffic(context,target,interfaces='all'):
    '''
    Executes 'show interfaces <interface> | include packets/sec' or
             'show interfaces | include packets/sec' and returns
    the sum of all packets/sec (in and out combined).

    Arguments:
   	target: Target device
	interfaces: (Optional) A comma-separated list of interfaces. Eg: "Gi1/0,Gi2/0".
	            If not specified, all interfaces are collected.
    '''

    PPS_RE = re.compile(r".* (?P<pps>\S+) packets/sec")

    if interfaces == "all":
        commands = ["show interfaces | include packets/sec"]
    else:
        commands = [ "show interfaces {} | include packets/sec".format(interface) 
			for interface in interfaces.split(",") ]

    with context.get_connection('cli') as cli:
        interfaces_output = cli.execute(commands)

    #Combine output into a string.
    output = ("\n").join(interfaces_output)

    #Search for int then sum of all pps   
    total_pps = sum( [ int(row.group("pps")) for row in re.finditer(PPS_RE,output) ] )

    return total_pps


