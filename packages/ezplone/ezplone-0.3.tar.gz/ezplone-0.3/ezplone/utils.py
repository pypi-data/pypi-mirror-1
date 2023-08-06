#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Assorted utilities for working with Plone, mostly from debug prompt.

Note that to sucessfully create content programatically from the debug prompt,
there is a magic preamble that must be called, wrapping the app in a request
and giving you the right permissions::

	from Testing.makerequest import makerequest
	app = makerequest(app)
	from ezplone import utils
	utils.switch_to_admin (app)

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

#__all__ = [
#	'TagAttrib',
#]


### CONSTANTS & DEFINES ###

### IMPLEMENTATION ###

def create_obj (par_folder, new_type, new_id, edit={}):
	"""
	Creates a new object of the type, edits and returns it.
	
	:Parameters:
		par_folder
			Folder to create content in.
		new_type : string
			Name of new object type to create, e.g. 'Document'
		new_id
			Id to give the new object.
		edit
			A series of fields and values to change in the new object.
			
	:Returns:
		The new object.
			
	Note that 'Pages' are created via 'Document' and that the body of a Page
	is accessed by editing 'text' and 'format' (e.g. 'text/html'). Note also
	that we no checking for id collision.
	
	"""
	# TODO: option to use constructcontent to bypass restrictions?
	# assert (type (new_id) == type ('')) # unicode
	par_folder.invokeFactory (type_name=new_type, id=new_id)
	new_obj = par_folder[new_id]
	if (edit):
		new_obj.edit (**edit) 
	new_obj.reindexObject()
	return new_obj
	
	
def switch_to_user (app, username):
	"""
	Change to this user and their permissions.
	"""
	# app must be site
	from AccessControl.SecurityManagement import newSecurityManager
	user = context.acl_users.getUserById (username)
	newSecurityManager (None, user)


def switch_to_admin (app):
	"""
	Change to the admin user and their permissions.
	"""
	# app must be site
	admin = app.acl_users.getUserById ('admin') 
	admin = admin.__of__(app.acl_users) 
	from AccessControl.SecurityManagement import newSecurityManager 
	newSecurityManager (None, admin)


def commit_transaction():
	"""
	Commit the current changes.
	
	Strictly speaking this is so simple that its hardly worth writing this
	function, but in practice it is useful to have a simple, readable and
	obvious one-liner.
	
	"""
	import transaction
	transaction.commit()



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ###################################################################
