"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-02-13 13:22:49 +0100 (Mi, 13 Feb 2008) $
    $Rev: 1405 $
    $Author: JensDiemer $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.utils.version import get_svn_revision

svn_revision = get_svn_revision("PyLucid")
if svn_revision == u'SVN-unknown':
    # No SVN checkout, a release?
    svn_revision = ""
else:
    # Add a space between the normal version number and the SVN revision number.
    svn_revision = " " + svn_revision

# PyLucid Version String
# Important for setuptools:
# - Only use . as a separator
# - No spaces: "0.8.0 RC2" -> "0.8.0RC2"
# http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
PYLUCID_VERSION = (0, 8, 0, svn_revision)
PYLUCID_VERSION_STRING = "0.8.0" + svn_revision


