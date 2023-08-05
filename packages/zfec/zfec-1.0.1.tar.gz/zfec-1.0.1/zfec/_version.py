
from pyutil.version import Version

# This is the version of this tree, as created by scripts/make-version.py from
# the Darcs patch information: the main version number is taken from the most
# recent release tag. If some patches have been added since the last release,
# this will have a -NN "build number" suffix. Please see
# pyutil.version for a description of what the different fields mean.

verstr = "1.0.1"
__version__ = Version(verstr)
