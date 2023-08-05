from distutils.core import setup

# Check deps

class DependencyFailed(Exception): pass
class VersionCheckFailed(DependencyFailed): pass

PYTHON_VERSION = '2.3'
TWISTED_VERSION = '2'

# -------------PYTHON VERSION----------
import sys, os
if sys.version < PYTHON_VERSION:
    raise VersionCheckFailed("Python "+PYTHON_VERSION+" or later is required")

#  ------------TWISTED-----------------
try:
    import twisted
except ImportError:
    raise DependencyFailed("You need Twisted - http://www.twistedmatrix.com/")

from twisted.copyright import version as twisted_version
if not twisted_version.startswith('SVN') and twisted_version < TWISTED_VERSION:
    raise VersionCheckFailed("Twisted "+TWISTED_VERSION+" or later is required")

# ---------------SOAPpy-----------------
try:
    import SOAPpy
except ImportError:
    raise DependencyFailed("You need SOAPpy")

    
setup(name='nattraverso',
	version='0.1.1',
	description='A NAT Traversal library',
	author='Raphael Slinckx',
	author_email='raphael@slinckx.net',
	url='http://raphael.slinckx.net/nattraverso.php',
	packages=['nattraverso', 'nattraverso.pynupnp']
	)
