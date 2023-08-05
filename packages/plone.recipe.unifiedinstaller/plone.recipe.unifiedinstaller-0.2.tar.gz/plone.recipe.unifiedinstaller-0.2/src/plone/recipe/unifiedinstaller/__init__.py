import os, re, shutil, logging
import zc.buildout
import zc.recipe.egg


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


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

        paths = [ self.writeTemplate('admin_text', 'adminPassword.txt') ]
        os.chmod(paths[0], 0600)

        if options.has_key('zeoserver') and options.has_key('clients'):
            paths = paths + self.writeZeoScripts()

        return paths


    def update(self):
        options = self.options

        paths = [ self.writeTemplate('admin_text', 'adminPassword.txt') ]
        os.chmod(paths[0], 0600)

        if options.has_key('zeoserver') and options.has_key('clients'):
            paths = paths + self.writeZeoScripts()

        return paths


    def writeTemplate(self, template, filename):
        options = self.options
        
        file_storage = options.get('file-storage', os.path.sep.join(('var', 'filestorage', 'Data.fs',)))
        file_storage = os.path.join(options['location'], file_storage)
        file_storage_dir = os.path.dirname(file_storage)

        script = read(template) % dict(bin_dir = options['bin-directory'],
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
            self.writeScript('mkplonesite.py', 'mkPloneSite.py'),
            self.writeScript('startcluster_template', 'startcluster.sh'),
            self.writeScript('shutdown_template', 'shutdowncluster.sh'),
            self.writeScript('restart_template', 'restartcluster.sh'),
            self.writeScript('status_template', 'clusterstatus.sh'),
        ]
