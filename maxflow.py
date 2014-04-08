import pysal as ps
import numpy as np
import networkx as nx
import maxflow_tools as mft

def genlenscaps(shp, cap=45):
    """
    A simple tool to build length and capacity dictionaries

    Steps:
    1.) Build shortest path lengths and capacities
    
    Requires:
    @shp = a pysal shapefile containing chain objects
    @cap = an integer specifying the upper bound on random capacities
    """
    lens, caps = mft.randcap(shp, cap)
    return lens,caps

def genrandst(shp, lens):
    """
    A simple tool to build random starting and ending points

    Steps:
    1.) build start and end points

    Requires: 
    @shp = a pysal shapefile containing chain objects
    @lens = a python dictionary with keys as edges and their length as values

    Outputs (start,end) where:
    @start = random node in @shp
    @end = random node in @shp
    
    """
    start = lens.keys()[np.random.randint(0,len(shp))][np.random.randint(0,1)]
    end = lens.keys()[np.random.randint(0,len(shp))][np.random.randint(0,1)]
    while start == end: #enforce different start and end
        end = lens.keys()[np.random.randint(0,len(shp))]
    return start,end

def gengraphs(shp, lens, caps):
    """
    A simple tool to build networkx graphs with random capacities
    
    Steps:
    1.) initialize empty graphs
    2.) build graphs using networkx

    Requires:
    @shp = a pysal shapefile containing chain objects
    @lens = a python dictionary with keys as edges and their length as values
    @caps = a python dictionary with keys as edges and their capacity as values
    
    Outputs (startgraph, resgraph) where:
    @startgraph = a networkx graph object equivalent to @resgraph
    @resgraph = a networkx graph object equivalent to @startgraph
    
    """
    startgraph = nx.Graph()
    resgraph = nx.Graph()
    for i in lens.keys():
        #G.add_nodes_from(i)
        resgraph.add_edge(i[0],i[1], weight = lens.get(i), cap = caps.get(i), flow=0)
        startgraph.add_edge(i[0],i[1], weight = lens.get(i), cap = caps.get(i), flow=0)
    return startgraph, resgraph 
    
def maxflow(startgraph, resgraph, caps, start, end):
    """
    An implementation of the Ford-Fulkerson MaxFlow/MinCut algorithm, paricularly the Edmonds-Karp type.

    Steps:
    1.) compute shortest path between start and end. Terminate if no path is found.
    2.) get capacities of shortest path edges
    3.) augment residual graph by dropping edges at max flow
    4.) augment starting graph by adding flow to all edges on shortest path and return to 1.)

    Requires:
    @startgraph = a networkx graph object equivalent to @resgraph where flow results will be stored
    @resgraph = a networkx graph object equivalent to @startgraph where augmenting paths will made and cut
    @caps = a python dictionary with edges as keys and their capacity as values
    @start = the starting node for the maxflow algorithm
    @end = the ending node for the maxflow algorithm

    Outputs (startgraph, resgraph, maxflow), where:
    @startgraph = original @startgraph with flows updated
    @resgraph = original @resgraph with augmenting paths removed
    @maxflow = total amount of flow through network
    """
    finished = False #sentinel
    #flowdict = {} #how some results will be reported
    it = 1
    maxflow = 0
    #lowlist = [] #list constituting mincut

    #find the minimum cut/max flow
    while not finished: 
        #low_edges = [] #for each iteration, have a set of dropped edges
        
        #termination check: if no shortest path exists in the residual graph, the graph is fully cut
        try:
            splist = nx.shortest_path(resgraph, start, end)
        except:
            print '\t\tno connectivity!\n\t\tcut complete!'
            break #termination criteria met: minimal cut achieved!
        
        #get capacities of current shortest path

        tlist = splist[:]
        pathcaps = {}
        while len(tlist) > 1: #pop through the copied shortest path list
            o = tlist.pop(0)
            d = tlist[0]
            if caps.get((o,d)) != None:
                pathcaps.update({(o,d):caps.get((o,d))})
            else:
                pathcaps.update({(o,d):caps.get((d,o))})
        
        #find low edge and its residual flow
        
        low_edge = min(pathcaps, key=pathcaps.get) 
        residual = caps.get(low_edge)
        if residual == None:
            residual = caps.get((low_edge[-1], low_edge[0])) #correct for asymmetric edge relationships
        
        #generate residual capacities, augment startgraph with flow and drop maxed edges from resgraph
        
        for i in pathcaps.keys():
            pathcaps[i] = pathcaps[i] - residual #generate residual capacity
            if pathcaps[i] == 0: #if edge flow is maxed out
                if i[1] in resgraph.edge[i[0]]: 
                    del resgraph.edge[i[0]][i[1]] #remove from graph
                    startgraph.edge[i[0]][i[1]]['flow'] += residual #augment flow
        #            low_edges.append(i) #track low edge
                else: #check in case asymmetrical
                    del resgraph.edge[i[1]][i[0]]
                    startgraph.edge[i[1]][i[0]]['flow'] += residual
        #            low_edges.append(i)            
            else: #if edge flow isn't maxed out
                if i[1] in resgraph.edge[i[0]]:
                    resgraph.edge[i[0]][i[1]]['cap'] = pathcaps[i] #update residual graph w/ residual capacity
                    startgraph.edge[i[0]][i[1]]['flow'] += residual #update real graph with current flow
                else:
                    resgraph.edge[i[1]][i[0]]['cap'] = pathcaps[i]
                    startgraph.edge[i[1]][i[0]]['flow'] += residual
        
        #report results
        
        #flowdict.update({it: (splist,residual)}) #store flow augmentation progress to a flowdict
        #lowlist.append(low_edges) #store low edges to a list
        maxflow += residual #keep track of the max flow going on
        #print 'maxflow at iteration ', it, 'is ', maxflow
        it = it + 1
    
    return startgraph, resgraph, maxflow#, flowdict, lowlist

if __name__ == "__main__":
    print 'Part A: GeoDaNet Example'
    shpf_a = ps.open('example_data/streets.shp')
    print '\nbuilding objects for maxflow'
    lens_a, caps_a = genlenscaps(shpf_a, cap=45)
    start_a, end_a = genrandst(shpf_a, lens_a)
    startgraph_a, resgraph_a = gengraphs(shpf_a, lens_a, caps_a)
    print '\tstarting maxflow'
    startgraph_a, resgraph_a, maxflow_a = maxflow(startgraph_a, resgraph_a, caps_a, start_a, end_a)
    
    print 'Part B: Barcelona from Simon'
    shpf_b = ps.open('example_data/barca/simon_maps/BCN_GrafVial_Trams_SHP.shp')
    
    print '\tbuilding objects for maxflow'
    lens_b, caps_b = genlenscaps(shpf_b, cap=20)
    start_b, end_b = genrandst(shpf_b, lens_b)
    startgraph_b, resgraph_b = gengraphs(shpf_b, lens_b, caps_b)
    print '\tstarting maxflow'
    startgraph_b, resgraph_b, maxflow_b = maxflow(startgraph_b, resgraph_b, caps_b, start_b, end_b)
    
    print 'Part C: Barcelona OSM'
    shpf_c = ps.open('example_data/barca/osm/barcelona.osm-line.shp')
    dbf_c = ps.open('example_data/barca/osm/barcelona.osm-line.dbf')
    vars = dbf_c.header

    highway = dbf_c.by_col('highway')
    roads = [ i for i,roadType in enumerate(highway) if roadType != '' ]

    print '\tbuilding lines'
    lines=[]
    i = 0
    for line in shpf_c:
        if i in roads:
            lines.append(line)
        i+=1

    print '\tbuilding objects for maxflow'
    lens_c, caps_c = genlenscaps(shpf_c, cap=10)
    start_c, end_c = genrandst(shpf_c, lens_c)
    startgraph_c, resgraph_c = gengraphs(shpf_c, lens_c, caps_c)
    print '\tto run maxflow, execute:\n\t\t startgraph_c, resgraph_c, maxflow_c = maxflow(startgraph_c, resgraph_c, caps_c, start_c, end_c)'
    #startgraph_c, resgraph_c, maxflow_c = maxflow(startgraph_c, resgraph_c, caps_c, start_c, end_c)
