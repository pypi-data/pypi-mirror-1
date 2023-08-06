"""
Post setup operations
"""

import sys, os, os.path, shutil
import pkg_resources as pr


class PostSetup(object):
    """
    I do post-setup file copying with equivalent user and group access
    permissions.
    """
    def __init__(self, srcDir, user, group):
        self.srcDir = srcDir
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
        doCopy = False
        if os.path.exists(destPath):
            # Exists, copy only if dest time less (older) than source
            # time
            times = [os.path.getmtime(x) for x in (srcPath, destPath)]
            if times[1] <= times[0]:
                doCopy = True
        else:
            # Doesn't exist, always copy
            doCopy = True
        if doCopy:
            shutil.copy(srcPath, destPath)
            print "%s -> %s" % (srcPath, destPath)
        # Ensure correct ownership of files, newly copied or not
        os.chown(destPath, self.uid, self.gid)

    def setup(self):
        for mungedPath in os.listdir(self.srcDir):
            if mungedPath.startswith('.'):
                continue
            srcPath = os.path.join(self.srcDir, mungedPath)
            self.copy(srcPath, '/', *mungedPath.split('_'))


def run(projectName, user, group):
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
            requirement = pr.Requirement.parse(projectName)
            srcDir = pr.resource_filename(requirement, 'misc')
            ps = PostSetup(srcDir, user, group)
            ps.setup()
            pr.cleanup_resources()
            return
    
    
