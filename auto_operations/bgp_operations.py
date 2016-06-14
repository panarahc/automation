#!/usr/bin/python

from collections import defaultdict
from operation_registry import OperationRegistry
from StringIO import StringIO
from lxml import etree
import helpers
import re


registry = OperationRegistry()


@registry.device_operation('get_bgp_asn',family='ios,iosxe')
def get_bgp_asn(context,target):
    '''
    IOS/IOS-XE: show run | include router bgp

    Returns:
    	BGP AS number
    '''

    ASN_RE = re.compile(r'router bgp (?P<asn>\d+)')
    commands = ['show run | include router bgp']

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    if output:
        asn = re.search(ASN_RE, output[0]).group('asn')
    return asn


@registry.device_operation('get_bgp_asn',family='junos')
def get_bgp_asn(context,target):
    '''
    JUNOS: show configuration routing-options autonomous-system

    Returns:
    	BGP AS number
    '''

    ASN_RE = re.compile(r'(?P<asn>\d+)')
    commands = ['show configuration routing-options autonomous-system']

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    if output:
        asn = re.search(ASN_RE, output[0]).group('asn')
    return asn

 
@registry.device_operation('get_prefixes_received_from_neighbor',family='ios,iosxe')
def get_prefixes_received_from_neighbor(context,target,neighbor,table=None):
    '''
    IOS/IOS-XE: show ip bgp neighbor <neighbor> received-routes

    Returns:
	A dict of prefixes with its BGP attributes
    '''

    commands = ['show ip bgp neighbor {} received-routes'.format(neighbor)]

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    template = 'bgp_table_ios.tmpl'
    result = helpers.template_parser(template,output[0])
    prefixes = dict()

    for row in result:
        prefixes[row[1]] = {'nexthop':row[2],
			    'metric':row[3],
			    'local_pref':row[4],
			    'weight':row[5],
			    'as_path':row[6],
			    'origin':row[7],
			    'status_codes':row[0]}

    return prefixes


@registry.device_operation('get_prefixes_received_from_neighbor',family='junos')
def get_prefixes_received_from_neighbor(context,target,neighbor,table='inet.0'):
    '''
    JUNOS: show route receive-protocol bgp <neighbor>

    Returns:
   	A dict of prefixes with its BGP attributes
    '''

    commands = ['show route receive-protocol bgp {} table {}'.format(neighbor,table)]

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    template = 'bgp_table_junos.tmpl'
    result = helpers.template_parser(template, output[0])
    prefixes = dict()

    for row in result:
        prefixes[row[1]] = {'nexthop':row[2],
                            'metric':row[3],
                            'local_pref':row[4],
                            'as_path':row[5],
                            'origin':row[6],
                            'status_codes':row[0]}

    return prefixes


@registry.device_operation('get_bgp_neighbors',family='ios,iosxe')
def get_bgp_neighbors(context,target):
    '''
    IOS/IOS-XE: show ip bgp summary

    Returns:
	A dict of neighbors and neighbor attributes
    '''

    commands = ['show ip bgp summary']

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    template = 'bgp_summary_ios.tmpl'
    result = helpers.template_parser(template,output[0])
    neighbors = dict()

    for row in result:
        neighbors[row[0]] = {'version':row[1],
                             'asn':row[2],
                             'msg_rcvd':row[3],
                             'msg_sent':row[4],
                             'table_version':row[5],
                             'in_queue':row[6],
                             'out_queue':row[7],
                             'up_down':row[8],
                             'state_prefixes':row[9]}

    return neighbors


@registry.device_operation('get_bgp_neighbors',family='junos')
def get_bgp_neighbors(context,target):
    '''
    JUNOS: show bgp summary

    Returns:
	A dict of neighbors and neighbor attributes
    '''

    commands = ['show bgp summary']

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    template = 'bgp_summary_junos.tmpl'
    result = helpers.template_parser(template,output[0])
    neighbors = dict()

    for row in result:
        neighbors[row[0]] = {'asn': row[1],
                             'msg_rcvd':row[2],
                             'msg_sent':row[3],
                             'out_queue':row[4],
                             'flaps':row[5],
                             'up_down':row[6],
                             'state_prefixes':row[7]}

    return neighbors


@registry.device_operation('get_bgp_neighbors_state',family='ios')
def get_bgp_neighbors_state(context,target,neighbors="all"):
    '''
    IOS: show ip bgp neighbors

    Returns:
        A list of dicts of BGP neighbors and state. 
    '''

    commands = list()

    if neighbors == "all":
        commands = ['show ip bgp neighbors']
    else:
        for neighbor in neighbors.split(","):
            commands.append("show ip bgp neighbors {}".format(neighbor))

    with context.get_connection("cli") as cli:
        output = cli.execute(commands)
    data = ("\n").join(output)

    template = 'bgp_neighbors_ios.tmpl'
    neighbors = list()
    result = helpers.template_parser(template,data)

    for elem in result:
        neighbors.append({'neighbor':elem[0],
			  'remote_asn':elem[1],
                          'description':elem[2],
                          'state':elem[3],
                          'peergroup':elem[4]})

    return neighbors
           

@registry.device_operation('get_bgp_peergroups',family='ios')
def get_bgp_peergroups(context,target):
    '''
    IOS: show run | begin router bgp

    Returns:
        A list of BGP peergroups configured. 
    '''

    PEERGROUP_RE = re.compile(r"\s*neighbor\s+(?P<peergroup>\S+)\s+peer-group\n") 
    commands = ["show run | begin router bgp"]

    with context.get_connection("cli") as cli:
        output = cli.execute(commands)

    peergroups = [ elem.group("peergroup") for elem in re.finditer(PEERGROUP_RE,output[0]) ]
    return peergroups 

