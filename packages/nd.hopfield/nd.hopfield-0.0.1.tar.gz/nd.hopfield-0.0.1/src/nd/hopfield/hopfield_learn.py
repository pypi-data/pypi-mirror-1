## -*- coding: utf-8 -*- #############################################
#######################################################################
"""Hopfield Learn Class Using to Learn Simple
Hopfiled Network

$Id: hopfield_learn.py 50901 2008-04-02 06:40:00Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50901 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
                
class HopfieldNetwork(object) :
    def __init__(self,dimension) :
        self.data = [[ [0] for x in xrange(0,dimension)] for y in xrange(0,dimension)]                    
        self.dimension = dimension

    def prnt(self) :
        for vector in self.data :
            for item in vector :
                print "%8i" % item[0],
            print

    def step(self,vector) :
        if len(vector) != self.dimension :
            raise ValueError

        res = []            
        for sample in self.data :
            ou = 0
            for x,w in zip(vector,sample) :
                ou += x*w[0]
            if ou >= 0 :
                res.append(1)
            else :
                res.append(-1)
                
        return res
        
    def work(self,res) :
        vector = None 
        while res != vector :
            vector = res
            for item in vector :
                print "%8i" % item,
            print
            
            res = self.step(vector)                                                                                             
            
class HopfieldNetworkLearn(object) :
    def __init__(self) :
        pass
        
    def learn(self,samples) :
        length = len(samples)
        net = HopfieldNetwork(len(samples[0]))
        for sample in samples :
            for x1,vector in zip(sample,net.data) :
                for x2,w in zip(sample,vector) :
                    if x1 is not x2 :
                        w[0] += x1*x2
                        
        for vector in net.data :
            for w in vector :
                w[0] = float(w[0]) / length
                
        return net
        
                        
        
