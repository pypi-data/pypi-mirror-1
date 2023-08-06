def do_errorlog(self, arg):
    from Products.Five.testbrowser import Browser
    admin = Browser()
    from Testing.ZopeTestCase import user_password
    admin.addHeader('Authorization', 'Basic %s:%s' % ('portal_owner', user_password))
    if arg:
        admin.open("http://nohost/plone/error_log/getLogEntryAsText?id=%s"%(arg))
        print admin.contents
    else:
        admin.open("http://nohost/plone/error_log/manage_main")
        c = admin.contents
        c=c.split("<h3>Exception Log (most recent first)</h3>")[1]
        c=c.split("div>")[1][:-5]
        if "No exceptions logged" in c:
            print "No exceptions have been logged"
        else:
            c=c.split('<td valign="top">')
            c=[a.split("</a>")[0] for a in c]
            for html in c:
                try:
                    url = html.split('href="')[1].split('"')[0].split('?id=')[1]
                    bad = html.split("<span>Exception</span>:\n    <span>")[1].split("</span>")[0]
                    print "Error:", url, "(",bad,")"
                except:
                    pass

import pdb
pdb.Pdb.do_errorlog = do_errorlog

