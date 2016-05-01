#!/usr/bin/python

from contextlib import contextmanager
from collections import defaultdict
from ncclient import manager
from helper_functions import * 
from operation_registry import OperationRegistry
import textfsm
import re


registry = OperationRegistry()


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
    facts['model'] = re.match(model_regex,output[0]).groupdict()['model']
    facts['image'] = re.match(show_ver_regex,output[0]).groupdict()['image']
    facts['version'] = re.match(show_ver_regex,output[0]).groupdict()['version']
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
    facts['image'] = re.match(show_ver_regex,output[0]).groupdict()['image']
    facts['version'] = re.match(show_ver_regex,output[0]).groupdict()['version']
    return facts

@registry.device_operation('get_facts',family='junos')
def get_facts_junos(context,target):

    hostname_regex = r"Hostname: (.*)"
    uptime_regex = r"System booted:.*\((?P<uptime>.+) ago\)"
    model_regex = r"Model:\s+(\S+)"
    version_regex = r"JUNOS Base\s.*\s\[(\S+)\]"
 
    with context.get_connection('cli') as cli:
        output = cli.execute(['show version','show system uptime'])

    facts = {}
    facts['hostname'] = re.search(hostname_regex, output[0]).group(1) 
    #facts['chassis'] = 
    #facts['serial_number'] =
    facts['uptime'] = re.search(uptime_regex,output[1]).groupdict()['uptime']
    facts['model'] = re.search(model_regex,output[0]).group(1)
    facts['version'] = re.search(version_regex,output[0]).group(1)   
    return facts        


@registry.device_operation('get_lldp_neighbors',family='ios')
def get_lldp_neighbors_ios(context,target):
    command = 'show lldp neighbors'

    with context.get_connection('cli'):
        output = context.execute(command)

    result = parse_with_textfsm('cisco_ios_show_lldp_neighbors.tmpl',output)
    return result  

