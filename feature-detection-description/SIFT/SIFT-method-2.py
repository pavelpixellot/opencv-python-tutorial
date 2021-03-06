import cv2 as cv

img = cv.imread("input-files/zaha-hadid.jpg")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
sift = cv.xfeatures2d.SIFT_create()
kp = sift.detect(gray, None)
kp, des = sift.compute(gray, kp)
img=cv.drawKeypoints(gray, kp, img, \
                     flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# cv.imwrite("output-files/sift_keypoints_4.jpg", img)
cv.imshow("Result", img)
k = cv.waitKey(0)
if k == 27:
    cv.destroyAllWindows()
