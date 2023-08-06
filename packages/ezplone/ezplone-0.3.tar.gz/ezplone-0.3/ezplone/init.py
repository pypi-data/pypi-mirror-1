#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper class for product initialisation.

This defines a class to be created and called in the initialise function of a
products top-level __init__.py file. It handles the necessary set-up and
initialisation for products types and tools. For example::

	from ezplone import EasyInitialiser  
	initer = EasyInitialiser (context, myconfig.PRODUCT_NAME)
	initer.initContent (mypermissions.ADD_PERMISSION)
	initer.initTools ([MyTool], 'my_tool.png')

"""

__docformat__ = "restructuredtext en"


### IMPORTS ###

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils

__all__ = [
	'EasyInitialiser',
]


### CONSTANTS & DEFINES ###

### INTERFACE ###

class EasyInitialiser (object):
	"""

	:Parameters:
		context
			Any object that can provide Zope context for contained methods.
		project_name
			The current product being initialised.

	For example::

		# in the products __init__.py
		def initialise (context):
			initer = EasyInitialiser (context, "MyProduct")

	"""
	def __init__ (self, context, project_name):
		self.context = context
		self.name = project_name

	def init_content (self, perm):
		"""

		For example::

			from mypermissions import ADD_PERMISSION
			initer.init_content (ADD_PERMISSION)

		"""
		content_types, constructors, ftis = process_types (listTypes (self.name),
			self.name)
		utils.ContentInit (self.name + ' Content', content_types=content_types,
			permission=perm, extra_constructors=constructors, fti=ftis,
		).initialize (self.context)

	def init_tools (self, tool_classes, tool_icon):
		"""

		Note that we don't include the product name in the TooInit call because
		it is now deprecated.

		:Parameters:
			tool_classes
				A tuple of tool classes to be initialised.
			tool_icon
				The image to appear with these tools in the ZMI.

		For example::

			import ReviTool
			theToolDict = {
				'cls': (ReviTool.ReviTool),
				'icon': 'revi_tool.png',
			}
			initer.initTool (theToolDict)

		"""
		utils.ToolInit (self.name + ' Tool',
			tools=tool_classes,
			icon=tool_icon,
		).initialize (self.context)


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ########################################################################
