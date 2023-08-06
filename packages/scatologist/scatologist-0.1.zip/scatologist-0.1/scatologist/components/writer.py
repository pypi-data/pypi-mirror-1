# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

class Writer:

    def __init__(self,filename,format_string):
        self.filename = filename
        self.format_string = format_string
        self.count = 0
        
    def process(self,row):
        f = open(self.filename,'a')
        f.write(self.format_string % row.__dict__)
        f.close()
        self.count += 1
        
    def formatted(self):
        return '%i rows written to %s' % (self.count,self.filename)
    
