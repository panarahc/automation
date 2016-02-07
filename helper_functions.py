#!/usr/bin/python

import textfsm
import re
from netaddr import *
from jinja2 import *


def render_config(tmpl,asn,prefix):
    subnets = list()
    prefixlen = prefix.split('/')[1]
    _subnets = list(IPNetwork(prefix).subnet(int(prefixlen)+1))
    for item in _subnets:
        subnets.append(item) 
    env = Environment(loader=FileSystemLoader('/home/amit/Code/automation'))
    template = env.get_template(tmpl)
    output = template.render(asn=asn,subnets=subnets)
    return output

def parse_with_textfsm(template_file,raw_output):
    template_handler = open(template_file)
    re_table = textfsm.TextFSM(template_handler)
    result = re_table.ParseText(raw_output)
    return result

def re_match(regex,output):
    output = re.match(regex,output,re.DOTALL)
    return output

def re_search(regex,output):
    output = re.search(regex,output,re.DOTALL)
    return output
