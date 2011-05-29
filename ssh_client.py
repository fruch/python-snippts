
__author__ = 'Fruch'
import paramiko
import os
import time

hostname = "127.0.0.1"
port = 22
username = "fruch"
password = "israeL"

# get host key, if we know one
hostkeytype = None
hostkey = None
try:
    host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
except IOError:
    try:
        # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
        host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
    except IOError:
        print '*** Unable to open host keys file'
        host_keys = {}

if host_keys.has_key(hostname):
    hostkeytype = host_keys[hostname].keys()[0]
    hostkey = host_keys[hostname][hostkeytype]
    print 'Using host key of type %s' % hostkeytype


#t = paramiko.Transport((hostname, port))
#t.connect(username=username, password=password, hostkey=hostkey)

#sftp = paramiko.SFTPClient.from_transport(t)
# dirlist on remote host
#dirlist = sftp.listdir('.')
#print "Dirlist:", dirlist
    

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname="127.0.0.1", port=port, username=username, password=password)
ssh.invoke_shell()
command = """python -c "import sys;sys.stdout.write("ready\n\n\n");sys.stdout.flush();sys.stdin.readline()"
"""

stdin, stdout, stderr = ssh.exec_command(command)

#print stdout.readlines()

time.sleep(2)

import rpyc

c = rpyc.Connection(rpyc.SlaveService,
            rpyc.Channel(rpyc.PipeStream(stdout, stdin)),{})
print dir(c)