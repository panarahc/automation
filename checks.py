#!/usr/bin/python

from framework import CheckOperation
from os_versions import supported_versions


@CheckOperation()
def get_prefixes_received_from_neighbor(context,target,neighbor):
    #print context.info
    prefixes = context.get_operation('get_prefixes_received_from_neighbor',target,neighbor)
    #print "Target: {}".format(target)
    #print "Neighbor: {}".format(neighbor)
    print prefixes 
    return None

@CheckOperation()
def check_prefixes_received_from_neighbor(context,target,neighbor):
    prefixes = context.get_operation('get_prefixes_received_from_neighbor',target,neighbor)
    #print "Target: {}".format(target)
    #print "Neighbor: {}".format(neighbor)
    print prefixes
    return None

@CheckOperation()
def get_lldp_neighbors(context,target):
    '''
    IOS: show lldp neighbors
    JUNOS: show lldp neighbors

    The functions returns a list of lists with each list-item containing remote device, local interface and remote interface.

    Arguments:
	target - target device on which the command should be executed.
    '''
    neighbors = context.get_operation('get_lldp_neighbors',target)
    print neighbors
    return None

