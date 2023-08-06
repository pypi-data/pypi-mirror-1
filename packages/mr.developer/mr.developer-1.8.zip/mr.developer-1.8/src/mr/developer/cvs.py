from mr.developer import common
import os
import subprocess

logger = common.logger

class CVSError(common.WCError):
    pass

class CVSWorkingCopy(common.BaseWorkingCopy):
    def cvs_command(self, source, command, **kwargs):
        name = source['name']
        path = source['path']
        url = source['url']
        cvs_root = source.get('cvs_root')
        
        self.output((logger.info, 'Running %s %r from CVS.' % (command, name)))
        cmd = ['cvs', command, '-Pf', '-d', name, url]
        if cvs_root:
            cmd[1:1] = ['-d', cvs_root]
        self.output((logger.debug, ' '.join(cmd)))

        ## because CVS can not work on absolute paths, we must execute cvs commands
        ## in parent directory of destination
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(path))

        try:
            cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = cmd.communicate()
        finally:
            os.chdir(old_cwd)
            
        if cmd.returncode != 0:
            raise CVSError('CVS %s for %r failed.\n%s' % (command, name, stderr))
        if kwargs.get('verbose', False):
            return stdout

    def checkout(self, source, **kwargs):
        name = source['name']
        path = source['path']
        update = self.should_update(source, **kwargs)
        if os.path.exists(path):
            if update:
                self.update(source, **kwargs)
            elif self.matches(source):
                self.output((logger.info, 'Skipped checkout of existing package %r.' % name))
            else:
                raise CVSError(
                    'Source URL for existing package %r differs. '
                    'Expected %r.' % (name, source['url']))
        else:
            return self.cvs_command(source, 'checkout', **kwargs)

    def matches(self, source):
        name = source['name']
        path = source['path']
        
        repo_file = os.path.join(path, 'CVS', 'Repository')
        if not os.path.exists(repo_file):
            raise CVSError('Can not find CVS/Repository file in %s.' % path)
        repo = open(repo_file).read().strip()        
        
        cvs_root = source.get('cvs_root')
        if cvs_root:
            root_file = os.path.join(path, 'CVS', 'Root')
            root = open(root_file).read().strip()            
            if cvs_root != root:
                return False
        
        return (source['url'] == repo)

    def status(self, source, **kwargs):
        name = source['name']
        path = source['path']
        
        ## because CVS can not work on absolute paths, we must execute cvs commands
        ## in parent directory of destination
        old_cwd = os.getcwd()
        os.chdir(path)
        try:
            cmd = subprocess.Popen(
                ['cvs', '-q', '-n', 'update'], cwd=path, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = cmd.communicate()
        finally:
            os.chdir(old_cwd)
        
        status = 'clean'
        for line in stdout:
            if line[0] == 'C':
                ## there is file with conflict
                status = 'conflict'
                break
            if line[0] in ('M', '?', 'A', 'R'):
                ## some files are localy modified
                status = 'modified'
                
        if kwargs.get('verbose', False):
            return status, stdout
        else:
            return status

    def update(self, source, **kwargs):
        name = source['name']
        path = source['path']
        if not self.matches(source):
            raise CVSError(
                "Can't update package %r, because its URL doesn't match." %
                name)
        if self.status(source) != 'clean' and not kwargs.get('force', False):
            raise CVSError(
                "Can't update package %r, because it's dirty." % name)
        return self.cvs_command(source, 'update', **kwargs)

common.workingcopytypes['cvs'] = CVSWorkingCopy
