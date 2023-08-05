""" run 'py.test --apigen=<this script>' to get documentation exported

    exports to /tmp/output by default, set the environment variable
    'APIGEN_TARGET' to override
"""

import py
from py.__.apigen import htmlgen
from py.__.apigen import linker

from templess import templess, nanosax
from layout import LayoutPage, get_apigenpath
from project import Project

def get_documentable_items(pkgdir):
    return 'templess', {
        'templess.xmlstring': templess.xmlstring,
        'templess.objectcontext': templess.objectcontext,
        'templess.node': templess.node,
        'templess.elnode': templess.elnode,
        'templess.templessnode': templess.templessnode,
        'templess.textnode': templess.textnode,
        'templess.cdatanode': templess.cdatanode,
        'templess.commentnode': templess.commentnode,
        'templess.treebuilderhandler': templess.treebuilderhandler,
        'templess.cgitemplate': templess.cgitemplate,
        'templess.template': templess.template,
        'nanosax.XMLError': nanosax.XMLError,
        'nanosax.nsparser': nanosax.nsparser,
        'nanosax.nshandler': nanosax.nshandler,
        'nanosax.echohandler': nanosax.echohandler,
    }

def build(pkgdir, dsa, capture):
    l = linker.TempLinker()
    proj = Project()

    targetdir = py.path.local(get_apigenpath())
    targetdir.ensure(dir=True)

    all_names = dsa._get_names(filter=lambda x, y: True)
    namespace_tree = htmlgen.create_namespace_tree(all_names)
    apb = htmlgen.ApiPageBuilder(targetdir, l, dsa, pkgdir, namespace_tree,
                                 proj, capture, LayoutPage)
    spb = htmlgen.SourcePageBuilder(targetdir, l, pkgdir, proj, capture,
                                    LayoutPage)

    apb.build_namespace_pages()
    class_names = dsa.get_class_names()
    apb.build_class_pages(class_names)
    function_names = dsa.get_function_names()
    apb.build_function_pages(function_names)
    spb.build_pages(pkgdir)
    l.replace_dirpath(targetdir)

