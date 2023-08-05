import sys
import os
import struct
import time
import re
import cStringIO
tagstrip_re = re.compile("<[^<>]*?>")
ccstrip_re = re.compile("\x1b\[(#\w+?|\d)m")

def decode_file(data, uid, strip_tags=True):
    ret = []
    decode_msg = lambda (i, c): chr(ord(c)^ord(uid[i%len(uid)]))
    data_length = len(data)
    pos = 0
    try:
        while pos < data_length - 20:
            timestamp, unknown, origin, length = data[pos:pos+4], data[pos+4:pos+8], data[pos+8:pos+12], data[pos+12:pos+16]
            timestamp = struct.unpack('i', timestamp)[0]
            origin = struct.unpack('i', origin)[0]
            length = struct.unpack('i', length)[0]
            timestamp = time.gmtime(timestamp)
            if length < 0: 
                pos += 4
                ret.append((timestamp, -1, ''))
                continue
            
            pos += 16
            if pos + length + 4 > data_length:
                pos += 4
                continue
                
            msg = data[pos:pos+length]
            msg = ''.join(map(decode_msg, enumerate(iter(msg))))
            if strip_tags:
                msg = tagstrip_re.sub("", msg)
                msg = ccstrip_re.sub("", msg)
            ret.append((timestamp, origin, msg))
            pos += length
            while data[pos:pos+4] != '\0\0\0\0' and pos < data_length - 4:
                pos+=1
            pos += 4
    except:
        pass
        #~ raise
    return ret

def decode_arch(profiles_dir, dest_dir):
    for account in os.listdir(profiles_dir):
        arch = os.path.join(profiles_dir, account, 'Archive')
        tarch = os.path.join(dest_dir, account)
        if not os.path.exists(dest_dir): os.mkdir(dest_dir)
        if not os.path.exists(tarch): os.mkdir(tarch)
        if os.path.isdir(arch):
            for section in ('Messages',): #'Conferences', 
                section = os.path.join(arch, section)
                if os.path.isdir(section):
                    for contact in os.listdir(section):
                        tcontact_path = os.path.join(tarch, contact)
                        if not os.path.exists(tcontact_path): os.mkdir(tcontact_path)
                        contact_path = os.path.join(section, contact)
                        for conversation in os.listdir(contact_path):
                            conversation_path = os.path.join(contact_path, conversation)
                            tconversation_path = os.path.join(tcontact_path, os.path.splitext(conversation)[0]+".txt")
                            if not os.path.exists(tconversation_path) or os.stat(tconversation_path).st_mtime < os.stat(conversation_path).st_mtime:
                                decoded = decode_file(file(conversation_path, 'rb').read(), account)
                                fh = file(tconversation_path, 'w')
                                for ts, org, msg in decoded:
                                    print>>fh, "[%s] %s: %s" % (
                                        time.strftime("%Y-%b-%d %H:%M:%S",ts), 
                                        org and contact or account,
                                        msg
                                    )
                                fh.close()
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--profile-dir", dest="profile", 
                      help='a DIR, eg: "C:\Program Files\Yahoo!\Messenger\Profiles"', metavar="DIR")
    parser.add_option("-d", "--destination",
                      dest="destination", default=".",
                      help="the destination DIR where to save the converted files", metavar="DIR")

    options, args = parser.parse_args(len(sys.argv) > 1 and sys.argv or ['-h'])
    #~ print options, args
    #~ decode_arch('Profiles', 'TextArchive')
    decode_arch(options.profile, options.destination)