import os
import glob
import logging

from subprocess import Popen, PIPE

# The function below (write_to_cmd) copied from bzrlib.patch
_do_close_fds = True
if os.name == 'nt':
    _do_close_fds = False

def write_to_cmd(args, input=""):
    """Spawn a process, and wait for the result

    If the process is killed, an exception is raised

    :param args: The command line, the first entry should be the program name
    :param input: [optional] The text to send the process on stdin
    :return: (stdout, stderr, status)
    """
    process = Popen(args, bufsize=len(input), stdin=PIPE, stdout=PIPE,
                    stderr=PIPE, close_fds=_do_close_fds)
    stdout, stderr = process.communicate(input)
    status = process.wait()
    if status < 0:
        raise Exception("%s killed by signal %i" % (args[0], -status))
    return stdout, stderr, status

class Recipe:
    """zc.buildout recipe for applying patches to a buildout
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.verbosity = int(buildout['buildout'].get('verbosity', 0))

    def update(self):
        pass

    def install(self):
        parts = []

        patch_cmd = self.options.get('patch-binary', 'patch').strip()
        patch_options = self.options.get('patch-options', '-p0 -f').split()
        patches = map(os.path.normpath, 
                      self.options.get('patches', '').splitlines())
        target = map(os.path.normpath, 
                     self.options.get('target', '').splitlines())

        all_patches = []
        all_targets = {}

        for p in map(glob.glob, patches):
            all_patches.extend(p)
            
        for t in target:
            for d in os.listdir(t):
                full = os.path.join(t, d)
                if os.path.isdir(full):
                    all_targets[d] = full
                    
        patch_by_prefix = {}
        for p in all_patches:
            prefix = os.path.basename(p).split('-')[0]
            prefix = prefix.lower()
            got = patch_by_prefix.setdefault(prefix, [])
            got.append(p)

        for t, full in all_targets.items():
            for p in patch_by_prefix.get(t.lower(), ()):
                target = full
                p_options = patch_options[:]
                self.logger.info('Patching: %s\n  with: %s', target, p)
                target = os.path.dirname(target)
                for i in range(3):
                    if i == 1 and status:
                        p_options[p_options.index('-f')] = '-t'
                    if i == 2:
                        p_options[p_options.index('-t')] = '-f'
                    command = [patch_cmd] + p_options + ['-d', target]
                    stdout, stderr, status = write_to_cmd(command, open(p, 'rb').read())
                    if self.verbosity > 20 or (i > 1 and status):
                        self.logger.info('Running command: %s', ' '.join(command))
                        if stderr:
                            self.logger.error(stderr)
                        if stdout:
                            self.logger.info(stdout)
                        self.logger.info('Command returned status: %s', status)
                    if not status and not i == 1:
                        break
        return ()

    update = install
