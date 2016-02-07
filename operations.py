#!/usr/bin/python

from netmiko import ConnectHandler
from contextlib import contextmanager
from ncclient import manager
from helper_functions import * 
from pyIOSXR import IOSXR
import textfsm
import re


class NetconfConnector(object):

    user = 'test123'
    pwd = 'test123'

    def __init__(self,parent):
        self.parent = parent

    @contextmanager
    def get_connection(self):
        try:
            hostname = self.parent.info['hostname']
            ip_address = self.parent.info['_id']
            device_type = self.parent.info['family']
            self.parent.conn = manager.connect(host=ip_address,port=830,username=NetconfConnector.user,password=NetconfConnector.pwd,timeout=3,device_params={'name':device_type},hostkey_verify=False)
            yield self.parent.conn
        finally:
            self.parent.conn.close_session() 

    def run_command(self,cmd):
        output = self.parent.conn.command(command=cmd,format='xml')
        return output


class SSHConnector(object):
    # username and password are defined as Class attributes
    user = 'test123'
    pwd = 'test123'

    def __init__(self,parent):
        self.parent = parent

    @contextmanager
    def get_connection(self):
        try:
            hostname = self.parent.info['hostname']
            ip_address = self.parent.info['_id']
            device_type = self.parent.info['family']
            device = {'device_type':device_type,'ip':ip_address,'username':SSHConnector.user,'password':SSHConnector.pwd}
            self.parent.conn = ConnectHandler(**device)
            yield self.parent.conn
        finally:
            self.parent.conn.disconnect()

    def run_command(self,cmd):
        output = self.parent.conn.send_command(cmd)
        return output


class SSHXRConnector(object):
    # username and password are defined as Class attributes
    user = 'test123'
    pwd = 'test123'

    def __init__(self,parent):
        self.parent = parent

    @contextmanager
    def get_connection(self):
        try:
            hostname = self.parent.info['hostname']
            ip_address = self.parent.info['_id']
            device_type = self.parent.info['family']
            self.parent.conn = IOSXR(hostname=ip_address,username=SSHXRConnector.user,password=SSHXRConnector.pwd)
            self.parent.conn.open()
            yield self.parent.conn
        finally:
            self.parent.conn.close()

    def push_config(self,config):
        try:
            self.parent.conn.load_candidate_config(config=config)
            self.parent.conn.commit_config() 
            return True
        except:
            return False 


class OperationRegistry(object):
    def __init__(self):
       self.func_map = {}

    def device_operation(self,f_name,family=None):
        def func_decorator(func):
            try:
                self.func_map[f_name].update({family:func})
            except:
                self.func_map[f_name] = {family:func}
            #print self.func_map
            def func_wrapper(*args,**kwargs):
                return func(*args,**kwargs)
            return func_wrapper
        return func_decorator  


registry = OperationRegistry()


@registry.device_operation('apply_filter_config',family='iosxr')
def apply_filter_config_iosxr(context,target,prefix):

    config = render_config('filter_hijack_prefixes_iosxr_tmpl.j2',context.info['bgp_asn'],prefix)
    with context.get_connection('cli_xr'):
        result = context.push_config(config)         
    return result


@registry.device_operation('get_facts',family='ios')
def get_facts_ios(context,target):
    '''
    '''
    model_regex = ".*Cisco\s(?P<model>\d+).*"
    show_ver_regex = ".*Software\s\((?P<image>.+)\),\sVersion\s(?P<version>.+), RELEASE.*"

    with context.get_connection('cli'):
        output1 = context.run_command('show version')
        output2 = context.run_command('show inventory')

    facts = {}
    facts['hostname'] = context.info['hostname']
    facts['chassis'] = re.search(r'"Chassis", DESCR: "(.+)"',output2).group(1).strip('\r')
    facts['uptime'] = re.search(r'(.+) uptime is (.+)',output1).group(2).strip('\r')
    facts['serial_number'] = re.search(r'SN: (.+)',output2).group(1).strip('\r')
    facts['model'] = re_match(model_regex,output1).groupdict()['model']
    facts['image'] = re_match(show_ver_regex,output1).groupdict()['image']
    facts['version'] = re_match(show_ver_regex,output1).groupdict()['version']
    return facts


@registry.device_operation('get_facts',family='junos')
def get_facts_junos(context,target):

    #uptime_regex = ".*\sup\s+(\S+),"
    model_regex = "Model:\s+(\S+)"
    version_regex = "JUNOS Base\s.*\s\[(\S+)\]"
 
    with context.get_connection('cli'):
        output1 = context.run_command('show version')
        output2 = context.run_command('show system uptime')

    facts = {}
    facts['hostname'] = context.info['hostname']
    #facts['chassis'] = 
    #facts['serial_number'] =
    #facts['uptime'] = re_search(uptime_regex,output2).group(1)
    facts['model'] = re_search(model_regex,output1).group(1)
    facts['version'] = re_search(version_regex,output1).group(1)   
    return facts        

@registry.device_operation('get_prefixes_received_from_neighbor',family='ios')
def get_prefixes_received_from_neighbor_ios(context,target,neighbor):
    '''
    Executes show ip bgp neighbor <neighbor> received-routes command and returns a list of prefixes.
    '''
    command = 'show ip bgp neighbor {} received-routes'.format(neighbor)
    
    with context.get_connection('cli'):
        output = context.run_command(command)
    
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
        output = context.run_command(command)

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
        output = context.run_command(command)

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
        output = context.run_command(command)

    neighbor_xpath = 'bgp-information/bgp-peer/peer-address'
    asn_xpath = 'bgp-information/bgp-peer/peer-as'

    parsed_neighbor = output.xpath(neighbor_xpath)
    parsed_asn = output.xpath(asn_xpath)
    bgp_neighbors = [ [i.text,j.text] for i,j in zip(parsed_neighbor,parsed_asn) ]
    return bgp_neighbors
 

@registry.device_operation('get_lldp_neighbors',family='ios')
def get_lldp_neighbors_ios(context,target):
    command = 'show lldp neighbors'

    #context.get_connection('cli')
    #with context.get_connection('cli') as cli:
    #    output = cli.run_command(command)

    output = open('cisco_lldp_neighbors.txt').read()
    result = parse_with_textfsm('cisco_ios_show_lldp_neighbors.tmpl',output)
    return result  

