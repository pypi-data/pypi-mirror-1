# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

class Histogram(dict):
    """Stores items in specified buckets"""

    def __init__(self,attribute_name,boundaries,format,header=None):
        """attribute name is the attribute to process.
        A numeric attribute should be used.
        boundaries is a tuple of the cut-off points
        format is a format string that may contain %(boundary)i
        for the boundary, %(band)s for the band and %(percentage)d
        for the percentage.
        %(cumulative)d may also be used for the cumulative percentage.
        header will be put at the top of the list if supplied"""
        self.attribute_name = attribute_name
        self.total = 0.0
        self.boundaries = boundaries
        self.format = format
        self.header = header
        for boundary in boundaries:
            self[boundary] = 0.0

    def process(self,obj):
        """Put an object in the appropriate buckets"""
        value = getattr(obj,self.attribute_name)
        for boundary in self.boundaries:
            if value < boundary:
                self[boundary] += 1
        self.total += 1

    def formatted(self):
        """Return a formatted version of the buckets."""
        result = []
        for i in range(len(self.boundaries)):
            boundary = self.boundaries[i]
            try:
                cumulative = 100*self[boundary]/self.total
                if i > 0:
                    percentage = cumulative - result[-1]['cumulative']
                else:
                    percentage = cumulative
            except ZeroDivisionError:
                percentage = -1
            if i==0:
                band = 'less than %s' % boundary
            else:
                band = 'between %s and %s' % (result[-1]['boundary'],boundary)
            result.append({
                'boundary':boundary,
                'percentage':percentage,
                'cumulative':cumulative,
                'band':band,
                })
        result.append({
                'boundary':0,
                'percentage':100.0-result[-1]['cumulative'],
                'cumulative':100,
                'band':'greater than %s' % result[-1]['boundary'],
                })
            
        return (self.header and self.header+'\n' or '')+'\n'.join([self.format % row for row in result])
        
