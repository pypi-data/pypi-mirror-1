import base64
import py_sha as sha
import md5
import ch
import cr
import packet
def hprint(l):
    for i in l:
        if isinstance(i,int) or isinstance(i,long):
            print "%02X" % i,
        else:
            print "%02X" % ord(i),
    print

def hash(u,p,seed):
    alphabet1 = "FBZDWAGHrJTLMNOPpRSKUVEXYChImkwQ"
    alphabet2 = "F0E1D2C3B4A59687abcdefghijklmnop"

    challenge_lookup = "qzec2tb3um1olpar8whx4dfgijknsvy5"
    operand_lookup = "+|&%/*^-"
    delimit_lookup = ",;"
    magic_work = 0
    magic = []
    for i in seed:
        if i in ['(',')']:
            continue
        if i.isdigit() or i.isalpha():
            if i in challenge_lookup:
                magic_work = (challenge_lookup.index(i)) << 3
            else:
                continue
        elif i in operand_lookup:
            magic.append( magic_work | (operand_lookup.index(i)) )

    for i in xrange(len(magic)-2, -1, -1):
        a = magic[i]
        b = magic[i+1]
        a = (a * 0xCD) & 0xFF
        a ^= b
        magic[i+1] = a
    c = []
    i = 1
    magic.extend([0]*(64-len(magic)))
    while len(c)<20:
        bl = 0
        cl = magic[i]
        i += 1
        if i+1>=len(magic): 
            print i
            break
        if cl > 0x7F:
            if cl < 0xE0:
                bl = cl = (cl & 0x1F) << 6
            else:
                bl = magic[i]
                i += 1
                cl = (cl & 0x0F) << 6
                bl = ((bl & 0x3F) + cl) << 6
            cl = magic[i]
            i += 1
            bl = (cl & 0x3F) + bl
        else:
            bl = cl

        c.append((bl & 0xff00) >> 8)  
        c.append(bl & 0xff)  
    mkey = c[:4]
    mkeystr = "".join(map(chr,mkey))
    mrest = "".join(map(chr,c[4:]))
    for x in xrange(0xFFFF):
        leave = False
        for y in xrange(5):
            hs = md5.new(mkeystr+"".join(map(chr,[x,x>>8,y]))).digest()
            if hs == mrest:
                leave = True
                break
        if leave:
            break
    if y != 0:
        updated_key = packet.to_int(reversed(mkeystr))
        updated_key = ch.count(updated_key, 0x60, y, x)
        updated_key = packet.to_int(packet.pack_int(updated_key,4))
        updated_key = ch.count(updated_key, 0x60, y, x)
        mkey[0] =  updated_key & 0xff
        mkey[1] = (updated_key >> 8) & 0xff
        mkey[2] = (updated_key >> 16) & 0xff
        mkey[3] = (updated_key >> 24) & 0xff
    mkeystr = "".join(map(chr,mkey))

    phash = cr.to_y64(md5.new(p).digest())
    r = cr.md5crypt(p, "_2S43d5f")
    rhash = cr.to_y64(md5.new(r).digest())
    xor_hash1 = ""
    for c in phash:
        xor_hash1 += chr(ord(c) ^ 0x36)
    xor_hash1 += chr(0x36) * (64-len(xor_hash1))
    xor_hash2 = ""
    for c in phash:
        xor_hash2 += chr(ord(c) ^ 0x5c)
    xor_hash2 += chr(0x5c) * (64-len(xor_hash2))
    sha_hash1 = sha.new(xor_hash1)
    sha_hash1.update(mkeystr)
    sha_dig1 = sha_hash1.digest(y > 2 and 1 or 0)
    
    sha_hash2 = sha.new(xor_hash2)

    sha_hash2.update(sha_dig1)
    sha_dig2 = sha_hash2.digest()

    resp6 = ''
    for c in xrange(0,20,2):
        val = ord(sha_dig2[c]) << 8
        val += ord(sha_dig2[c+1]) 
        look  = val >> 0x0b
        look &= 0x1f
        if look >= len(alphabet1):
            break
        resp6 += alphabet1[look] + '='

        look  = val >> 0x06
        look &= 0x1f
        if look >= len(alphabet2):
            break
        resp6 += alphabet2[look]
                                
        look  = val >> 0x01
        look &= 0x1f
        if look >= len(alphabet2):
            break
        resp6 += alphabet2[look]

        look = val & 0x01
        if look >= len(delimit_lookup):
            break
        resp6 += delimit_lookup[look]
    




    xor_hash1 = ""
    for c in rhash:
        xor_hash1 += chr(ord(c) ^ 0x36)
    xor_hash1 += chr(0x36) * (64-len(xor_hash1))
    xor_hash2 = ""
    for c in rhash:
        xor_hash2 += chr(ord(c) ^ 0x5c)
    xor_hash2 += chr(0x5c) * (64-len(xor_hash2))

    sha_hash1 = sha.new(xor_hash1)
    sha_hash1.update(mkeystr)
    sha_dig1 = sha_hash1.digest(y > 2 and 1 or 0)
    
    sha_hash2 = sha.new(xor_hash2)
    sha_hash2.update(sha_dig1)
    sha_dig2 = sha_hash2.digest()
    resp96 = ''
    for c in xrange(0,20,2):
        val = ord(sha_dig2[c]) << 8
        val += ord(sha_dig2[c+1]) 
        look  = val >> 0x0b
        look &= 0x1f
        if look >= len(alphabet1):
            break
        resp96 += alphabet1[look] + '='

        look  = val >> 0x06
        look &= 0x1f
        if look >= len(alphabet2):
            break
        resp96 += alphabet2[look]
                                
        look  = val >> 0x01
        look &= 0x1f
        if look >= len(alphabet2):
            break
        resp96 += alphabet2[look]

        look = val & 0x01
        if look >= len(delimit_lookup):
            break
        resp96 += delimit_lookup[look]

    return [ '0',u, '6',resp6, '96',resp96, '1',u ]

if __name__ == "__main__":
    print hash('ionel_mc','qweasd','i^(p%c%2*u-r-(b^k*2%h/p|8)^i/c/n)&3-x%h^h|y/k|k+a%8&f+c-a*c/f^b%b')
