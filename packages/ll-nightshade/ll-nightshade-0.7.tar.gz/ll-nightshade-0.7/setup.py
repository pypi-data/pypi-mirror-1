#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-nighshade


__version__ = "$Revision: 1.15 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/nightshade/setup.py,v $


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools


DESCRIPTION = """
ll-nightshade provides classes that can be used in a CherryPy pagetree to
publish the result of calling TOXIC function on the web.
"""


CLASSIFIERS="""
Development Status :: 3 - Alpha
Environment :: Web Environment
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing :: Markup :: HTML
Topic :: Text Processing :: Markup :: XML
"""


KEYWORDS = """
# misc
CherryPy
toxic
Oracle
PL/SQL
function
RSS
"""


args = dict(
	name="ll-nightshade",
	version="0.7",
	description="Serve the output of Oracle functions/procedures with CherryPy",
	long_description=DESCRIPTION,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/nightshade/",
	download_url="http://www.livinglogic.de/Python/nightshade/Download.html",
	license="Python",
	classifiers=[c for c in CLASSIFIERS.strip().splitlines() if c.strip() and not c.strip().startswith("#")],
	keywords=", ".join(k for k in KEYWORDS.strip().splitlines() if k.strip() and not k.strip().startswith("#")),
	packages=["ll"],
	package_dir={"": "src"},
	install_requires=[
		"ll-orasql >= 1.17.3",
	],
	namespace_packages=["ll"],
	zip_safe=False,
)


if __name__ == "__main__":
	tools.setup(**args)
