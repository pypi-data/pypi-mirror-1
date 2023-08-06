# Copyright(c) gert.cuykens@gmail.com
# Only use this if you can not set a public key on the remote server
# Source http://pexpect.sourceforge.net

from pxssh import pxssh, ExceptionPxssh

try:
    s = pxssh()
    s.login ('127.0.0.1', 'gert', '***')
    s.sendline ('uptime')
    s.prompt()
    print s.before
    s.sendline ('ls -l')
    s.prompt()
    print s.before
    s.sendline ('df')
    s.prompt()
    print s.before
    s.sendline ('su')
    s.expect('Password:')
    s.sendline ('***')
    s.synch_original_prompt()
    s.set_unique_prompt()
    s.sendline ('ps aux')
    s.prompt()
    print s.before
    s.sendline ('exit')
    s.logout()

except ExceptionPxssh, e:
    print "pxssh failed"
    print str(e)

"""
import pexpect
import sys

child = pexpect.spawn("ssh gert@127.0.0.1")
#child.logfile = sys.stdout

i = child.expect(['assword:', r'yes/no'],timeout=120)
if i==0:
    child.sendline('***')
elif i==1:
    child.sendline('yes')
    child.expect('assword:', timeout=120)
    child.sendline('***')
child.expect(':~\$ ')
print child.before

child.sendline('ls -l')
child.expect(':~\$ ')
print child.before

child.sendline('su')
child.expect('assword:')
child.sendline('***')
child.expect(':/# ')
print child.before

child.sendline('ls -l')
child.expect(':/# ')
print child.before
"""
