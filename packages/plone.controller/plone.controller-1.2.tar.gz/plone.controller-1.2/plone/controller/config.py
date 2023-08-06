import sys, os

_cluster = None

debug = os.environ.has_key('DEBUG')

def setCluster(cluster):
    global _cluster
    _cluster = cluster

def getCluster():
    global _cluster
    return _cluster
