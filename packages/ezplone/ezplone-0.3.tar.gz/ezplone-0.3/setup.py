from setuptools import setup, find_packages
import ezplone

def extract_desc (text):
	"""
	Extract descriptions from module docstring.
	
	Note: assumes Unix eolns in source and destination.
	"""
	brief = detailed = ''
	text = text.strip()
	if (text):
		doclines = text.split ('\n')
		doclines = [x.rstrip() for x in doclines]
		text = '\n'.join (doclines)
		sections = text.split ('\n\n')
		brief = sections[0]
		detailed = '\n'.join (sections[1:])
	return brief, detailed

brief, detailed = extract_desc (ezplone.__doc__)
print brief
print detailed

setup (
	name='ezplone',
	version=ezplone.__version__,
	description=brief,
	long_description=detailed,
	classifiers=[
		"Framework :: Plone",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: BSD License",
	],
	keywords='plone install product utilities debug',
	author='Paul-Michael Agapow',
	author_email='agapow@bbsrc.ac.uk',
	url='http://www.agapow.net/software/ezplone',
	license='BSD',
	packages=find_packages (exclude=[
		'ez_setup',
		'tests',
	]),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		'setuptools',
		# -*- Extra requirements: -*-
	],
	entry_points="""
		# -*- Entry points: -*-
	""",
)
