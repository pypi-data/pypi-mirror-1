Introduction
============

Adds the "errorlog" command to pdb sessions.  This is only useful in functional test cases in PloneTestCase.::

    (Pdb) errorlog
    (Pdb) admin.open("http://nohost/plone/createObject")
    *** HTTPError: HTTP Error 500: Internal Server Error
    (Pdb) admin.open("http://nohost/plone/createObject")
    *** HTTPError: HTTP Error 500: Internal Server Error
    (Pdb) admin.open("http://nohost/plone/createObject")
    *** HTTPError: HTTP Error 500: Internal Server Error
    (Pdb) errorlog
    Error: 1218794437.680.454937341407 ( Type name not specified )
    Error: 1218794437.10.341611383065 ( Type name not specified )
    Error: 1218794436.540.661922508086 ( Type name not specified )
    (Pdb) errorlog 1218794437.10.341611383065
    Traceback (innermost last):
      Module ZPublisher.Publish, line 115, in publish
      Module ZPublisher.mapply, line 88, in mapply
      Module ZPublisher.Publish, line 41, in call_object
      Module Products.CMFFormController.FSControllerPythonScript, line 104, in __call__
      Module Products.CMFFormController.Script, line 145, in __call__
      Module Products.CMFCore.FSPythonScript, line 108, in __call__
      Module Shared.DC.Scripts.Bindings, line 311, in __call__
      Module Shared.DC.Scripts.Bindings, line 348, in _bindAndExec
      Module Products.CMFCore.FSPythonScript, line 164, in _exec
      Module None, line 10, in createObject
       - <FSControllerPythonScript at /plone/createObject>
       - Line 10
    Exception: Type name not specified


Yay?


Pre-requisites
==============

A Plone functional test case.  This can work with zope in theory, but it's written with plone assumptions in mind.

