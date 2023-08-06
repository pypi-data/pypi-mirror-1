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
    except NotImplementedError:
        pass
    except HookCall, exception:
        hookresult = exception

    print """
    </head>
    <body>

    <div class="header">
    <H1>Logilab Vm</H1>
    <H3>a virtual machines manager</H3>
    </div>"""


    if hookresult:
        print """<div class="hook">"""
        if hookresult.value:
            print """<H1>Archives - Failure (hook)</H1>"""
        else:
            print """<H1>Archives - Success (hook)</H1>"""

        print "%s" % str(hookresult)
    elif results:
        results.sort()
        results.reverse()
        print """
        <div class="table">
        <table border="1">
        <caption></caption>
        <tbody>
        <tr>
        <td><H1>archive</H1></td>
        <td><H1>description</H1></td>
        </tr>"""

        for result in results:
            match = RGX_ARCHIVE.match(result)
            if match:
                display = "%s - %s/%s/%s %s:%s:%s" % (match.groups()[0], 
                    match.groups()[1], match.groups()[2], match.groups()[3],
                    match.groups()[4], match.groups()[5], match.groups()[6])
                print """
                <tr>
                <td>%s</td>
                <td>%s</td>
                </tr>""" % (result, display)
            else:
                print """
                <tr>
                <td>%s</td>
                <td>%s</td>
                </tr>""" % (result, result)

        print """
        </tbody>
        </table>"""
    else:
        print """
        <div class="warning">
        <H1>No archives</H1>"""
    
    print """</div>"""

    print """
    <div class="actionform">
    <form method="POST" action="index.py">
    <H1>Save VM status into archives:</H1>
    <input type="text" name="archive" size="20" maxlength="50" value="auto"/>
     ("auto" or empty for automatic)<br/>
    <input type="submit" name="submit" value="Save">
    <input type="hidden" name="action" value="save"/>
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
