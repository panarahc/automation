#!/usr/bin/python

import paramiko
from contextlib import contextmanager
import time
import textfsm
from helper_functions import *
import os


class DeviceConnector(object):

    # username and password are defined as Class attributes
    user = 'test123'
    pwd = 'test123'

    #@contextmanager
    def get_connection(self,type):
        if type == 'cli':
            return self._get_connection_cli(type)
        elif type == 'snmp':
            return self._get_connection_snmp(type)
 
    def _get_connection_snmp(self,type):
        print "Got connection : {}".format(type)
        return None

    #@contextmanager
    def _get_connection_cli(self,type):
        #try:
        hostname = self.info['_id']
        ip_address = self.info['ip_address']
	    #self.ssh = paramiko.SSHClient()
            #self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #self.ssh.connect(hostname,username=DeviceConnector.user,password=DeviceConnector.pwd)
            #yield self.ssh
        print "Hostname : {}, IP Address : {}".format(hostname,ip_address)
        print "Got connection : {}".format(type)
        return None
        #finally:
            #self.ssh.close()   

    def run_command(self,cmd):
        stdin,stdout,stderr = self.ssh.exec_command(cmd)
        return stdout.read()


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
    return None


@registry.device_operation('get_prefixes_received_from_neighbor',family='ios')
def get_prefixes_received_from_neighbor_ios(context,target,neighbor):
    '''
    Executes show ip bgp neighbor <neighbor> received-routes command and returns a list of prefixes.
    '''
    command = 'show ip bgp neighbor {} received-routes'.format(neighbor)
    
    context.get_connection('cli')
    #with closing(context.get_connection('cli')) as cli:
    #    output = cli.run_command(command)
    
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
    return command  

@registry.device_operation('get_prefixes_received_from_neighbor',family='junos')
def get_prefixes_received_from_neighbor_junos(context,target,neighbor):
    '''
    Executes show route receive-protocol bgp <neighbor> command and returns a list of prefixes.
    '''
    command = 'show route receive-protocol bgp {}'.format(neighbor)
    
    context.get_connection('cli')
    #with closing(context.get_connection('cli')) as cli:
    #    output = cli.run_command(command)

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
    return command

@registry.device_operation('get_lldp_neighbors',family='ios')
def get_lldp_neighbors_ios(context,target):
    command = 'show lldp neighbors'

    context.get_connection('cli')
    #with context.get_connection('cli') as cli:
    #    output = cli.run_command(command)

    os.chdir('/Users/abhagat/Code/textfsm')
    output = open('cisco_lldp_neighbors.txt').read()
    result = parse_with_textfsm('cisco_ios_show_lldp_neighbors.tmpl',output)
    return result  

