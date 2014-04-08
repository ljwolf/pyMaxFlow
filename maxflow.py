import pysal as ps
import numpy as np
import networkx as nx
import maxflow_tools as mft


shp = ps.open('example_data/streets.shp')
lens, caps = mft.randcap(shp, 45)

start = lens.keys()[np.random.randint(0,len(shp))][np.random.randint(0,1)]
end = lens.keys()[np.random.randint(0,len(shp))][np.random.randint(0,1)]
while start == end: #enforce different start and end
    end = lens.keys()[np.random.randint(0,len(shp))]
startgraph = nx.Graph()
resgraph = nx.Graph()
for i in lens.keys():
    #G.add_nodes_from(i)
    resgraph.add_edge(i[0],i[1], weight = lens.get(i), cap = caps.get(i), flow=0)
    startgraph.add_edge(i[0],i[1], weight = lens.get(i), cap = caps.get(i), flow=0)
    
    

finished = False #sentinel
flowdict = {} #how some results will be reported
iter = 1
maxflow = 0
lowlist = []
while not finished: 
    low_edges = [] #for each iteration, have a set of the dropped edges
    try:
        splist = nx.shortest_path(resgraph, start, end)
    except:
        break #termination!
    tlist = splist[:]
    pathcaps = {}
    while len(tlist) > 1: #pop through the copied splist to get local capacities
        o = tlist.pop(0)
        d = tlist[0]
        if caps.get((o,d)) != None:
            pathcaps.update({(o,d):caps.get((o,d))})
        else:
            pathcaps.update({(o,d):caps.get((d,o))})
    low_edge = min(pathcaps, key=pathcaps.get) #find low edge and its residual flow
    residual = caps.get(low_edge)
    if residual == None:
        residual = caps.get((low_edge[-1], low_edge[0])) #correct for asymmetric edge relationships
    for i in pathcaps.keys():
        pathcaps[i] = pathcaps[i] - residual #generate residual capacity
        if pathcaps[i] == 0: #if edge flow is maxed out
            if i[1] in resgraph.edge[i[0]]: 
                del resgraph.edge[i[0]][i[1]] #remove from graph
                startgraph.edge[i[0]][i[1]]['flow'] += residual #augment flow
                low_edges.append(i) #track low edge
            else: #check in case asymmetrical
                del resgraph.edge[i[1]][i[0]]
                startgraph.edge[i[1]][i[0]]['flow'] += residual
                low_edges.append(i)            
        else: #if edge flow isn't maxed out
            if i[1] in resgraph.edge[i[0]]:
                resgraph.edge[i[0]][i[1]]['cap'] = pathcaps[i] #update residual graph w/ residual capacity
                startgraph.edge[i[0]][i[1]]['flow'] += residual #update real graph with current flow
            else:
                resgraph.edge[i[1]][i[0]]['cap'] = pathcaps[i]
                startgraph.edge[i[1]][i[0]]['flow'] += residual
    flowdict.update({iter: (splist,residual)}) #store flow augmentation progress to a flowdict
    lowlist.append(low_edges) #store low edges to a list
    maxflow += residual #keep track of the max flow going on

print 'finished!\n\t Residual graph is in res, final graph is in startgraph,'
print '\t iteration history in flowdict and lowlist, and maxflow is ',maxflow
