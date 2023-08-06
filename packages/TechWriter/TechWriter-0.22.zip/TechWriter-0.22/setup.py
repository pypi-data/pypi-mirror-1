#! /usr/bin/env python

from distutils.core import setup

import TechWriter

setup(
    name         = "TechWriter",
    description  = "A package for reading and converting TechWriter documents.",
    author       = "David Boddie",
    author_email = "david@boddie.org.uk",
    url          = "http://www.boddie.org.uk/david/Projects/Python/TechWriter",
    version      = TechWriter.__version__,
    packages     = ["TechWriter",
                    "TechWriter/Writers"],
    scripts      = ["Tools/tw2latex.py",
                    "Tools/tw2html.py",
                    "Tools/tw2odt.py"]
    )
