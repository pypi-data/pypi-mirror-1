""" layout definition for generating api/source documents

    this is the place where customization can be done
"""

import py
import os
from py.__.doc import confrest
from py.__.apigen import linker

here = py.magic.autopath().dirpath()

def get_apigenpath():
    target = os.environ.get('APIGEN_TARGET')
    if target is None:
        target = here.join('../../apigen_templess').strpath
    return target

class LayoutPage(confrest.Page):
    """ this provides the layout and style information """

    stylesheets = [(here.join('style.css'), 'style.css')]
    scripts = [(py.__package__.getpath().join('apigen/api.js'), 'api.js')]

    def __init__(self, *args, **kwargs):
        self.nav = kwargs.pop('nav')
        super(LayoutPage, self).__init__(*args, **kwargs)

    def get_relpath(self):
        return linker.relpath(self.targetpath.strpath,
                              get_apigenpath()) + '/'

    def set_content(self, contentel):
        self.contentspace.append(contentel)

    def fill(self):
        super(LayoutPage, self).fill()
        self.menubar[:] = []
        self.body.insert(0, self.nav)

    def setup_scripts_styles(self, copyto=None):
        for path, name in self.stylesheets:
            if copyto:
                copyto.join(name).write(path.read())
            self.head.append(py.xml.html.link(type='text/css',
                                              rel='stylesheet',
                                              href=self.get_relpath() + name))
        for path, name in self.scripts:
            if copyto:
                copyto.join(name).write(path.read())
            self.head.append(py.xml.html.script(type="text/javascript",
                                                src=self.get_relpath() + name))

