"""
Post setup operations
"""

import sys, os, os.path, shutil


class PostSetup(object):
    """
    I do post-setup file copying with equivalent user and group access
    permissions.
    """
    def __init__(self, user, group):
        self.user, self.group = user, group

    def _get_UID(self):
        import pwd
        return pwd.getpwnam(self.user)[2]
    uid = property(_get_UID)

    def _get_GID(self):
        import grp
        return grp.getgrnam(self.group)[2]
    gid = property(_get_GID)
    
    def prepareDirectory(self, dirParts):
        for k in xrange(len(dirParts)-1):
            thisDir = os.path.join(*dirParts[:k+1])
            if not os.path.exists(thisDir):
                os.makedirs(thisDir)
                # Ensure correct permissions of the created directory (don't
                # touch existing ones)
                os.chown(thisDir, self.uid, self.gid)
                os.chmod(thisDir, 0770)
    
    def copy(self, srcPath, *destPathParts):
        self.prepareDirectory(destPathParts[:-1])
        destPath = os.path.join(*destPathParts)
        if os.path.exists(destPath):
            # Exists, copy only if dest time less (older) than source
            # time
            times = [os.path.getmtime(x) for x in (srcPath, destPath)]
            if times[1] <= times[0]:
                shutil.copy(srcPath, destPath)
        else:
            # Doesn't exist, always copy
            shutil.copy(srcPath, destPath)
        # Ensure correct ownership of files
        os.chown(destPath, self.uid, self.gid)
        print "%s -> %s" % (srcPath, destPath)

    def setup(self):
        for mungedPath in os.listdir('misc'):
            if mungedPath.startswith('.'):
                continue
            srcPath = os.path.join('misc', mungedPath)
            self.copy(srcPath, '/', *mungedPath.split('_'))


def run(user, group):
    """
    When a C{setup.py} script is called with one of the C{install*} commands
    and includes a call this method, the files in the C{misc} subdirectory are
    processed via a L{PostSetup} object.
    """
    ignore = sys.platform.startswith('win')
    for arg in sys.argv:
        if arg in ('-h', '--help'):
            ignore = True
            continue
        if not ignore and arg.startswith('install'):
            ps = PostSetup(user, group)
            ps.setup()
            return
    
    
