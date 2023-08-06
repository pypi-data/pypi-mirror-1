# -*- coding: utf-8 -*-
"""Recipe zope2"""
import os
import sys
import shutil
import zc.buildout
import subprocess
import os
from zc.recipe.egg import Scripts
from plone.recipe.zope2instance import Recipe as zope2instance
from plone.recipe.zope2zeoserver import Recipe as zope2zeoserver

OPTIONS_OVERIDES = {
'event-log-custom':"""
<logfile>
    path STDERR
    level INFO
</logfile>
""",
'access-log-custom':"""
<logfile>
    path STDERR
    format %(message)s
</logfile>
""",
}

WSGI_WRAPPER = """
class Application(object):
    app = None
    def __call__(environ, start_response):
        return self.app(environ, start_response)
application = Application()
"""

class Instance(zope2instance):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):

        eggs  = options.get('eggs', '')
        extra_eggs = ['plone.recipe.zope2instance', 'plone.recipe.zope2zeoserver', 'PasteScript', 'repoze.zope2', 'WebError']
        extra_eggs.append(options['recipe'])
        for egg in extra_eggs:
            if egg not in eggs:
                eggs += '\n%s' % egg
        options['eggs']  = eggs
        options['scripts'] = '\npaster_serve=%(name)s\nmod_wsgi=%(name)s.wsgi' % dict(name=name)

        self.scripts = Scripts(buildout, name, options.copy())

        options['zope2-location'] = os.path.dirname(__file__)
        for k, v in OPTIONS_OVERIDES.items():
            if not options.get(k, None):
                options[k] = v
        zope2instance.__init__(self, buildout, name, options)

    def patch_binaries(self, *args):
        pass
    def install_scripts(self):
        pass

    def install(self):
        """Installer"""
        # install instance
        result = [zope2instance.install(self)]

        ini = os.path.join(self.buildout['buildout']['directory'], '%s.ini' % self.name)
        if not os.path.isfile(ini):
            template = open(os.path.join(os.path.dirname(__file__), 'template.ini'), 'rb')
            fd = open(ini, 'wb')
            http_address = self.options.get('http-address', '8080')
            if ':' in http_address:
                host, port = http_address.split(':')
            else:
                host = '127.0.0.1'
                port = http_address
            conf = os.path.join(self.options['location'], 'etc', 'zope.conf')
            fd.write(template.read() % dict(host=host, port=port, conf=conf))
            fd.close()
            print 'Generated config file %r' % ini

        # paster script
        self.scripts.options['initialization'] = WSGI_WRAPPER
        self.scripts.options['arguments'] = 'application, %r' % ini
        result.extend(self.scripts.install())

        return tuple(result)


    def update(self):
        result = [zope2instance.update(self)]
        result.extend(self.scripts.update())
        return tuple(result)

class Server(zope2zeoserver):

    def __init__(self, buildout, name, options):
        eggs  = options.get('eggs', '')
        for egg in ['plone.recipe.zope2zeoserver', 'ZODB3']:
            if egg not in eggs:
                eggs += '\n%s' % egg
        options['eggs']  = eggs
        options['zope2-location'] = '' #None #os.path.dirname(__file__)
        options['recipe'] = 'plone.recipe.zope2zeoserver'
        zope2zeoserver.__init__(self, buildout, name, options)

    def ws_locations(self):
        if self._ws_locations is None:
            self._ws_locations = [d.location for d in self.zodb_ws]
            # account for zope2-location, if provided
        return self._ws_locations
    ws_locations = property(ws_locations)
