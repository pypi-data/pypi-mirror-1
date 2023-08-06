import teamrubber.pdberrorlog
f = teamrubber.pdberrorlog.parseHTML
import os 

testdir="/".join(teamrubber.pdberrorlog.__file__.split("/")[:-1])

def test_ParseEmpty():
    try:
        fo = open(os.path.join(testdir, "emptylog.html"))
        html = fo.read()
    finally:
        fo.close()
    g=f(html)
    assert g.next() == "No exceptions have been logged"

def test_ParseTwo():
    try:
        fo = open(os.path.join(testdir, "twoentries.html"))
        html = fo.read()
    finally:
        fo.close()
    g=f(html)
    expected = ["Error: 1221817239.180.338908870352 (Unauthorized : You are not allowed to access '@@make_subsite' in this context)", 
                'Error: 1221817156.90.470496493856 (Unauthorized : &lt;AccessControl.unauthorized.Unauthorized instance at 0x80f84c200&gt;)']
    g=list(g)
    assert g == expected
    assert len(g) == 2
    

def test_ParseTwenty():
    try:
        fo = open(os.path.join(testdir, "twentyentries.html"))
        html = fo.read()
    finally:
        fo.close()
    g=f(html)
    expected= ['Error: 1221781839.570.0558058142555 (IndexError : list index out of range)',
               'Error: 1221738606.920.906405871843 (IndexError : list index out of range)',
               'Error: 1221645386.460.808034108747 (IndexError : list index out of range)',
               'Error: 1221568796.150.108459545141 (IndexError : list index out of range)',
               'Error: 1221522862.860.953007184733 (IndexError : list index out of range)',
               'Error: 1221366176.30.221317116024 (IndexError : list index out of range)',
               'Error: 1220805754.40.70903488123 (Unauthorized : &lt;strong&gt;You are not authorized to access this resource.&lt;/strong&gt;)',
               'Error: 1220805751.380.468533217346 (Unauthorized : &lt;strong&gt;You are not authorized to access this resource.&lt;/strong&gt;)',
               'Error: 1220805749.340.752590698955 (Unauthorized : &lt;strong&gt;You are not authorized to access this resource.&lt;/strong&gt;)',
               'Error: 1220805674.120.206381832728 (Unauthorized : &lt;strong&gt;You are not authorized to access this resource.&lt;/strong&gt;)',
               'Error: 1220804897.570.468533217346 (IndexError : list index out of range)',
               'Error: 1220804849.30.752590698955 (IndexError : list index out of range)',
               'Error: 1220804802.720.206381832728 (IndexError : list index out of range)',
               'Error: 1220773495.40.498301382021 (IndexError : list index out of range)',
               'Error: 1220666116.30.337235209594 (IndexError : list index out of range)',
               'Error: 1228266116.30.337235493018 (IndexError : list index out of range)',
               'Error: 1220666068.210.571025736134 (IndexError : list index out of range)',
               'Error: 1220666018.490.320280638421 (IndexError : list index out of range)',
               'Error: 1220621176.930.0379970953879 (IndexError : list index out of range)',
               'Error: 1220578798.40.0607898497445 (IndexError : list index out of range)']
    g=list(g)
    assert g == expected
    assert len(g) == 20