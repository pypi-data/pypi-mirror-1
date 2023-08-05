import py
mypath = py.magic.autopath().dirpath()
import atexit

class ApigenLinkWriter(object):
    def get_link(self, base, path):
        rel = path.relto(base)
        return '../apigen/source/%s.html' % (rel,)

linkwriter = ApigenLinkWriter()

class Directory(py.test.collect.Directory):
    def run(self):
        if self.fspath == mypath:
            return ['test', 'doc']
        return super(Directory, self).run()

