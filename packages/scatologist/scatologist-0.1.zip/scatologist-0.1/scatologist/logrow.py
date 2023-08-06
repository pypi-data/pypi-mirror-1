# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.
from datetime import datetime

class LogRow:

    valid = False
    
    def __init__(self, line, path):
        mo = self.regex.match(line)
        if mo is None:
            return
        self.valid = True
        self.path = path # file system path
        for key, value in mo.groupdict().items():
            setattr(self, key, value)
        self.raw = mo.group(0)
        self.post_process()
        
    def post_process(self):
        pass
    
    def __getitem__(self,name):
        return getattr(self,name)

    def __repr__(self):
        return '<LogRow %s - %s>' % (self.timestamp,self.uri)
