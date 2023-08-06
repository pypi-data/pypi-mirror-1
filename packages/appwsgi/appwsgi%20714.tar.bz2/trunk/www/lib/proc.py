# Copyright(c) gert.cuykens@gmail.com
# Only use this when you can not copy your public ssh key
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

