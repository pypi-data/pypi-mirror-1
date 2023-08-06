from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interfaces import IFactory

from AccessControl import getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.ZopeSecurityPolicy import getRoles
from Acquisition import aq_parent
from Acquisition import aq_base
from Acquisition import aq_inner
import OFS.subscribers
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFPlone.FactoryTool import TempFolder, FactoryTool, FACTORY_INFO
from Products.CMFPlone.utils import base_hasattr
from ZODB.POSException import ConflictError

methods = ('__ac_local_roles__','get_valid_userids','valid_roles','userdefined_roles','owner_info','allowedContentTypes')

_marker = []

def cached(func):
    def new_func(self):
        d = '_data_%s'%func.__name__
        data = getattr(self, d, _marker)
        if data is not _marker:
            return data
        res = func(self)
        setattr(self, d, res)
        return res
    return new_func

for m in methods:
    fn = getattr(TempFolder, m)
    setattr(TempFolder, m, cached(fn))

def _createObjectByType(type_name, container, id, *args, **kw):
    """This function replaces Products.CMFPlone.utils._createObjectByType.
    
    If no product is set on fti, use IFactory to lookup the factory.
    Additionally we add 'container' as 'parent' kw argument when calling the
    IFactory implementation. this ensures the availability of the acquisition
    chain if needed inside the construction logic.
    
    The kw argument hack is some kind of semi-valid since the IFactory interface
    promises the __call__ function to accept all given args and kw args.
    As long as the specific IFactory implementation provides this signature
    everything works well unless any other 3rd party factory expects another
    kind of object as 'parent' kw arg than the provided one. 
    """
    id = str(id)
    typesTool = getToolByName(container, 'portal_types')
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError, 'Invalid type %s' % type_name

    if not fti.product:
        m = queryUtility(IFactory, fti.factory, None)
        if m is None:
            raise ValueError, ('Product factory for %s was invalid' %
                               fti.getId())
        kw['parent'] = container
        ob = m(id, *args, **kw)
        # its not set by factory.
        container[id] = ob
    else:
        p = container.manage_addProduct[fti.product]
        m = getattr(p, fti.factory, None)
        if m is None:
            raise ValueError, ('Product factory for %s was invalid' %
                               fti.getId())
        # construct the object
        m(id, *args, **kw)
        ob = container._getOb( id )
    
    return fti._finishConstruction(ob)

# Try making a FauxArchetypeTool that intercepts
class FauxArchetypeTool(object):
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, tool):
        self.tool = tool

    def getCatalogsByType(self,type_name):
        return []

    def __getattr__(self, id):
        return getattr(self.tool, id)

def __getitem__(self, id):
    # Zope's inner acquisition chain for objects returned by __getitem__ will be
    # portal -> portal_factory -> temporary_folder -> object
    # What we really want is for the inner acquisition chain to be
    # intended_parent_folder -> portal_factory -> temporary_folder -> object
    # So we need to rewrap...
    portal_factory = aq_parent(self)
    intended_parent = aq_parent(portal_factory)

    # If the intended parent has an object with the given id, just do a passthrough
    if hasattr(intended_parent, id):
        return getattr(intended_parent, id)

    # rewrap portal_factory
    portal_factory = aq_base(portal_factory).__of__(intended_parent)
    # rewrap self
    temp_folder = aq_base(self).__of__(portal_factory)

    if id in self.objectIds():
        return (aq_base(self._getOb(id)).__of__(temp_folder)).__of__(intended_parent)
    else:
        type_name = self.getId()
        try:
            self.archetype_tool = FauxArchetypeTool(getToolByName(self, 'archetype_tool'))
            _createObjectByType(type_name, self, id)
            #self.invokeFactory(id=id, type_name=type_name)
        except ConflictError:
            raise
        except:
            # some errors from invokeFactory (AttributeError, maybe others)
            # get swallowed -- dump the exception to the log to make sure
            # developers can see what's going on
            getToolByName(self, 'plone_utils').logException()
            raise
        obj = self._getOb(id)
        
        # keep obj out of the catalog
        obj.unindexObject()

        # additionally keep it out of Archetypes UID and refs catalogs
        if base_hasattr(obj, '_uncatalogUID'):
            obj._uncatalogUID(obj)
        if base_hasattr(obj, '_uncatalogRefs'):
            obj._uncatalogRefs(obj)

        return (aq_base(obj).__of__(temp_folder)).__of__(intended_parent)

TempFolder.__getitem__ = __getitem__


def _setObject(self, id, object, roles=None, user=None, set_owner=1,
               suppress_events=True):
    """Set an object into this container.

    Also sends IObjectWillBeAddedEvent and IObjectAddedEvent.
    """
    ob = object # better name, keep original function signature
    v = self._checkId(id)
    if v is not None:
        id = v
    t = getattr(ob, 'meta_type', None)

    # If an object by the given id already exists, remove it.
    for object_info in self._objects:
        if object_info['id'] == id:
            self._delObject(id)
            break

    self._objects = self._objects + ({'id': id, 'meta_type': t},)
    self._setOb(id, ob)
    ob = self._getOb(id)

    if set_owner:
        # TODO: eventify manage_fixupOwnershipAfterAdd
        # This will be called for a copy/clone, or a normal _setObject.
        ob.manage_fixupOwnershipAfterAdd()

        # Try to give user the local role "Owner", but only if
        # no local roles have been set on the object yet.
        if getattr(ob, '__ac_local_roles__', _marker) is None:
            user = getSecurityManager().getUser()
            if user is not None:
                userid = user.getId()
                if userid is not None:
                    ob.manage_setLocalRoles(userid, ['Owner'])

    OFS.subscribers.compatibilityCall('manage_afterAdd', ob, ob, self)

    return id

TempFolder._setObject = _setObject

# Override listTypeInfo
def listTypeInfo( self, container=None ):
    """
        Return a sequence of instances which implement the
        TypeInformation interface, one for each content
        type registered in the portal.
    """
    request = getattr(self, 'REQUEST', None)
    verify = self.objectIds()
    key = 'listTypeInfo'
    if container is None:
        key = '%s-None'%key
    elif not shasattr(aq_base(container), 'UID'):
        key = '%s-%s' % (key, container.getId())
    else:
        key = '%s-%s' % (key, container.UID())
    verify_key = "verify-%s" % key

    if request is not None and getattr(request, verify_key, None)==key:
        tmp = request.get(key, None)
        if tmp is not None:
            return tmp

    typelist = []
    for t in self.objectValues():
        # Filter out things that aren't TypeInformation and
        # types for which the user does not have adequate permission.
        if not ITypeInformation.providedBy(t):
            continue
        elif not t.getId():
            # XXX What's this used for ?
            # Not ready.
            continue
        typelist.append(t)

    # Check permissions
    if container is None:
        res = typelist
        if request is not None:
            request.set(key, res)
        return res

    if not typelist:
        res = []
        if request is not None:
            request.set(key, [])
            request.set(verify_key, verify)
        return res

    addcontext = container
    portal_membership = getToolByName(self, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()

    rolesInContext = dict.fromkeys(member.getRolesInContext(addcontext))
    if not rolesInContext:
        res = []
        if request is not None:
            request.set(key, [])
        return res

    dispatcher = getattr(addcontext, 'manage_addProduct', None)
    if dispatcher is None:
        res = []
        if request is not None:
            request.set(key, [])
        return res

    result = []

    # XXX need to handle constraintypes as well
    all_meta = None
    for ti in typelist:
        if not ti.factory:
            continue

        if not ti.product:
            m = queryUtility(IFactory, ti.factory, None)
            if m is not None:
                if all_meta is None:
                    # Set up the meta type -> permission dict
                    all_meta = {}
                    for d in container.all_meta_types():
                        all_meta[d['name']] = d['permission']
                perm = all_meta.get(ti.content_meta_type, None)
                if perm is not None:
                    roles = rolesForPermissionOn(perm, container)

        else:
            p = None
            try:
                p = dispatcher[ti.product]
            except AttributeError:
                continue

            m = getattr(p, ti.factory, None)

            if m is None:
                continue

            roles = getRoles(p, ti.factory, m, [])


        if [r for r in roles if rolesInContext.has_key(r)]:
            result.append(ti)

    if request is not None:
        request.set(key, result)
    return result

from Products.CMFCore.TypesTool import TypesTool
TypesTool.listTypeInfo = listTypeInfo

def getDefaultAddableTypes(self, context=None):
    """returns a list of normally allowed objects as ftis.
    Exactly like PortalFolder.allowedContentTypes except this
    will check in a specific context.
    """
    if context is None:
        context = self

    if shasattr(aq_base(context), 'UID'):
        uid = context.UID()
    else:
        uid = hash(context)
    key = 'defaulttypes%s' % uid
    tmp = self.REQUEST.get(key, None)
    if tmp is not None:
        return tmp

    portal_types = getToolByName(self, 'portal_types')
    myType = portal_types.getTypeInfo(self)
    if myType is None:
        res = portal_types.listTypeInfo()
        self.REQUEST.set(key, res)
        return res

    typelist = []    
    for t in portal_types.objectValues():
        # Filter out things that aren't TypeInformation and
        # types for which the user does not have adequate permission.
        if not ITypeInformation.providedBy(t):
            continue
        if not t.getId():
            # XXX What's this used for ?
            # Not ready.
            continue
        if myType.allowType( t.getId() ):
            typelist.append( t )

    if not typelist:
        res = []
        self.REQUEST.set(key, res)
        return res

    addcontext = context
    portal_membership = getToolByName(self, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()

    rolesInContext = dict.fromkeys(member.getRolesInContext(addcontext))
    if not rolesInContext:
        res = []
        self.REQUEST.set(key, res)
        return res

    dispatcher = getattr(addcontext, 'manage_addProduct', None)
    if dispatcher is None:
        res = []
        self.REQUEST.set(key, res)
        return res

    result = []
    
    # XXX need to handle constraintypes as well
    for ti in typelist:
        if not ti.product and not ti.factory:
            continue
        
        if not ti.product:
            m = queryUtility(IFactory, ti.factory, None)
            if m is None:
                continue
            
            mt = None
            for d in context.all_meta_types():
                if d['name'] == ti.content_meta_type:
                    mt = d
                    break
            if not mt:
                continue
            
            perm = mt['permission']
            if perm is None:
                continue
            roles = rolesForPermissionOn(perm, context)
        else:
            p = None
            try:
                p = dispatcher[ti.product]
            except AttributeError:
                continue
    
            m = getattr(p, ti.factory, None)
    
            if m is None:
                continue
    
            roles = getRoles(p, ti.factory, m, [])
    
        if [r for r in roles if rolesInContext.has_key(r)]:
            result.append(ti)

    self.REQUEST.set(key, result)
    return result

from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixin
ConstrainTypesMixin.getDefaultAddableTypes = getDefaultAddableTypes

from Products.CMFCore.PortalFolder import PortalFolderBase
PortalFolderBase.allowedContentTypes = getDefaultAddableTypes

def _constructInstance(self, container, id, *args, **kw):
    """Products.CMFCore.TypesTool.FactoryTypeInformation._constructInstance
    replacement.
    
    Use new style factory if no product is set on fti.
    Additionally we add 'container' as 'parent' kw argument when calling the
    IFactory implementation. this ensures the availability of the acquisition
    chain if needed inside the construction logic.
    
    The kw argument hack is some kind of semi-valid since the IFactory interface
    promises the __call__ function to accept all given args and kw args.
    As long as the specific IFactory implementation provides this signature
    everything works well unless any other 3rd party factory expects another
    kind of object as 'parent' kw arg than the provided one.
    """
    # XXX: this method violates the rules for tools/utilities:
    # it depends on self.REQUEST
    id = str(id)

    if self.product:
        # oldstyle factory
        m = self._getFactoryMethod(container, check_security=0)

        if getattr(aq_base(m), 'isDocTemp', 0):
            kw['id'] = id
            newid = m(m.aq_parent, self.REQUEST, *args, **kw)
        else:
            newid = m(id, *args, **kw)
        # allow factory to munge ID
        newid = newid or id

    else:
        # newstyle factory
        factory = getUtility(IFactory, self.factory)
        kw['parent'] = container
        obj = factory(id, *args, **kw)
        rval = container._setObject(id, obj)
        newid = isinstance(rval, basestring) and rval or id

    return container._getOb(newid)

from Products.CMFCore.TypesTool import FactoryTypeInformation
FactoryTypeInformation._constructInstance = _constructInstance

def _getTempFolder(self, type_name):
    
    factory_info = self.REQUEST.get(FACTORY_INFO, {})
    tempFolder = factory_info.get(type_name, None)
    if tempFolder:
        tempFolder = aq_inner(tempFolder).__of__(self)
        return tempFolder
    
    # make sure we can add an object of this type to the temp folder
    types_tool = getToolByName(self, 'portal_types')
    if not type_name in types_tool.TempFolder.allowed_content_types:
        # update allowed types for tempfolder
        types_tool.TempFolder.allowed_content_types=(types_tool.listContentTypes())
        
    tempFolder = TempFolder(type_name).__of__(self)

    factory_info[type_name] = tempFolder
    self.REQUEST.set(FACTORY_INFO, factory_info)
    return tempFolder

FactoryTool._getTempFolder = _getTempFolder
