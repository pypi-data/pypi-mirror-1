from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, error

import time
import thread
import threading
import pprint
import auth
import packet
import consts

def sfind(s, c, m, e):
    p = s.find(c, m)
    if p == -1:
        return e
    else:
        return p+1
def clear_tags(msg):
    msg = str(msg)
    ret = ''
    i = 0
    end = len(msg)
    while i < end:
        if msg[i:i+4].lower() == '<alt':
            i = sfind(msg,'>',i,end)
        if msg[i:i+6].lower() == '</alt>':
            i += 6
        elif msg[i:i+6].lower() == '<font ':
            i = sfind(msg,'>',i,end)
        elif msg[i] == chr(27):
            i = sfind(msg,'m',i,end)
        else:
            ret += msg[i]
            i += 1
    return ret
class Session:
    def __init__(t, u, p, threaded = True, daemonic = False, autoconnect=False, disc_on_err=True):
        t.login_id = u
        t.sess = 0
        t.disc_on_err = disc_on_err
        t.logged = False
        t.passwd = p
        t.ver = 14
        t.status = 0
        t.contacts = ''
        t.ignores = ''
        t.identities = ''
        t.identity_list = []
        t.contact_dict = {}
        t.contact_status = {}
        t.ignore_list = []
        t.daemonic = daemonic
        t.threaded = threaded
        if autoconnect:
            t.connect()
    def start_new_thread(t, func, args=()):
        th = threading.Thread(target=func, args=args)
        th.setDaemon(t.daemonic)
        th.start()
        return th

    def disconnect(t):
        t.sock.shutdown(SHUT_RDWR)
    def connect(t):
        t.err = None
        t.sess = 0
        t.logged = False
        t.status = 0
        t.contacts = ''
        t.ignores = ''
        t.identities = ''
        t.identity_list = []
        t.sock = socket( AF_INET, SOCK_STREAM)
        t.sock.setblocking(1)
        t.sock.connect( ("scs.msg.yahoo.com", 5050) )
        t.send_pk(consts.SERVICE_HANDSHAKE, [])
        t.contact_dict = {}
        t.contact_status = {}
        t.ignore_list = []
        if t.threaded:
            t.worker = t.start_new_thread(t.listener)
            t.on_connect()
        else:
            t.worker = None
            t.on_connect()
            t.listener()
        
    def listener(t):
        t.connected = True
        while t.connected:
            try:
                header = t.sock.recv(20)
                if header:
                    try:
                        pheader = packet.parse_header(header)
                        sz = 0 
                        data = ''
                        while sz < pheader[1]:
                            data += t.sock.recv(pheader[1] - sz)
                            sz = len(data)
                        p = packet.ParsePacket(pheader, data)
                        t.sess = p.sess
                        t.status = p.status
                        if p.svc == consts.SERVICE_HANDSHAKE:
                            t.send_pk(consts.SERVICE_AUTH, ["1",t.login_id])
                        elif p.svc == consts.SERVICE_AUTH:
                            try:
                                t.send_pk(consts.SERVICE_AUTHRESP, auth.hash(t.login_id, t.passwd, p[94]))
                            except:
                                print repr(p)
                                raise
                        elif p.svc == consts.SERVICE_AUTHRESP:
                            if p[66]:
                                t.on_login_fail(p[66])
                        elif p.svc == consts.SERVICE_PING:
                            t.send_pk(consts.SERVICE_PING, [])
                            #print 'Keepalive msg sent.'
                        elif p.svc == consts.SERVICE_LOGIN:
                            #print repr(p)
                            t.start_new_thread(t.process_contacts)
                            if p[66]:
                                t.start_new_thread(t.on_login_fail,(p[66],))
                            else:
                                if not t.logged:
                                    t.logged = True
                                    t.start_new_thread(t.on_login)
                                t.start_new_thread(t.process_status,(p,))
                        elif p.svc == consts.SERVICE_LOGOUT:
                            t.err = p[66]
                        elif p.svc == consts.SERVICE_LIST:
                            if p[87]:
                                t.contacts += p[87]
                            if p[88]:
                                t.ignores += p[88]
                        elif p.svc == consts.SERVICE_STATUS:
                            t.start_new_thread(t.process_status,(p,))
                        elif p.svc == consts.SERVICE_REMBUDDY:
                            t.start_new_thread(t.on_rem_contact_req, (p[1], p[7], p[65]))
                        elif p.svc == consts.SERVICE_BUDDYREQ:
                            #print repr(p)
                            if p[13] == '2':
                                t.start_new_thread(t.on_add_contact_deny,(p[4], p[14]))
                            elif p[13] == '1':
                                t.start_new_thread(t.on_add_contact_approval,(p[4],))
                            else:
                                t.start_new_thread(t.on_add_contact_req, (p[4], p[14]))
                        else:
                            t.start_new_thread(t.on_packet,(p,))
                    except packet.BadHeader:
                        if t.disc_on_err:
                            t.connected = False
                            t.sock.close()
                            t.start_new_thread(t.on_disconnect,('PARSE ERROR',))
                            break
                        else:
                            continue
                    
                    
                else:
                    #print "EMPTY RECV (Disconnected)"
                    if t.connected:
                        t.connected = False
                        t.sock.close()
                        t.start_new_thread(t.on_disconnect,(t.err or 'CONNECTION CLOSED',))

                    break
            except error:
                if t.connected:
                    t.connected = False
                    t.sock.close()
                    t.start_new_thread(t.on_disconnect,(t.err or 'CONNECTION CLOSED',))

            except:
                import traceback
                traceback.print_exc()

    def send_pk(t, svc, msgs, status = None):
        if status==None:
            status = t.status
        p = packet.MakePacket(t.ver, svc, status, t.sess, msgs)
        #print repr(p)
        t.sock.send(str(p))

    def process_status(t,p):
        name = state = msg = away = idle = None
        for i,m in p.iter(): 
            if i == '7':
                name = m
            elif i == '10':
                state = m
            elif i == '19':
                msg = m
            elif i == '47':
                away = m
            elif i == '137':
                idle = m
            elif i == '13':
                if p.svc == consts.SERVICE_LOGOUT and m == '0':
                    state = -1
                if name:
                    t.contact_status[name] = {'state':state, 'msg':msg, 'away':away, 'idle':idle}
                    t.on_status_change(name, consts.status[int(state)],t.contact_status[name])
    def process_contacts(t):
        #print repr(t.contacts)
        for c in t.contacts.split('\n'):
            c = c.strip()
            if c:
                sec, lst = c.split(':')
                t.contact_dict[sec] = lst.split(',')
        for c in t.ignores.split(','):
            t.ignore_list.append(c)
    def on_packet(t, p):

        if p.svc == consts.SERVICE_MESSAGE:
            #print repr(p)
            t.on_message_packet(p[1] or p[4], p[5], p[14] or p[16])
        elif p.svc == consts.SERVICE_NOTIFY:
            t.on_notify_packet(p[4], p[49], p) 
        else:
            t.on_unknown_packet(p)
    def send_msg(t, dst, text):
        t.send_pk(consts.SERVICE_MESSAGE, ['0',t.login_id,'1',t.login_id,'5',dst,'14',text])
    def set_status(t, msg='', type='AVAILABLE', away=False, idle = False):
        if msg:
            stat = consts.status['CUSTOM']
            type = 'CUSTOM'
        else:
            stat = consts.status.get(type,'AVAILABLE')

        if type == 'AVAILABLE':
            svc = consts.SERVICE_ISBACK
        #elif type == 'CUSTOM':
        #    svc = away and consts.SERVICE_ISAWAY or consts.SERVICE_ISBACK
        else:
            svc = consts.SERVICE_ISAWAY
        
        pk = ['10', stat]
        if msg:
            pk.extend(['19', msg])
            pk.extend(['47', away and '1' or '0'])
        #print pk
        t.send_pk(svc, pk)
    def rem_contact(t, who, where, id = None):
        t.send_pk(consts.SERVICE_REMBUDDY, ['1',id or t.login_id,'7',who,'65',where])
    def deny_add_req(t, who, reason):
        t.send_pk(consts.SERVICE_BUDDYREQ, ['4',t.login_id,'5',who,'13','2','97','1','14',reason])
    def deny_add_req_ex(t, who, reason):
        t.send_pk(consts.SERVICE_DENYBUDDY, ['1',t.login_id,'7',who,'14',reason],1)

    def approve_add_req(t, who):
        t.send_pk(consts.SERVICE_BUDDYREQ, ['4',t.login_id,'5',who,'13','1'])
    def add_contact(t, who, where, reason = None):
        pk = ['1',t.login_id,'7',who,'65',where]
        if reason:
            pk.extend(['14',reason])
        t.send_pk(consts.SERVICE_ADDBUDDY, pk)


    # overwrite these ..
    def on_add_contact_deny(t, who, reason):
        pass
    def on_add_contact_approval(t, who):
        pass
    def on_rem_contact_req(t, src, who, where):
        t.contact_list[where].remove(who)
    def on_add_contact_req(t, who, where):
        pass
    def on_unknown_packet(t, p):
        pass
    def on_message_packet(t, src, dst, msg):
        pass
    def on_notify_packet(t, src, msg, p):
        pass
    def on_disconnect(t,err):
        pass
    def on_login(t):
        pass
    def on_login_fail(t):
        pass
    def on_connect(t):
        pass
if __name__ == "__main__":
    pass