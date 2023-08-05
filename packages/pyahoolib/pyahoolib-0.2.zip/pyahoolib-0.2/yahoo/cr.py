import md5
import base64
def md5crypt(password, salt, magic='$1$'):
    m = md5.new()
    m.update(password + magic + salt)

    mixin = md5.md5(password + salt + password).digest()
    for i in range(0, len(password)):
        m.update(mixin[i % 16])

    i = len(password)
    while i:
        if i & 1:
            m.update('\x00')
        else:
            m.update(password[0])
        i >>= 1

    final = m.digest()
    for i in range(1000):
        m2 = md5.md5()
        if i & 1:
            m2.update(password)
        else:
            m2.update(final)
        if i % 3:
            m2.update(salt)
        if i % 7:
            m2.update(password)
        if i & 1:
            m2.update(final)
        else:
            m2.update(password)
        final = m2.digest()

    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    rearranged = ''
    for a, b, c in ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = ord(final[a]) << 16 | ord(final[b]) << 8 | ord(final[c])
        for i in range(4):
            rearranged += itoa64[v & 0x3f]; v >>= 6
    v = ord(final[11])
    for i in range(2):
        rearranged += itoa64[v & 0x3f]; v >>= 6
    return magic + salt + '$' + rearranged
def to_y64(s):
    y64aphabet = "._CDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return base64.b64encode(s,y64aphabet).replace('=','-')
   

if __name__ == "__main__":
    #$1$_2S43d5f$WjsGkIRx4ZUewyw0nZpZS1
    a = md5crypt('xxx', "_2S43d5f")
    print a
    print 'hLxkGQ1hC1sPp9vF.cA_sg--'
    b = to_y64(md5.new(a).digest())
    print b