import pysal as ps
import numpy as np
#thanks to serge rey sjrey@asu.edu
#shp = ps.open('example_data/streets.shp')
#dbf = ps.open('example_data/streets.dbf')

def randcap(ps_shp, upper):
    lengths = {}
    capacities = {}
    for i in range(len(ps_shp)):
        lengths.update({(ps_shp[i].vertices[0], ps_shp[i].vertices[-1]): ps_shp[i].arclen})
        capacities.update({(ps_shp[i].vertices[0], ps_shp[i].vertices[-1]): np.random.randint(0, high=upper)})
    return lengths, capacities

def mk_edgeIncidence(shp):
    from collections import defaultdict #import high performance dictionary constructor
    segments = defaultdict(list) #defaultdict is like a dictionary constructor with an defined missing value
    vertices = defaultdict(list) #here it's list
    for i,line in enumerate(shp): 
        for j in range(len(line.vertices)-1):
            o = line.vertices[j] #pair vertices together to make edges
            d = line.vertices[j+1]
            vertices[o].append((o,d)) #also set them as neighbors
            vertices[d].append((o,d)) 
            segments[(o,d)].append(i) #set incident pairs as edges
    edgeIncidence = defaultdict(list)
    for key in vertices:
        if len(vertices[key])>1:
            neighbors=vertices[key]
            for j in neighbors:
                edgeIncidence[j].extend(neighbors)
    for edge in edgeIncidence:
        edgeIncidence[edge] = [ neighbor for neighbor in edgeIncidence[edge] if neighbor != edge ]
    return edgeIncidence


