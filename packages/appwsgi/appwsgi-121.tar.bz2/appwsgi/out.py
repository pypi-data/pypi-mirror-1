from smtplib import SMTP

def text(r,db,s):
    j = '{"sid":"'+str(s.SID)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    if db.LASTROWID: j+=' "row":"'+str(db.LASTROWID)+'",\n'
    if db.ERROR: j+=' "error":"'+db.ERROR+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    j=j.encode('utf-8')
    r('200 OK', [('Content-Type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j)))])
    return [j]

def mail(t,s,db):
    f='me'
    p='**'
    m='From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (f, t, s, db.json())
    try:
        server=SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(f,p)
        server.sendmail(f,t,m)
        #server.rset()
        #server.quit()
        db.ERROR="send succesfully"
    except: 
        db.ERROR="mail not send"

