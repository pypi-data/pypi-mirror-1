import os
import subprocess
import logging
import zc.buildout

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(name)
        
        self.base_dir = buildout['buildout']['directory']
        self.parts = 'parts'
        self.options['location'] = os.path.join(self.base_dir, self.parts, self.name)
        
    def install(self):
        base_location = self.base_dir
        location = os.path.join(base_location,self.parts)
        if not os.path.exists(location):
            os.makedirs(location)

        for url, path in self.urls():
            abs_path = os.path.join(location, path)
            self.logger.info(path)
            self.command('bzr branch %s %s' % (url, abs_path))
        
        return os.path.join(base_location, self.parts, self.name)

    def update(self):
        # No updates when offline
        if self.buildout['buildout'].get('offline') == 'true':
            return

        base_location = self.base_dir
        location = os.path.join(base_location,self.parts)

        for url, path in self.urls():
            abs_path = os.path.join(location, path)
            self.logger.info(path)
            self.command('bzr pull', abs_path)

    def command(self, cmd, working_dir=None):
        if working_dir is not None:
            old_cwd = os.getcwd()
            os.chdir(working_dir)
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(
            cmd, shell=True, stdout=output)

        if working_dir is not None:
            os.chdir(old_cwd)
        assert command.wait() == 0

    def urls(self):
        for line in self.options['urls'].splitlines():
            if line:
                try:
                    url, target = line.split()
                except ValueError:
                    raise zc.buildout.UserError('Invalid URL specification: ' + line)
                else:
                    yield url, target


def uninstall(name, options):
    # Check if there are modifications before buildout removes everything
    return #FIXME: we can't check the real location from here
    location = options['location']
    old_cwd = os.getcwd()

    try:
        for f in os.listdir(location):
            branch = os.path.join(location, f)
            os.chdir(branch)
            command = subprocess.Popen('bzr status',
                                       shell=True, stdout=subprocess.PIPE)
            assert command.wait() == 0
            output = command.stdout.read()
            if output.strip(): # there are changes
                raise zc.buildout.UserError('Uncommitted changes:\n' + output)
    finally:
        os.chdir(old_cwd)
