import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('input-files/messi.jpg')
mask = np.zeros(img.shape[:2], np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)
rect = (50, 50, 450, 290)
cv.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_RECT)
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
img = img*mask2[:, :, np.newaxis]
plt.imshow(img), plt.show()
# cv.imwrite('output-files/messi-result-data_n.jpg', img)