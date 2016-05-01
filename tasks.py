#!/usr/bin/python

from framework import CheckOperation
#from os_versions import supported_versions


@CheckOperation()
def apply_filter_config(context,target,prefixes):
    output = context.get_operation('apply_filter_config',target,prefixes)
    #result[target] = {'prefixes':(', ').join(prefixes), 'device_changed':output} 

@CheckOperation()
def filter_invalid_prefix_by_asn(context,target,contents,result):
    output = context.get_operation('filter_invalid_prefix_by_asn',target,contents)
    result[target] = {'data':contents, 'device_changed':output}

@CheckOperation()
def get_facts(context,target):
    facts = context.get_operation('get_facts')
    print facts
    return None

@CheckOperation()
def get_interfaces(context,target, interfaces='all'):
    print context.__dict__
    interfaces = context.get_operation('get_interfaces')
    print interfaces
    return None

@CheckOperation()
def get_bgp_asn(context,target):
    asn = context.get_operation('get_bgp_asn')
    print "BGP ASN configured on device {} is {}".format(target,asn)
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
	target - target device on which command is executed.
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

