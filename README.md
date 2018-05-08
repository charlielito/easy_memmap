# Numpy Memmap easy wrapper for array manipulation

Python2/3 memmap wrapper to share arrays easily between processes in real time. 


## Installation

You can install `easy_memmap` from pip using

```
pip install easy_memmap
```

or using

```
pip install git+https://github.com/charlielito/easy_memmap
```


### Numpy [d]types supported 
The library accepts any type of the following supported by `numpy`

* `np.bool`
* `np.int8, np.int16, np.int32, np.int64`
* `np.uint8, np.uint16, np.uint32, np.uint64`
* `np.float16, np.float32, np.float64`


## Usage

The program that shares the array can be

```python
from easy_memmap import EasyMemmap
import numpy as np

m = EasyMemmap(mode="w", name="mytest")

data = np.zeros((480,640,4))
m.write(data)
```

And the programm that reads the array

```python
from easy_memmap import EasyMemmap

m = EasyMemmap(mode="r", name="mytest")

data = m.read()
```

The name of the `EasyMemmap` object needs to be the same, otherwise it won't be able to find the data and it will return `None`

To see other usages streaming in real time images from a web_camera, see `examples`