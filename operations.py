#!/usr/bin/python

from contextlib import contextmanager
from collections import defaultdict
from ncclient import manager
from helper_functions import * 
import textfsm
import re


class OperationRegistry(object):
    def __init__(self):
       self.func_map = defaultdict(dict)

    def device_operation(self,f_name,family=None):
        def func_decorator(func):
            self.func_map[f_name].update({family:func})
            #print self.func_map
            def func_wrapper(*args,**kwargs):
                return func(*args,**kwargs)
            return func_wrapper
        return func_decorator  


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

    if interfaces != 'all':
        intf_list = interfaces.split(',')
        commands = [ 'show interfaces {}'.format(intf) for intf in intf_list ]
    else:
        commands = ['show interfaces']

    with context.get_connection('netconf') as nc:
        output = nc.execute(commands)

    print output
    return None


@registry.device_operation('apply_filter_config',family='iosxr')
def apply_filter_config_iosxr(context,target,prefixes):

    config = render_config('filter_hijack_prefixes_iosxr_tmpl.j2',context.info['bgp_asn'],prefix)
    with context.get_connection('cli_xr'):
        result = context.push_config(config)         
    return result

@registry.device_operation('apply_filter_config',family='ios')
def apply_filter_config_ios(context,target,prefixes):
    '''
    '''
        
    config = render_template_config(template_name='filter_prefix_iosxe.j2',prefixes=prefixes)
    with context.get_connection('cli') as cli, cli.authorize():
        result = cli.configure(config)
    return result

@registry.device_operation('filter_invalid_prefix_by_asn',family='iosxe')
def filter_invalid_prefix_by_asn_iosxe(context,target,contents):
    '''
    '''
                   
    config = render_template_config(template_name='filter_invalid_prefix_by_asn_iosxe.j2',contents=contents)
    with context.get_connection('cli'):
        result = context.push_config(config,privileged=True)
    return result

@registry.device_operation('get_facts',family='ios')
def get_facts_ios(context,target):
    '''
    '''
    model_regex = ".*Cisco\s(?P<model>\d+).*"
    show_ver_regex = ".*Software\s\((?P<image>.+)\),\sVersion\s(?P<version>.+), RELEASE.*"

    with context.get_connection('cli') as cli:
        output = cli.execute(['show version','show inventory'])

    facts = {}
    facts['hostname'] = context.info['hostname']
    facts['chassis'] = re.search(r'"Chassis", DESCR: "(.+)"',output[1]).group(1).strip('\r')
    facts['uptime'] = re.search(r'(.+) uptime is (.+)',output[0]).group(2).strip('\r')
    facts['serial_number'] = re.search(r'SN: (.+)',output[1]).group(1).strip('\r')
    facts['model'] = re_match(model_regex,output[0]).groupdict()['model']
    facts['image'] = re_match(show_ver_regex,output[0]).groupdict()['image']
    facts['version'] = re_match(show_ver_regex,output[0]).groupdict()['version']
    return facts

@registry.device_operation('get_facts',family='iosxe')
def get_facts_iosxe(context,target):
    '''
    '''
    model_regex = "cisco\s+(?P<model>\d+)\s+processor"
    show_ver_regex = ".*Software\s\((?P<image>.+)\),\sVersion\s(?P<version>.+), RELEASE.*"

    with context.get_connection('cli') as cli:
        output = cli.execute(['show version','show inventory'])

    facts = {}
    facts['hostname'] = context.info['hostname']
    facts['chassis'] = re.search(r'"Chassis", DESCR: "(.+)"',output[1]).group(1).strip('\r')
    facts['uptime'] = re.search(r'(.+) uptime is (.+)',output[0]).group(2).strip('\r')
    facts['serial_number'] = re.search(r'SN: (.+)',output[1]).group(1).strip('\r')
    facts['model'] = re.search(r'cisco (.+) processor',output[0]).group(1)
    facts['image'] = re_match(show_ver_regex,output[0]).groupdict()['image']
    facts['version'] = re_match(show_ver_regex,output[0]).groupdict()['version']
    return facts

@registry.device_operation('get_facts',family='junos')
def get_facts_junos(context,target):

    #uptime_regex = ".*\sup\s+(\S+),"
    model_regex = "Model:\s+(\S+)"
    version_regex = "JUNOS Base\s.*\s\[(\S+)\]"
 
    with context.get_connection('cli') as cli:
        output = cli.execute(['show version','show system uptime'])

    facts = {}
    facts['hostname'] = context.info['hostname']
    #facts['chassis'] = 
    #facts['serial_number'] =
    #facts['uptime'] = re_search(uptime_regex,output[1]).group(1)
    facts['model'] = re_search(model_regex,output[0]).group(1)
    facts['version'] = re_search(version_regex,output[0]).group(1)   
    return facts        

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

    command = 'show bgp summary'

    with context.get_connection('netconf'):
        output = context.execute(command)

    neighbor_xpath = 'bgp-information/bgp-peer/peer-address'
    asn_xpath = 'bgp-information/bgp-peer/peer-as'

    parsed_neighbor = output.xpath(neighbor_xpath)
    parsed_asn = output.xpath(asn_xpath)
    bgp_neighbors = [ [i.text,j.text] for i,j in zip(parsed_neighbor,parsed_asn) ]
    return bgp_neighbors
 

@registry.device_operation('get_lldp_neighbors',family='ios')
def get_lldp_neighbors_ios(context,target):
    command = 'show lldp neighbors'

    with context.get_connection('cli'):
        output = context.execute(command)

    result = parse_with_textfsm('cisco_ios_show_lldp_neighbors.tmpl',output)
    return result  

