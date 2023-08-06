Options
=======

site-id
    The id of the Plone site that the script will create.  This will also be used to update the site once created.  Default: Plone

admin-user
    The id of an admin user that will be used as the 'Manager'.  Default: admin

products-initial
    A list of products to quickinstall just after initial site creation

profiles-inital
    A list of GenericSetup profiles to run just after initial site creation.  Profiles have the following format: <package_name>:<profile> (e.g. my.package:default)

products
    A list of products to quickinstall each time buildout is run

profiles
    A list of GenericSetup profiles to run each time buildout is run

instance
    The name of the instance that will run the script. Default: instance

zeoserver
    The name of the zeoserver part that should be used.  This is only required if you are using a zope/zeo setup. Default: not set

site-replace
    Replace any existing plone site named site-id. Default: false
