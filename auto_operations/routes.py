#!/usr/bin/python

from operation_registry import OperationRegistry
from textwrap import dedent
from itertools import izip
import jtextfsm as textfsm
import StringIO


registry = OperationRegistry()

IOS_SHOW_IP_ROUTE_PREFIX_TEMPLATE = StringIO.StringIO(dedent("""\
    Value ROUTE_ENTRY (\S+)
    Value KNOWN_VIA (.*)
    Value ADMIN_DISTANCE (\d+)
    Value METRIC (\d+)
    Value NEXTHOP (\d+\.\d+\.\d+\.\d+)

    Start
      ^Routing entry for ${ROUTE_ENTRY}
      ^\s*Known via \"${KNOWN_VIA}\",\s*distance\s*${ADMIN_DISTANCE},\s*metric\s*${METRIC}
      ^\s*Last update from ${NEXTHOP}
    """))
 

@registry.device_operation('get_route',family='ios,iosxe')
def get_route(context, target, prefix):
    """Get output of 'show ip route <prefix> and parse it."""

    commands = ["show ip route {}".format(prefix)]
    with context.get_connection("cli") as cli:
        response = cli.execute(commands)

    fsm = textfsm.TextFSM(IOS_SHOW_IP_ROUTE_PREFIX_TEMPLATE)
    parsed_output = fsm.ParseText(response[0])

    key_list = ["entry", "known_via", "admin_distance", "metric", "nexthop"]
    return dict(zip(key_list, parsed_output[0]))
