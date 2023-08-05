import os, re, shutil, logging
import zc.buildout
import zc.recipe.egg

class Recipe:

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.options, self.name = buildout, options, name

        # logging.getLogger(self.name).info(buildout['buildout'])

        options['scripts'] = '' # suppress script generation.
        options['location'] = buildout['buildout']['directory']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        
        options.setdefault('shell-command', '/bin/sh')
        options.setdefault('sudo-command', '')

        zeoserver = options.get('zeoserver')
        if zeoserver is None:
            # look for server definitions in the buildout
            servers = [part for part in buildout.keys() if buildout[part].get('recipe', '') == 'plone.recipe.zope2zeoserver']
            if len(servers) == 1:
                options['zeoserver'] = servers[0]

        if options.get('zeoserver'):
            clients = options.get('clients')
            if clients is None:
                # look for client definitions in the buildout
                clients = [part for part in buildout.keys() if buildout[part].get('recipe', '') == 'plone.recipe.zope2instance']
                options['clients'] = '\n'.join( clients )
            options.setdefault('start-command', 'startcluster.sh')
            options.setdefault('stop-command', 'shutdowncluster.sh')
        else:
            options.setdefault('start-command', 'instance start')
            options.setdefault('stop-command', 'instance stop')

        options.setdefault('primary-port', '8080')


    def install(self):
        options = self.options

        paths = [ self.writeTemplate(admin_text, 'adminPassword.txt') ]
        os.chmod(paths[0], 0600)

        if options.has_key('zeoserver') and options.has_key('clients'):
            paths = paths + self.writeZeoScripts()

        return paths


    def update(self):
        options = self.options

        paths = [ self.writeTemplate(admin_text, 'adminPassword.txt') ]
        os.chmod(paths[0], 0600)

        if options.has_key('zeoserver') and options.has_key('clients'):
            paths = paths + self.writeZeoScripts()

        return paths


    def writeTemplate(self, template, filename):
        options = self.options
        
        file_storage = options.get('file-storage', os.path.sep.join(('var', 'filestorage', 'Data.fs',)))
        file_storage = os.path.join(options['location'], file_storage)
        file_storage_dir = os.path.dirname(file_storage)

        script = template % dict(bin_dir = options['bin-directory'],
                                  location = options['location'],
                                  zeoserver = options.get('zeoserver', ''),
                                  clients = ' '.join(options.get('clients', '').split()),
                                  shell_cmd = options['shell-command'],
                                  start_cmd = options['start-command'],
                                  stop_cmd = options['stop-command'],
                                  password = options['user'].split(':')[1],
                                  user = options['user'].split(':')[0],
                                  port = options['primary-port'],
                                  sudo_cmd = options['sudo-command'],
                                  file_storage = file_storage,
                                  file_storage_dir = file_storage_dir,)
        
        open(filename, 'w').write(script)

        return filename
        

    def writeScript(self, template, filename):
        options = self.options
        
        script_path = os.path.join(options['bin-directory'], filename)
        self.writeTemplate(template, script_path)
        os.chmod(script_path, 0755)
        return script_path


    def writeZeoScripts(self):
        return [
            self.writeScript(mkplonesite, 'mkPloneSite.py'),
            self.writeScript(startcluster_template, 'startcluster.sh'),
            self.writeScript(shutdown_template, 'shutdowncluster.sh'),
            self.writeScript(status_template, 'clusterstatus.sh'),
        ]



startcluster_template = """#!%(shell_cmd)s
#
# ZEO cluster startup script
#
if [ -e %(file_storage)s ]
then
	FIRST_TIME="N"
else
	FIRST_TIME="Y"
fi
echo 'Starting ZEO server...'
%(bin_dir)s/%(zeoserver)s start
sleep 1
if [ $FIRST_TIME = "Y" ]
then
	echo 'This is the first start of this instance.'
	echo 'Creating Data.fs and a Plone site.'
	echo 'We only need to do this once, but it takes some time.'
	echo 'Creating Plone site at /Plone in ZODB...'
	%(bin_dir)s/client1 run %(bin_dir)s/mkPloneSite.py 2>> %(location)s/var/log/firststart.log
fi
for client in %(clients)s
do
    sleep 1
    echo Starting $client
    %(bin_dir)s/$client start
done
"""

shutdown_template = """#!%(shell_cmd)s
#
# ZEO cluster shutdown script
#
for client in %(clients)s
do
    echo Stopping $client
    %(bin_dir)s/$client stop
    sleep 1
done
echo 'Stopping ZEO server...'
%(bin_dir)s/%(zeoserver)s stop
"""

restart_template = """#!%(shell_cmd)s
#
# ZEO cluster restart script
#
echo 'Restarting ZEO server...'
%(bin_dir)s/%(zeoserver)s restart
for client in %(clients)s
do
    sleep 1
    echo Restarting $client
    %(bin_dir)s/$client restart
done
"""

status_template = """#!%(shell_cmd)s
# Cluster Status Discovery

if [ ! -w %(file_storage)s ]; then
    echo "You lack the rights necessary to run this script; Try sudo $0"
    exit 1
fi

echo "ZEO Server:"
%(bin_dir)s/%(zeoserver)s status
for client in %(clients)s
do
    sleep 1
    echo $client
    %(bin_dir)s/$client status
done
"""


mkplonesite = """from sys import exit

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
"""


admin_text ="""Use the account information below to log into the Zope Management Interface
The account has full 'Manager' privileges.
 
  Username: %(user)s
  Password: %(password)s
 
Before you start Plone, you should review the settings in:
 
  %(location)s/buildout.cfg
 
Adjust the ports Plone uses before starting the site, if necessary,
and run %(bin_dir)s/buildout
to apply settings.
 
To start Plone, issue the following command in a terminal window:
 
  %(sudo_cmd)s %(bin_dir)s/%(start_cmd)s
 
To stop Plone, issue the following command in a terminal window:
 
  %(sudo_cmd)s %(bin_dir)s/%(stop_cmd)s

After starting, Zope should be available at http://localhost:%(port)s/
and Plone at http://localhost:%(port)s/Plone .
"""