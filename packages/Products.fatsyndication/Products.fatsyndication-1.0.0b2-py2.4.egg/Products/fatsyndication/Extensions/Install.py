# Standard library imports
from cStringIO import StringIO

# Archetypes imports
from Products.Archetypes.Extensions.utils import install_subskin

# Product imports
from Products.fatsyndication.config import PROJECTNAME, GLOBALS


def install(self, reinstall=False):
    out = StringIO()

    install_subskin(self, out, GLOBALS)
    print >> out, "Installed skin for %s.\n" % PROJECTNAME
    #perms.setupPortalSecurity(self, out)

    print >> out, "Successfully installed %s.\n" % PROJECTNAME
    return out.getvalue()

