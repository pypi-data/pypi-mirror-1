
from patch import applyPatches
from zope.interface import implements
from interfaces import IPatchUtility
from logging import getLogger, INFO

APPLIED = False

log = getLogger('portalfactoryfix')
log.setLevel(INFO)

class PatchApplicator( object ):

    implements( IPatchUtility )
    
    def __init__( self ):
        global APPLIED
        if not APPLIED:
            log.info("Applied Portal Factory No Write Patch")
            applyPatches()
            APPLIED = True
            
