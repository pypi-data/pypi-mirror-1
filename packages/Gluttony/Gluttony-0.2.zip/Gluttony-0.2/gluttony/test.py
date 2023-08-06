'''
Created on 2010/2/19

@author: User
'''

import pygraphviz as pgv
print 'd'
G=pgv.AGraph()
G.add_node('a')
G.add_edge('b','c')
print repr(G)