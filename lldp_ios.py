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
    mac = _search(data, 'Chassis id: (\S+)')
    neighbor['chassis_id'] = mac.group(1) if mac else ''

    # Parse the data to find neighbor port
    intf = _search(data, r'\nPort id: (.*)')
    neighbor['port_description'] = intf.group(1) if intf else ''

    # Parse the data to find neighbor port description
    port_desc = _search(data, r'Port Description: (.*)')
    neighbor['port_id'] = port_desc.group(1) if port_desc else ''

    # Parse the data to find neighbor system name
    name = _search(data, r'System\s+Name: (\S+)')
    neighbor['neighbor_device'] = name.group(1) if name else ''

    # Parse the data to find neighbor system description
    desc = data.splitlines()[6]
    neighbor['platform'] = desc if desc else ''

    # Parse the data to find neighbor mgmt ip
    mgmt_addr = _search(data, r'\sIP:\s+(.*)\n')
    neighbor['mgmt_address'] = mgmt_addr.group(1) if mgmt_addr else ''

    return neighbor

output = open('cisco_ios_lldp_neighbor_detail.txt').read()

result = _parse_raw_neighbor(output)
print result
