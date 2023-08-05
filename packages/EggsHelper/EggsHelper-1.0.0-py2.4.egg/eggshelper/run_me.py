# #!/usr/bin/env python2.4
#
# run_me.py
#
# Christian Seberino
# chris@seberino.org
# December 5, 2006
#
# Contains a dependency on the Twisted egg just to show off setuptools.

import twisted.internet

print """
Eggs are managed by setuptools which replaces distutils.

To 'eggify' your package, build it using this package as a skeleton.

An egg is a zip compressed Python package that incidentally can be installed
and imported with regards to Python 2.4 just like normal modules.

In addition to setup.py, you'll need the ez_setup.py script in your source
tree.  This script has the ability to install setuptools when needed if not
installed already.

See NOTES.txt in doc directory for more information.
"""
