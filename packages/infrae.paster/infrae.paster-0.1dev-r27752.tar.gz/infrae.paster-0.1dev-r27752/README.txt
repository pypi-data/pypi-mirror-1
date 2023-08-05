infrae.paster
=============

Create a part using paster. For example::

  [cms]
  recipe = infrae.paster
  template = plone3_buildout
  zope2_install = 
  plone_products_install = 
  zope_user = admin
  zope_password = admin
  http_port = 8080
  debug_mode = off
  verbose_security = off

The ``template`` option defines which paster template to use. Others
options are the one used by the template.


Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.paster/trunk#egg=infrae.paster-dev>`_.
