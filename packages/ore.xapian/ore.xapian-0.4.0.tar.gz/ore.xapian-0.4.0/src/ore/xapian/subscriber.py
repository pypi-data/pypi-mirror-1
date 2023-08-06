import interfaces
from zope.security.proxy import removeSecurityProxy

# event handlers for an object lifecycle
def objectAdded( object, event ):
    if removeSecurityProxy:
        object = removeSecurityProxy( object )
    interfaces.IOperationFactory( object ).add()
    
def objectModified( object, event ):
    if removeSecurityProxy:
        object = removeSecurityProxy( object )    
    interfaces.IOperationFactory( object ).modify()
    
def objectDeleted( object, event ):
    if removeSecurityProxy:
        object = removeSecurityProxy( object )    
    interfaces.IOperationFactory( object ).remove()
