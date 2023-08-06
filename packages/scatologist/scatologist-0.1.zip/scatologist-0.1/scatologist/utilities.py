# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.


class AttributeCategoriser:

    def __init__(self,attribute):
        self.attribute = attribute

    def __call__(self,obj):
        return getattr(obj,self.attribute)
    
