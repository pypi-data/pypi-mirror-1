# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe template"""
from Cheetah.Template import Template as CheetahTemplate
import pkg_resources
import logging
import urllib
import sys, os
from os.path import join

class Template:
    """This recipe is used by zc.buildout"""

    template_dir = os.path.dirname(os.path.abspath(__file__))
    template = None
    executable = False

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        if self.template:
            self.source = join(self.template_dir, self.template)
        else:
            self.source = options['source']

        self.destination = options.get('destination',
                buildout.get('bin-directory',''))

        self.kwargs = dict(name=name,
                           options=options,
                           buildout=buildout)

    def install(self):
        """installer"""
        generated = []
        logger = logging.getLogger(self.name)

        if self.source.startswith('http://'):
            source = urllib.urlopen(self.source).read()
        else:
            source = open(self.source).read()
        template = CheetahTemplate(source=source,
                                   searchList=[self.kwargs])

        destination = os.path.join(self.destination, self.name)

        if self.executable:
            contents = '#!%s\n%s' % (sys.executable, template)
        else:
            contents = '%s' % template

        if self.executable and sys.platform == 'win32':
            exe = destination + '.exe'
            open(exe, 'wb').write(
                pkg_resources.resource_string('setuptools', 'cli.exe')
            )
            generated.append(exe)
            dest = destination+'-script.py'
        else:
            dest = destination

        open(dest, 'w').write(contents)

        if self.__class__.executable:
            logger.info("Generated script %r.", self.name)
            try:
                os.chmod(dest, 0755)
            except (AttributeError, os.error):
                pass
        else:
            logger.info("Generated file %r.", self.name)
        return generated

    update = install

class Script(Template):

    executable = True

class ProxyVhost(Template):

    template = 'proxy_vhost_tmpl'
    rewrite = ''

    def __init__(self, buildout, name, options):
        Template.__init__(self, buildout, name, options)
        buildout_root = buildout.get('directory',
                                     os.path.abspath('.'))
        self.kwargs.update(dict(
            logs=options.get('log-directory',
                           join(buildout_root, 'var', 'logs')),
            root=options.get('document-root',
                           join(buildout_root, 'var', 'www')),
            ip=options.get('ip', '127.0.0.1'),
            port=options.get('port', '8080'),
            http_port=options.get('http_port', '80'),
            path=options.get('path','/'),
            ))
        try:
            self.kwargs['rewrite'] = options.get('rewrite',
                                             self.rewrite % self.kwargs)
        except:
            raise ValueError('%s\n%s' % (self.rewrite,self.kwargs))

class Zope2Vhost(ProxyVhost):
    rewrite = "http://%(ip)s:%(port)s/VirtualHostBase/http/%(name)s:%(http_port)s%(path)s/VirtualHostRoot/$1"

class Zope3Vhost(ProxyVhost):
    rewrite = "http://%(ip)s:%(port)s/++vh++http:%(name)s:%(http_port)s/++/$1"

class SquidVhost(ProxyVhost):
    rewrite = "http://%(ip)s:%(port)s/http/%(name)s/%(http_port)s/$1"

