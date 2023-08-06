import os
from sys import modules, exc_info
from logging import getLogger

from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Acquisition import aq_base, aq_parent, aq_inner, aq_get
from AccessControl import ClassSecurityInfo

LOG = getLogger('dm.zopepatches.zclasses')




##############################################################################
## Patch work

# put back 'App.Factory'
import Factory
modules['App.Factory'] = Factory

# partially reinstate 'AccessControl.Permissions'
from AccessControl import Permissions
Permissions.manage_zclasses = 'Manage Z Classes'

# give 'App.ProductRegistry' its '_product_zclasses' back
from App.ProductRegistry import ProductRegistry
ProductRegistry._product_zclasses = ()

# reinstate "OFS.PropertySheets"
from OFS.PropertySheets import PropertySheet

class FixedSchema(PropertySheet):
    """A Fixed-schema property sheet has no control over it's schema

    It gets its schema from another proprtysheet but has control over
    its value storage.

    This mix-in is used for ZClass instance proprtysheets, which store
    their data in instances, but get their schema from the
    proprtysheet managed in the ZClass.
    """

    def __init__(self, id, base, md=None):
        FixedSchema.inheritedAttribute('__init__')(self, id, md)
        self._base=base

    def _propertyMap(self):
        # Return a tuple of mappings, giving meta-data for properties.
        r = []
        for d in self._base._propertyMap():
            d = d.copy()
            mode = d.get('mode', 'wd')
            if 'd' in mode:
                d['mode']=filter(lambda c: c != 'd', mode)
            r.append(d)

        return tuple(r)

    def propertyMap(self):
        return self._propertyMap()

    def property_extensible_schema__(self):
        return 0
        return self._base._extensible

InitializeClass(FixedSchema)

from OFS import PropertySheets
PropertySheets.FixedSchema = FixedSchema



##############################################################################
## Code originally from "ZClasses.__init__"
##  not sure whether we really need it (as 'ZClasses' is not a product).
import ZClass
import ZClassOwner

createZClassForBase = ZClass.createZClassForBase

# Names of objects added by this product:
meta_types=(
    {'name': ZClass.ZClass.meta_type,
     'action':'manage_addZClassForm'},
    )

# Attributes (usually "methods") to be added to folders to support
# creating objects:
meta_types=(
    {'name': ZClass.ZClass.meta_type,
     'action':'manage_addZClassForm'},
    )

methods={
    'manage_addZClassForm': ZClass.manage_addZClassForm,
    'manage_addZClass': ZClass.manage_addZClass,
    'manage_subclassableClassNames': ZClassOwner.manage_subclassableClassNames,

    }

__ac_permissions__=(
    # To add items:
    ('Add Zope Class',
     ('manage_addZClassForm', 'manage_addZClass',
      'manage_subclassableClassNames')),
    )

misc_={}



##############################################################################
## Patch work

# reinstante 'Zope2.App.ClassFactory.ClassFactory'
import OFS.Uninstalled

def ClassFactory(jar, module, name,
                  _silly=('__doc__',), _globals={},
                  ):
    try:
        if module[:1]=='*':
            # ZCLass! Yee ha!
            return jar.root()['ZGlobals'][module]
        else:
            m=__import__(module, _globals, _globals, _silly)

        return getattr(m, name)
    except:
        return OFS.Uninstalled.Broken(jar, None, (module, name))

from Zope2.App import ClassFactory as _CF
_CF.ClassFactory = ClassFactory

# reinstate 'AccessControl.PermissionMapping'
def _isBeingAccessedAsZClassDefinedInstanceMethod(self):
        p=getattr(self,'__parent__',None)
        if p is None: return 0          # Not wrapped
        base=getattr(p, 'aq_base', None)
        return type(base) is PermissionMapper

from AccessControl.PermissionMapping import RoleManager
RoleManager._isBeingAccessedAsZClassDefinedInstanceMethod = _isBeingAccessedAsZClassDefinedInstanceMethod

# reinstate 'AccessControl.Role.RoleManager'
from AccessControl.Role import RoleManager
RoleManager.manage_options = ( # we might come too late.
          {'label':'Security', 'action':'manage_access',
         'help':('OFSP','Security.stx'),
         'filter': lambda self: not aq_get(self, '_isBeingUsedAsAMethod_', 0),
         },
        {'label':'Define Permissions', 'action':'manage_access',
         # do not know yet how to reinstate deleted help files
         # 'help':('OFSP','Security_Define-Permissions.stx'),
         'filter': lambda self: aq_get(self, '_isBeingUsedAsAMethod_', 0),
         },
        )

_ori_manage_access = RoleManager.manage_access

def manage_access(self, REQUEST, **kw):
        """Return an interface for making permissions settings.
        """
        if hasattr(self, '_isBeingUsedAsAMethod') and \
           self._isBeingUsedAsAMethod():
            return apply(self._method_manage_access,(), kw)
        else:
            return _ori_manage_access(self, REQUEST, **kw)

RoleManager.manage_access = manage_access
RoleManager._method_manage_access=DTMLFile('dtml/methodAccess', globals())


# partially reinstate "App.Management.Tabs"
def class_manage_path(self):
        if self.__class__.__module__[:1] != '*':
            return
        path = getattr(self.__class__, '_v_manage_path_roles', None)
        if path is None:
            meta_type = self.meta_type
            for zclass in self.getPhysicalRoot()._getProductRegistryData(
                'zclasses'):
                if zclass['meta_type'] == meta_type:
                    break
            else:
                self.__class__._v_manage_path_roles = ''
                return
            path = self.__class__._v_manage_path_roles = (
                '%(product)s/%(id)s' % zclass)
        if path:
            return '/Control_Panel/Products/%s/manage_workspace' % path

from App.Management import Tabs

Tabs.class_manage_path = class_manage_path
Tabs.class_manage_path__roles__ = None # public


# partialy reinstate "App.Product"
from AccessControl.Permissions import manage_zclasses
from Factory import Factory
ZClasses = modules[__name__]

from App.Product import ProductFolder
ProductFolder.all_meta_types = {'name': 'Product', 'action': 'manage_addProductForm',
                    'permission': manage_zclasses},
ProductFolder.meta_types = ProductFolder.all_meta_types
ProductFolder.manage_addProductForm = DTMLFile('dtml/addProduct', globals())

def manage_addProduct(self, id, title, REQUEST=None):
        """ Create a product.
        """
        i=Product(id, title)
        self._setObject(id,i)
        if REQUEST is not None:
            return self.manage_main(self,REQUEST,update_menu=1)

ProductFolder.manage_addProduct = manage_addProduct

from App.Product import Product
from App.Permission import PermissionManager

Product._isBeingUsedAsAMethod_ = 1
Product.meta_types = (
        ZClasses.meta_types +
        PermissionManager.meta_types +
        (
            {
                'name': Factory.meta_type,
                'action': 'manage_addPrincipiaFactoryForm'
                },
            )
        )
Product.manage_addZClassForm = ZClasses.methods['manage_addZClassForm']
Product.manage_addZClass = ZClasses.methods['manage_addZClass']
Product.manage_subclassableClassNames = ZClasses.methods['manage_subclassableClassNames']
Product.manage_addPrincipiaFactoryForm = DTMLFile('dtml/addFactory', globals())

def manage_addPrincipiaFactory(
        self, id, title, object_type, initial, permission=None, REQUEST=None):
        """ Add a ZClass factory
        """
        i = Factory(id, title, object_type, initial, permission)
        self._setObject(id,i)
        factory = self._getOb(id)
        factory.initializePermission()
        if REQUEST is not None:
            return self.manage_main(self,REQUEST,update_menu=1)
Product.manage_addPrincipiaFactory = manage_addPrincipiaFactory

def zclass_product_name(self):
        return self.id
Product.zclass_product_name = zclass_product_name    

import zlib
class CompressedOutputFile:
    def __init__(self, rot):
        self._c=zlib.compressobj()
        self._r=[]
        self._rot=rot
        rot.encrypt('')

    def write(self, s):
        self._r.append(self._rot.encryptmore(self._c.compress(s)))

    def getdata(self):
        self._r.append(self._rot.encryptmore(self._c.flush()))
        return ''.join(self._r)

class CompressedInputFile:
    _done=0
    def __init__(self, f, rot):
        self._c=zlib.decompressobj()
        self._b=''
        if isinstance(rot, str):
            import rotor
            rot=rotor.newrotor(rot)
        self._rot=rot
        rot.decrypt('')
        self._f=f

    def _next(self):
        if self._done: return
        l=self._f.read(8196)
        if not l:
            l=self._c.flush()
            self._done=1
        else:
            l=self._c.decompress(self._rot.decryptmore(l))
        self._b=self._b+l

    def read(self, l=None):
        if l is None:
            while not self._done: self._next()
            l=len(self._b)
        else:
            while l > len(self._b) and not self._done: self._next()
        r=self._b[:l]
        self._b=self._b[l:]

        return r

    def readline(self):
        l=self._b.find('\n')
        while l < 0 and not self._done:
            self._next()
            l=self._b.find('\n')
        if l < 0: l=len(self._b)
        else: l=l+1
        r=self._b[:l]
        self._b=self._b[l:]
        return r

# sad that I need to copy this monster
from App.Product import doInstall, ihasattr

def initializeProduct(productp, name, home, app):
    # Initialize a levered product
    import Globals  # to set data
    products = app.Control_Panel.Products
    fver = ''

    if hasattr(productp, '__import_error__'): ie=productp.__import_error__
    else: ie=None

    # Retrieve version number from any suitable version.txt
    for fname in ('version.txt', 'VERSION.txt', 'VERSION.TXT'):
        try:
            fpath = os.path.join(home, fname)
            fhandle = open(fpath, 'r')
            fver = fhandle.read().strip()
            fhandle.close()
            break
        except IOError:
            continue

    old=None
    try:
        if ihasattr(products,name):
            old=getattr(products, name)
            if ihasattr(old,'version') and old.version==fver:
                if hasattr(old, 'import_error_') and \
                   old.import_error_==ie:
                    # Version hasn't changed. Don't reinitialize.
                    return old
    except: pass

    try:
        f=CompressedInputFile(open(home+'/product.dat','rb'), name+' shshsh')
    except:
        f=fver and (" (%s)" % fver)
        product=Product(name, 'Installed product %s%s' % (name,f))
    else:
        meta=cPickle.Unpickler(f).load()
        product=app._p_jar.importFile(f)
        product._objects=meta['_objects']

    if old is not None:
        app._manage_remove_product_meta_type(product)
        products._delObject(name)
        for id, v in old.objectItems():
            try: product._setObject(id, v)
            except: pass

    products._setObject(name, product)
    #product.__of__(products)._postCopy(products)
    product.icon='p_/InstalledProduct_icon'
    product.version=fver
    product.home=home
    product.thisIsAnInstalledProduct=1

    if ie:
        product.import_error_=ie
        product.title='Broken product %s' % name
        product.icon='p_/BrokenProduct_icon'
        product.manage_options=(
            {'label':'Traceback', 'action':'manage_traceback'},
            )

    for name in ('README.txt', 'README.TXT', 'readme.txt'):
        path = os.path.join(home, name)
        if os.path.isfile(path):
            product.manage_options=product.manage_options+(
                {'label':'README', 'action':'manage_readme'},
                )
            break

    # Ensure this product has a refresh tab.
    found = 0
    for option in product.manage_options:
        if option.get('label') == 'Refresh':
            found = 1
            break
    if not found:
        product.manage_options = product.manage_options + (
            {'label':'Refresh', 'action':'manage_refresh',
             'help': ('OFSP','Product_Refresh.stx')},)

    if not doInstall():
        transaction.abort()
        return product

    # Give the ZClass fixup code in Application
    Globals.__disk_product_installed__ = 1
    return product

from App import Product as ZProduct
ZProduct.initializeProduct = initializeProduct


# reinstate "App.ProductsContext"
def registerZClass(self, Z, meta_type=None):
        base_class=Z._zclass_
        module=base_class.__module__
        name=base_class.__name__
        _registerZClass(Z, module, name)

def _registerZClass(Z, module, name):
        key="%s/%s" % (module, name)

        if module[:9]=='Products.': module=module.split('.')[1]
        else: module=module.split('.')[0]

        info="%s: %s" % (module, name)

        Products.meta_class_info[key]=info
        Products.meta_classes[key]=Z

def registerBaseClass(self, base_class, meta_type=None):
        #
        #   Convenience method, now deprecated -- clients should
        #   call 'ZClasses.createZClassForBase()' themselves at
        #   module import time, passing 'globals()', so that the
        #   ZClass will be available immediately.
        #
        Z = ZClasses.createZClassForBase( base_class, self._ProductContext__pack )
        return Z

from App.ProductContext import ProductContext
ProductContext.registerZClass = registerZClass
ProductContext.registerBaseClass = registerBaseClass


# partially reinstate 'OFS.misc_'
from OFS.misc_ import p_
from App.ImageFile import ImageFile

p_.Factory_icon = ImageFile('www/factory.gif', globals())
p_.Methods_icon = ImageFile('methods.gif', globals())
p_.Propertysheets_icon = ImageFile('propertysheets.gif', globals())



# reinstate "OFS.Application"
from OFS.Application import Application

def fixupZClassDependencies(self, rebuild=0):
        # Note that callers should not catch exceptions from this method
        # to ensure that the transaction gets aborted if the registry
        # cannot be rebuilt for some reason. Returns true if any ZClasses
        # were registered as a result of the call or the registry was
        # rebuilt.
        jar=self._p_jar
        result=0

        if rebuild:
            from BTrees.OOBTree import OOBTree
            jar.root()['ZGlobals'] = OOBTree()
            result = 1

        zglobals =jar.root()['ZGlobals']
        reg_has_key=zglobals.has_key

        products=self.Control_Panel.Products
        for product in products.objectValues():
            items=list(product.objectItems())
            finished_dict={}
            finished = finished_dict.has_key
            while items:
                name, ob = items.pop()
                base=aq_base(ob)
                if finished(id(base)):
                    continue
                finished_dict[id(base)] = None
                try:
                    # Try to re-register ZClasses if they need it.
                    if hasattr(base,'_register') and hasattr(base,'_zclass_'):
                        class_id=getattr(base._zclass_, '__module__', None)
                        if class_id and not reg_has_key(class_id):
                            ob._register()
                            result=1
                            if not rebuild:
                                LOG.info('Registered ZClass: %s' % ob.id)
                    # Include subobjects.
                    if hasattr(base, 'objectItems'):
                        m = list(ob.objectItems())
                        items.extend(m)
                    # Try to find ZClasses-in-ZClasses.
                    if hasattr(base, 'propertysheets'):
                        ps = ob.propertysheets
                        if (hasattr(ps, 'methods') and
                            hasattr(ps.methods, 'objectItems')):
                            m = list(ps.methods.objectItems())
                            items.extend(m)
                except:
                    LOG.warn('Broken objects exist in product %s.' % product.id,
                             exc_info=exc_info())

        return result

def checkGlobalRegistry(self):
        """Check the global (zclass) registry for problems, which can
        be caused by things like disk-based products being deleted.
        Return true if a problem is found"""
        try:
            keys=list(self._p_jar.root()['ZGlobals'].keys())
        except:
            LOG.error(
                'A problem was found when checking the global product '\
                'registry.  This is probably due to a Product being '\
                'uninstalled or renamed.  The traceback follows.',
                exc_info=exc_info())
            return 1
        return 0

Application.fixupZClassDependencies = fixupZClassDependencies
Application.fixupZClassDependencies__roles__ = () # private

Application.checkGlobalRegistry = checkGlobalRegistry
Application.checkGlobalRegistry__roles__ = () # private


from OFS.Application import AppInitializer
_app_ori_initialize = AppInitializer.initialize

def initialize(self):
    _app_ori_initialize(self)
    self.install_zglobals()
    self.check_zglobals()

def install_zglobals(self):
        app = self.getApp()

        # Make sure we have ZGlobals
        root=app._p_jar.root()
        if not root.has_key('ZGlobals'):
            from BTrees.OOBTree import OOBTree
            root['ZGlobals'] = OOBTree()
            self.commit('Added ZGlobals')

def check_zglobals(self):
        import Globals
        if not doInstall():
            return

        app = self.getApp()

        # Check for dangling pointers (broken zclass dependencies) in the
        # global class registry. If found, rebuild the registry. Note that
        # if the check finds problems but fails to successfully rebuild the
        # registry we abort the transaction so that we don't leave it in an
        # indeterminate state.

        did_fixups=0
        bad_things=0
        try:
            if app.checkGlobalRegistry():
                LOG.info(
                    'Beginning attempt to rebuild the global ZClass registry.')
                app.fixupZClassDependencies(rebuild=1)
                did_fixups=1
                LOG.info(
                    'The global ZClass registry has successfully been rebuilt.')
                transaction.get().note('Rebuilt global product registry')
                transaction.commit()
        except:
            bad_things=1
            LOG.error('The attempt to rebuild the registry failed.',
                       exc_info=True)
            transaction.abort()

        # Now we need to see if any (disk-based) products were installed
        # during intialization. If so (and the registry has no errors),
        # there may still be zclasses dependent on a base class in the
        # newly installed product that were previously broken and need to
        # be fixed up. If any really Bad Things happened (dangling pointers
        # were found in the registry but it couldn't be rebuilt), we don't
        # try to do anything to avoid making the problem worse.
        if (not did_fixups) and (not bad_things):

            # App.Product.initializeProduct will set this if a disk-based
            # product was added or updated and we are not a ZEO client.
            if getattr(Globals, '__disk_product_installed__', None):
                try:
                    LOG.info('New disk product detected, determining if we need '
                             'to fix up any ZClasses.')
                    if app.fixupZClassDependencies():
                        LOG.info('Repaired broken ZClass dependencies.')
                        self.commit('Repaired broked ZClass dependencies')
                except:
                    LOG.error('Attempt to fixup ZClass dependencies after '
                              'detecting an updated disk-based product failed.',
                              exc_info=exc_info())
                    transaction.abort()

AppInitializer.initialize = initialize
AppInitializer.install_zglobals = install_zglobals
AppInitializer.check_zglobals = check_zglobals


# reinstate "OFS.Cache"
from OFS import Cache
from AccessControl.Role import _isBeingUsedAsAMethod

def filterCacheTab(ob):
    if _isBeingUsedAsAMethod(ob):
        # Show tab when in a ZClass def that uses Cacheable as a base.
        parent = aq_parent(aq_inner(ob))
        return Cache.isCacheable(parent)
    else:
        return managersExist(ob)

Cache.filterCacheTab = filterCacheTab

from OFS.Cache import Cacheable
# we may come too late for derived classes
Cacheable.manage_options[0]['filter'] = filterCacheTab
Cacheable.ZCacheable_isAMethod = _isBeingUsedAsAMethod

def ZCacheable_getObAndView(self, view_name):
        """
        If this object is a method of a ZClass and we're working
        with the primary view, uses the ZClass instance as ob
        and our own ID as the view_name.  Otherwise returns
        self and view_name unchanged.
        """
        ob = self
        if not view_name and self.ZCacheable_isAMethod():
            # This is a ZClass method.
            ob = aq_parent(aq_inner(self))
            if isCacheable(ob):
                view_name = self.getId()
            else:
                # Both the parent and the child have to be
                # cacheable.
                ob = self
        return ob, view_name

Cacheable.ZCacheable_getObAndView = ZCacheable_getObAndView

ori_ZCacheable_getModTime = Cacheable.ZCacheable_getModTime

def ZCacheable_getModTime(self, mtime_func=None):
    mtime = ori_ZCacheable_getModTime(self, mtime_func)
    if self.ZCacheable_isAMethod():
        # This is a ZClass method.
        klass = getattr(aq_base(self), '__class__', None)
        instance = aq_parent(aq_inner(self))
        base = aq_base(instance)
        mtime = max(getattr(base, '_p_mtime', mtime), mtime)
        klass = getattr(base, '__class__', None)
        if klass:
            mtime = max(getattr(klass, '_p_mtime', mtime), mtime)

Cacheable.ZCacheable_getModTime = ZCacheable_getModTime


# reinstate 'OFS.FindSupport'
from OFS.FindSupport import FindSupport

def ZopeFind(self, obj, obj_ids=None, obj_metatypes=None,
                 obj_searchterm=None, obj_expr=None,
                 obj_mtime=None, obj_mspec=None,
                 obj_permission=None, obj_roles=None,
                 search_sub=0,
                 REQUEST=None, result=None, pre=''):
        """Zope Find interface"""

        if result is None:
            result=[]

            if obj_metatypes and 'all' in obj_metatypes:
                obj_metatypes=None

            if obj_mtime and type(obj_mtime)==type('s'):
                obj_mtime=DateTime(obj_mtime).timeTime()

            if obj_permission:
                obj_permission=p_name(obj_permission)

            if obj_roles and type(obj_roles) is type('s'):
                obj_roles=[obj_roles]

            if obj_expr:
                # Setup expr machinations
                md=td()
                obj_expr=(Eval(obj_expr), md, md._push, md._pop)

        base = aq_base(obj)

        if hasattr(base, 'objectItems'):
            try:    items=obj.objectItems()
            except: return result
        else:
            if getattr(base, 'meta_type', None) == 'Z Class':
                try:    items=obj.propertysheets.methods.objectItems()
                except: return result
            else:
                return result

        try: add_result=result.append
        except:
            raise AttributeError, `result`

        for id, ob in items:
            if pre: p="%s/%s" % (pre, id)
            else:   p=id

            dflag=0
            if hasattr(ob, '_p_changed') and (ob._p_changed == None):
                dflag=1

            bs = aq_base(ob)
            if (
                (not obj_ids or absattr(bs.getId()) in obj_ids)
                and
                (not obj_metatypes or (hasattr(bs, 'meta_type') and
                 bs.meta_type in obj_metatypes))
                and
                (not obj_searchterm or
                 (hasattr(ob, 'PrincipiaSearchSource') and
                  ob.PrincipiaSearchSource().find(str(obj_searchterm)) >= 0
                  )
                 or
                 (hasattr(ob, 'SearchableText') and
                  ob.SearchableText().find(str(obj_searchterm)) >= 0)
                 )
                and
                (not obj_expr or expr_match(ob, obj_expr))
                and
                (not obj_mtime or mtime_match(ob, obj_mtime, obj_mspec))
                and
                ( (not obj_permission or not obj_roles) or \
                   role_match(ob, obj_permission, obj_roles)
                )
                ):
                add_result((p, ob))
                dflag=0

            is_zclass = getattr(bs, 'meta_type', None) == 'Z Class'
            if search_sub and (hasattr(bs, 'objectItems') or is_zclass):
                if is_zclass:
                    subob = ob.propertysheets.methods
                    sub_p = '%s/propertysheets/methods' % p
                else:
                    subob = ob
                    sub_p = p
                self.ZopeFind(subob, obj_ids, obj_metatypes,
                                   obj_searchterm, obj_expr,
                                   obj_mtime, obj_mspec,
                                   obj_permission, obj_roles,
                                   search_sub,
                                   REQUEST, result, sub_p)
            if dflag: ob._p_deactivate()

        return result

FindSupport.ZopeFind = ZopeFind


# reinstate "Shared.DC.ZRDB.DA"
from Shared.DC.ZRDB.DA import DA, change_database_methods

DA._zclass = None
DA.manage_advancedForm=DTMLFile('dtml/advanced', globals())

ori_manage_advanced = DA.manage_advanced

def manage_advanced(self, max_rows, max_cache, cache_time,
                    class_name, class_file, direct=None,
                    REQUEST=None, zclass='', connection_hook=None):
    if zclass:
        for d in self.aq_acquire('_getProductRegistryData')('zclasses'):
            if ("%s/%s" % (d.get('product'),d.get('id'))) == zclass:
                self._zclass=d['meta_class']
                break
    else: self._zclass = None
    return ori_manage_advanced(self, max_rows, max_cache, cache_time,
                               class_name, class_file, direct,
                               REQUEST, connection_hook)

DA.manage_advanced = manage_advanced

# sad that we need to copy this monster
def __call__(self, REQUEST=None, __ick__=None, src__=0, test__=0, **kw):
        """Call the database method

        The arguments to the method should be passed via keyword
        arguments, or in a single mapping object. If no arguments are
        given, and if the method was invoked through the Web, then the
        method will try to acquire and use the Web REQUEST object as
        the argument mapping.

        The returned value is a sequence of record objects.
        """

        __traceback_supplement__ = (SQLMethodTracebackSupplement, self)

        if REQUEST is None:
            if kw:
                REQUEST=kw
            else:
                if hasattr(self, 'REQUEST'):
                    REQUEST=self.REQUEST
                else:
                    REQUEST={}

        # connection hook
        c = self.connection_id
        # for backwards compatability
        hk = self.connection_hook
        # go get the connection hook and call it
        if hk:
            c = getattr(self, hk)()
           
        try:
            dbc=getattr(self, c)
        except AttributeError:
            raise AttributeError, (
                "The database connection <em>%s</em> cannot be found." % (
                c))

        try:
            DB__=dbc()
        except: raise DatabaseError, (
            '%s is not connected to a database' % self.id)

        if hasattr(self, 'aq_parent'):
            p=self.aq_parent
            if self._isBeingAccessedAsZClassDefinedInstanceMethod():
                p=p.aq_parent
        else:
            p=None

        argdata=self._argdata(REQUEST)
        argdata['sql_delimiter']='\0'
        argdata['sql_quote__']=dbc.sql_quote__

        security=getSecurityManager()
        security.addContext(self)
        try:
            try:
                query=apply(self.template, (p,), argdata)
            except TypeError, msg:
                msg = str(msg)
                if string.find(msg,'client') >= 0:
                    raise NameError("'client' may not be used as an " +
                        "argument name in this context")
                else: raise
        finally:
            security.removeContext(self)

        if src__:
            return query

        if self.cache_time_ > 0 and self.max_cache_ > 0:
            result=self._cached_result(DB__, query, self.max_rows_, c)
        else:
            result=DB__.query(query, self.max_rows_)

        if hasattr(self, '_v_brain'):
            brain=self._v_brain
        else:
            brain=self._v_brain=getBrain(self.class_file_, self.class_name_)

        zc=self._zclass
        if zc is not None: zc=zc._zclass_

        if type(result) is type(''):
            f=StringIO()
            f.write(result)
            f.seek(0)
            result = File(f,brain,p, zc)
        else:
            result = Results(result, brain, p, zc)
        columns = result._searchable_result_columns()
        if test__ and columns != self._col:
            self._col=columns

        # If run in test mode, return both the query and results so
        # that the template doesn't have to be rendered twice!
        if test__:
            return query, result

        return result

DA.__call__ = __call__
def manage_product_zclass_info(self):
        r=[]
        Z=self._zclass
        Z=getattr(Z, 'aq_self', Z)
        for d in self.aq_acquire('_getProductRegistryData')('zclasses'):
            z=d['meta_class']
            if hasattr(z._zclass_,'_p_deactivate'):
                # Eek, persistent
                continue
            x={}
            x.update(d)
            x['selected'] = (z is Z) and 'selected' or ''
            del x['meta_class']
            r.append(x)

        return r

DA.manage_product_zclass_info = manage_product_zclass_info
DA.security = ClassSecurityInfo()
DA.security.declareProtected(change_database_methods,
                              'manage_product_zclass_info')
InitializeClass(DA)


# reinstate "Testing.ZopeTestCase.utils"
from Testing.ZopeTestCase.utils import layer
from Testing.ZopeTestCase import utils

@layer.appcall
def setupZGlobals(app):
    '''Sets up the ZGlobals BTree required by ZClasses.'''
    root = app._p_jar.root()
    if not root.has_key('ZGlobals'):
        from BTrees.OOBTree import OOBTree
        root['ZGlobals'] = OOBTree()
        transaction.commit()

utils.setupZGlobals = setupZGlobals
utils.__all__.append('setupZGlobals')


###############################################################################
## More patchwork
import Products.BTreeFolder2.BTreeFolder2
import OFS.Image, OFS.Folder, AccessControl.User
import OFS.DTMLMethod, OFS.DTMLDocument, OFS.PropertySheets
import OFS.OrderedFolder
from Products import OFSP

createZClassForBase( OFS.DTMLMethod.DTMLMethod, OFSP
                   , 'ZDTMLMethod', 'DTML Method' )
createZClassForBase( OFS.DTMLDocument.DTMLDocument, OFSP
                   , 'ZDTMLDocument', 'DTML Document' )
createZClassForBase( OFS.Image.Image, OFSP
                   , 'ZImage', 'Image' )
createZClassForBase( OFS.Image.File, OFSP
                   , 'ZFile', 'File' )
createZClassForBase( OFS.Folder.Folder, OFSP
                   , 'ZFolder', 'Folder' )
createZClassForBase( OFS.OrderedFolder.OrderedFolder, OFSP )
createZClassForBase( AccessControl.User.UserFolder, OFSP
                   , 'ZUserFolder', 'User Folder' )
createZClassForBase( AccessControl.User.User, OFSP
                   , 'ZUser', 'User' )

createZClassForBase(Products.BTreeFolder2.BTreeFolder2.BTreeFolder2, Products.BTreeFolder2)

from ObjectManager import ZObjectManager
_registerZClass(ZObjectManager, "ZClasses", "ObjectManager")


###############################################################################
## Now add the 'ZClasses' alias
modules['ZClasses'] = modules[__name__]
