import numpy as np
import os
import re
import time
import json


class EasyMemmap(object):
    PREFIX = "easy_memmap"
    CONF = "shape"  
    DATA = "data"
    NUMPY_TYPES = [np.int8, np.int16, np.int32, np.int64,
                  np.uint8, np.uint16, np.uint32, np.uint64,
                  np.float16, np.float32, np.float64, np.bool]
    MEMMAP_PATH = "/tmp"

    def __init__(self, mode, memmap_path = "/tmp", name = None):
        super(EasyMemmap,self).__init__()
        self.MEMMAP_PATH = memmap_path
        self.mode = mode
        self.memmap_file = None

        if mode == "w":
            self.name = name if name is not None else self._get_next_name()
        else:
            self.name = name
            if name is not None:
                if self._check_file(self.name):
                    self._init_memmap_r()

    def _create_folder(self):
        path = self.get_full_name()
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            print("Memmap folder already exists, ignoring")

    # In case of no name, the name is just the next integer starting from 0
    def _get_next_name(self):
        numeric_names = self._get_numeric_memmap_files()
        if not numeric_names:
            return "0"
        else:
            return str(numeric_names[-1]+1)

    # Get only names that are numeric (created mostly by default)
    def _get_numeric_memmap_files(self):
        folders = self.get_memmap_files()
        numeric_dirs = []
        for folder in folders:
            if folder.isdigit():
                numeric_dirs.append(int(folder))
        return sorted(numeric_dirs)

    # Init for writing mode
    def _init_memmap_w(self, data):

        self._create_folder()

        shape = data.shape
        shape_memmap = np.memmap(os.path.join(self.get_full_name(),EasyMemmap.CONF), dtype = np.uint16,
                                              mode="w+", shape = (len(shape)+1,) )
        # the last number after the shape refers to the numpy type index according to the list
        # NUMPY_TYPES supported
        shape_list = list(shape)
        index_type = [i for i, val in enumerate(EasyMemmap.NUMPY_TYPES) if val == data.dtype][0]
        shape_list.append(index_type)
        shape_memmap[:] = shape_list[:]

        self.memmap_file = np.memmap(os.path.join(self.get_full_name(),EasyMemmap.DATA), dtype = data.dtype, mode = 'w+',
                                shape = shape)
        self.memmap_file[:] = data[:]

    # Init for reading mode
    def _init_memmap_r(self):
        shape_memmap = np.memmap(os.path.join(self.get_full_name(),EasyMemmap.CONF), dtype = np.uint16,
                                              mode = "r",)
        self.memmap_file = np.memmap(os.path.join(self.get_full_name(), EasyMemmap.DATA), 
                                    dtype = EasyMemmap.NUMPY_TYPES[shape_memmap[-1]], 
                                    mode = 'r', shape = tuple(shape_memmap[:-1]) )
    
    # Checks if a file or memmap folder exists in the easy memmap domain
    def _check_file(self, name):
        available_files = self.get_memmap_files()
        if not (name in available_files):
            print("File {} not found".format(name))
            return False
        else:
            return True       

    # Sets name, only for reading mode. In writing mode the name is set at beginning
    # Return true if the file exists and the variable could be set
    def set_name(self, name):
        if self.mode == "r":
            if self._check_file(name):
                self.name = name
                self._init_memmap_r()
                return True
            else:
                return False
        else:
            print('In "w" mode changing name after initialization is not allowed')
            return False

    # Waits until the file is available or a timer is out
    def wait_until_available(self, name = None, time2wait = None):
        time2wait = time2wait if time2wait is not None else 1000000 #very big number
        name = self.name if name is None else name
        timer = time.time()
        while not self.set_name(name) and (time.time() - timer < time2wait):
            time.sleep(2)

    
    # Get the absolute path to the file
    def get_full_name(self):
        if self.name is not None:
            return os.path.join(self.MEMMAP_PATH, EasyMemmap.PREFIX + "_" + self.name)
        else:
            return None

    # Return all the posible easy-memmap compatible folders
    @classmethod    
    def get_memmap_files(self, path=None):
        if path is not None:
            dirs = next(os.walk(path))[1]
        else:
            dirs = next(os.walk(self.MEMMAP_PATH))[1]
        memmap_dirs = []
        p = re.compile(EasyMemmap.PREFIX + r"_(?P<name>.*)")
        for _dir in dirs:
            info = p.match(_dir)
            if info:
                dinfo = info.groupdict()
                memmap_dirs.append(dinfo["name"])
        return memmap_dirs

    # Writes data to file
    def write(self, data):
        if self.memmap_file is None:
            self._init_memmap_w(data)
        else:
            self.memmap_file[:] = data[:]
    
    # Reads data from file
    def read(self):
        if self.memmap_file is None:
            return None
        else:
            return self.memmap_file


# Class for handling RGB Images (3D imarrays only) stack together with a meta data on them (labels)
class MultiImagesMemmap(EasyMemmap):
    LABELS_FILENAME = "meta.json"
    
    def __init__(self, mode, labels = None, memmap_path = "/tmp", name = None, axis = 2):
        super(MultiImagesMemmap,self).__init__(mode, memmap_path, name)
        self.labels_dict =  None
        
        if self.mode == "w":
            if not (0<=axis<=2) and isinstance(axis, int):
                raise RuntimeError("Axis must be an integer value between 0 and 2 [0-2]")

            self.axis = axis

            if not labels:
                raise RuntimeError("Labels string list must be provided in initialization")
            
            else:
                self.labels_dict = {key:value for value,key in enumerate(labels)}
                self.labels = labels
                self.num_labels = len(labels)

        else:
            if self.name is not None:
                if self._check_file(self.name):
                    self._load_labels()


    def _get_image(self, number):
        if self.memmap_file is None:
            return None
        else:
            axis_dim = self.memmap_file.shape[self.axis]
            base_dim = axis_dim//self.num_labels

            if self.axis == 2:
                return self.memmap_file[:,:,number*base_dim:number*base_dim+base_dim]
            elif self.axis == 1:
                return self.memmap_file[:,number*base_dim:number*base_dim+base_dim,:]
            elif self.axis == 0:
                return self.memmap_file[number*base_dim:number*base_dim+base_dim,:,:]
            else:
                return None

    def _load_labels(self):
        self.labels_dict = json.load(open(os.path.join(self.get_full_name(),self.LABELS_FILENAME)) ) #read camera number configuration
        # remove axis element from dict and save the result
        self.axis = self.labels_dict.pop("axis")
        self.num_labels = len(self.labels_dict.values()) 

    # Overload set name method to load the config.json or meta data for images
    def set_name(self, name):
        if EasyMemmap.set_name(self, name):
            self._load_labels()
            return True
        else:
            return False


    def get_labels(self):
        return self.labels_dict

    # Overload read method to read images if a key is provided
    def read(self, key = None):
        if key is None:
            return EasyMemmap.read(self)
        else:
            if self.memmap_file is None:
                return None
            else:
                if key in self.labels_dict:
                    return self._get_image(self.labels_dict[key])
                else:
                    return None

    # overload init memmap for writing to save locally a file with the meta data
    def _init_memmap_w(self, data):
        EasyMemmap._init_memmap_w(self, data)

        axis_len = self.memmap_file.shape[self.axis]
        # If number of images does not fit with the shape of the data, raise error
        if axis_len%self.num_labels != 0:
            raise RuntimeError(
                """
                Number of labels ({}) don't match in axis {} of data shape {}. 
                Number of images must match in the corresponding axis 
                of the data structure.  
                """.format(self.num_labels, self.axis, str(self.memmap_file.shape))
            )

        # DEPRECATED: before just dropped to fit the number of images
        # number_images = axis_len/self.num_labels     
        # if len(self.labels) > number_images: #elminate last labels
        #     self.labels = self.labels[:number_images]
        #     self.labels_dict = {key:value for value,key in enumerate(self.labels)}

        with open(os.path.join(self.get_full_name(), self.LABELS_FILENAME),'w') as fp: # save mapp dict as a Json
            # save also axis in config
            self.labels_dict.update(dict(axis=self.axis))
            json.dump(self.labels_dict,fp)