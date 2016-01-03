#!/usr/bin/python

from framework import CheckOperation
#from os_versions import supported_versions


@CheckOperation()
def get_facts(context,target):
    facts = context.get_operation('get_facts',target)
    print facts
    return None

@CheckOperation()
def get_prefixes_received_from_neighbor(context,target,neighbor):
    prefixes = context.get_operation('get_prefixes_received_from_neighbor',target,neighbor)
    print prefixes 
    return None

@CheckOperation()
def check_prefixes_received_from_neighbor(context,target,neighbor,prefixes):
    received_prefixes = context.get_operation('get_prefixes_received_from_neighbor',target,neighbor)
    for prefix in prefixes:
        if prefix in received_prefixes:
            print 'Prefix {} received from neighbor'.format(prefix)
        else:
            print 'Prefix {} not received from neighbor'.format(prefix)
    return None

@CheckOperation()
def get_bgp_neighbors(context,target):
    '''
    IOS: show ip bgp summary
    JUNOS: show bgp summary

    Arguments:
	target - target device on which the command should be executed.
    '''

    neighbors = context.get_operation('get_bgp_neighbors',target)
    for neighbor in neighbors:
        print neighbor[0] 
    return None

@CheckOperation()
def get_lldp_neighbors(context,target):
    '''
    IOS: show lldp neighbors
    JUNOS: show lldp neighbors

    The function returns a list of lists with each list-item containing remote device, local interface and remote interface.

    Arguments:
	target - target device on which the command should be executed.
    '''

    neighbors = context.get_operation('get_lldp_neighbors',target)
    print neighbors
    return None

