import time
import pprint
from yahoo.session import Session, clear_tags
from yahoo.consts import *
import os

class YahooClient(Session):
    def on_unknown_packet(t, p):
        print "Recieved unknown packet - svc id: 0x%X(%d)" % (p.svc,p.svc)
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
    y = YahooClient('ionel_cm','asdqwe', daemonic=True)
    y.connect()
    try:
        os.mkfifo('MYFIFO')
    except:
        import traceback
        traceback.print_exc()
    
    while 1:
        if y.logged:
            fh = file('MYFIFO','r')
            while 1:
                ln = fh.readline()
                if not ln:
                    break
                print "*** Sending:", repr(ln)
                y.send_msg('ionel_mc',ln)
            fh.close()