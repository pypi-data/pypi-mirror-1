import time
import pprint
import yahoo
import socket
from yahoo.session import Session, clear_tags
from yahoo.consts import *

class YahooClient(Session):
    def on_unknown_packet(t, p):
        print "Recieved unknown packet - svc id: 0x%X(%d)" % (p.svc,p.svc)
        #print repr(p)
    def on_message_packet(t, src, dst, msg):
        print "From <%s>: %s" % (src, clear_tags(msg))
    def on_notify_packet(t, src, msg, p):
        print "%s: %s." % (src,msg)
    def on_disconnect(t,err):
        if err == LOGIN_DUPL:
            print "Disconnected due to duplicate login."
        else:
            print "Disconnected for unkown reason."
        time.sleep(2)
        print "Reconnecting..."
        t.connect()
    def on_login(t):
        print "Contacts: ",
        pprint.pprint(t.contact_dict, indent=4)
        t.set_status('Powered by: %s !' % yahoo.__version__)
        #t.set_status(type='BRB')
        time.sleep(10)
        t.sock.shutdown(socket.SHUT_RDWR)
    def on_login_fail(t,err):
        print "Failed to login because:",
        if err == LOGIN_UNAME:
            print 'invalid username.'
        elif err == LOGIN_PASSWD:
            print 'bad password.'
        elif err == LOGIN_LOCK:
            print 'account locked.'
        else:
            print 'unkown reason.'
    def on_connect(t):
        if t.worker:
            print "Daemonic worker:",t.worker.isDaemon() 
    def on_status_change(t, name, status, details):
        print "%s - %s %s" % (name, status, details)
if __name__ == "__main__":
    import getpass
    #y = YahooClient(raw_input('user:'),getpass.getpass('passwd:'), daemonic=True)
    y = YahooClient('ionel_cm','qweasd', daemonic=False)
    y.connect()
    while 1:
        time.sleep(100)
