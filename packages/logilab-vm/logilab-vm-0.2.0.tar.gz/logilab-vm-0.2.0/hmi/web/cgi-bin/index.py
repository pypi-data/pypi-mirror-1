#!/usr/bin/env python

import cgitb; cgitb.enable() # print out detailled reports
import cgi
import sys
import ConfigParser
from os import listdir, system
from os.path import basename, isfile, join
sys.stderr = sys.stdout
from logilabvm.lib import _execute, _CONFIGFILE, VMError, HookCall, ExecError, \
    show, start, stop, resume, suspend, \
    save, restore, migrate, create, delete

def main():
    print "Content-Type: text/html" # HTML is following
    print                           # blank line, end of headers

    print """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>loglab-vm</title>
    <link href="/style.css" rel="stylesheet" type="text/css"/>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>
    </head>
    <body>

    <div class="header">
    <H1>Logilab Vm</H1>
    <H3>a virtual machines manager</H3>
    </div>"""

    # proceed to the action if any
    proceed()

    # print the action table
    vmlist()

    # print the create list and link
    creationlist()

def creationlist():
    """
    Print the create list using templates
    """

    print """
    <div class="create">"""

    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)
    open(_CONFIGFILE)
    templatesdir = config.get('MAIN','templates')

    try:
        templates = [ f for f in listdir(templatesdir) if isfile(join(templatesdir, f)) ]
    except OSError:
        templates = None

    if not templates:
        print """
        <H3>No templates for creation</H3>"""
        return

    print """
    <div class="form">
    <form method="POST" action="create.py">
    <H1>Creation templates: </H1>
    <select name="template">"""

    for template in templates:
        print """<option value="%s">%s</option>""" % (join(templatesdir, template), template)

    print """
    </select> <input type="submit" name="submit" value="Create">
    </form>
    </div>
    """

def vmlist():
    """
    Print a table containing all VMs, their hypervisor, status, etc.
    """

    results = show.run(["--all"])

    # check if any bug
    for result in results:
        if result['value']:
            error("Can not retrieve VMs informations, \
                please contact an administrator<br/>%s" %
                result['stderr'])
            return

    ## print table header
    print """
    <div class="table">
    <table border="1">
    <caption></caption>
    <tbody>
    <tr>
    <td><H1>name</H1></td>
    <td><H1>hypervisor</H1></td>
    <td><H1>state</H1></td>
    <td><H1>actions</H1></td>
    </tr>"""

    ## print table content
    for result in results:
        ## print VM infos
        print """
        <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>""" % (result['name'], 
        result['hyper'], result['state'])

        ## print VM actions
        print """
        <td>
        <table border="0" class="tableactions">
        <caption></caption>
        <tbody>
        <tr>"""

        if result['state'] == "running":
            print "<td><a href=index.py?action=stop&name=%s>stop</a></td>" % result['name']
            print "<td><a href=index.py?action=suspend&name=%s>suspend</a></td>" % result['name']
            print "<td><a href=save.py?name=%s>save</a></td>" % result['name']
            print "<td><a href=migrate.py?name=%s>migrate</a></td>" % result['name']
        elif result['state'] == "shut off":
            print "<td><a href=index.py?action=start&name=%s>start</a></td>" % result['name']
            print "<td><a href=restore.py?name=%s>restore</a></td>" % result['name']
            print "<td><a href=migrate.py?name=%s>migrate</a></td>" % result['name']
            print "<td><a href=index.py?action=delete&name=%s>delete</a></td>" % result['name']
        elif result['state'] == "paused":
            print "<td><a href=index.py?action=stop&name=%s>stop</a></td>" % result['name']
            print "<td><a href=index.py?action=resume&name=%s>resume</a></td>" % result['name']
            print "<td><a href=save.py?name=%s>save</a></td>" % result['name']
            print "<td><a href=migrate.py?name=%s>migrate</a></td>" % result['name']
        elif result['state'] == "blocked":
            print "<td><a href=index.py?action=stop&name=%s>stop</a></td>" % result['name']
            print "<td><a href=index.py?action=suspend&name=%s>suspend</a></td>" % result['name']
            print "<td><a href=save.py?name=%s>save</a></td>" % result['name']
            print "<td><a href=migrate.py?name=%s>migrate</a></td>" % result['name']
        elif result['state'] == "shutdown":
            print "<td>-</td>"
        elif result['state'] == "crashed":
            print "<td>-</td>"
        elif result['state'] == "dying":
            print "<td>-</td>"
        else :
            print "<td>unknown state</td>"

        print """
        </tr>
        </tbody>
        </table>
        </td>
        </tr>"""

    ## print table footer
    print """
    </tbody>
    </table>
    </div>"""

def proceed():
    """
    Proceed to the given action and print result
    """

    form = cgi.FieldStorage()

    # no actino to proceed
    if not form.has_key('action'):
        return
    action = form.getfirst("action").upper()

    if not action == "CREATE" and not form.has_key('name'):
        error("no name")
        return
    name = form.getfirst("name")

    try:
        if action == "START":
            result = start.run(sysargs=[name],
                usage="")[0]
        elif action == "STOP":
            result = stop.run(sysargs=["--force", name],
                usage="")[0]
        elif action == "SUSPEND":
            result = suspend.run(sysargs=[name],
                usage="")
        elif action == "RESUME":
            result = resume.run(sysargs=[name],
                usage="")
        elif action == "MIGRATE":
            if not form.has_key('destination'):
                error("no destination")
                return
            destination = form.getfirst("destination")

            if form.has_key('live'):
                result = migrate.run(sysargs=[name, destination, "--live"],
                    usage="")
            else:
                result = migrate.run(sysargs=[name, destination],
                    usage="")
        elif action == "RESTORE":
            if not form.has_key('archive'):
                error("no archive selected")
                return
            archive = form.getfirst("archive")

            result = restore.run(sysargs=[name, "--archive", archive],
                usage="")
        elif action == "SAVE":
            if not form.has_key('archive'):
                error("no archive mentioned")
                return
            archive = form.getfirst("archive")

            if not archive or archive.upper() == "AUTO":
                result = save.run(sysargs=[name],
                    usage="")
            else:
                result = save.run(sysargs=[name, "--filename", basename(archive)],
                    usage="")
        elif action == "CREATE":
            system("groups")
            if not form.has_key('template'):
                error("no template mentioned")
                return
            template = form.getfirst("template")

            env = {}
            for key in [ el for el in form.keys() if el not in ["submit", "action", "template"] ]:
                env[key] = form.getfirst(key)
            result = _execute(template, env=env)
        elif action == "DELETE":
            result = delete.run(sysargs=[name],
                usage="")
        else:
            error("action")

        if result['value']:
            failure(result)
        else:
            success(result)

    except AttributeError, msg:
        failure({ 'name' : name, 'stderr' : "Wrong arguments: %s" % msg })
    except VMError, msg:
        failure({ 'name' : name, 'stderr' : "%s" % msg })
    except HookCall, exception:
        hook({ 'name' : name, 'exception' : exception })
    except NotImplementedError:
        failure({ 'name' : name, 'stderr' : "Functionality not implemented for this hypervisor, please set a hook" })
    except ExecError, msg:
        failure({ 'name' : name, 'stderr' : "Execution error:<br/>%s" % msg })
    except Exception, msg:
        failure({ 'name' : name, 'stderr' : str(msg) })

def success(result):
    if result.has_key("name"):
        print """
        <div class="success">
        <H1>%s - Success</H1>
        %s
        </div>""" % (result['name'], result['stdout'])
    else:
        print """
        <div class="success">
        <H1>Success</H1>
        %s
        </div>""" % result['stdout']

def failure(result):
    if result.has_key("name"):
        print """
        <div class="failure">
        <H1>%s - Failure</H1>
        %s
        </div>""" % (result['name'], (result['stderr'] or result['stdout']))
    else:
        print """
        <div class="failure">
        <H1>Failure</H1>
        %s
        </div>""" % (result['stderr'] or result['stdout'])

def error(msg):
    print """
    <div class="error">
    <H1>Error</H1>
    %s
    </div>""" % msg

def hook(result):
    if result['exception'].value:
        print """
        <div class="failure">
        <H1>%s - Failure (hook)
        </H1>""" % result['name']
    else:
        print """
        <div class="success">
        <H1>%s - Success (hook)
        </H1>""" % result['name']
    
    print """
    %s
    </div>""" % str(result['exception'])


main()
