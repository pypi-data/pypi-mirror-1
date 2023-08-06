
from patch import applyPatches
from zope.interface import implements
from interfaces import IPatchUtility

APPLIED = False

class PatchApplicator( object ):

    implements( IPatchUtility )
    
    def __init__( self ):
        global APPLIED
        if not APPLIED:
            applyPatches()
            APPLIED = True
            
