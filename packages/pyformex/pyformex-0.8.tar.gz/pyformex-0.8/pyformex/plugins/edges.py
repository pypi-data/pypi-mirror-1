#!/usr/bin/env python pyformex.py
# $Id$
##
##  This file is part of pyFormex 0.8 Release Sat Jun 13 10:22:42 2009
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Website: http://pyformex.berlios.de/
##  Copyright (C) Benedict Verhegghe (bverheg@users.berlios.de) 
##  Distributed under the GNU General Public License version 3 or later.
##
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
"""A class for handling edges.

(c) 2009 Benedict Verhegghe

The Edges class is used to discretely model one-dimensional geometry.
"""

import os,tempfile
import pyformex as GD
from connectivity import *
from utils import runCommand, changeExt,countLines,mtime,hasExternal
from formex import *
from gui.drawable import interpolateNormals

from numpy import *


############################################################################
# The QuadSurface class

from plugins.surface import coordsmethod

class Edges(object):
    """A class for handling discrete 1D geometrical elements.

    Edges are tuples of two points, describing a straight linear segment in
    3D space.
    """

    def __init__(self,*args):
        """Create a new Edges object.

        The collection contains nel edges, each having 2 vertices with
        3 coordinates.
        The surface can be initialized from one of the following:
        - a (nel,2,3) shaped array of floats ;
        - a 2-plex Formex with nel elements ;
        - an (ncoords,3) float array of vertex coordinates and
          an (nel,2) integer array of vertex numbers ;

        Internally, the Edges are stored in a (coords,elems) tuple.
        """
        self.coords = None
        self.elems = None
        self.props = None
##         self.lengths = None
##         self.directions = None
##         self.econn = None
##         self.conn = None
##         self.eadj = None
##         self.adj = None
##         if hasattr(self,'edglen'):
##             del self.edglen
        if len(args) == 0:
            return
        if len(args) == 1:
            # a Formex model
            a = args[0]
            if not isinstance(a,Formex):
                a = Formex(a)
            if a.nplex() != 2:
                raise ValueError,"Expected a plex-2 Formex"
            self.coords,self.elems = a.feModel()
            self.props = a.p

        elif len(args) == 2:
            a = Coords(args[0])
            if len(a.shape) != 2:
                raise ValueError,"Expected a 2-dim coordinates array"
            self.coords = a
            
            a = asarray(args[1])
            if a.dtype.kind != 'i' or a.ndim != 2 or a.shape[1] != 2:
                raise "Got invalid second argument"
            if a.max() >= self.coords.shape[0]:
                raise ValueError,"Some vertex number is too high"
            self.elems = a

        else:
            raise RuntimeError,"Too many arguments"


    def setOrient(self):
        """Orient the edges.

        The edges are oriented from the lowest to the highest vertex number.
        The return value returns True for the elements that were not changed.
        """
        orient = self.elems[:,0] < self.elems[:,1]
        self.elems = sort(self.elems,axis=1)
        return orient
 

    def getElems(self,original=False):
        """Return the element definitions, by default with sorted orienation.

        If original = True, the vertex order is the same on creation.
        The default is to return the lowest vertex number first.
        """
        if original and self.orient is not None:
            return where(self.orient,self.elems,roll(self.elems,-1,axis=1))
        else:
            return self.elems


    def compress(self):
        """Remove all unused vertices.

        The coordinates of the vertices that are not referenced by any
        of the edges are remoed from the coordinate table, and the edge
        definitions and update to reflect the new node numbering.
        """
        newnrs = unique1d(self.elems)
        reverse = -ones(self.ncoords(),dtype=int32)
        reverse[newnrs] = arange(newnrs.size,dtype=int32)
        self.coords = self.coords[newnrs]
        self.edges = reverse[self.edges]


    def append(self,S):
        """Merge another surface with self.

        This just merges the data sets, and does not check
        whether the surfaces intersect or are connected!
        This is intended mostly for use inside higher level functions.
        """
        self.refresh()
        S.refresh()
        coords = concatenate([self.coords,S.coords])
        elems = concatenate([self.elems,S.elems+self.ncoords()])
        ## What to do if one of the surfaces has properties, the other one not?
        ## The current policy is to use zero property values for the Surface
        ## without props
        prop = None
        if self.p is not None or S.p is not None:
            if self.p is None:
                self.p = zeros(shape=self.nelems(),dtype=Int)
            if S.p is None:
                p = zeros(shape=S.nelems(),dtype=Int)
            else:
                p = S.p
            prop = concatenate((self.p,p))
        self.__init__(coords,elems)
        self.setProp(prop)



def compactElems(edges,faces):
    """Return compacted elems from edges and faces.

    This is the inverse operation of expandElems.
    """
    elems = edges[faces]
    flag1 = (elems[:,0,0]==elems[:,1,0]) + (elems[:,0,0]==elems[:,1,1])
    flag2 = (elems[:,2,0]==elems[:,1,0]) + (elems[:,2,0]==elems[:,1,1])
    nod0 = where(flag1,elems[:,0,1],elems[:,0,0])
    nod1 = where(flag1,elems[:,0,0],elems[:,0,1])
    nod2 = where(flag2,elems[:,2,0],elems[:,2,1])
    elems = column_stack([nod0,nod1,nod2])
    return elems


def areaNormals(x):
    """Compute the area and normal vectors of a collection of triangles.

    x is an (ntri,3,3) array of coordinates.

    Returns a tuple of areas,normals.
    The normal vectors are normalized.
    The area is always positive.
    """
    area,normals = vectorPairAreaNormals(x[:,1]-x[:,0],x[:,2]-x[:,1])
    area *= 0.5
    return area,normals


############################################################################


def surfaceInsideLoop(coords,elems):
    """Create a surface inside a closed curve defined by coords and elems.

    coords is a set of coordinates.
    elems is an (nsegments,2) shaped connectivity array defining a set of line
    segments forming a closed loop.

    The return value is coords,elems tuple where
    coords has one more point: the center of th original coords
    elems is (nsegment,3) and defines triangles describing a surface inside
    the original curve.
    """
    coords = Coords(coords)
    if coords.ndim != 2 or elems.ndim != 2 or elems.shape[1] != 2 or elems.max() >= coords.shape[0]:
        raise ValueError,"Invalid argument shape/value"
    x = coords[unique1d(elems)].center().reshape(-1,3)
    n = zeros_like(elems[:,:1]) + coords.shape[0]
    elems = concatenate([elems,n],axis=1)
    coords = Coords.concatenate([coords,x])
    return coords,elems


def fillHole(coords,elems):
    """Fill a hole surrounded by the border defined by coords and elems.
    
    Coords is a (npoints,3) shaped array of floats.
    Elems is a (nelems,2) shaped array of integers representing the border
    element numbers and must be ordered.
    """
    triangles = empty((0,3,),dtype=int)
    while shape(elems)[0] != 3:
        elems,triangle = create_border_triangle(coords,elems)
        triangles = row_stack([triangles,triangle])
    # remaining border
    triangles = row_stack([triangles,elems[:,0]])
    return triangles


###########################################################################
    #
    #   Return information about a TriSurface
    #

    def ncoords(self):
        return self.coords.shape[0]

    def nedges(self):
        return self.edges.shape[0]

    def nfaces(self):
        return self.faces.shape[0]

    # The following are defined to get a unified interface with Formex
    nelems = nfaces
   
    def nplex(self):
        return 3
    
    def ndim(self):
        return 3

    npoints = ncoords

    def vertices(self):
        return self.coords
    
    def shape(self):
        """Return the number of ;points, edges, faces of the TriSurface."""
        return self.coords.shape[0],self.edges.shape[0],self.faces.shape[0]
       
    def copy(self):
        """Return a (deep) copy of the surface.

        If an index is given, only the specified faces are retained.
        """
        self.refresh()
        S = TriSurface(self.coords.copy(),self.elems.copy())
        if self.p is not None:
            S.setProp(self.p)
        return S
    
    def select(self,idx,compress=True):
        """Return a TriSurface which holds only elements with numbers in ids.

        idx can be a single element number or a list of numbers or
        any other index mechanism accepted by numpy's ndarray
        By default, the vertex list will be compressed to hold only those
        used in the selected elements.
        Setting compress==False will keep all original nodes in the surface.
        """
        self.refresh()
        S = TriSurface(self.coords, self.elems[idx])
        if self.p is not None:
            S.setProp(self.p[idx])
        if compress:
            S.compress()
        return S
    

    # Properties
    def setProp(self,p=None):
        """Create or delete the property array for the TriSurface.

        A property array is a rank-1 integer array with dimension equal
        to the number of elements in the TriSurface.
        You can specify a single value or a list/array of integer values.
        If the number of passed values is less than the number of elements,
        they wil be repeated. If you give more, they will be ignored.
        
        If a value None is given, the properties are removed from the TriSurface.
        """
        if p is None:
            self.p = None
        else:
            p = array(p).astype(Int)
            self.p = resize(p,(self.nelems(),))
        return self

    def prop(self):
        """Return the properties as a numpy array (ndarray)"""
        return self.p

    def maxprop(self):
        """Return the highest property value used, or None"""
        if self.p is None:
            return None
        else:
            return self.p.max()

    def propSet(self):
        """Return a list with unique property values."""
        if self.p is None:
            return None
        else:
            return unique(self.p)
 
    # Test and clipping functions
    

    def test(self,nodes='all',dir=0,min=None,max=None):
        """Flag elements having nodal coordinates between min and max.

        This function is very convenient in clipping a TriSurface in a specified
        direction. It returns a 1D integer array flagging (with a value 1 or
        True) the elements having nodal coordinates in the required range.
        Use where(result) to get a list of element numbers passing the test.
        Or directly use clip() or cclip() to create the clipped TriSurface
        
        The test plane can be defined in two ways, depending on the value of dir.
        If dir == 0, 1 or 2, it specifies a global axis and min and max are
        the minimum and maximum values for the coordinates along that axis.
        Default is the 0 (or x) direction.

        Else, dir should be compaitble with a (3,) shaped array and specifies
        the direction of the normal on the planes. In this case, min and max
        are points and should also evaluate to (3,) shaped arrays.
        
        nodes specifies which nodes are taken into account in the comparisons.
        It should be one of the following:
        - a single (integer) point number (< the number of points in the Formex)
        - a list of point numbers
        - one of the special strings: 'all', 'any', 'none'
        The default ('all') will flag all the elements that have all their
        nodes between the planes x=min and x=max, i.e. the elements that
        fall completely between these planes. One of the two clipping planes
        may be left unspecified.
        """
        if min is None and max is None:
            raise ValueError,"At least one of min or max have to be specified."
        self.refresh()
        f = self.coords[self.elems]
        if type(nodes)==str:
            nod = range(f.shape[1])
        else:
            nod = nodes

        if type(dir) == int:
            if not min is None:
                T1 = f[:,nod,dir] > min
            if not max is None:
                T2 = f[:,nod,dir] < max
        else:
            if not min is None:
                T1 = f.distanceFromPlane(min,dir) > 0
            if not max is None:
                T2 = f.distanceFromPlane(max,dir) < 0

        if min is None:
            T = T2
        elif max is None:
            T = T1
        else:
            T = T1 * T2
        if len(T.shape) == 1:
            return T
        if nodes == 'any':
            T = T.any(1)
        elif nodes == 'none':
            T = (1-T.any(1)).astype(bool)
        else:
            T = T.all(1)
        return T


    def clip(self,t):
        """Return a TriSurface with all the elements where t>0.

        t should be a 1-D integer array with length equal to the number
        of elements of the TriSurface.
        The resulting TriSurface will contain all elements where t > 0.
        """
        return self.select(t>0)


    def cclip(self,t):
        """This is the complement of clip, returning a TriSurface where t<=0.
        """
        return self.select(t<=0)


    # Some functions for offsetting a surface
    
    # Data conversion

    def toFormex(self):
        """Convert the surface to a Formex."""
        self.refresh()
        return Formex(self.coords[self.elems],self.p)

    
    def feModel(self):
        """Return a tuple of nodal coordinates and element connectivity."""
        return self.coords,self.elems




####################### Geometrical Data ######################


    def avgVertexNormals(self):
        """Compute the average normals at the vertices."""
        self.refresh()
        return interpolateNormals(self.coords,self.elems,atNodes=True)


    def areaNormals(self):
        """Compute the area and normal vectors of the surface triangles.

        The normal vectors are normalized.
        The area is always positive.

        The values are returned and saved in the object.
        """
        if self.areas is None or self.normals is None:
            self.refresh()
            self.areas,self.normals = areaNormals(self.coords[self.elems])
        return self.areas,self.normals


    def facetArea(self):
        return self.areaNormals()[0]
        

    def area(self):
        """Return the area of the surface"""
        area = self.areaNormals()[0]
        return area.sum()


    def volume(self):
        """Return the enclosed volume of the surface.

        This will only be correct if the surface is a closed manifold.
        """
        self.refresh()
        x = self.coords[self.elems]
        return surface_volume(x).sum()


    def edgeConnections(self):
        """Find the elems connected to edges."""
        if self.econn is None:
            self.econn = reverseIndex(self.faces)
        return self.econn
    

    def nodeConnections(self):
        """Find the elems connected to nodes."""
        if self.conn is None:
            self.refresh()
            self.conn = reverseIndex(self.elems)
        return self.conn
    

    def nEdgeConnected(self):
        """Find the number of elems connected to edges."""
        return (self.edgeConnections() >=0).sum(axis=-1)
    

    def nNodeConnected(self):
        """Find the number of elems connected to nodes."""
        return (self.nodeConnections() >=0).sum(axis=-1)


    def edgeAdjacency(self):
        """Find the elems adjacent to elems via an edge."""
        if self.eadj is None:
            nfaces = self.nfaces()
            rfaces = self.edgeConnections()
            # this gives all adjacent elements including element itself
            adj = rfaces[self.faces].reshape(nfaces,-1)
            #print adj.shape
            fnr = arange(nfaces).reshape(nfaces,-1)
            #print fnr.shape
            # remove the element itself
            #print adj != fnr
            #print (adj != fnr).shape
            self.eadj = adj[adj != fnr].reshape((nfaces,-1))
        return self.eadj


    def nEdgeAdjacent(self):
        """Find the number of adjacent elems."""
        return (self.edgeAdjacency() >=0).sum(axis=-1)


    def nodeAdjacency(self):
        """Find the elems adjacent to elems via one or two nodes."""
        if self.adj is None:
            self.refresh()
            self.adj = adjacent(self.elems,self.nodeConnections())
        return self.adj


    def nNodeAdjacent(self):
        """Find the number of adjacent elems."""
        return (self.nodeAdjacency() >=0).sum(axis=-1)


    def surfaceType(self):
        ncon = self.nEdgeConnected()
        nadj = self.nEdgeAdjacent()
        maxcon = ncon.max()
        mincon = ncon.min()
        manifold = maxcon == 2
        closed = mincon == 2
        return manifold,closed,mincon,maxcon


    def borderEdges(self):
        """Detect the border elements of TriSurface.

        The border elements are the edges having less than 2 connected elements.
        Returns True where edge is on the border.
        """
        return self.nEdgeConnected() <= 1


    def borderEdgeNrs(self):
        """Returns the numbers of the border edeges."""
        return where(self.nEdgeConnected() <= 1)[0]


    def borderNodeNrs(self):
        """Detect the border nodes of TriSurface.

        The border nodes are the vertices belonging to the border edges.
        Returns a list of vertex numbers.
        """
        border = self.edges[self.borderEdgeNrs()]
        return unique1d(border)
        

    def isManifold(self):
        return self.surfaceType()[0] 


    def isClosedManifold(self):
        stype = self.surfaceType()
        return stype[0] and stype[1]

    def checkBorder(self):
        """Return the border of TriSurface as a set of segments."""
        border = self.edges[self.borderEdges()]
        closed,loop = closedLoop(border)
        print "the border is of type %s" % closed
        print loop


    def fillBorder(self,method=0):
        """If the surface has a single closed border, fill it.

        Filling the border is done by adding a single point inside
        the border and connectin it with all border segments.
        This works well if the border is smooth and nearly planar.
        """
        border = self.edges[self.borderEdges()]
        closed,loop = closedLoop(border)
        if closed == 0:
            if method == 0:
                coords,elems = surfaceInsideLoop(self.coords,loop)
                newS = TriSurface(coords,elems)
            else:
                elems = fillHole(self.coords,loop)
                newS = TriSurface(self.coords,elems)
            self.append(newS)


    def border(self):
        """Return the border of TriSurface as a Plex-2 Formex."""
        return Formex(self.coords[self.edges[self.borderEdges()]])


    def edgeCosAngles(self):
        """Return the cos of the angles over all edges.
        
        The surface should be a manifold (max. 2 elements per edge).
        Edges with only one element get angles = 1.0.
        """
        conn = self.edgeConnections()
        # Bail out if some edge has more than two connected faces
        if conn.shape[1] != 2:
            raise RuntimeError,"TriSurface is not a manifold"
        angles = ones(self.nedges())
        conn2 = (conn >= 0).sum(axis=-1) == 2
        n = self.areaNormals()[1][conn[conn2]]
        angles[conn2] = dotpr(n[:,0],n[:,1])
        return angles


    def edgeAngles(self):
        """Return the angles over all edges (in degrees)."""
        return arccos(self.edgeCosAngles()) / rad


    def data(self):
        """Compute data for all edges and faces."""
        if hasattr(self,'edglen'):
            return
        self.areaNormals()
        edg = self.coords[self.edges]
        edglen = length(edg[:,1]-edg[:,0])
        facedg = edglen[self.faces]
        edgmin = facedg.min(axis=-1)
        edgmax = facedg.max(axis=-1)
        altmin = 2*self.areas / edgmax
        aspect = edgmax/altmin
        self.edglen,self.facedg,self.edgmin,self.edgmax,self.altmin,self.aspect = edglen,facedg,edgmin,edgmax,altmin,aspect 


    def aspectRatio(self):
        self.data()
        return self.aspect

 
    def smallestAltitude(self):
        self.data()
        return self.altmin


    def longestEdge(self):
        self.data()
        return self.edgmax


    def shortestEdge(self):
        self.data()
        return self.edgmin

   
    def stats(self):
        """Return a text with full statistics."""
        bbox = self.bbox()
        manifold,closed,mincon,maxcon = self.surfaceType()
        self.data()
        angles = self.edgeAngles()
        area = self.area()
        if manifold and closed:
            volume = self.volume()
        else:
            volume = 0.0
        print  (
            self.ncoords(),self.nedges(),self.nfaces(),
            bbox[0],bbox[1],
            mincon,maxcon,
            manifold,closed,
            self.areas.min(),self.areas.max(),
            self.edglen.min(),self.edglen.max(),
            self.altmin.min(),self.aspect.max(),
            angles.min(),angles.max(),
            area,volume
            )
        s = """
Size: %d vertices, %s edges and %d faces
Bounding box: min %s, max %s
Minimal/maximal number of connected faces per edge: %s/%s
Surface is manifold: %s; surface is closed: %s
Smallest area: %s; largest area: %s
Shortest edge: %s; longest edge: %s
Shortest altitude: %s; largest aspect ratio: %s
Angle between adjacent faces: smallest: %s; largest: %s
Total area: %s; Enclosed volume: %s   
""" % (
            self.ncoords(),self.nedges(),self.nfaces(),
            bbox[0],bbox[1],
            mincon,maxcon,
            manifold,closed,
            self.areas.min(),self.areas.max(),
            self.edglen.min(),self.edglen.max(),
            self.altmin.min(),self.aspect.max(),
            angles.min(),angles.max(),
            area,volume
            )
        return s


##################  Partitioning a surface #############################


    def edgeFront(self,startat=0,okedges=None,front_increment=1):
        """Generator function returning the frontal elements.

        startat is an element number or list of numbers of the starting front.
        On first call, this function returns the starting front.
        Each next() call returns the next front.
        front_increment determines haw the property increases at each
        frontal step. There is an extra increment +1 at each start of
        a new part. Thus, the start of a new part can always be detected
        by a front not having the property of the previous plus front_increment.
        """
        print "FRONT_INCREMENT %s" % front_increment
        p = -ones((self.nfaces()),dtype=int)
        if self.nfaces() <= 0:
            return
        # Construct table of elements connected to each edge
        conn = self.edgeConnections()
        # Bail out if some edge has more than two connected faces
        if conn.shape[1] != 2:
            GD.warning("Surface is not a manifold")
            return
        # Check size of okedges
        if okedges is not None:
            if okedges.ndim != 1 or okedges.shape[0] != self.nedges():
                raise ValueError,"okedges has incorrect shape"

        # Remember edges left for processing
        todo = ones((self.nedges(),),dtype=bool)
        elems = clip(asarray(startat),0,self.nfaces())
        prop = 0
        while elems.size > 0:
            # Store prop value for current elems
            p[elems] = prop
            yield p

            prop += front_increment

            # Determine border
            edges = unique(self.faces[elems])
            edges = edges[todo[edges]]
            if edges.size > 0:
                # flag edges as done
                todo[edges] = 0
                # take connected elements
                if okedges is None:
                    elems = conn[edges].ravel()
                else:
                    elems = conn[edges[okedges[edges]]].ravel()
                elems = elems[(elems >= 0) * (p[elems] < 0) ]
                if elems.size > 0:
                    continue

            # No more elements in this part: start a new one
            print "NO MORE ELEMENTS"
            elems = where(p<0)[0]
            if elems.size > 0:
                # Start a new part
                elems = elems[[0]]
                prop += 1


    def nodeFront(self,startat=0,front_increment=1):
        """Generator function returning the frontal elements.

        startat is an element number or list of numbers of the starting front.
        On first call, this function returns the starting front.
        Each next() call returns the next front.
        """
        p = -ones((self.nfaces()),dtype=int)
        if self.nfaces() <= 0:
            return
        # Construct table of elements connected to each element
        adj = self.nodeAdjacency()

        # Remember nodes left for processing
        todo = ones((self.npoints(),),dtype=bool)
        elems = clip(asarray(startat),0,self.nfaces())
        prop = 0
        while elems.size > 0:
            # Store prop value for current elems
            p[elems] = prop
            yield p

            prop += front_increment

            # Determine adjacent elements
            elems = unique1d(adj[elems])
            elems = elems[(elems >= 0) * (p[elems] < 0) ]
            if elems.size > 0:
                continue

            # No more elements in this part: start a new one
            elems = where(p<0)[0]
            if elems.size > 0:
                # Start a new part
                elems = elems[[0]]
                prop += 1


    def walkEdgeFront(self,startat=0,nsteps=-1,okedges=None,front_increment=1):
        for p in self.edgeFront(startat=startat,okedges=okedges,front_increment=front_increment):
            #print "NSTEPS=%d"%nsteps
            #print p
            if nsteps > 0:
                nsteps -= 1
            elif nsteps == 0:
                break
        return p


    def walkNodeFront(self,startat=0,nsteps=-1,front_increment=1):
        for p in self.nodeFront(startat=startat,front_increment=front_increment):
            if nsteps > 0:
                nsteps -= 1
            elif nsteps == 0:
                break
        return p


    def growSelection(self,sel,mode='node',nsteps=1):
        """Grows a selection of a surface.

        p is a single element number or a list of numbers.
        The return value is a list of element numbers obtained by
        growing the front nsteps times.
        The mode argument specifies how a single frontal step is done:
        'node' : include all elements that have a node in common,
        'edge' : include all elements that have an edge in common.
        """
        if mode == 'node':
            p = self.walkNodeFront(startat=sel,nsteps=nsteps)
        elif mode == 'edge':
            p = self.walkEdgeFront(startat=sel,nsteps=nsteps)
        return where(p>=0)[0]
    

    def partitionByEdgeFront(self,okedges,firstprop=0,startat=0):
        """Detects different parts of the surface using a frontal method.

        okedges flags the edges where the two adjacent triangles are to be
        in the same part of the surface.
        startat is a list of elements that are in the first part. 
        The partitioning is returned as a property type array having a value
        corresponding to the part number. The lowest property number will be
        firstprop
        """
        return firstprop + self.walkEdgeFront(startat=startat,okedges=okedges,front_increment=0)
    

    def partitionByNodeFront(self,firstprop=0,startat=0):
        """Detects different parts of the surface using a frontal method.

        okedges flags the edges where the two adjacent triangles are to be
        in the same part of the surface.
        startat is a list of elements that are in the first part. 
        The partitioning is returned as a property type array having a value
        corresponding to the part number. The lowest property number will be
        firstprop
        """
        return firstprop + self.walkNodeFront(startat=startat,front_increment=0)


    def partitionByConnection(self):
        return self.partitionByNodeFront()


    def partitionByAngle(self,angle=180.,firstprop=0,startat=0):
        conn = self.edgeConnections()
        # Flag edges that connect two faces
        conn2 = (conn >= 0).sum(axis=-1) == 2
        # compute normals and flag small angles over edges
        cosangle = cosd(angle)
        n = self.areaNormals()[1][conn[conn2]]
        small_angle = ones(conn2.shape,dtype=bool)
        small_angle[conn2] = dotpr(n[:,0],n[:,1]) >= cosangle
        return firstprop + self.partitionByEdgeFront(small_angle)


    def cutAtPlane(self,*args,**kargs):
        """Cut a surface with a plane."""
        self.__init__(self.toFormex().cutAtPlane(*args,**kargs))


    def connectedElements(self,target,elemlist=None):
        """Return the elements from list connected with target"""
        if elemlist is None:
            A = self
            elemlist = arange(self.nelems())
        else:
            A = self.select(elemlist)
        if target not in elemlist:
            return []
        
        p = A.partitionByConnection()
        prop = p[elemlist == target]
        return elemlist[p==prop]


##################  Smooth a surface #############################

    def smoothLowPass(self,n_iterations=2,lambda_value=0.5):
        """Smooth the surface using a low-pass filter."""
        mu_value = -1.02*lambda_value
        adj = adjacencyList(self.edges)
        bound_edges = self.borderEdgeNrs()
        inter_vertex = resize(True,self.ncoords())
        inter_vertex[unique1d(self.edges[bound_edges])] = False
        inter_vertices = where(inter_vertex)[0]
        p = self.coords
        for step in range(n_iterations):
            p[inter_vertex] = asarray([p[i] + lambda_value*(p[adj[i]]-p[i]).mean(0) for i in inter_vertices])
            p[inter_vertex] = asarray([p[i] + mu_value*(p[adj[i]]-p[i]).mean(0) for i in inter_vertices])
    
    
    def smoothLaplaceHC(self,n_iterations=2,lambda_value=0.5,alpha=0.,beta=0.2):
        """Smooth the surface using a Laplace filter and HC algorithm."""
        adj = adjacencyList(self.edges)
        bound_edges = self.borderEdgeNrs()
        inter_vertex = resize(True,self.ncoords())
        inter_vertex[unique1d(self.edges[bound_edges])] = False
        inter_vertices = where(inter_vertex)[0]    
        o = self.coords.copy()
        p = self.coords
        for step in range(n_iterations):
            pn = [ p[i] + lambda_value*(p[adj[i]]-p[i]).mean(0) for i in range(len(adj)) ]
            b = pn - (alpha*o + (1-alpha)*p)
            p[inter_vertex] = asarray([pn[i] - (beta*b[i] + (1-beta)*b[adj[i]].mean(0)) for i in inter_vertices])


########################## Methods using GTS #############################

    def check(self,verbose=False):
        """Check the surface using gtscheck."""
        cmd = 'gtscheck'
        if verbose:
            cmd += ' -v'
        tmp = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Checking with command\n %s" % cmd)
        cmd += ' < %s' % tmp
        sta,out = runCommand(cmd,False)
        os.remove(tmp)
        GD.message(out)
        if sta == 0:
            GD.message('The surface is a closed, orientable non self-intersecting manifold')
 

    def split(self,base,verbose=False):
        """Check the surface using gtscheck."""
        cmd = 'gtssplit -v %s' % base
        if verbose:
            cmd += ' -v'
        tmp = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Splitting with command\n %s" % cmd)
        cmd += ' < %s' % tmp
        sta,out = runCommand(cmd)
        os.remove(tmp)
        if sta or verbose:
            GD.message(out)
   

    def coarsen(self,min_edges=None,max_cost=None,
                mid_vertex=False, length_cost=False, max_fold = 1.0,
                volume_weight=0.5, boundary_weight=0.5, shape_weight=0.0,
                progressive=False, log=False, verbose=False):
        """Coarsen the surface using gtscoarsen."""
        if min_edges is None and max_cost is None:
            min_edges = self.nedges() / 2
        cmd = 'gtscoarsen'
        if min_edges:
            cmd += ' -n %d' % min_edges
        if max_cost:
            cmd += ' -c %d' % max_cost
        if mid_vertex:
            cmd += ' -m'
        if length_cost:
            cmd += ' -l'
        if max_fold:
            cmd += ' -f %f' % max_fold
        cmd += ' -w %f' % volume_weight
        cmd += ' -b %f' % boundary_weight
        cmd += ' -s %f' % shape_weight
        if progressive:
            cmd += ' -p'
        if log:
            cmd += ' -L'
        if verbose:
            cmd += ' -v'
        tmp = tempfile.mktemp('.gts')
        tmp1 = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Coarsening with command\n %s" % cmd)
        cmd += ' < %s > %s' % (tmp,tmp1)
        sta,out = runCommand(cmd)
        os.remove(tmp)
        if sta or verbose:
            GD.message(out)
        GD.message("Reading coarsened model from %s" % tmp1)
        self.__init__(*read_gts(tmp1))        
        os.remove(tmp1)
   

    def refine(self,max_edges=None,min_cost=None,
               log=False, verbose=False):
        """Refine the surface using gtsrefine."""
        if max_edges is None and min_cost is None:
            max_edges = self.nedges() * 2
        cmd = 'gtsrefine'
        if max_edges:
            cmd += ' -n %d' % max_edges
        if min_cost:
            cmd += ' -c %d' % min_cost
        if log:
            cmd += ' -L'
        if verbose:
            cmd += ' -v'
        tmp = tempfile.mktemp('.gts')
        tmp1 = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Refining with command\n %s" % cmd)
        cmd += ' < %s > %s' % (tmp,tmp1)
        sta,out = runCommand(cmd)
        os.remove(tmp)
        if sta or verbose:
            GD.message(out)
        GD.message("Reading refined model from %s" % tmp1)
        self.__init__(*read_gts(tmp1))        
        os.remove(tmp1)


    def smooth(self,lambda_value=0.5,n_iterations=2,
               fold_smoothing=None,verbose=False):
        """Smooth the surface using gtssmooth."""
        cmd = 'gtssmooth'
        if fold_smoothing:
            cmd += ' -f %s' % fold_smoothing
        cmd += ' %s %s' % (lambda_value,n_iterations)
        if verbose:
            cmd += ' -v'
        tmp = tempfile.mktemp('.gts')
        tmp1 = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Smoothing with command\n %s" % cmd)
        cmd += ' < %s > %s' % (tmp,tmp1)
        sta,out = runCommand(cmd)
        os.remove(tmp)
        if sta or verbose:
            GD.message(out)
        GD.message("Reading smoothed model from %s" % tmp1)
        self.__init__(*read_gts(tmp1))        
        os.remove(tmp1)


#### THIS FUNCTION RETURNS A NEW SURFACE
#### WE MIGHT DO THIS IN FUTURE FOR ALL SURFACE PROCESSING

    def boolean(self,surf,op,inter=False,check=False,verbose=False):
        """Perform a boolean operation with surface surf.

        """
        ops = {'+':'union', '-':'diff', '*':'inter'}
        cmd = 'gtsset'
        if inter:
            cmd += ' -i'
        if check:
            cmd += ' -s'
        if verbose:
            cmd += ' -v'
        cmd += ' '+ops[op]
        tmp = tempfile.mktemp('.gts')
        tmp1 = tempfile.mktemp('.gts')
        tmp2 = tempfile.mktemp('.gts')
        GD.message("Writing temp file %s" % tmp)
        self.write(tmp,'gts')
        GD.message("Writing temp file %s" % tmp1)
        surf.write(tmp1,'gts')
        GD.message("Performing boolean operation with command\n %s" % cmd)
        cmd += ' %s %s > %s' % (tmp,tmp1,tmp2)
        sta,out = runCommand(cmd)
        os.remove(tmp)
        os.remove(tmp1)
        if sta or verbose:
            GD.message(out)
        GD.message("Reading result from %s" % tmp2)
        S = TriSurface.read(tmp2)        
        os.remove(tmp2)
        return S



##########################################################################
################# Non-member and obsolete functions ######################

def read_error(cnt,line):
    """Raise an error on reading the stl file."""
    raise RuntimeError,"Invalid .stl format while reading line %s\n%s" % (cnt,line)


def degenerate(area,norm):
    """Return a list of the degenerate faces according to area and normals.

    A face is degenerate if its surface is less or equal to zero or the
    normal has a nan.
    """
    return unique(concatenate([where(area<=0)[0],where(isnan(norm))[0]]))



def magic_numbers(elems,magic):
    elems = elems.astype(int64)
    elems.sort(axis=1)
    mag = ( elems[:,0] * magic + elems[:,1] ) * magic + elems[:,2]
    return mag


def demagic(mag,magic):
    first2,third = mag / magic, mag % magic
    first,second = first2 / magic, first2 % magic
    return column_stack([first,second,third]).astype(int32)


def find_row(mat,row,nmatch=None):
    """Find all rows in matrix matching given row."""
    if nmatch is None:
        nmatch = mat.shape[1]
    return where((mat == row).sum(axis=1) == nmatch)[0]


def find_nodes(nodes,coords):
    """Find nodes with given coordinates in a node set.

    nodes is a (nnodes,3) float array of coordinates.
    coords is a (npts,3) float array of coordinates.

    Returns a (n,) integer array with ALL the node numbers matching EXACTLY
    ALL the coordinates of ANY of the given points.
    """
    return concatenate([ find_row(nodes,c) for c in coords])


def find_first_nodes(nodes,coords):
    """Find nodes with given coordinates in a node set.

    nodes is a (nnodes,3) float array of coordinates.
    coords is a (npts,3) float array of coordinates.

    Returns a (n,) integer array with THE FIRST node number matching EXACTLY
    ALL the coordinates of EACH of the given points.
    """
    res = [ find_row(nodes,c) for c in coords ]
    return array([ r[0] for r in res ])



def find_triangles(elems,triangles):
    """Find triangles with given node numbers in a surface mesh.

    elems is a (nelems,3) integer array of triangles.
    triangles is a (ntri,3) integer array of triangles to find.
    
    Returns a (ntri,) integer array with the triangles numbers.
    """
    magic = elems.max()+1

    mag1 = magic_numbers(elems,magic)
    mag2 = magic_numbers(triangles,magic)

    nelems = elems.shape[0]
    srt = mag1.argsort()
    old = arange(nelems)[srt]
    mag1 = mag1[srt]
    pos = mag1.searchsorted(mag2)
    tri = where(mag1[pos]==mag2, old[pos], -1)
    return tri
    

if __name__ == 'draw':

    import simple

    clear()
    n = 4
    F = simple.line([0.,0.,0.],[1.,0.,0.],n=n).setProp(1)
    G = F.reverseElements().translate([0.,0.25,0.]).setProp(2)
    H = connect([F,G]).setProp(3)
    draw(F+G+H)
    
    E = Edges(F+G+H)

    print E.coords
    print E.elems

    orient = E.setOrient()
    print orient

    A = E.elems
    print A
    print roll(A[1-orient],-1,axis=1)
    print A
    exit()
    
    print E.elems[:,where(orient,0,1)]

    A
    print roll(E.elems,-1,axis=1)
    A = E.elems
    B = roll(E.elems,-1,axis=1)
    C = self.orient
    print A.shape,B.shape
    peinr 
    #print E.getElems()
    #print E.getElems(True)
    
# End
