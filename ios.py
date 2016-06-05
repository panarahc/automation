#!/usr/bin/python

from shell import *
from contextlib import contextmanager


NET_PASSWD_RE = re.compile(r"[\r\n]?password: $", re.I)

def to_list(val):
    if isinstance(val, (list, tuple)):
        return list(val)
    elif val is not None:
        return [val]
    else:
        return list()


class CLI(object):

    enable_password = 'test123'
    username = 'test123'
    password = 'test123'

    def __init__(self,host,port=None):
        self.connection = None
        self._connected = False
        self.host = host 
        self.port = port or 22

    @property
    def connected(self):
        return self._connected

    @contextmanager
    def connect(self):
        try:
            self.connection = Shell()
            self.connection.open(self.host, port=self.port, username=CLI.username, password=CLI.password)
            self._connected = True
            self.connection.send('terminal length 0')
            yield self
            self.disconnect()
        except:
            raise

    @contextmanager
    def authorize(self):
        passwd = CLI.enable_password 
        self.connection.send(Command('enable',prompt = NET_PASSWD_RE, response = passwd)) 
        yield self

    def execute(self, commands, **kwargs):
        try:
            if not self.connected:
                self.connect()
            return self.connection.send(commands, **kwargs)
        except:
            raise 

    def configure(self, commands):
        commands = to_list(commands)
        commands.insert(0, 'configure terminal revert timer idle 1')
        commands.append('end')
        commands.append('configure confirm')
        responses = self.execute(commands)
        responses.pop(0)
        return responses

    def disconnect(self):
        self.connection.close()
        self._connected = False

