=====================
gp.svndevelop package
=====================

.. contents::

What is gp.svndevelop ?
=======================

This package allow you to checkout some package and use them as developed
eggs with zc.buildout.


Why buildout sucks a bit ?
==========================

Buildout fail When you specify a develop egg who does not exist::

  >>> cd(sample_buildout)

  >>> write('buildout.cfg','''
  ... [buildout]
  ... develop=my.testing
  ... parts=
  ... ''')

  >>> print system(buildout)
  Develop: '/...buildout/my.testing'
  Traceback (most recent call last):
  ...
  IOError: [Errno 2] No such file or directory: '/...buildout/my.testing'
  ...

A solution: a simple checkout before anything else
==================================================

A solution is to use this package as a buildout extension and to provide some
svn urls in the svn-develop option::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... develop=my.testing
  ... svn-develop=%s/my.testing/trunk#egg=my.testing
  ... parts=
  ... ''' % repository)

Then if you run buildout again, the package will be checkout from the
repository::

  >>> print system(buildout)
  A    my.testing/LICENSE
  A    my.testing/my
  A    my.testing/my/__init__.py
  A    my.testing/my/testing
  A    my.testing/my/testing/__init__.py
  A    my.testing/my/testing/README.txt
  A    my.testing/setup.py
  ...
  Develop: '/...buildout/my.testing'

Using eggs in an existing directory
===================================

This extension is also a way to use an existing directory. Imagine you already
have the my.testing package in a directory::

  >>> ls(package_dir)
  -  LICENSE
  d  my
  -  setup...


Then you don't want to re-checkout. The solution is to provide a develop-dir::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... develop=my.testing
  ... develop-dir=%s
  ... parts=
  ... ''' % os.path.dirname(package_dir))

We can delete the checkout::

  >>> import shutil
  >>> shutil.rmtree(os.path.join(sample_buildout, 'my.testing'))

And run buildout again::

  >>> print system(buildout)
  Develop: '/...Package/my.testing'

It works fine but now the package is not in the buildout dir::

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  parts

Buildout use the one in our develop-dir::

  >>> cat(sample_buildout, 'develop-eggs', 'my.testing.egg-link')
  /...Package/my.testing
  .

Of course you can put the develop-dir option in your ~/.buildout/default.cfg

Omit the develop directive
==========================

You can omit the develop option and get develop eggs directly from the
svn-develop one::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... svn-develop=%s/my.testing/trunk#egg=my.testing
  ... parts=
  ... ''' % repository)

This will install the my.testing package as a develop egg::

  >>> print system(buildout)
  A    my.testing/LICENSE
  A    my.testing/my
  A    my.testing/my/__init__.py
  A    my.testing/my/testing
  A    my.testing/my/testing/__init__.py
  A    my.testing/my/testing/README.txt
  A    my.testing/setup.py
  ...
  Develop: '/...buildout/my.testing'


