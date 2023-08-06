#!/usr/bin/env python

import cgitb; cgitb.enable() # print out detailled reports
import cgi
from functions import redirect

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

    print """
    </head>
    <body>
    <div class="header">
    <H1>Logilab Vm</H1>
    <H3>a virtual machines manager</H3>
    </div>"""

    print """
    <div class="actionform">
    <form method="POST" action="index.py">
    <H1>Destination: <input type="text"name="destination" size="20" maxlength="50"/></H1>
    <H1>Live: <input type="checkbox" name="live" checked="yes"/></H1>
    <input type="submit" name="submit" value="Migrate">
    <input type="hidden" name="action" value="migrate"/>
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
