# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

class DistinctCounter(dict):
    """
    Splits rows into categories and then counts the number
    of hits in each category.
    """

    def __init__(self,format,categorise):
        self.format = format
        self.categorise = categorise

    def process(self,obj):
        self[self.categorise(obj)]=True

    def count(self):
        return len(self.keys())
    
    def formatted(self):
        return self.format % self.count()

    
