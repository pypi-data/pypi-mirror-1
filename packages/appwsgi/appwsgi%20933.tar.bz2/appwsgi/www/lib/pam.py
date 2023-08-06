# Copyright(c) gert.cuykens@gmail.com
import PAM

def pam_conv(auth, query_list, userData):
    resp = [('*****', 0)]
    return resp

auth = PAM.pam()
auth.start('passwd')
auth.set_item(PAM.PAM_USER, 'root')
auth.set_item(PAM.PAM_CONV, pam_conv)
try:
    auth.authenticate()
    auth.acct_mgmt()
except PAM.error, resp:
    print 'DENIED %s' % resp
except:
    print 'ERROR'
else:
    print 'OK'

