#!/usr/bin/env python

import cgitb; cgitb.enable() # print out detailled reports
import cgi
from re import compile
from functions import redirect

_ENTRY = "#(?P<name>\w+)=(?P<default>\S*)([^\n\r]+?#(?P<help>[^\n\r]+))?"
RGX_ENTRY = compile(_ENTRY)
RGX_TEMPLATE = compile("#BEGINPARAM\n(?P<content>(.*\n)*)#ENDPARAM")

def main():
    print """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>loglab-vm</title>
    <link href="/style.css" rel="stylesheet" type="text/css"/>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>"""

    form = cgi.FieldStorage()

    # no template
    if not form.has_key('template'):
        redirect("Please use the create menu in index to process")
        return
    template = form.getfirst("template")
    
    # open the templatefile
    tempfile = open(template)

    # retrieve only the template part
    content = RGX_TEMPLATE.search(tempfile.read()).groupdict()['content']

    # construct to buffer to print in case error while parsing
    buffer = """
    </head>
    <body>
    <div class="header">
    <H1>Logilab Vm</H1>
    <H3>a virtual machines manager</H3>
    </div>
    <div class="actionform">
    <form method="POST" action="index.py">"""

    # parse and fill in the form
    for line in content.splitlines():
        match = RGX_ENTRY.match(line)
        if not match:
            redirect("Wrong syntax in %s :<br>%s" % (template, line))
            return
        else:
            ldict = match.groupdict()
            name = ldict['name'].capitalize()
            help = ldict['help'].lower() if ldict['help'] else ""
            buffer = buffer + """
            <font class="name">%s: </font>
            <input type="text" name="%s" size="20" maxlength="50" value="%s"/>
            <font class="help">%s</font><br/>""" % \
            (name, ldict['name'], ldict['default'], help)

    # print the buffer
    print buffer
    # ... end the end of page
    print """
    <input type="submit" name="submit" value="Create">
    <input type="reset" name="reset" value="Reset">
    <input type="hidden" name="action" value="create"/>
    <input type="hidden" name="template" value="%s"/>
    </form>
    </div>
    <div class="footer">
    <a href="index.py">back</a>
    </div>
    </body>
    </html>""" % template

main()
