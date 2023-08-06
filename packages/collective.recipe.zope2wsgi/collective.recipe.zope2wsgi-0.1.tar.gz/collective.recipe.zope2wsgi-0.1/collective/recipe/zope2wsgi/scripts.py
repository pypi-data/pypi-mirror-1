# -*- coding: utf-8 -*-
import sys

def serve(application, ini):
    import paste.script.command
    if ini not in sys.argv:
        sys.argv.append(ini)
    print 'Loading %s ...' % ini
    paste.script.command.run()

def mod_wsgi(application, ini):
    from paste.deploy import loadapp
    application.app = loadapp('config:' + ini)

