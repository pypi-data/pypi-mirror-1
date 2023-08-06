#!/usr/bin/env python

def redirect(message):
    """
    Use this function after printing <html><head> to stop and redirect to the index page
    """
    print """
    <meta http-equiv="Refresh" content="5; url=index.py"/>
    </head>
    <body>
    <H1>Error</H1>
    %s<br/>
    If your are not redirected in 5 secondes, please <a href=index.py>click here</a>
    </body>
    </html>""" % message
