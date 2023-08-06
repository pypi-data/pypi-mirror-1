import os, os.path

from collective.buildout.cluster.base import ClusterBase

class ZEOServer(ClusterBase):
    """Represents a ZEO Server
    """

    service = 'ZEO'
