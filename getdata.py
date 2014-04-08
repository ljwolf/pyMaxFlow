#!/bin/python
import tarfile
import urlgrabber

print("Downloading data")
urlgrabber.urlgrab("http://www.public.asu.edu/~lwolf2/data/barcelona.osm.tar.gz")

tfile = tarfile.open("barcelona.osm.tar.gz", "r:gz")

print("Extracting data")
tfile.extractall('.')

print("Done!")
