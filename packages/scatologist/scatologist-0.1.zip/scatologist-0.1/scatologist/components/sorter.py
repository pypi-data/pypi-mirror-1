# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

class Sorter(list):
    """Keeps a list of the highest-most items,
    such as 10 longest response times"""

    def __init__(self,attribute_name,length,format,header=None):
        """attribute name is the attribute to sort on.
        A numeric attribute should be used.
        length is the number of items to keep in the list
        format is a format string to apply to each entry in the list.
        header is an optional header for the list"""
        self.attribute_name=attribute_name
        self.length=length
        self.header = header
        self.format = format

    def process(self,obj):
        """Append an object to the list and put it in the right place"""
        self.append((
            getattr(obj,self.attribute_name),
            obj
            ))
        self.sort()
        self[:]=self[-self.length:]

    def formatted(self):
        """Return a formatted version of the list."""
        self.reverse()
        result = [self.header or ('Highest '+self.attribute_name+':')]
        result.extend([self.format % row for key,row in self])
        return '\n'.join(result)
        
class AverageSorter(dict):
    """Stores all values seen for key_attribute. Then, for each
    key_attribute, the number of times it is seen is recorded along
    with the a running total of value_attribute, allowing the average
    highest items to be displayed"""

    def __init__(self,key_attribute,value_attribute,length,format,header=None):
        self.key_attribute = key_attribute
        self.value_attribute = value_attribute
        self.length = length
        self.format = format
        self.header = header

    def process(self,row):
        key = getattr(row,self.key_attribute)
        value = getattr(row,self.value_attribute)
        if key in self:
            count,sum = self[key]
        else:
            count,sum = 0,0.0
        count+=1
        sum+=value
        self[key]=count,sum

    def formatted(self):
        result = [self.header or ('Highest Average '+self.value_attribute+':')]
        for k,v in sorted(self.items(),
                          key=lambda i:i[1][1]/i[1][0],
                          reverse=True)[:self.length]:
            count,sum = v
            mean = sum/count
            result.append(self.format % dict(
                    key=k,
                    value=sum,
                    count=count,
                    mean=mean
                    ))
        return '\n'.join(result)
        
