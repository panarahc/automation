#!/usr/bin/python

from collections import defaultdict
from ncclient import manager
from operation_registry import OperationRegistry
import re


registry = OperationRegistry()


@registry.device_operation('get_bgp_asn',family='iosxe')
def get_bgp_asn_iosxe(context,target):
    '''
    Executes "show run | include router bgp" command and parses the output
    to get BGP AS number.

    Arguments:
    	target: Target device
    '''

    ASN_REGEX = re.compile(r'router bgp (?P<asn>\d+)')
    commands = ['show run | include router bgp']

    with context.get_connection('cli') as cli:
        output = cli.execute(commands)

    if output:
        asn = re.search(ASN_REGEX, output[0]).group('asn')
    return asn

 
@registry.device_operation('get_prefixes_received_from_neighbor',family='ios')
def get_prefixes_received_from_neighbor_ios(context,target,neighbor):
    '''
    Executes show ip bgp neighbor <neighbor> received-routes command and returns a list of prefixes.
    '''
    command = 'show ip bgp neighbor {} received-routes'.format(neighbor)

    with context.get_connection('cli') as cli:
        output = cli.execute(command)

    template = 'ios_show_ip_bgp.tmpl'
    result = parse_with_textfsm(template,output)
    prefixes = []
    for row in result:
        if row[1]:
            prefixes.append(row[1])
    return prefixes


@registry.device_operation('get_prefixes_received_from_neighbor',family='junos')
def get_prefixes_received_from_neighbor_junos(context,target,neighbor):
    '''
    Executes show route receive-protocol bgp <neighbor> command and returns a list of prefixes.
    '''
    command = 'show route receive-protocol bgp {}'.format(neighbor)

    with context.get_connection('netconf'):
        output = context.execute(command)

    prefixes_xpath = 'route-information/route-table/rt/rt-destination'
    parsed_output = output.xpath(prefixes_xpath)
    prefixes = [ item.text for item in parsed_output ]
    return prefixes


@registry.device_operation('get_bgp_neighbors',family='ios')
def get_bgp_neighbors_ios(context,target):
    '''
    Executes 'show ip bgp summary' command and returns a list of lists with BGP neighbors and corresponding ASN.

    Sample output:
        [['10.1.2.2', '200'], ['10.1.3.3', '300']]
    '''
    command = 'show ip bgp summary'

    with context.get_connection('cli'):
        output = context.execute(command)

    template = 'ios_show_ip_bgp_summary.tmpl'
    bgp_neighbors = parse_with_textfsm(template,output)
    return bgp_neighbors


@registry.device_operation('get_bgp_neighbors',family='junos')
def get_bgp_neighbors_junos(context,target):
    '''
    Executes 'show bgp summary' command and returns a list of lists with BGP neighbors and corresponding ASN.
    '''

    commands = ['show bgp summary']

    with context.get_connection('netconf') as nc:
        output = nc.execute(commands)

    neighbor_xpath = 'bgp-information/bgp-peer/peer-address'
    asn_xpath = 'bgp-information/bgp-peer/peer-as'

    parsed_neighbor = output[0].xpath(neighbor_xpath)
    parsed_asn = output[0].xpath(asn_xpath)
    bgp_neighbors = [ [i.text,j.text] for i,j in zip(parsed_neighbor,parsed_asn) ]
    return bgp_neighbors




