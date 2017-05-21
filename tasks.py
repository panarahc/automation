#!/usr/bin/python

from framework import CheckOperation
#from os_versions import supported_versions
from auto_operations.helpers import interface_expand


@CheckOperation()
def apply_config(context,target,commands):
    """
    Arguments:
	commands: A list of commands.
    """

    result = context.get_operation('apply_config')
    return result


@CheckOperation()
def config_replace(context,target,filename):
    """
    Replaces running-config of the device with a new file.

    Arguments:
	filename: Config file to replace running-config.
    """

    result = context.get_operation('config_replace')
    return result


@CheckOperation()
def get_config_diff(context, target, file1, file2):
    """
    Runs a diff between two files on the device and returns a diff.

    Arguments:
    	target: Target device
	file1: Config file1 eg. system:running-config
	file2: Config file2 eg. scp://file2
    """

    result = context.get_operation('get_config_diff')
    return result


@CheckOperation()
def get_device_traffic(context,target):
    """
    Check to get total traffic (pps) going through the device.
    It uses get_interfaces_traffic operation.

    Arguments:
	target: Target device
    """

    result = context.get_operation('get_interfaces_traffic')
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
    return facts


@CheckOperation()
def get_interfaces(context,target, interfaces='all'):
    '''
    Arguments:
	target: Target device
	interfaces: Default is 'all'. It also accepts a comma-separated list of interfaces eg. 'xe-0/0/1,xe-0/0/2'
    '''

    interfaces = context.get_operation('get_interfaces')
    return interfaces

@CheckOperation()
def get_interfaces_utilization(context, target, interfaces='all'):
    '''
    Arguments:
        target: Target device
        interfaces: Default is 'all'. It also accepts a comma-separated list of interfaces eg. 'xe-0/0/1,xe-0/0/2'
    '''

    def append_to_list(_intf):
        bandwidth = _intf.bandwidth
        interfaces_util.append({'name': _intf.name,
                                'description': _intf.description,
                                'input_utilization': calculate_utilization(_intf.input_rate, bandwidth),
                                'output_utilization': calculate_utilization(_intf.output_rate, bandwidth)})


    device_interfaces = context.get_operation('get_interfaces')

    interfaces_util = list() 
    if interfaces == 'all':
        for interface in device_interfaces:
            append_to_list(interface)
    else:
        input_interfaces = [ interface_expand(intf) for intf in interfaces.split(',') ]
        for intf in input_interfaces:
            append_to_list(filter(lambda x: x.name==intf, device_interfaces)[0])
    return interfaces_util


def calculate_utilization(rate, bandwidth):
    return (int(rate) / float(bandwidth)) * 100


@CheckOperation()
def get_route_entry(context, target, prefix):
    """Get entry from the route table that matches the prefix."""

    route_entry = context.get_operation("get_route")

    return route_entry["entry"]


@CheckOperation()
def get_ospf_neighbors(context, target):
    '''
    Gets OSPF neighbors and state on device.
    '''

    neighbors = context.get_operation('get_ospf_neighbors')
    return neighbors


@CheckOperation()
def get_bgp_asn(context,target):
    '''
    Arguments:
        target: Target device
    ''' 

    asn = context.get_operation('get_bgp_asn')
    return asn


@CheckOperation()
def get_prefixes_received_from_neighbor(context,target,neighbor,table=None):
    '''
    Arguments:
        target: Target device
        neighbor: BGP neighbor IP address
        table: By default, inet.0 (IPv4) routing tables for JUNOS
    '''

    prefixes = context.get_operation('get_prefixes_received_from_neighbor')
    return prefixes


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
def get_bgp_neighbors(context, target):
    """Get a list of BGP neighbors for a given device."""

    response = context.get_operation("get_bgp_neighbors")
    neighbors = [ row["neighbor"] for row in response ]
    return neighbors


@CheckOperation()
def get_bgp_neighbors_state(context, target, neighbors="all"):
    '''
    Performs a get_bgp_neighbors_state operation and returns a dict
    of form {neighbor:state}

    Arguments:
  	target: Target device
	neighbors: A comma-separated list of BGP neighbor IP addresses. Default is all. 
    '''

    neighbors_state = context.get_operation('get_bgp_neighbors_state')
    return neighbors_state


@CheckOperation()
def get_bgp_peergroups(context,target):
    '''
    Arguments:
	target: Target device

    Returns:
	A list of BGP peergroups configured on device.
    '''

    peergroups = context.get_operation('get_bgp_peergroups')
    return peergroups


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
    return neighbors

@CheckOperation()
def get_mpls_table(context, target):
    '''
    IOS: show mpls forwarding-table

    The function returns a list of dicts with each list-item containing
    local label, remote label, prefix, interface, nexthop.

    Arguments:
       target - target device
    '''

    labels = context.get_operation('get_mpls_table')
    return labels
