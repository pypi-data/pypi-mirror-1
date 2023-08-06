import sys 
from zanshin import ServerHandle

def __usage():
    print >>sys.stderr, 'usage: %s [options]'    

#For now, set the server/share information manually.
host='localhost'
share_path = '/slide/files/'
username='root'
password='root'
port=8080

def main(argv):
    print "starting synch"
    svr = ServerHandle.ServerHandle(host, port, username, password)
    share = svr.getResource(share_path)
    getRemoteInfo(share)
    upload(share)

def getRemoteInfo(share):
    #propfind
    resources = share.getAllChildren()

def upload(share):
    if share.supportsLocking():
        print "next step: share.lock()"
    else:
        print "oops"

if __name__ == "__main__":
    main(sys.argv[1:])

