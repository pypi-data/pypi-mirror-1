# to be run with "bin/zopectl run"
from Testing.makerequest import makerequest
app = makerequest(app)
REQUEST = app.REQUEST

# make sure 'addProduct' works
p=app.Control_Panel.Products
apf = p.manage_addProductForm
x = apf()
assert '<form action="manage_addProduct" method="POST">' in x
p.manage_addProduct(id='zc_tzc', title='ZClasses test')
zcp = p.zc_tzc

# ensure ZClasses can be created
x = zcp.manage_addZClassForm()
zcp.manage_addZClass('zc', meta_type='zc', CreateAFactory=1, zope_object=1)
zc = zcp.zc

# ensure ZInstances can be created
assert 'zc' in [m['name'] for m in app.all_meta_types()]
x = app.manage_addProduct['zc_tzc'].zc_factory.index_html(REQUEST)
assert '<form action="zc_add">' in x
# we must login to be able to add the instance
from AccessControl.User import system
from AccessControl.SecurityManagement import newSecurityManager
newSecurityManager(None, system)
REQUEST.form['id'] = 'zc1' # funny parameter passing
zc1 = app.manage_addProduct['zc_tzc'].zc_add(0)

# ensure property sheets can be created
psc = zc.propertysheets.common
x = psc.manage_addCommonSheetForm()
assert '<FORM ACTION="manage_addCommonSheet" METHOD="POST">' in x
psc.manage_addCommonSheet('properties', '')
ps = psc.properties
ps.manage_addProperty('p1', 'Property 1', 'string')
assert zc1.p1 == 'Property 1'

# ensure use of property sheets as views
views = zc.propertysheets.views
x = views.manage()
assert '<form action="manage_add" method="post">' in x
assert '<option>propertysheets/properties/manage</option>' in x
views.manage_add('Properties', 'propertysheets/properties/manage', '')
x = views.manage()
assert 'Properties' in x
assert 'Properties' in [o['label'] for o in zc1.manage_options]

# ensure methods can be created
methods = zc.propertysheets.methods
methods.manage_addProduct['PageTemplates'].manage_addPageTemplate('index_html')
# for unknown reasons, "methods" tries hard to append a blank
assert 'index_html ' in methods.objectIds()

# ensure us()e of methods as views
x = views.manage()
assert '<option>index_html</option>' in x
views.manage_add('View', 'index_html', '')
assert 'View' in [o['label'] for o in zc1.manage_options]

# ensure "ZClasses: ObjectManager" works
zcp.manage_addZClass('zom', baseclasses=['ZClasses/ObjectManager'], meta_type='zom', CreateAFactory=1, zope_object=1)
zom = zcp.zom
assert 'Subobjects' in [o['label'] for o in zom.manage_options]
REQUEST.form['id'] =  REQUEST.other['id'] = 'zom1'
zom1 = app.manage_addProduct['zc_tzc'].zom_add(0)
assert zom1.all_meta_types() == ()
so = zom.propertysheets.subobjects
so.manage_edit(meta_types=('File',), isFolderish=True)
assert 'File' in [mt['name'] for mt in zom1.all_meta_types()]

# ensure permissions work
zcp.manage_addPermission('zc_tzc_permission', '', 'zc_tzc_permission')
zp = zc.propertysheets.permissions
x = zp.manage()
assert '>zc_tzc_permission</option>' in x
zp.manage_edit(('Add zcs', 'zc_tzc_permission'))
assert zp.classDefinedPermissions() == ['Add zcs', 'zc_tzc_permission']
x = ps.manage_security()
assert 'Manage properties' in x
assert '<option>zc_tzc_permission</option>' in x
ps.manage_setPermissionMapping(['Manage properties'], ['zc_tzc_permission'])
x = zc1.manage_access(REQUEST)
assert '<a href="manage_permissionForm?permission_to_manage=zc_tzc_permission">zc_tzc_permission</a>' in x
zc1p = zc1.propertysheets.properties
zc1.manage_permission('zc_tzc_permission', ['Authenticated'], True)
assert 'Authenticated' in zc1p.manage__roles__
