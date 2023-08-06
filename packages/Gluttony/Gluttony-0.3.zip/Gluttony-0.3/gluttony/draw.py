'''
Created on 2010/2/20

@author: User
'''
import cPickle as pickle
import networkx as nx
import matplotlib.pyplot as plt

def getProjectName(req):
    """Get project name in a pretty form:
    
    name-version
    
    """
    return '%s-%s' % (req.name, req.installed_version)

dependencies = pickle.load(open('plone.pickle'))
def convert(pair):
    return (getProjectName(pair[0]), getProjectName(pair[1]))
plainDependencies = map(convert, dependencies)

print 'Add edges...'
dg = nx.DiGraph()
dg.add_edges_from(plainDependencies)
print 'Drawing...'
nx.draw_spring(dg)
plt.show()