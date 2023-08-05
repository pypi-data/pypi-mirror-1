from setuptools import setup, find_packages
import sys, os

name = "plone.recipe.deliverance"

version = '1.0b1'

setup(name=name,
      version=version,
      description="Install Deliverance",
      long_description="""\
Install the Deliverance proxy as an out-of-process transform.

This will probably only work on Unix systems with Bash shells. Tested 
primarily on OS X.

Add this to your buildout.cfg::

 [buildout]
 parts = deliverance

 [deliverance]
 recipe = plone.recipe.deliverance

This will download the Deliverance egg and its dependencies. It will also 
fetch and build libxml2 and libxslt from source. 

A new script will be written to the top-level 'bin' directory, called 
'deliverance' (taken from the name of thes buildout part). This sets up the 
environment appropriately and then starts the Deliverance daemon.

A Deliverance configuration file will be generated in 
deliverance/deliverance-proxy.ini. You can edit this - it will not be 
overridden when buildout is re-run, although it will be re-generated if it is
removed.

The files deliverance/rules/rules.xml and deliverance/rules/standardrules.xml
contain a example rules. An example theme is installed in 
deliverance/static/theme.html. If you change these, they will not be
overridden. If you remove the 'rules' and 'static' directories, they will
be recreated with these example files, otherwise they are left alone.

Other possible options for the deliverance section include:

 eggs -- Any other eggs you may want to install. By default, this is just the
  Deliverance egg (and its dependencies, of course).
  
 scripts -- Any console scripts to install. By default, this includes
  'paster'. Set this an empty value to disable script generation (for example
  if another recipe is installing 'paster')
  
 libxml2_url -- A URL from which the libxml2 sources can be downloaded. If you 
   do not want libxml2 to be installed, set this to an empty value. Otherwise,
   a default "known good" version is downloaded and compiled.
   
 libxslt_url -- A URL from which libxslt sources can be downloaded. Again,
   set this to an empty value to avoid compiling libxslt.

The following options affect the generated deliverance-proxy.ini configuration
file.
   
 debug -- Set to true or false to enable or disable deliverance error 
   reporting.
   
 host -- The host to bind the Deliverance process to. By default, it will
   listen to any IP address.
   
 port -- The port for the Deliverance process. Defaults to 8000.
 
 proxy -- The URL being proxied by Deliverance. Defaults to 
   http://localhost:8080.
   
 theme -- A URI for the theme. To specify a path relative to the 'deliverance'
   prefix it with "/.deliverance/". The default is 
   /.deliverance/static/theme.html
   
 rules -- A URI for the rules file. Again, use "/.deliverance" to specify a
   path relative to the 'deliverance' directory. The default is
   /.deliverance/rules/rules.xml
   
 rewrite -- Rewrite all headers and internal links to appear to come from the 
   proxied server. Defaults to 'true'.
   
 transparent -- Do not rewrite the Host header when passing on a request.
   Defaults to 'true'.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Framework :: Buildout",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Programming Language :: Python",
          ],
      keywords='',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/collective/buildout/plone.recipe.deliverance',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires = [
        'zc.buildout', 
        'setuptools', 
        'zc.recipe.egg',
      ],
      dependency_links = [
        'http://download.zope.org/distribution/'
      ],
      entry_points = {
        'zc.buildout': ['default = %s:Recipe' % name]},
      )
