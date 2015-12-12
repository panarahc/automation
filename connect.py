#!/usr/bin/python

import paramiko
from contextlib import contextmanager

@contextmanager
def get_ssh(host):
    user = 'abhagat'
    pwd = 'Heena2015!'
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,username=user,password=pwd,allow_agent=False,look_for_keys=False)
        yield ssh
    finally:
        ssh.close()    


with get_ssh('localhost') as ssh:
    cmd = 'ls -l /Users/abhagat/Code/autochecks'
    stdin,stdout,stderr = ssh.exec_command(cmd)
    print stdout
    print '+'*40
    cmd = 'ls -l /Users/abhagat/Code'
    stdin,stdout,stderr = ssh.exec_command(cmd)
    print stdout
