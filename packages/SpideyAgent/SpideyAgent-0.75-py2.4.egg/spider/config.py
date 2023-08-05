# The settings in this file should not vary depending on the deployment
# environment. devcfg.py and prodcfg.py are the locations for
# the different deployment settings. Settings in this file will
# be overridden by settings in those other files.

# The commented out values below are the defaults

# VIEW

# which view (template engine) to use if one is not specified in the
# template name
# tg.defaultview = "kid"

# kid.outputformat="html"
# kid.encoding="utf-8"

# The sitetemplate is used for overall styling of a site that
# includes multiple TurboGears applications
# tg.sitetemplate="<packagename.templates.templatename>"

# Allow every exposed function to be called as json,
# tg.allow_json = False

# Set to True if you'd like all of your pages to include MochiKit
# tg.mochikit_all = False



# VISIT TRACKING
# Each visit to your application will be assigned a unique visit ID tracked via
# a cookie sent to the visitor's browser.
# --------------

# Enable Visit tracking
# visit.on=False

# Number of minutes a visit may be idle before it expires.
# visit.timeout=20

# The name of the cookie to transmit to the visitor's browser.
# visit.cookie.name="tg-visit"

# Domain name to specify when setting the cookie (must begin with . according to
# RFC 2109). The default (None) should work for most cases and will default to
# the machine to which the request was made. NOTE: localhost is NEVER a valid
# value and will NOT WORK.
# visit.cookie.domain=None

# Specific path for the cookie
# visit.cookie.path="/"



# IDENTITY
# General configuration of the TurboGears Identity management module
# --------

# Switch to turn on or off the Identity management module
# identity.on=False

# [REQUIRED] URL to which CherryPy will internally redirect when an access
# control check fails. If Identity management is turned on, a value for this
# option must be specified.
# identity.failure_url=None

# The IdentityProvider to use -- defaults to the SqlObjectIdentityProvider which
# pulls User, Group, and Permission data out of your model database.
# identity.provider="sqlobject"

# The names of the fields on the login form containing the visitor's user ID
# and password. In addition, the submit button is specified simply so its
# existence may be stripped out prior to passing the form data to the target
# controller.
# identity.form.user_name="user_name"
# identity.form.password="password"
# identity.form.submit="login"

# What sources should the identity provider consider when determining the
# identity associated with a request? Comma separated list of identity sources.
# Valid sources: form, visit, http_auth
# identity.source="form,http_auth,visit"


# SqlObjectIdentityProvider
# Configuration options for the default IdentityProvider
# -------------------------

# The classes you wish to use for your Identity model. Leave these commented out
# to use the default classes for SqlObjectIdentityProvider. Or set them to the
# classes in your model. NOTE: These aren't TG_* because the TG prefix is
# reserved for classes created by TurboGears.
# identity.soprovider.model.user="spider.model.User"
# identity.soprovider.model.group="spider.model.Group"
# identity.soprovider.model.permission="spider.model.Permission"

# The password encryption algorithm used when comparing passwords against what's
# stored in the database. Valid values are 'md5' or 'sha1'. If you do not
# specify an encryption algorithm, passwords are expected to be clear text.
#
# The SqlObjectProvider *will* encrypt passwords supplied as part of your login
# form, but it is *your* responsibility to make certain the database contains
# passwords encrypted using this algorithm. To make life easier you can call
#     turbogears.identity.current_provider.encrypt_password( pw )
# to encrypt a password using the algorithm of the current provider.
# identity.soprovider.encryption_algorithm=None

path("/static")
static_filter.on = True
static_filter.dir = absfile("spider", "static")

path("/favicon.ico")
static_filter.on = True
static_filter.file = absfile("spider", "static/images/favicon.ico")
          
