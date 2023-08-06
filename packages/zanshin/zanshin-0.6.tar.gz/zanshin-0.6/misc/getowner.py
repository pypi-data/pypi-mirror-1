import httplib, davlib

cn = davlib.DAV("www.sharemation.com")
cn.setauth("milele", "")
target = "/heikki2/hello.txt"
opt = cn.options(target)
opt.read()

if opt.status != 200 :
    print "Error getting options response: %d" % opt.status

elif "access-control" not in opt.getheader("DAV"):
    print "Server does not support access control"

else:
    pf = cn.getprops(target, "DAV:owner")
    body = pf.read()
    if pf.status != 207 or "owner" not in body:
        print "Server error?"
    owner = body[body.find("owner")+5:]
    owner = owner[0:owner.find("owner")]
    print owner
