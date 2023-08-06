import re
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
        for a in parseHTML(admin.contents):
            print a
        

def parseHTML(html):
    c = html
    c=c.split("<h3>Exception Log (most recent first)</h3>")[1]
    c=c.split("div>")[1][:-5]
    if "No exceptions logged" in c:
        yield "No exceptions have been logged"
    else:
        c=c.split('<td valign="top">')
        c=[a.split("</a>")[0] for a in c]
        for html in c:
            try:
                a = re.compile("<span>(.*?)</span>")
                b = re.compile("id=([0-9.]*)\"")
                url = b.findall(html)[0]
                bads=a.findall(html)
                yield "Error: " + url + " (" + bads[0] + " : " + bads[1] +")"
            except IndexError:
                pass

import pdb
pdb.Pdb.do_errorlog = do_errorlog

