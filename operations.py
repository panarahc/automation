#!/usr/bin/python

from netmiko import ConnectHandler
from contextlib import contextmanager
from ncclient import manager
from helper_functions import _search,_match 
import time
import textfsm
import re


class NetconfConnector(object):

    user = 'test123'
    pwd = 'test123'

    def __init__(self,parent):
        self.parent = parent

    @contextmanager
    def get_connection(self,connect_type):
        try:
            hostname = self.parent.info['_id']
            ip_address = self.parent.info['ip_address']
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
    def get_connection(self,connect_type):
        try:
            hostname = self.parent.info['_id']
            ip_address = self.parent.info['ip_address']
            device_type = self.parent.info['family']
            device = {'device_type':device_type,'ip':ip_address,'username':SSHConnector.user,'password':SSHConnector.pwd}
            self.parent.conn = ConnectHandler(**device)
            yield self.parent.conn
        finally:
            self.parent.conn.disconnect()

    def run_command(self,cmd):
        output = self.parent.conn.send_command(cmd)
        return output


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
    facts['_id'] = target
    facts['chassis'] = re.search(r'"Chassis", DESCR: "(.+)"',output2).group(1).strip('\r')
    facts['uptime'] = re.search(r'(.+) uptime is (.+)',output1).group(2).strip('\r')
    facts['serial_number'] = re.search(r'SN: (.+)',output2).group(1).strip('\r')
    facts['model'] = _match(model_regex,output1).groupdict()['model']
    facts['image'] = _match(show_ver_regex,output1).groupdict()['image']
    facts['version'] = _match(show_ver_regex,output1).groupdict()['version']
    return facts


@registry.device_operation('get_facts',family='junos')
def get_facts_junos(context,target):

    uptime_regex = ".*\sup\s+(\S+),"
    model_regex = "Model:\s+(\S+)"
    version_regex = "JUNOS Base\s.*\s\[(\S+)\]"
 
    with context.get_connection('cli'):
        output1 = context.run_command('show version')
        output2 = context.run_command('show system uptime')

    facts = {}
    facts['_id'] = target
    #facts['chassis'] = 
    #facts['serial_number'] =
    facts['uptime'] = _search(uptime_regex,output2).group(1)
    facts['model'] = _search(model_regex,output1).group(1)
    facts['version'] = _search(version_regex,output1).group(1)   
    return facts        

@registry.device_operation('get_prefixes_received_from_neighbor',family='ios')
def get_prefixes_received_from_neighbor_ios(context,target,neighbor):
    '''
    Executes show ip bgp neighbor <neighbor> received-routes command and returns a list of prefixes.
    '''
    command = 'show ip bgp neighbor {} received-routes'.format(neighbor)
    
    with context.get_connection('cli'):
        output = context.run_command(command)
    
    #prefixes = []
    #template = open('cisco_show_ip_bgp.tmpl')
    #re_table = textfsm.TextFSM(template)
    #
    #results = re_table.ParseText(output)
    #for row in results:
    #    if row[1]:
    #        prefixes.append(row[1])
    #
    #return prefixes
    return output  

@registry.device_operation('get_prefixes_received_from_neighbor',family='junos')
def get_prefixes_received_from_neighbor_junos(context,target,neighbor):
    '''
    Executes show route receive-protocol bgp <neighbor> command and returns a list of prefixes.
    '''
    command = 'show route receive-protocol bgp {}'.format(neighbor)
    
    with context.get_connection('netconf'):
        output = context.run_command(command)

    #prefixes = []
    #template = open('junos_bgp_prefixes_received_from_neighbor.tmpl')
    #re_table = textfsm.TextFSM(template)
    #
    #results = re_table.ParseText(output)
    #for row in results:
    #    if row[1]:
    #        prefixes.append(row[1])
    #
    #return prefixes
    return output

@registry.device_operation('get_lldp_neighbors',family='ios')
def get_lldp_neighbors_ios(context,target):
    command = 'show lldp neighbors'

    #context.get_connection('cli')
    #with context.get_connection('cli') as cli:
    #    output = cli.run_command(command)

    output = open('cisco_lldp_neighbors.txt').read()
    result = parse_with_textfsm('cisco_ios_show_lldp_neighbors.tmpl',output)
    return result  

