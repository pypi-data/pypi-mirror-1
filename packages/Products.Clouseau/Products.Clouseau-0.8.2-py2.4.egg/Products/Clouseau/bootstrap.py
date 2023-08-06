# this is the first code that is run by a session
from AccessControl.SecurityManagement import newSecurityManager
from zope.app.component.hooks import setSite 
from Testing.makerequest import makerequest
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

app = transaction_manager.beginAndGetApp()
# login the current user
portal = getToolByName(self, "portal_url").getPortalObject()
acl_users = portal.acl_users

uid = acl_users.getUserById(userid)
if uid:
    user = uid.__of__(acl_users)
    newSecurityManager(None, user)

response_output = StringIO()
app = makerequest(app, stdout=response_output)
try:
    setSite(portal)
except AttributeError:
    # Plone 2.5 sites do not have a site manager
    pass

# context is added in the new_namespace
if context:
    context = app.unrestrictedTraverse(context, None)
    if context is None:
        del context
else:
    # not needed
    del context

# clean out variables
del uid
del acl_users
del self
del transaction_manager
del userid
del StringIO
del makerequest
del newSecurityManager
del setSite
del getToolByName
