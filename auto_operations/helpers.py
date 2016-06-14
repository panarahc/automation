#!/usr/bin/python

import textfsm
import re
import netaddr
import jinja2


def render_config(tmpl,asn,prefix):
    subnets = list()
    prefixlen = prefix.split('/')[1]
    _subnets = list(netaddr.IPNetwork(prefix).subnet(int(prefixlen)+1))
    for item in _subnets:
        subnets.append(item) 
    env = jinja2.Environment(loader=FileSystemLoader('/home/amit/Code/automation'))
    template = env.get_template(tmpl)
    output = template.render(asn=asn,subnets=subnets)
    return output

def template_parser(filename,raw_output):
    template_file = '/usr/local/bin/Code/automation/auto_operations/templates/' + filename 
    template_handler = open(template_file)
    re_table = textfsm.TextFSM(template_handler)
    result = re_table.ParseText(raw_output)
    return result

