Tested with
===========

A buildout using plone 3.1

Required options
================

Make sure to add unzip = true into your [buildout] part, so that you don't have problems with packages being zip safe.

Supported options
=================

The recipe supports the following option:

addpackages=

You can choose the "extra" packages you want to use with the "addpackages" option. The names listed correspond to the names of the packages. So you could do addpackages=getpaid.discount

Available packages:

* getpaid.authorizedotnet
* getpaid.clickandbuy
* getpaid.formgen
* getpaid.googlecheckout
* getpaid.ogone
* getpaid.payflowpro
* getpaid.paymentech
* getpaid.paypal
* getpaid.pxpay
* getpaid.flatrateshipping
* getpaid.ups
* getpaid.discount
* getpaid.report
* getpaid.warehouse
* getpaid.SalesforcePloneFormGenAdapter

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
