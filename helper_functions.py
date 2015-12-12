#!/usr/bin/python

import textfsm


def parse_with_textfsm(template_file,raw_output):
    template_handler = open(template_file)
    re_table = textfsm.TextFSM(template_handler)
    result = re_table.ParseText(raw_output)
    return result
