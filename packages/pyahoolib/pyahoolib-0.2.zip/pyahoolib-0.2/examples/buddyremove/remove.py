#!D:\Python25\python.exe
import cgi
import sys
import os
from yahoo.session import Session
from yahoo.consts import *

print "Content-type: text/html"
print 

form = cgi.FieldStorage()
if form.has_key('id'):
    id = form['id'].value
else:
    print '<h2>No id !</h2>'
    sys.exit()
if form.has_key('pass'):
    pwd = form['pass'].value
else:
    print '<h2>No password !</h2>'
    sys.exit()
if form.has_key('who'):
    who = form['who'].value
else:
    print '<h2>No target !</h2>'
    sys.exit()
if form.has_key('msg'):
    msg = form['msg'].value
else:
    msg = ''

class YM(Session):
    def on_login(t):
        t.deny_add_req_ex(who,msg)
        print '<h2>Deny packet sent !</h2>'
        t.disconnect()

    def on_login_fail(t,err):
        print "<h2>Failed to login because:",
        if err == LOGIN_UNAME:
            print 'invalid username.',
        elif err == LOGIN_PASSWD:
            print 'bad password.',
        elif err == LOGIN_LOCK:
            print 'account locked.',
        else:
            print 'unkown reason.',
        print '</h2>'
        
    def on_disconnect(t,err):
        pass

y = YM(id, pwd, daemonic=False)
y.connect()



