# The Vision Egg: ThreeDeeMath
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id: ThreeDeeMath.py 1271 2003-12-01 23:44:16Z astraw $

"""
Vertex and matrix operations - simulate OpenGL transforms.

"""

import math
import Numeric, MLab

__cvs__ = '$Revision: 1271 $'.split()[1]
__date__ = ' '.join('$Date: 2003-12-01 15:44:16 -0800 (Mon, 01 Dec 2003) $'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

def make_homogeneous_coord_rows(v):
    """Convert vertex (or row-wise vertices) into homogeneous coordinates."""
    v = Numeric.array(v,typecode=Numeric.Float) # copy
    if len(v.shape) == 1:
        v = v[Numeric.NewAxis,:] # make a rank-2 array
    if v.shape[1] == 3:
        ws = Numeric.ones((v.shape[0],1),typecode=Numeric.Float)
        v = Numeric.concatenate( (v,ws), axis=1 )
    return v

def normalize_homogeneous_rows(v):
    v = Numeric.asarray(v)
    homog = make_homogeneous_coord_rows(v)
    r = (homog/homog[:,3,Numeric.NewAxis])[:,:3]
    if len(homog.shape) > len(v.shape):
        r = Numeric.reshape(r,(3,))
    return r

class TransformMatrix:
    def __init__(self,matrix=None):
        if matrix is None:
            self.matrix = MLab.eye(4,typecode=Numeric.Float)
        else:
            self.matrix = matrix

    def __make_normalized_vert3(self, x, y, z ):
        mag = math.sqrt( x**2 + y**2 + z**2 )
        return Numeric.array((x,y,z))/mag

    def rotate(self, angle_degrees, axis_x, axis_y, axis_z ):
        """Follows the right hand rule.

        I visualize the right hand rule most easily as follows:
        Naturally, using your right hand, wrap it around the axis of
        rotation. Your fingers now point in the direction of rotation.
        
        """
        angleRadians = angle_degrees / 180.0 * math.pi
        u = self.__make_normalized_vert3(axis_x, axis_y, axis_z )
        u=-u #follow right hand rule
        S = Numeric.zeros( (3,3), Numeric.Float )
        S[0,1] = -u[2]
        S[0,2] = u[1]
        S[1,0] = u[2]
        S[1,2] = -u[0]
        S[2,0] = -u[1]
        S[2,1] = u[0]
        U = Numeric.outerproduct(u,u)
        R = U + math.cos(angleRadians)*(MLab.eye(3)-U) + math.sin(angleRadians)*S
        R = Numeric.concatenate( (R,Numeric.zeros( (3,1), Numeric.Float)), axis=1)
        R = Numeric.concatenate( (R,Numeric.zeros( (1,4), Numeric.Float)), axis=0)
        R[3,3] = 1.0
        self.matrix = Numeric.matrixmultiply(R,self.matrix)

    def translate(self, x, y, z):
        T = MLab.eye(4,typecode=Numeric.Float)
        T[3,0] = x
        T[3,1] = y
        T[3,2] = z
        self.matrix = Numeric.matrixmultiply(T,self.matrix)
    
    def scale(self, x, y, z):
        T = MLab.eye(4,typecode=Numeric.Float)
        T[0,0] = x
        T[1,1] = y
        T[2,2] = z
        self.matrix = Numeric.matrixmultiply(T,self.matrix)

    def get_matrix(self):
        return self.matrix
    
    def transform_vertices(self,verts):
        v = Numeric.asarray(verts)
        homog = make_homogeneous_coord_rows(v)
        r = Numeric.matrixmultiply(homog,self.matrix)
        if len(homog.shape) > len(v.shape):
            r = Numeric.reshape(r,(4,))
        return r
