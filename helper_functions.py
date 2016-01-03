#!/usr/bin/python

import textfsm
import re


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
