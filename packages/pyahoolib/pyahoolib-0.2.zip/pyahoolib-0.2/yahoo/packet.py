import struct
import socket

class BadHeader(Exception):
    pass
def pack(lst):
    return "".join(chr(i) for i in lst)

MSG_SEP = pack([0xC0, 0x80])

def to_int(s):
    c = 0
    for i in s:
        c <<= 8
        c += ord(i)
    return c        

def parse_header(h):
    #print repr(h)
    if h[0:4]=="YMSG" and len(h) == 20:
        return (
            #toint(h[4:8]),
            to_int(h[5]),    #version
            #
            to_int(h[8:10]), #length
            to_int(h[10:12]),#service id
            to_int(h[12:16]),#status
            to_int(h[16:20]) #session id
        )

    else:
        raise BadHeader(h) 
def pack_int(n,size):
    s = ""
    for i in xrange(size):
        s = chr(n&0xFF) + s
        n >>= 8
    return s
def ParseString(s):
    t = Packet()
    t.header = s[:20]
    t.type = "STR"
    t.ver, t.len, t.svc, t.status, t.sess = parse_header(t.header)
    if t.len:
        t.body = s[20:20+t.len]
        t.messages = t.body.split(MSG_SEP)[0:-1]
    else:
        t.body, t.messages = "", []
    return t

def ParsePacket(header, data):
    t = Packet()
    t.header = header
    t.type = "IN"
    t.ver, t.len, t.svc, t.status, t.sess = t.header
    if t.len:
        t.body = data
        t.messages = t.body.split(MSG_SEP)[0:-1]
    else:
        t.body, t.messages = "", []
    return t

def MakePacket(ver, svc, status, sess, messages):
    t = Packet()
    t.type = "OUT"
    t.ver, t.svc, t.status, t.sess, t.messages = ver, svc, status, sess, messages
    return t

class Packet:
    def __init__(t):
        t.len = 0
    def __repr__(t):
        return """
-==========-
Type:       %s
Version:    %s
Service ID: 0x%X (%d)
Status:     0x%X (%d)
Session ID: %s
Length:     %s
Body: %r
-==========-
""" % (t.type, t.ver, t.svc, t.svc, t.status, t.status, t.sess, t.len, t.messages)

    def __str__(t):
        if t.messages:
            msg = MSG_SEP.join(t.messages) + MSG_SEP 
        else:
            msg = ""
        return "YMSG\0%s\0\0%s%s%s%s%s" % \
                (
                    chr(t.ver),
                    pack_int(len(msg),2),
                    pack_int(t.svc,2),
                    pack_int(t.status,4),
                    pack_int(t.sess,4),
                    msg
                )
    def iter(t):
        for x,y in zip(t.messages[0::2],t.messages[1::2]):
            yield (x,y)
    def __getitem__(t, key):
        try:
            return t.messages[1::2][t.messages[::2].index(str(key))]
        except:
            return None

if __name__ == "__main__":
    a = [   0x59, 0x4D, 0x53, 0x47,
            0x00, 0x0E, 0x00, 0x00, 
            0x00, 0x00, 
            0x00, 0x4C, 
            0x00, 0x00, 0x00, 0x00, 
            0xA1, 0x44, 0xB5, 0x23
        ]
    x = parse_header(pack(a))
    print x
    print MakePacket( *(x[0],)+x[2:]+([],) ) == pack(a)
    print 