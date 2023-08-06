from p4a.plonevideo import sitesetup
from p4a.z2utils import utils as z2utils

def install(portal):
    sitesetup.setup_portal(portal)

def uninstall(portal, reinstall, name='p4a.plonevideo'):
    z2utils.persist_five_components(portal, name)
    if not reinstall:
        sitesetup.unsetup_portal(portal)
