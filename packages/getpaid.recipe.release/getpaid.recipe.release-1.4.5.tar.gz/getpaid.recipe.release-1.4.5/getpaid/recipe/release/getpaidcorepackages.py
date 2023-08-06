import os, subprocess

class Software:
    """ general software """
    type = 'Software'

    name = None
    download_url = None
    archive_rename = None
    productdir_rename = None
    filename = None
    parent = None
    version = None

    destination = 'downloads'

    def __init__(self, name, download_url, productdir=None, archive_rename=None, version=None):
        self.name = name
        self.download_url = download_url
        self.productdir_rename = productdir
        self.archive_rename = archive_rename
        self.version = version

class PyModule(Software):
    """ python module """

    type = 'PyModule'
    destination = 'lib/python'

    def post_extract(self, destination, me):
        cwd=os.getcwd()
        me=me.split('/')[0]
        os.chdir(os.path.join(destination, me))
        res=subprocess.call(["python2.4", "setup.py", "install_lib",
            "--install-dir=%s" % destination])
        if res!=0:
            raise RuntimeError, "Failed to setup package"

        os.chdir(destination)
        subprocess.call(["rm", "-rf", me])
        os.chdir(cwd)

CHEESE_SOURCE = 'http://pypi.python.org/packages/source/'
GETPAID_SOURCE = 'http://getpaid.googlecode.com/files/'

# XXX NOTES
# gchecky and zc.authorizedotnet are installed by default

GETPAID_BASE_PACKAGES = [
    PyModule('ore.viewlet', CHEESE_SOURCE + 'o/ore.viewlet/ore.viewlet-0.2.1.tar.gz', version="0.2.1"),
    PyModule('getpaid.core', CHEESE_SOURCE + 'g/getpaid.core/getpaid.core-0.7.4.tar.gz', version="0.7.4"),
    PyModule('Products.PloneGetPaid', CHEESE_SOURCE + 'P/Products.PloneGetPaid/Products.PloneGetPaid-0.7.9.tar.gz', version="0.7.9"),
    PyModule('getpaid.wizard', CHEESE_SOURCE + 'g/getpaid.wizard/getpaid.wizard-0.3.tar.gz', version="0.3"),
    PyModule('getpaid.nullpayment', CHEESE_SOURCE + 'g/getpaid.nullpayment/getpaid.nullpayment-0.3.1.tar.gz', version="0.3.1"),
]

GETPAID_DEPENDENCIES = [
    PyModule('five.intid', CHEESE_SOURCE + 'f/five.intid/five.intid-0.2.0.tar.gz', version="0.3.0"),
    PyModule('hurry.workflow', GETPAID_SOURCE + 'hurry.workflow-0.9.1-getpaid.tar.gz', version="0.9.1-getpaid"),
    PyModule('simplejson', CHEESE_SOURCE + 's/simplejson/simplejson-2.0.3.tar.gz', version="2.0.3"),
    PyModule('yoma.batching', GETPAID_SOURCE + 'yoma.batching-0.2.1-getpaid.tar.gz', version="0.2.1-getpaid"),
    PyModule('zc.resourcelibrary', GETPAID_SOURCE + 'zc.resourcelibrary-0.5-getpaid.tar.gz', version="0.5-getpaid"),
    PyModule('zc.table', GETPAID_SOURCE + 'zc.table-0.5.1-getpaid.tar.gz', version="0.5.1-getpaid"),
]

GETPAID_OTHER_PACKAGES = {
    # payment processors
    'getpaid.authorizedotnet': PyModule('getpaid.authorizedotnet', CHEESE_SOURCE + 'g/getpaid.authorizedotnet/getpaid.authorizedotnet-0.3.1.tar.gz', version="0.3.1"),
    'getpaid.googlecheckout': PyModule('getpaid.googlecheckout', CHEESE_SOURCE + 'g/getpaid.googlecheckout/getpaid.googlecheckout-0.3.tar.gz', version="0.3"),
    'getpaid.ogone': PyModule('getpaid.ogone', CHEESE_SOURCE + 'g/getpaid.ogone/getpaid.ogone-0.3.tar.gz', version="0.3"),
    'getpaid.payflowpro': PyModule('getpaid.payflowpro', CHEESE_SOURCE + 'g/getpaid.payflowpro/getpaid.payflowpro-1.0b1.tar.gz', version="1.0b1"),
    'getpaid.paymentech': PyModule('getpaid.paymentech', CHEESE_SOURCE + 'g/getpaid.paymentech/getpaid.paymentech-0.3.tar.gz', version="0.3"),
    'getpaid.paypal': PyModule('getpaid.paypal', CHEESE_SOURCE + 'g/getpaid.paypal/getpaid.paypal-0.4.3.tar.gz', version="0.4.3"),
    'getpaid.pxpay': PyModule('getpaid.pxpay', CHEESE_SOURCE + 'g/getpaid.pxpay/getpaid.pxpay-0.3.tar.gz', version="0.3"),
    'getpaid.clickandbuy': PyModule('getpaid.clickandbuy', CHEESE_SOURCE + 'g/getpaid.clickandbuy/getpaid.clickandbuy-0.1.tar.gz', version="0.1"),
    # shipping
    'getpaid.flatrateshipping': PyModule('getpaid.flatrateshipping', CHEESE_SOURCE + 'g/getpaid.flatrateshipping/getpaid.flatrateshipping-0.2.tar.gz', version="0.2"),
    'getpaid.ups': PyModule('getpaid.ups', CHEESE_SOURCE + 'g/getpaid.ups/getpaid.ups-0.3.tar.gz', version="0.3"),
    # discount
    'getpaid.discount': PyModule('getpaid.discount', CHEESE_SOURCE + 'g/getpaid.discount/getpaid.discount-0.8.2.tar.gz', version="0.8.2"),
    # others
    'getpaid.formgen': PyModule('getpaid.formgen', CHEESE_SOURCE + 'g/getpaid.formgen/getpaid.formgen-0.2.3.tar.gz', version="0.2.3"),
    'getpaid.report': PyModule('getpaid.report', CHEESE_SOURCE + 'g/getpaid.report/getpaid.report-0.1.1.tar.gz', version="0.1.1"),
    'getpaid.warehouse': PyModule('getpaid.warehouse', CHEESE_SOURCE + 'g/getpaid.warehouse/getpaid.warehouse-0.3.tar.gz', version="0.3"),
    'getpaid.SalesforcePloneFormGenAdapter': PyModule('getpaid.SalesforcePloneFormGenAdapter', CHEESE_SOURCE + 'g/getpaid.SalesforcePloneFormGenAdapter/getpaid.SalesforcePloneFormGenAdapter-1.0b2.tar.gzg', version="1.0b2"),
}

GETPAID_PACKAGES = GETPAID_BASE_PACKAGES + GETPAID_DEPENDENCIES
