
from util.version import Version

# This is the version of this tree, as created by misc/make-version.py from
# the Darcs patch information: the main version number is taken from the most
# recent release tag. If some patches have been added since the last release,
# this will have a -NN "build number" suffix. Please see
# allmydata.util.version for a description of what the different fields mean.

verstr = "0.4.0-220"
__version__ = Version(verstr)
