"""

Make Archetypes content factory aware, by not having it indexed at all while
. This prevents lots of spurious transactions in. It does potentially cause
breakage for reference browser usage.


"""
from Acquisition import aq_inner, aq_parent

try:
    from Products.CacheSetup.patch_utils import call as cachefu_call
except ImportError:
    cachefu_call = None

def isFactoryContained( obj ):
    o = aq_parent(aq_inner(obj))
    if o is None: return False
    return o.meta_type == 'TempFolder'

def referenceAfterAdd( self, item, container ):
    if isFactoryContained( self ):
        return
    return self.referenceAfterAdd( item, container )

def uncatalogUID( self, aq, uc=None ):
    if isFactoryContained( self ):
        return
    return self.at_uncatalogUID( aq, uc )
    
def uncatalogRefs( self, aq, uc=None, rc=None ):
    if isFactoryContained( self ):
        return
    return self.at_uncatalogRefs( aq, uc, rc )

def reindexObject( self, idxs=() ):
    if isFactoryContained( self ):
        return
    return self.at_reindexObject( idxs )

def reindexObjectSecurity( self, skip_self=False ):
    if isFactoryContained( self ):
        return
    return self.at_reindexObjectSecurity( skip_self )

def unindexObject( self ):
    if isFactoryContained( self ):
        return
    return self.at_unindexObject()

def indexObject( self ):
    if isFactoryContained( self ):
        return
    return self.at_indexObject()


def managePermission( self, permission_to_manage,
                       roles=[], acquire=0, REQUEST=None ):
    if isFactoryContained( self ):
        return cachefu_call(self, 'manage_permission',
                            permission_to_manage,
                            roles, acquire, REQUEST )
    else:
        return self.zopeManagePermission( permission_to_manage,
                                          roles, acquire, REQUEST )
    
def applyPatches( ):
    from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
    from Products.Archetypes.Referenceable import Referenceable

    Referenceable.referenceAfterAdd = Referenceable.manage_afterAdd
    Referenceable.manage_afterAdd = referenceAfterAdd
    
    Referenceable.at_uncatalogUID = Referenceable._uncatalogUID
    Referenceable._uncatalogUID = uncatalogUID
    
    Referenceable.at_uncatalogRefs = Referenceable._uncatalogRefs
    Referenceable._uncatalogRefs = uncatalogRefs
    
    CatalogMultiplex.at_indexObject = CatalogMultiplex.indexObject
    CatalogMultiplex.indexObject = indexObject

    CatalogMultiplex.at_reindexObject = CatalogMultiplex.reindexObject
    CatalogMultiplex.reindexObject = reindexObject    

    CatalogMultiplex.at_unindexObject = CatalogMultiplex.unindexObject
    CatalogMultiplex.unindexObject = unindexObject

    CatalogMultiplex.at_reindexObjectSecurity = CatalogMultiplex.reindexObjectSecurity
    CatalogMultiplex.reindexObjectSecurity= reindexObjectSecurity
    
    if False: #cachefu_call: # This needs to be called after CacheSetup Monkey Patches
        from AccessControl.Role import RoleManager
        RoleManager.zopeManagePermission = RoleManager.manage_permission
        RoleManager.manage_permission = managePermission
        
        
    
