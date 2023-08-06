from smtplib import SMTP

def mail(t,s,m):
    f='me'
    p='**'
    m='From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (f, t, s, m)
    try :
        server=SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(f,p)
        server.sendmail(f,t,m)
        #server.rset()
        #server.quit()
    except : return '{"error":"mail not send"}'
    return '{"error":"send succesfully"}'
