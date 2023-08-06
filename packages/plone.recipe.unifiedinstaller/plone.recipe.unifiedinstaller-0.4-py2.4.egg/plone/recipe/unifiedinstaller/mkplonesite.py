from sys import exit

import transaction

from AccessControl.SecurityManagement import \
    newSecurityManager, noSecurityManager

from Testing.makerequest import makerequest


app = makerequest(app)
admin_username='admin'

oids = app.objectIds()
pid = 'Plone'
if pid in oids:
    print "A Plone site already exists"
    exit(1)

acl_users = app.acl_users
user = acl_users.getUser(admin_username)
if user:
    user = user.__of__(acl_users)
    newSecurityManager(None, user)
    #print "Retrieved the admin user"
else:
    print "Retrieving admin user failed"
    exit(1)

factory = app.manage_addProduct['CMFPlone']
factory.addPloneSite(pid, title='Portal')
print "Added Plone"

transaction.commit()
noSecurityManager()

print "Finished adding Plone site"
