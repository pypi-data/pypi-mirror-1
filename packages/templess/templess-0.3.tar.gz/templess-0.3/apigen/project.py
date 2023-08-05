""" this contains the code that actually builds the pages using layout.py

    building the docs happens in two passes: the first one takes care of
    collecting contents and navigation items, the second builds the actual
    HTML
"""

import py
from py.__.apigen.project import Project as _Project

class Project(_Project):
    logo = py.xml.html.a(
        py.xml.html.img(
            src='http://templess.johnnydebris.net/chrome/common/templess.png',
            title='logo',
        ),
        id='logo',
        href='http://templess.johnnydebris.net/',
    )

