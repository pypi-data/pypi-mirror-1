"""
Options are as follows:

The id of the plone site to be created.
    --site-id=Plone
Replace any existing plone site named site-id. Defaults to off.
    --site-replace=off
The user to run the script as (needs to be a Manager at the root)
    --admin-user=admin
Add one --products argument per product you want to quickinstall when initially
creating the site.
    --products-initial=MyProductName
Add one --products argument per product you want to quickinstall upon
every run of buildout.
    --products=MyProductName
Add one --profiles-initial argumanet per profile you want to run after the
quickinstall has run when initially creating the site.
    --profiles-inital=my.package:default
Add one --profiles argument per profile you want to run after the
quickinstall has run each time the buildout has been run.
    --profiles=my.package:default
"""

from datetime import datetime
import transaction
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Testing import makerequest
from optparse import OptionParser
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException


now_str = datetime.now().strftime('%Y-%m-%d-%H%M%S')

parser = OptionParser()
parser.add_option(
    "-s",
    "--site-id",
    dest="site_id",
    default="Plone-%s" % now_str
)
parser.add_option(
    "-r",
    "--site-replace",
    dest="site_replace",
    default="off"
)
parser.add_option(
    "-u",
    "--admin-user",
    dest="admin_user",
    default="admin"
)
parser.add_option(
    "-p",
    "--products-initial",
    dest="products_initial",
    action="append",
    default=[]
)
parser.add_option(
    "-a",
    "--products",
    dest="products",
    action="append",
    default=[]
)
parser.add_option(
    "-g",
    "--profiles-initial",
    dest="profiles_initial",
    action="append",
    default=[]
)
parser.add_option(
    "-x",
    "--profiles",
    dest="profiles",
    action="append",
    default=[]
)

(options, args) = parser.parse_args()
site_id = options.site_id
site_replace = options.site_replace
admin_user = options.admin_user
# the madness with the comma is a result of product names with spaces
def getProductsWithSpace(opts):
    return [x.replace(',', '') for x in opts]
products = getProductsWithSpace(options.products)
profiles_initial = getProductsWithSpace(options.profiles_initial)
profiles = getProductsWithSpace(options.profiles)

TRUISMS = [
    'yes',
    'on',
    'true',
    'sure',
    'ok',
    '1',
]

def create(site_id, products):
    oids = app.objectIds()
    if site_id in oids:
        # XXX make the site_replace opt a Boolean, handle the TRUISM in
        # the recipe
        if site_replace.lower() in TRUISMS and hasattr(app, site_id):
            try:
                app.manage_delObjects([site_id,])
            except LinkIntegrityNotificationException:
                pass
            transaction.commit()
            print "Removed existing Plone Site"
            oids = app.objectIds()
        else:
            print "A Plone Site already exists and will not be replaced"
            return
    # actually add in Plone
    if site_id not in oids:
        factory = app.manage_addProduct['CMFPlone']
        factory.addPloneSite(site_id, create_userfolder=1)
        print "Added Plone Site"
    # install some products
    plone = getattr(app, site_id)
    if plone:
        products_initial = getProductsWithSpace(options.products_initial)
        print "Quickinstalling: %s" % products_initial
        qit = plone.portal_quickinstaller
        products_initial = set(products_initial)
        install_ids = set([x['id'] for x in qit.listInstallableProducts(skipInstalled=0)])
        install_products = install_ids.intersection(products_initial)
        if install_products:
            qit.installProducts(products=install_products, reinstall=True)
    # run GS profiles
    stool = plone.portal_setup
    print "Running profiles: %s" % profiles_initial
    for profile in profiles_initial:
        if not profile.startswith('profile-'):
            profile = "profile-%s" % profile
        stool.runAllImportStepsFromProfile(profile)
    # commit the transaction
    transaction.commit()
    print "Finished"

app = makerequest.makerequest(app)
# set up security manager
acl_users = app.acl_users
user = acl_users.getUser(admin_user)
if user:
    user = user.__of__(acl_users)
    newSecurityManager(None, user)
    print "Retrieved the admin user"
else:
    print "Retrieving admin user failed"

# create the plone site
create(site_id, products)
# run profiles or install products
if products or profiles:
    plone = getattr(app, site_id)
if products:
    print "Quick installing: %s" % products
    qit = plone.portal_quickinstaller
    products = set(products)
    install_ids = set([x['id'] for x in qit.listInstallableProducts(skipInstalled=0)])
    install_products = install_ids.intersection(products)
    if install_products:
        qit.installProducts(products=install_products, reinstall=True)
    transaction.commit()
if profiles:
    print "Running profiles: %s" % profiles
    stool = plone.portal_setup
    for profile in profiles:
        if not profile.startswith('profile-'):
            profile = "profile-%s" % profile
        stool.runAllImportStepsFromProfile(profile)
    transaction.commit()
noSecurityManager()
