import cv2
from easy_memmap import EasyMemmap

v = cv2.VideoCapture(0)
_, image = v.read()

m = EasyMemmap(mode="w", name="mycamera2")

while True:
    _, image = v.read()
    m.write(image)
    cv2.imshow("Writer", image)
    cv2.waitKey(1)