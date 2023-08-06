#===============================================================================
# Copyright 2009 Matt Chaput
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

import math, random


class Cluster(object):
    def __init__(self, points, distancefn):
        assert len(points)
        self.points = points
        plen = len(points[0])
        if not all(len(p) == plen for p in points[1:]):
            raise ValueError("All points must have the same dimensions")
        self.n = plen
        
        self._centroid = None
        self.distancefn = distancefn
    
    def __repr__(self):
        return "<%s:%r>" % (self.__class__.__name__, self.points)
    
    @property
    def centroid(self):
        if self._centroid is not None:
            return self._centroid
        points = self.points
        np = len(points)
        c = tuple(sum(p[i] for p in points) / np for i in xrange(self.n))
        self._centroid = c
        return c
    
    def update(self, points):
        oldc = self.centroid
        self.points = points
        self._centroid = None
        return self.distancefn(oldc, self.centroid)
    
    def append(self, item):
        self.points.append(item)
        self._centroid = None


def kmeans(points, k, distancefn, cutoff):
    points = points[:]
    random.shuffle(points)
    clusters = [Cluster(ls, distancefn) for ls in [points[n::n+1] for n in xrange(k)]]
    it = 0
    while True:
        it += 1
        print "it=", it
        lists = [[] for _ in xrange(len(clusters))]
        for p in points:
            mindist, minindex = min((distancefn(p, cluster.centroid), i)
                                    for i, cluster in enumerate(clusters))
            lists[minindex].append(p)
        
        biggestmove = max(clusters[i].update(lists[i]) for i in xrange(len(clusters)))
        print "biggestmove=", biggestmove
        if biggestmove < cutoff: break
    
    return clusters
    

def distance(a, b, power=2):
    n = len(a)
    if n != len(b): raise ValueError("Can't compare points of different dimensions")
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in xrange(n)))


def test_kmeans(numpoints, k, cutoff=0.5, lower=-200, upper=200):
    points = [(random.uniform(lower, upper), random.uniform(lower, upper))
              for _ in xrange(numpoints)]
    print "POINTS:", points
    clusters = kmeans(points, k, distance, cutoff)
    print "CLUSTERS:"
    for cluster in clusters:
        print "  ", cluster

if __name__ == "__main__":
    test_kmeans(100, 5)









