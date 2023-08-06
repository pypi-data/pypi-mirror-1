# Pull Zope configuration from .installed.cfg.
# It's a convenient place to get all the data
# for a buildout configuration because all the
# buildout variables are expanded already.

import os, os.path
import sha
import binascii

from collective.buildout.cluster.base import ClusterBase

class ZEOClient(ClusterBase):
    """Represents a ZEO Client
    """

    service = 'Zope'

    def _getEmergencyUserFile(self):
        return os.path.join(self.getInstanceHome(), 'access')

    def isEmergencyUser(self):
        return os.path.exists(self._getEmergencyUserFile())

    def removeEmergencyUser(self):
        os.remove(self._getEmergencyUserFile())

    def createEmergencyUser(self, username, pw1, pw2):
        if not username:
            raise ValueError, "No username"
        if not pw1:
            raise ValueError, "No password"
        if pw1 != pw2:
            raise ValueError, "Passwords do not match"
        pw = "{SHA}" + binascii.b2a_base64(sha.new(pw1).digest())[:-1]
        fh = open(self._getEmergencyUserFile(), 'w')
        try:
            fh.write('%s:%s\n' % (username, pw))
        finally:
            fh.close()

    def getURL(self):
        return "http://localhost:%s/Plone" % self.getPort("http")

    def getManageURL(self):
        return "http://localhost:%s/manage" % self.getPort("http")
