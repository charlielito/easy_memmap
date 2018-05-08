import cv2
from easy_memmap import EasyMemmap
import time

m = EasyMemmap(mode="r")
print("Available streams: {}".format(EasyMemmap.get_memmap_files()))

while not m.set_name("mycamera2"):
    print("Waiting for stream to be ready...")
    time.sleep(2)

while True:
    image = m.read()
    cv2.imshow("Reader", image)
    cv2.waitKey(1)