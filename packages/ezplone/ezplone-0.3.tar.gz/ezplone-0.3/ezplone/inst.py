#!/usr/bin/env python
# encoding: utf-8
"""
Helper class for product (de)installation.

This defines a class to be created and called in the install and uninstall
functions of a products ``Extensions/Install.py`` file. It handles the
necessary creation and deletion of product configlets, tools and properties.

For example, a typical install would look like this::

	from ezplone import inst
	installer = inst.EasyInstaller ('MyProduct', 'mypr')
	installer.install_dependencies (['Archetypes', 'CMFUSer'])
	installer.install_types (installer.out, listTypes (PROJECTNAME),
		PROJECTNAME)
	installer.install_subskin (installer.out, GLOBALS)
	installer.install_workflow ('revi_workflow')
	installer.install_configlets (my_configlets)
	for tool in _tools:
		installer.install_tool (tool)
	installutils.install_product_properties (props)
	installer.log ("Successfully installed %s." % PROJECTNAME")
	return installer.get_log()
	
A typical uninstall might look like this::

	from ezplone import inst
	uninstaller = inst.EasyUninstaller (self, config.PRODUCT_NAME,
		myconfig.PRODUCT_ABBR)
	uninstaller.uninstall_configlets (_configlets)
	uninstaller.uninstall_tool (ReviTool)
	uninstaller.log ("Successfully uninstalled %s." % config.PRODUCT_NAME)
	return uninstaller.get_log()


"""

__docformat__ = "restructuredtext en"


## CONSTANTS & DEFINES: ###

### IMPORTS ###

import cStringIO
import exceptions

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

__all__ = [
	'EasyInstaller',
	'EasyUninstaller',
	'require_modules',
]


### IMPLEMENTATION ###

### UTILITIES

def require_modules (names):
	"""
	A simple way of checking if modules are available. 
	
	:Parameters:
		names : list
			A list of module names.
	
	It's sometimes useful in old-style Products to check if required modules
	(not Products) are available, so a Product doesn't get installed and then
	not work because of missing libraries. This function so, by simply trying
	to import those modules, throwing if there is a problem and thus halting
	Product installation.
	
	"""
	if (type (names) != type ([])):
		names = [names]
	fail = []
	for mod_name in names:
		try:
			__import__ (mod_name)
		except:
			fail.append (mod_name)
	if fail:
		raise exceptions.ImportError (', '.join (fail))


### BASE CLASS

class _BaseEasyClass (object):
	"""
	A base class for deriving (un)installers.
	
	There should be no need to access this directly as it is simply a base
	for the installer and uninstaller classes.

	"""
	def __init__ (self, context, product_name, id_prefix=None):
		"""
		Base class ctor.
		
		:Parameters:
			context
				Any site object suitable for obtaining context.
			product_name
				The name of the product to be (de)installed.
			id_prefix
				A prefix to be used for automatic generation of ids where none
				are given, e.g. automatically naming the product property sheet
				'prefix_properties'. If not supplied, it is constructed from
				the name of the product.
		
		"""
		self.context = context
		self.name = product_name
		if (id_prefix is None):
			id_prefix = self.name.lower().strip().replace (' ', '')
		self.id_prefix = id_prefix
		self.out = cStringIO.StringIO()


	def log (self, msg):
		"""
		Spit a message to the logging stream.
		"""
		print >> self.out, msg


	def get_log (self):
		"""
		Return string of installation log.
		"""
		return self.out.getvalue()


### INSTALLER

class EasyInstaller (_BaseEasyClass):
	"""
	Helper functions for installation, wrapped in a class.

	This should be instatiated in a products ``install`` method, and methods
	called as needed.

	"""
	def __init__ (self, context, product_name, globals, id_prefix=None):
		"""
		Class ctor.

		:Parameters:
			context
				Any site object suitable for obtaining context.
			product_name
				Self descriptive.
			id_prefix
				For building configlet (etc.) names. See ``_BaseEasyClass``.
			globals
				Product global namespace.

		This prepares the class for calling methods. If id_prefix (which could
		be used later for automatic construction of object names) is not
		supplied, it will be constructed from cleaning up the product name.
				
		For example::

			installer = (app, "MyProduct", 'mypr')

		"""
		_BaseEasyClass.__init__ (self, context, product_name, id_prefix)
		self.globals = globals


	def install_dependencies (self, req_products):
		"""
		Ensure prerequisite products are installed.

		:Parameters:
			req_products
				A sequence of required product names.

		For example::

			installer.install_dependencies (self, ['Archetypes', 'CMFUser'])

		"""
		theQuickInst = getToolByName (self.context, 'portal_quickinstaller')
		for item in req_products:
			theQuickInst.installProduct (item)
			self.log ("Installed other necessary product (%s)." % item)
		self.log ("Finished installing dependencies.")

	def install_types (self):
		installTypes (self.context, self.out, listTypes (self.name), self.name)

	def install_subskin (self):
		install_subskin (self.context, self.out, self.globals)


	def install_tool (self, tool_cls):
		"""
		Install any product tools.

		This will install any tools that are not already present. Note that the
		argument is a list of tool classes rather than a single tool name. This
		is for consistency with other function.

		:Parameters:
			tool_cls
				The tool class - not name as a string - to be installed.

		For example::

			installer.install_tool (MyToolClass)

		"""
		if (not hasattr (self.context, tool_cls.id)):
			portal = getToolByName (self.context, 'portal_url').getPortalObject()
			portal.manage_addProduct[self.name].manage_addTool (
				tool_cls.meta_type, None)
			self.log ('Installed tool %s.' % tool_cls.meta_type)
		else:
			self.log ("Couldn't add tool %s as it was already present." %
				tool_cls.meta_type)


	def install_product_properties (self, props=[], sheet_name=None):
		"""
		Create a sheet and properties for the product.

		Note that if the property sheet already exists, it is left in place. If
		no sheet name is given, it is generated from the product name. It is
		always stored as member `sheet_name`.

		:Parameters:
			props
				A sequence of dictionaries of form {name, value, type}. If
				``value`` is not supplied, it is set to blank.
			sheet_name
				The sheet to be created. If no name is supplied, it is created as
				``PRODUCTNAME_properties``.
			
		For example::
		
			_props = (
				{
					'name': 'map_names',
					'seed': [],
					'type': 'lines',
				},
			)
			installer.install_product_properties (_props, 'myproduct_properties')
		
		"""
		# TODO: assert prop types?
		if (sheet_name is None):
			sheet_name = self.id_prefix + "_properties"
		self.sheet_name = sheet_name
		from ezplone import prop
		prop.create_property_sheet (self.context, self.sheet_name, self.name)
		for item in props:
			prop.set_properties (self.context, self.sheet_name, [
				{
					'name': item['name'],
					'value': item.get ('value', ''),
					'type': item['type'],
				}
			], overwrite=True)
		self.log ('Installed site properties')


	def install_configlets (self, configlet_list):
		"""
		Add the configlets to the portal control panel.

		The configlet definition is a dictionary of configlet properties for
		setup. For example::

			configlets = (
				{
					'id'          : 'myproduct_prefs',
					'name'        : 'MyProduct Setup',
					'action'      : 'string:${portal_url}/myproduct_prefs',
					'condition'   : '',
					'category'    : 'Products',
					'visible'     : 1,
					'appId'       : 'MYPRODUCT',
					'permission'  : ManagePortal,
					'description' : 'Configure MyProduct',
					'imageUrl'    : 'myproduct_prefs.png',
				},
			)

			installer.install_configlets (configlets)

		"""
		# TODO: have specailised 'installPrefsConfiglet', 'installUserConfiglet'?
		configTool = getToolByName (self.context, 'portal_controlpanel', None)
		assert (configTool), "couldn't find portal_controlpanel for configlets"
		for conf in configlet_list:
			configTool.registerConfiglet (**conf)
			self.log ('Installed configlet %s.' % conf['id'])


	def install_workflow (self, workflow_id=None):
		"""
		Install customised workflow.

		"""
		if (workflow_id is None):
			workflow_id = self.id_prefix + "_workflow"
		self.workflow_id = workflow_id
		theWorkflowTool = getToolByName (self.context, 'portal_workflow')
		theWorkflowTool.manage_addWorkflow (
			id=self.workflow_id,
			workflow_type='%s (%s Workflow)' % (self.workflow_id, self.name),
		)
		self.log ('Added custom workflow %s.' % self.workflow_id)


### UNINSTALLER

class EasyUninstaller (_BaseEasyClass):
	"""
	Helper functions for deinstallation, wrapped in a class.

	This should be instantiated in a products ``deinstall`` method, and methods
	called as needed.

	"""
	def __init__ (self, context, product_name, id_prefix=None):
		"""
		Class ctor.

		This prepares the class for calling methods. If id_prefix (which could
		be used later for automatic construction of object names) is not
		supplied, it will be constructed from cleaning up the product name.

		:Parameters:
			context
				Any site object suitable for obtaining context.
			product_name
				Self descriptive.
			id_prefix
				For building configlet (etc.) names.

		For example::

			uninstaller = (page, "MyProduct", 'mypr')

		"""
		_BaseEasyClass.__init__ (self, context, product_name, id_prefix)


	def uninstall_configlets (self, configlet_list):
		"""
		Remove product configlets from the portal control panel.

		"""
		configTool = getToolByName (self.context, 'portal_controlpanel', None)
		assert (configTool), \
			"can't find portal_controlpanel for removing configlets"
		for conf in configlet_list:
			configTool.unregisterConfiglet(conf['id'])
			self.log ('Removed configlet %s' % conf['id'])


	def uninstall_tool (self, tool_cls):
		"""
		Remove product tools from the portal control panel.

		"""
		theActionTool = getToolByName (self.context, 'portal_actions', None)
		assert (theActionTool), "can't find portal_actions for removing tools"
		theActionTool.deleteActionProvider (tool_cls.id)
		self.log ('Removed product tools.')



### MAIN ###

if __name__ == "__main__":
	_test()


### END ###
