# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 10:16:29 2021

@author: Mustafa
"""

    def shortest_dist(self, u, v):
        def helper(x, path, i):
            
#            print(i*'-' + 'Nodes: ', u, x)
            
            #Base Cases
            if x in path:
                return
            
            path = path + [x]
            
            if v in self.neighbors(x):
                self.relax(u, x, v)
                return
            
            if self.neighbors(x) == set():
                return
            
            #Recursive Step
            else:
                for neighbor, weight in self.neighbors(x):
                    
                    if (u, neighbor) not in self.dist:
                        self.dist[(u, neighbor)] = float('inf')
                        
                    self.relax(u, x, neighbor)
                    a = helper(neighbor, path, i+1)
                return
        
        for node in self.nodes()
        for n in range(len(self.nodes()) - 1):
            b = helper(u, [] ,0)