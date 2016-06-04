#!/usr/bin/python

from framework import CheckOperation
#from os_versions import supported_versions


@CheckOperation()
def apply_config(context,target,commands):
    """
    Arguments:
	commands: A list of commands in string or list form."
    """

    result = context.get_operation('apply_config')
    return result


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
    '''
    Arguments:
	target: Target device
	interfaces: Default is 'all'. It also accepts a comma-separated list of interfaces eg. 'xe-0/0/1,xe-0/0/2'
    '''

    interfaces = context.get_operation('get_interfaces')
    print interfaces
    return None


@CheckOperation()
def get_bgp_asn(context,target):
    '''
    Arguments:
        target: Target device
    ''' 

    asn = context.get_operation('get_bgp_asn')
    print "BGP ASN configured on device {} is {}".format(target,asn)
    return None


@CheckOperation()
def get_prefixes_received_from_neighbor(context,target,neighbor,table=None):
    '''
    Arguments:
        target: Target device
        neighbor: BGP neighbor IP address
        table: By default, inet.0 (IPv4) routing tables for JUNOS
    '''

    prefixes = context.get_operation('get_prefixes_received_from_neighbor')
    print prefixes 
    return None


@CheckOperation()
def check_prefixes_received_from_neighbor(context,target,neighbor,prefixes):
    received_prefixes = context.get_operation('get_prefixes_received_from_neighbor')
    for prefix in prefixes:
        if prefix in received_prefixes:
            print 'Prefix {} received from neighbor'.format(prefix)
        else:
            print 'Prefix {} not received from neighbor'.format(prefix)
    return None


@CheckOperation()
def get_bgp_neighbors(context,target):
    '''
    Arguments:
	target: Target device
    '''

    neighbors = context.get_operation('get_bgp_neighbors')
    #print neighbors 
    return neighbors


@CheckOperation()
def get_lldp_neighbors(context,target):
    '''
    IOS: show lldp neighbors
    JUNOS: show lldp neighbors

    The function returns a list of lists with each list-item containing remote device, local interface and remote interface.

    Arguments:
	target - target device on which the command should be executed.
    '''

    neighbors = context.get_operation('get_lldp_neighbors')
    print neighbors
    return None

