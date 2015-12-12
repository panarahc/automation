#!/usr/bin/python

import re

def _search(data, regex):
    if data and regex:
        reg = re.compile(r'%s' % regex)
        match = reg.search(data)
        if match:
            return match
        else:
            return None

def _parse_raw_neighbor(data):

    if not data:
        return

    neighbor = dict()

    # Parse the data to find neighbor mac address
    mac = _search(data, 'Chassis\s+ID\s+:\s+(\S+)')
    neighbor['chassis_id'] = mac.group(1) if mac else ''

    # Parse the data to find neighbor port
    intf = _search(data, r'\nPort ID\s+: (\S+)')
    neighbor['port_id'] = intf.group(1) if intf else ''

    # Parse the data to find neighbor port description
    port_desc = _search(data, r'Port description\s+: (.*)')
    neighbor['port_description'] = port_desc.group(1) if port_desc else ''

    # Parse the data to find neighbor system name
    name = _search(data, r'System\s+name\s+: (\S+)')
    neighbor['neighbor_device'] = name.group(1) if name else ''

    # Parse the data to find neighbor system description
    desc = _search(data, r'System Description\s+: (.*)\n')
    neighbor['platform'] = desc.group(1) if desc else ''

    # Parse the data to find neighbor mgmt ip
    mgmt_addr = _search(data, r'Management\s+Address\s+:\s+(.*)\n')
    neighbor['mgmt_address'] = mgmt_addr.group(1) if mgmt_addr else ''

    return neighbor

output = open('junos_lldp_neighbor_detail.txt').read()

result = _parse_raw_neighbor(output)
print result
