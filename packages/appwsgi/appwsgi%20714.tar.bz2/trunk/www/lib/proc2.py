from pxssh import pxssh

try:
    s = pxssh()
    s.login ('127.0.0.1', 'gert', '123')
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
    s.sendline ('123')
    s.sync_original_prompt()
    s.set_unique_prompt()
    s.prompt()
    print s.before
    s.sendline ('df')
    s.prompt()
    print s.before
    s.sendline ('exit')
    s.logout()

except ExceptionPxssh, e:
    print "pxssh failed on login."
    print str(e)

