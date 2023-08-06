# Pull Zope configuration from .installed.cfg.
# It's a convenient place to get all the data
# for a buildout configuration because all the
# buildout variables are expanded already.


import sys

_cluster = None

def setCluster(cluster):
    global _cluster
    _cluster = cluster

def getCluster():
    global _cluster
    return _cluster
