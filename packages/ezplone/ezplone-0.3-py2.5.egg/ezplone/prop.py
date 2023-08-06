#!/usr/bin/env python
# encoding: utf-8
"""
Assorted utilities for handling properties.

These functions wrap the more verbose CMF functions for setting and getting
properties in single, terse calls. They also catch errors, which is handy for
development. Within ezplone they are called from the installer, but are placed
as standalone function here so they can be used outside the installation
process.

"""

__docformat__ = "restructuredtext en"


## CONSTANTS & DEFINES: ###

### IMPORTS ###

from Products.CMFCore.utils import getToolByName

__all__ = [
	'create_property_sheet',
	'get_property_sheet',
	'set_properties',
	'get_property',
]


### IMPLEMENTATION ###

def create_property_sheet (context, sheet_id, product_name=None):
	"""
	Creates a property sheet.

	Throws if sheet is already present.

	:Parameters:
		context
			Any site object suitable for obtaining context.
		sheet_id
			A string giving the name of the property sheet.
		product_name
			Self descriptive, used only to usefully name sheet.

	:Returns:
		The newly created sheet.

	"""
	# TODO: overwrite option if sheet is already present.
	# TODO: harmonize language between new, set and add
	if (not hasattr (context.portal_properties, sheet_id)):
		context.portal_properties.addPropertySheet (sheet_id, '%s properties' %
			product_name or sheet_id)
	return get_property_sheet (context, sheet_id)


def get_property_sheet (context, sheet_id):
	"""
	Return the named property sheet.

	:Parameters:
		context
			Any site object suitable for obtaining context.
		sheet_id
			A string giving the name of the property sheet.

	For example::

		theSheet = get_property_sheet (page, 'revi_props')

	"""
	theProps = getattr (context.portal_properties, sheet_id, None)
	assert (theProps), "couldn't get property sheet %s" % sheet_id
	return theProps


def set_properties (context, sheet_id, props_list, overwrite=True):
	"""
	Initialise the sheet with the given properties.

	:Parameters:
		context
			Any site object suitable for obtaining context.
		sheet_id
			A string giving the name of the property sheet.
		props_list
			A sequence of dicts with name, type, value
		overwrite : boolean
			If true (the default), existing properties are over-written.

	"""
	# TODO: check type of properties?
	# TODO: allow passing of existing sheet
	theProps = get_property_sheet (context, sheet_id)
	for prop in props_list:
		if (theProps.hasProperty (prop['name'])):
			if (overwrite):
				theProps.manage_changeProperties ({prop['name']: prop['value']})
		else:
			theProps._setProperty (prop['name'], prop['value'], prop['type'])


def get_property (context, sheet_id, prop_name):
	"""
	Return the value of the given property.

	:Parameters:
		context
			Any site object suitable for obtaining context.
		sheet_id
			A string giving the name of the property sheet.
		prop_name
			Property to be returned.

	:Returns:
		The value of the given property.

	"""
	# TODO: allow passing of existing sheet?
	# TODO: check that prop exists?
	theProps = get_property_sheet (context, sheet_id)
	return theProps.get_property (prop_name)



### MAIN ###

if __name__ == "__main__":
	_test()


### END ###
