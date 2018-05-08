import cv2
from easy_memmap import EasyMemmap, MultiImagesMemmap
import time

m = MultiImagesMemmap(mode="r")
print("Available streams: {}".format(EasyMemmap.get_memmap_files()))

m.wait_until_available("mycamera3")

print("Labels: {}".format(m.get_labels()))

while True:
    image0 = m.read("C")
    image1 = m.read("B")
    cv2.imshow("Reader0", image0)
    cv2.imshow("Reader1", image1)
    cv2.waitKey(1)