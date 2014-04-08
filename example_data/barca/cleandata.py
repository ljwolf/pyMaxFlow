#thanks to Serge Rey
import pysal as ps

filename_shp = "barcelona.osm-line.shp"
shp = ps.open(filename_shp)

filename_dbf = "barcelona.osm-line.dbf"
dbf = ps.open(filename_dbf)
vars = dbf.header #stores all items in header as variables

highway = dbf.by_col('highway')

roads = [i for i,roadType in enumerate(highway) if roadType != '']

def getlines(shapefile, filterlist):
    lines = []
    i = 0
    for line in shapefile:
        if i in filterlist:
            lines.append(line)
        i+=1
    return lines

lines = getlines(shp, roads)

from collections import defaultdict
segments = defaultdict(list)
vertices = defaultdict(list)
for i,line in enumerate(lines):
    for j in range(len(line.vertices)-1):
        o = line.vertices[j]
        d = line.vertices[j+1]
        vertices[o].append((o,d))
        vertices[d].append((o,d))
        segments[(o,d)].append(i)

edgeIncidence = defaultdict(list)
for key in vertices:
    if len(vertices[key])>1:
        neighbors=vertices[key]
        for j in neighbors:
            edgeIncidence[j].extend(neighbors)

for edge in edgeIncidence:
    edgeIncidence[edge] = [ neighbor for neighbor in edgeIncidence[edge] if neighbor != edge ]

w = ps.W(neighbors=edgeIncidence)

#Do shortest path between start and end
#augment path: each upper capacity minus upper capacity of constraining link
#drop constraining link from graph


