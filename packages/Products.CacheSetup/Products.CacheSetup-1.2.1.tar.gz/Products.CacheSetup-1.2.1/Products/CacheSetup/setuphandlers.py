from Products.CMFCore.utils import getToolByName
from zope.event import notify

try:
    from Products.Archetypes.event import ObjectInitializedEvent
    AT15 = True
except ImportError:
    # Plone 2.5 compatibility
    AT15 = False

def setupVarious(context):
    logger = context.getLogger("CacheSetup")
    if context.readDataFile("cachesetup-various.txt") is None:
        logger.info("Nothing to do")
        return

    site = context.getSite()

    # The tool is not created through the standard AT factory method,
    # so we need to do the required initialization here.
    pcs = getToolByName(site, "portal_cache_settings")
    if getattr(pcs, "_at_creation_flag", True):
        pcs.initializeArchetype()
        pcs.unmarkCreationFlag()
        if AT15: notify(ObjectInitializedEvent(pcs))
        logger.info("Initialized cache settings tool")
    pcs.updateInstalledVersion()


