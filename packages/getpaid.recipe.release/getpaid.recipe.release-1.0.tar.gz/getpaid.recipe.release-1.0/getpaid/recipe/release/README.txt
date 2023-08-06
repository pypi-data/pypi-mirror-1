Tested with
===========

A buildout using plone 3.1

Required options
================

You need to have the following find-links so that the getpaid recipe can find the packages.

find-links=

- http://getpaid.googlecode.com/files/hurry.workflow-0.9.1-getpaid.tar.gz
- http://getpaid.googlecode.com/files/yoma.batching-0.2.1-getpaid.tar.gz
- http://getpaid.googlecode.com/files/zc.resourcelibrary-0.5-getpaid.tar.gz
- http://getpaid.googlecode.com/files/zc.table-0.5.1-getpaid.tar.gz
- http://download.zope.org/distribution/ssl-for-setuptools-1.10

Make sure also to add unzip = true into your [buildout] part, so that you don't have problems with packages being zip safe.

Supported options
=================

The recipe supports the following option:

addpackages=

You can choose the "extra" packages you want to use with the "addpackages" option. The names listed correspond to the names of the packages. So you could do addpackages=getpaid.discount


What to add in your buildout
============================

We are assuming you have your own buildout created.

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = 
    ...     yourownparts
    ...     getpaid
    ...
    ... unzip = true
    ...
    ... [getpaid]
    ... recipe = getpaid.recipe.release
    ...
    ... addpackages=
    ...     getpaid.paymentech
    ...     getpaid.discount
    ... 
    ... find-links=
    ...     http://getpaid.googlecode.com/files/hurry.workflow-0.9.1-getpaid.tar.gz
    ...     http://getpaid.googlecode.com/files/yoma.batching-0.2.1-getpaid.tar.gz
    ...     http://getpaid.googlecode.com/files/zc.resourcelibrary-0.5-getpaid.tar.gz
    ...     http://getpaid.googlecode.com/files/zc.table-0.5.1-getpaid.tar.gz
    ...     http://download.zope.org/distribution/ssl-for-setuptools-1.10
    ...
    ... [instance]
    ... eggs = 
    ...     yourowneggs
    ...     ${getpaid:eggs}
    ...
    ... [zope2]
    ... (...)
    ... fake-zope-eggs = true
    ... skip-fake-eggs = 
    ... additional-fake-eggs = ZODB3
    ... """)


In resume:

- you add the getpaid part
- in the getpaid part, you can choose the "extra" packages you want to use with the "addpackages" option
- by default, the following packages are installed: ore.viewlet, getpaid.core, Products.PloneGetPaid, getpaid.wizard, getpaid.nullpayment, five.intid, hurry.workflow, simplejson, yoma.batching, zc.resourcelibrary and zc.table
- then you will have to run bin/buildout, start your instance and quickinstall PloneGetPaid
