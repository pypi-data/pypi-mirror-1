#!/usr/bin/env python

from distutils.core import setup
setup(name='bug.gd',
      version='0.1.8',
      description='Get help for Python errors in your interactive console',
      author='ted from bug.gd',
      author_email='bugs@bug.gd',
      py_modules=['buggd', 'buggdXMLRPC', 'error_help', 'buggdUtil'],
      url='http://bug.gd/download/',
      scripts=['error_help_config.py'],
     )

# Tell the user he/she need to run config
print """\n***** bug.gd error network\n\nHello! You're installing the bug.gd error network package. This tool is
designed to find workarounds to common errors.\n"""

print """\n\n******** Setup is ALMOST complete!
******** Setup is ALMOST complete!

To complete installation you need to run the script error_help_config.py from your python scripts directory."""

