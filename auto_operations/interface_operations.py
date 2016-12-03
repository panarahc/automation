#!/usr/bin/python

import re
import StringIO
import jtextfsm as textfsm
from operation_registry import OperationRegistry
from collections import namedtuple
from textwrap import dedent


registry = OperationRegistry()

INTERFACE_ATTRIBUTES = ['name', 'admin_status', 'oper_status', 'ip_address', 'bandwidth', 'input_rate',
              'output_rate', 'input_bytes', 'output_bytes']

INTERFACE = namedtuple('INTERFACE', INTERFACE_ATTRIBUTES)


@registry.device_operation('get_interfaces',family='junos')
def get_interfaces(context,target,interfaces='all'):
    '''
    Executes 'show interfaces <interface>' command and returns a dict of interfaces with all its attributes.

    Arguments:
 	target: Target device
	interfaces: (Optional) A comma-separated list of interfaces. If not specified, all interfaces are collected.
    '''

    if interfaces:
        intf_list = interfaces.split(',')
        commands = [ 'show interfaces {}'.format(intf) for intf in intf_list ] 
    else:
	commands = ['show interfaces']

    with context.get_connection('netconf') as nc:
        output = nc.execute(commands)

    return None


@registry.device_operation('get_interfaces',family='ios,iosxe')
def get_interfaces(context,target,interfaces='all'):
    '''
    Executes 'show interfaces <interface>' command and returns a list of interfaces with all its attributes.

    Arguments:
        target: Target device
        interfaces: (Optional) A comma-separated list of interfaces. If not specified, all interfaces are collected.
    '''

    INTERFACE_IOS_TEMPLATE = StringIO.StringIO(dedent("""\
        Value name (\S+)
        Value admin_status (up|administratively down)
        Value oper_status (up|down)
        Value ip_address (\S+)
        Value bandwidth (\d+)
        Value input_rate (\d+)
        Value output_rate (\d+)
        Value input_bytes (\d+)
        Value output_bytes (\d+)

        Start
          ^\S+ is (up|administratively down) -> Continue.Record
          ^${name}\s*is\s*${admin_status},\s*line protocol\s*is\s*${oper_status}
          ^\s*Internet address is ${ip_address}
          ^\s*MTU.*, BW ${bandwidth}
          ^\s*.*input rate ${input_rate}
          ^\s*.*output rate ${output_rate}
          ^\s*.*packets input, ${input_bytes}
          ^\s*.*packets output, ${output_bytes}
    """))

    if interfaces == 'all':
        commands = ['show interfaces']
    else:
        commands = [ 'show interfaces {}'.format(intf) for intf in interfaces.split(",") ]

    with context.get_connection('cli') as cli:
        response = cli.execute(commands)

    fsm = textfsm.TextFSM(INTERFACE_IOS_TEMPLATE)
    parsed_result = fsm.ParseText(("\n").join(response))
    return [ INTERFACE(*intf_attributes) for intf_attributes in parsed_result ]  
    

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

