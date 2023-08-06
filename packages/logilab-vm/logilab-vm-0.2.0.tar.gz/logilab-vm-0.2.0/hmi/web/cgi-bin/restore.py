#!/usr/bin/env python

import cgitb; cgitb.enable() # print out detailled reports
import cgi
from re import compile
from logilabvm.lib import archives, HookCall
from functions import redirect

RGX_ARCHIVE = compile("^(?P<name>.+)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})$")
def main():
    print """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>loglab-vm</title>
    <link href="/style.css" rel="stylesheet" type="text/css"/>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>"""

    form = cgi.FieldStorage()

    # no actino to proceed
    if not form.has_key('name'):
        redirect("Please use the VM table to process to an action")
        return
    name = form.getfirst("name")

    hookresult = False
    results = None
    try:
        results = archives.run(sysargs=[name], usage="")['result']
        if not results:
            redirect("There is no archive found for %s" % name)
            return
    except NotImplementedError:
        redirect("Functionality not implemented for this hypervisor, please set a hook")
        return
    except HookCall, exception:
        hookresult = exception

    print """
    </head>
    <body>

    <div class="header">
    <H1>Logilab Vm</H1>
    <H3>a virtual machines manager</H3>
    </div>"""

    print """<div class="actionform">"""

    if hookresult:
        if hookresult.value:
            print """<H1>Archives - Failure (hook)</H1>"""
        else:
            print """<H1>Archives - Success (hook)</H1>"""

        print "%s" % str(hookresult)

        print """
        <form method="POST" action="index.py">
        <H1>Name of the archive to restore: </H1>
        <input type="text" name="archive" size="20" maxlength="50"/>"""
    elif results:
        results.sort()
        results.reverse()
        print """
        <form method="POST" action="index.py">
        <H1>Select an archive to restore:</H1>
        <select name="archive">"""

        for result in results:
            match = RGX_ARCHIVE.match(result)
            if match:
                display = "%s - %s/%s/%s %s:%s:%s" % (match.groups()[0], 
                    match.groups()[1], match.groups()[2], match.groups()[3],
                    match.groups()[4], match.groups()[5], match.groups()[6])
                print """<option value="%s">%s</option>""" % (result, display)
            else:
                print """<option value="%s">%s</option>""" % (result, result)
    
    print """
    </select> <input type="submit" name="submit" value="Restore">
    <input type="hidden" name="action" value="restore"/>
    <input type="hidden" name="name" value="%s"/>
    </form>
    </div>""" % name

    print """
    <div class="footer">
    <a href="index.py">back</a>
    </div>
    </body>
    </html>"""

main()
