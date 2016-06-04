#!/usr/bin/python

#-------------------------------------------------------------------
# This connect script is adapted from Ansible's module_utils.shell
# module with minor customization.
#-------------------------------------------------------------------

import re
import socket
import paramiko
from StringIO import StringIO


ANSI_RE = re.compile(r'(\x1b\[\?1h\x1b=)')

CLI_PROMPTS_RE = [
    re.compile(r'[\r\n]?[a-zA-Z]{1}[a-zA-Z0-9-]*[>|#|%](?:\s*)$'),
    re.compile(r'[\r\n]?[a-zA-Z]{1}[a-zA-Z0-9-]*\(.+\)#(?:\s*)$'),
    re.compile(r'[\r\n]?[a-zA-Z]{1}[a-zA-Z0-9-]*@[a-zA-Z0-9]*[>|#|%](?:\s*)$')
]

CLI_INPUTS_RE = [
    re.compile(r'Destination filename.*'),
    re.compile(r'Overwrite the previous NVRAM.*')
]

CLI_ERRORS_RE = [
    re.compile(r"% ?Error"),
    re.compile(r"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"% Invalid input"),
    re.compile(r"(?:Incomplete|ambiguous) command"),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found"),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"syntax error"),
    re.compile(r"unknown command")
]

def to_list(val):
    if isinstance(val, (list, tuple)):
        return list(val)
    elif val is not None:
        return [val]
    else:
        return list()


class ShellError(Exception):

    def __init__(self, msg, command=None):
        super(ShellError, self).__init__(msg)
        self.message = msg
        self.command = command


class Command(object):

    def __init__(self, command, prompt=None, response=None):
        self.command = command
        self.prompt = prompt
        self.response = response

    def __str__(self):
        return self.command


class Shell(object):

    def __init__(self, prompts_re=None, errors_re=None, inputs_re=None, kickstart=False):
        self.ssh = None
        self.shell = None

        self.kickstart = kickstart
        self._matched_prompt = None

        self.prompts = prompts_re or CLI_PROMPTS_RE
        self.errors = errors_re or CLI_ERRORS_RE
        self.inputs = inputs_re or CLI_INPUTS_RE

    def open(self, host, port=22, username=None, password=None,
            timeout=10, key_filename=None, pkey=None, look_for_keys=None,
            allow_agent=False):

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if not look_for_keys:
            look_for_keys = password is None

        self.ssh.connect(host, port=port, username=username, password=password,
                    timeout=timeout, look_for_keys=look_for_keys, pkey=pkey,
                    key_filename=key_filename, allow_agent=allow_agent)

        self.shell = self.ssh.invoke_shell()
        self.shell.settimeout(10)

        if self.kickstart:
            self.shell.sendall('\n')

        self.receive()

    def strip(self, data):
        return ANSI_RE.sub('', data)

    def receive(self, cmd=None):
        recv = StringIO()

        while True:
            data = self.shell.recv(200)

            recv.write(data)
            recv.seek(recv.tell() - 200)

            window = self.strip(recv.read())

            if isinstance(cmd, Command):
                self.handle_input(window, prompt=cmd.prompt,
                                  response=cmd.response)

            try:
                if self.read(window):
                    resp = self.strip(recv.getvalue())
                    return self.sanitize(cmd, resp)
            except ShellError, exc:
                exc.command = cmd
                raise

    def send(self, commands):
        responses = list()
        try:
            for command in to_list(commands):
                cmd = '%s\r' % str(command)
                self.shell.sendall(cmd)
                responses.append(self.receive(command))
        except socket.timeout, exc:
            raise ShellError("timeout trying to send command", cmd)
        return responses

    def close(self):
        self.shell.close()

    def handle_input(self, resp, prompt, response):
        if not prompt or not response:
            return

        prompt = to_list(prompt)
        response = to_list(response)

        for pr, ans in zip(prompt, response):
            match = pr.search(resp)
            if match:
                cmd = '%s\r' % ans
                self.shell.sendall(cmd)

    def sanitize(self, cmd, resp):
        cleaned = []
        for line in resp.splitlines():
            if line.startswith(str(cmd)) or self.read(line):
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    def read(self, response):
        for regex in self.inputs:
            if regex.search(response):
                self.shell.sendall('\n')

        for regex in self.errors:
            if regex.search(response):
                raise ShellError('matched error in response: %s' % response)

        for regex in self.prompts:
            match = regex.search(response)
            if match:
                self._matched_prompt = match.group()
                return True
