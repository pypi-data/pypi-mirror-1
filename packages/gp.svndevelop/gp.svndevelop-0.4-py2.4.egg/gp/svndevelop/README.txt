=====================
gp.svndevelop package
=====================

.. contents::

What is gp.svndevelop ?
=======================

This package allow you to checkout some package and use them as developed
eggs with ``zc.buildout``.


Why ``zc.buildout`` sucks a bit ?
=================================

``zc.buildout`` fail When you specify a develop egg who does not exist::

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

A solution is to use this package as a ``zc.buildout`` extension and to provide
some svn urls in the ``svn-develop`` option::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... develop=../my.testing
  ... svn-develop=%s/my.testing/trunk#egg=my.testing
  ... parts=
  ... ''' % repository)

Then if you run ``buildout`` again, the package will be checkout from the
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

Notice that the develop option is set to the parent directory but the package
is not checked out in it. Why ? Well this is my arbitrary policy. I don't want
to have extra eggs out of my ``buildout`` environment. You can use the
``develop-dir`` option (see below) for this.

Using eggs in an existing directory
===================================

This extension is also a way to use an existing directory. Imagine you already
have the ``my.testing`` package in a directory::

  >>> ls(package_dir)
  -  LICENSE
  d  my
  -  setup...

Then you don't want to re-checkout. The solution is to provide a
``develop-dir``::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... develop=../my.testing
  ... develop-dir=%s
  ... svn-develop=%s/my.testing/trunk#egg=my.testing
  ... parts=
  ... ''' % (os.path.dirname(package_dir), repository))

And run ``buildout`` again::

  >>> print system(buildout)
  Develop: '/...Package/my.testing'

It works fine but now the package in the ``buildout`` dir is not used by
``buildout``::

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  my.testing
  d  parts

``buildout`` use the one in our ``develop-dir``::

  >>> cat(sample_buildout, 'develop-eggs', 'my.testing.egg-link')
  /...Package/my.testing
  .

If the package is not found in ``develop-dir``, it will be checkout::

  >>> rmdir(package_dir)
  >>> print system(buildout)
  A    my.testing/LICENSE
  A    my.testing/my
  A    my.testing/my/__init__.py
  A    my.testing/my/testing
  A    my.testing/my/testing/__init__.py
  A    my.testing/my/testing/README.txt
  A    my.testing/setup.py
  ...
  Develop: '/...Package/my.testing'

Of course you can put the ``develop-dir`` option in your
``~/.buildout/default.cfg``

Cleanup test::

  >>> import shutil
  >>> shutil.rmtree(os.path.join(sample_buildout, 'my.testing'))

Omit the develop directive
==========================

You can omit the develop option and get develop eggs directly from the
``svn-extend-develop`` one::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... svn-extend-develop=%s/my.testing/trunk#egg=my.testing
  ... parts=
  ... ''' % repository)

This will install the ``my.testing`` package as a develop egg::

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

Auto update develop directories
===============================

The extension will update develop directories if they already exist::

  >>> rmdir(sample_buildout, 'my.testing', 'my', 'testing')
  >>> print system(buildout)
  A    ...sample-buildout/my.testing/my/testing
  A    ...sample-buildout/my.testing/my/testing/__init__.py
  A    ...sample-buildout/my.testing/my/testing/README.txt
  ...
  Develop: '...sample-buildout/my.testing'


Develop eggs from existing parts
================================

Warning, use this option only if you know what you're doing. I think at this
time, I'm the only one to know until you've read the code ;)

The extension can scan eggs in parts and set them as develop::

  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... eggs=my.testing
  ... scan-eggs=true
  ... develop-dir=%s
  ... parts=
  ... ''' % os.path.dirname(package_dir))

The if you run ``buildout`` again, the develop egg is used::

  >>> print system(buildout)
  At revision 1.
  Develop: '/...Package/my.testing'

This will not work if a version is specified::


  >>> write('buildout.cfg','''
  ... [buildout]
  ... extensions=gp.svndevelop
  ... eggs=my.testing>=01
  ... scan-eggs=true
  ... develop-dir=%s
  ... parts=
  ... ''' % os.path.dirname(package_dir))
  >>> print system(buildout)

If scan-eggs exist, the extension will also try to set your recipes as develop
eggs.  
