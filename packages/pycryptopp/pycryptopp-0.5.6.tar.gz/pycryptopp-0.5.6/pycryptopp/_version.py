
try:
    from pyutil.version_class import Version as pyutil_Version
    Version = pyutil_Version
except ImportError:
    from distutils.version import LooseVersion as distutils_Version
    Version = distutils_Version

# This is the version of this tree, as created by setup.py darscver (from the pyutil
# library) from the Darcs patch information: the main version number is taken
# from the most recent release tag. If some patches have been added since the
# last release, this will have a -NN "build number" suffix. Please see
# pyutil.version_class for a description of what the different fields mean.

verstr = "0.5.6"
__version__ = Version(verstr)
