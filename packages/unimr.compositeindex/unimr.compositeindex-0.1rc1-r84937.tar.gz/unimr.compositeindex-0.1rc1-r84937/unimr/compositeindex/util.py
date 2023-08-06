

_marker = []

class PermuteKeywordList:
    """
        returns a flat list of a sequential
        permutation of keyword lists.
        Example:

        A = [[1,2,3],[4,5],[6,7]]

        tree permutation
 
               6
              / 
             4
            / \
           /   7
          1   
           \   6
            \ /
             5
              \
               7
 
               6
              / 
             4
            / \
           /   7
          2   
           \   6
            \ /
             5
              \
               7
          
               6
              / 
             4
            / \
           /   7
          3   
           \   6
            \ /
             5
              \
               7

     
     corresponds to following flat list

         [[1,4,6],[1,4,7],[1,5,6],[1,5,7],
          [2,4,6],[2,4,7],[2,5,6],[2,5,7],
          [3,4,6],[3,4,7],[3,5,6],[3,5,7]]


    """

    
    
    def __init__(self,A):
        """ A -- list of keyword lists"""
        self.keys=[]
        self.walking(A)
        

    def walking(self,A,f=_marker):

        if f is _marker:
            f = []

        if A[:1]:
            first = A[0]
            for l in first:
                next = f[:] + [l]
                self.walking(A[1:],next)
            
        else:
            self.keys.append(tuple(f))




