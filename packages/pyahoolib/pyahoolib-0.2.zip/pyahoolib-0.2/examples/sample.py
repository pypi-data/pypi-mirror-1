import time
import pprint
import yahoo
from yahoo.session import Session, clear_tags
from yahoo.consts import *

class YahooClient(Session):
    def on_unknown_packet(t, p):
        print "Recieved unknown packet - svc id: 0x%X(%d)" % (p.svc,p.svc)
        #print repr(p)
        #if p.svc == 15:
        #    print repr(p)
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
        t.set_status('Powered by: %s ! http://ionel.zapto.org/browser/ym' % yahoo.__version__)
        #t.set_status(type='BRB')
        #
        #t.send_pk(SERVICE_ADDBUDDYVALIDATE, ['0',t.login_id])
        #t.send_pk(SERVICE_BUDDYREQ, ['1',t.login_id,'4','ionel_mc','13','2','14','wha'])
        time.sleep(1)
        print 'BAM'
        #t.send_pk(0x86, ['1',t.login_id,'7','ionel_mc','13','2','14','muie'], 0)
        #t.send_pk(SERVICE_ADDBUDDYVALIDATE, ['0',t.login_id],1)
        t.deny_add_req_ex('ionel_mc', 'aaaaaaaaaaaa')
        #t.rem_contact('ionel_mc','test')

        #t.rem_contact('cristian2104','test')
        #t.deny_add_req('cristian2104', '')
        for g in t.contact_dict.keys():
            print 'g:',g
            for c in t.contact_dict[g]:
                print 'c:',c
                t.rem_contact(c,g)
                time.sleep(1)
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
    def on_rem_contact_req(t, src, who, where):
        print "Request to remove contact '%s' from '%s'." % (who,where)
    def on_add_contact_req(t, who, msg):
        print "%s requested a buddy add. He said: '%s'" % (who,msg)
        if msg == "please":
            print "Approving (he said 'please')."
            #t.deny_add_req(who, 'Please is not enough !')
            #t.deny_add_req_ex(who, 'Please is not enough !')
            t.approve_add_req(who)
            t.add_contact(who, 'test')
        else:
            print "Denying the bastard."
            t.deny_add_req(who, 'Say please fucker !')
    def on_add_contact_deny(t, who, reason):
        print "%s denied my buddy add request because: '%s'." % (who,reason)
    def on_add_contact_approval(t, who):
        print "%s approved my add request." % who

if __name__ == "__main__":
    print '--'
    import getpass
    #y = YahooClient(raw_input('user:'),getpass.getpass('passwd:'), daemonic=True)
    y = YahooClient('ionel_cm','qweasd', daemonic=True)
    y.connect()
    import time
    while 1:
        if y.logged:
            y.send_msg(raw_input('who:'),raw_input('text:'))
        time.sleep(0.5)