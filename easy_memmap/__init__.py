import numpy as np

class EasyMemmap(object):
    def __init__(self, memmap_path = "/tmp"):
        super(EasyMemmap,self).__init__()
        self.memmap_path = memmap_path

    
    def write(self, image):
        pass

    def read(self, file):
        pass