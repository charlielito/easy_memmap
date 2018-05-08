import cv2
import numpy as np
from easy_memmap import MultiImagesMemmap

v0 = cv2.VideoCapture(0)
v1 = cv2.VideoCapture(4)

labels = ["C", "B", "F"]
m = MultiImagesMemmap(mode="w", name="mycamera3", labels=labels)
print(m.get_labels())

while True:
    _, image0 = v0.read()
    _, image1 = v1.read()
    data = np.concatenate([image0, image1], axis=2)
    m.write(data)
    cv2.imshow("Writer0", image0)
    cv2.imshow("Writer1", image1)
    cv2.waitKey(1)