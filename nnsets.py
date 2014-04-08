"""
levi john wolf
ljw@levijohnwolf.com
6 Dec 2013
"""


#setting up the import and statistics for the eberly shapefile
import pysal as ps
import networkx as nx
import numpy as np
import scipy as sp

#defining all significant functions
def euclideanmins(plist, param):
    """
    calculates a euclidean nearest neighbor set of size 'param'

    plist -- some list of tuples that indicates a point set in 2-dimensions
    param -- number of members of the nearest neighbor set needed

    """
    eucnndict = {}
    esps = {}
    for i in plist:
        for j in plist:
            if i != j:
                esps.update({(i, j): ((i[0] - j[0])**2 + (i[1] - j[1])**2)**.5})
        values = esps.values()
        values.sort()
        values = values[0:param]
        eucnns = []
        for k in values:
            for m in esps.keys():
                if esps.get(m) == k:
                    eucnns.append((m,k))
            eucnndict.update({i:eucnns})
    return eucnndict

def getVerts(psgraph):
    """
    extracts the vertices from a list of pysal chains

    psgraph -- a list of pysal chain objects.

    """
    psgraphVerts = []
    for i in range(len(psgraph)):
        for j in range(len(psgraph[i].vertices)):
            psgraphVerts.append(psgraph[i].vertices[j])
    return psgraphVerts

def make_psedgedict(psgraph):
    """
    make an edge length dictionary from a list of pysal chains

    psgraph -- a list of pysal chain objects
    """
    psgraphVerts = set()
    esps = {}
    for i in psgraph:
        jdist = ( (i.vertices[0][0] - i.vertices[1][0] )**2 + (i.vertices[0][1] - i.vertices[1][1])**2)**.5
        esps.update({(i.vertices[0], i.vertices[1]): jdist})    
    return esps

def edgedict2nx(edgedict):
    """
    make a networkx graph object using a dictionary of points and lengths

    edgedict -- a dictionary of keys and values
    edgedict.keys() -- point tuple in 2-dimensions that becomes an edge in an nx graph
    edgedict.values() -- the length of the edge in question
    """
    nx_eberlyGraph = nx.Graph()
    for i in edgedict.keys():
        nx_eberlyGraph.add_edge(i[0], i[1], length = edgedict.get(i))
    return nx_eberlyGraph

def make_nxedgedict(nxgraph):
    """
    make an edge length dictionary from a networkx graph

    nxgraph -- a networkx graph object

    """
    edgedict = {}
    for i in range(len(nxgraph.edges())):
        edgeLength =( (nxgraph.edges()[i][0][0] - nxgraph.edges()[i][1][0])**2 
                    +(nxgraph.edges()[i][0][1] - nxgraph.edges()[i][1][1])**2)**.5
        edgedict.update({nxgraph.edges()[i]:edgeLength})
    return edgedict

def make_pathdict(edgedict, nxgraph):
    """
    make a dictionary of paths between nodes in a networkx graph

    edgedict -- a dictionary of keys and values
    edgedict.keys() -- point tuple in 2-dimensions that represents an edge in the nx graph
    edgedict.values() -- the length of the edge in questin
    nxgraph -- a networkx graph object corresponding to the edgedict
    """
    nx_eberlySPs = nx.shortest_paths.all_pairs_shortest_path(nxgraph)
    pathdict = {}
    for i in nxgraph.nodes():
        for j in nx_eberlySPs.get(i).keys():
            if i != j:
                pathdict.update({(i, j):[]})
                workpath = nx_eberlySPs.get(i).get(j)
                lengths = []
                for k in range(len(workpath)-1):
                    if (workpath[k], workpath[k+1]) in edgedict:
                        lengths.append(edgedict.get((workpath[k], workpath[k+1])))
                    elif (workpath[k+1], workpath[k]) in edgedict:
                        lengths.append(edgedict.get((workpath[k+1], workpath[k])))
                pathdict.get((i, j)).append(sum(lengths))
    return pathdict

def dictminsearch(dictofdict, param, zeroflag = 'True'):    
    """
    general purpose dictionary of dictionary minimizer

    dictofdict -- a dictionary of dictionaries to be searched
    dictofdict.get(i) -- the value dictionary for the ith key of dictofdict
    param -- the desired length of dictofdict.get(i)
    zeroflag -- decides whether to count "0" as a minimizing value for comparison
    """
    mindict = {}
    for i in dictofdict.keys():
        values = dictofdict.get(i).values()
        values.sort()
        if zeroflag:
            while 0 in values:
                values.remove(0)
        values = values[0:param]
        mins = []
        for k in values:
            for m in dictofdict.get(i).keys():
                if dictofdict.get(i).get(m) == k:
                    mins.append((m, k))
        mindict.update({i:mins})
    return  mindict

if __name__ == '__main__':


    #open pysal files
    eberlyGraph = ps.open('data/eberly_net.shp').read()
    eberlyPointsOn = ps.open('data/eberly_net_pts_onnetwork.shp').read()
    eberlyPointsOff = ps.open('data/eberly_net_pts_offnetwork.shp').read()

    #prep the spatial distance values for the vertices & points on and off the graph
    eVerts = sp.spatial.distance_matrix(eberlyGraphVerts, eberlyGraphVerts, 2)
    eVertsOn = sp.spatial.distance_matrix(eberlyGraphVerts, eberlyPointsOn, 2)
    eVertsOff = sp.spatial.distance_matrix(eberlyGraphVerts, eberlyPointsOff, 2)
    
    #make pysal edge dict
    ps_edges = make_psedgedict(eberlyGraph)
    
    #build nx graph with only vertexes in the eberly graph
    nx_eberlyVerts = edgedict2nx(ps_edges)
    #build nx graph with points on the eberly graph
    nx_eberlyPoints = edgedict2nx(ps_edges).add_nodes_from(eberlyPointsOn)
    
    #make shortest paths for both vertex and point graphs
    networkspsVerts = nx.shortest_path_length(nx_eberlyVerts, weight='length')
    networkspsPoints = nx.shortest_path_length(nx_eberlyPoints, weight='length')
    
    #make nearest neighbor sets for both vertex and point graphs on network
    netnnsetsVerts = dictminsearch(networkspsVerts, 5)
    netnnsetsPoints = dictminsearch(networkspsPoints, 5)
    #make nearest neighbor set for vertex graph in euclidean space
    #eucnnsetsVerts = euclideanmins(eberlyGraphVerts, 5)

    ##TO DO:
    #implement euclidean nearest neighbor sets
    #figure out how to do the rms and pearson's r
    #implement spanning network simulator
    #talk to serge?
