
# Camera Calibration

_You can view [IPython Nootebook](README.ipynb) report._

----

## Contents

- [GOAL](#GOAL)
- [Basics](#Basics)
- [Code](#Code)
  - [Setup](#Setup)
  - [Calibration](#Calibration)
  - [Undistortion](#Undistortion)
- [Re-projection Error](#Re-projection-Error)
- [Exercises](#Exercises)

## GOAL

In this section:

- We will learn about distortions in camera, intrinsic and extrinsic parameters of camera etc.
- We will learn to find these parameters, undistort images etc.

## Basics

Today's cheap pinhole cameras introduces a lot of distortion to images. Two major distortions are radial distortion and tangential distortion.

Due to radial distortion, straight lines will appear curved. Its effect is more as we move away from the center of image. For example, one image is shown below, where two edges of a chess board are marked with red lines. But you can see that border is not a straight line and doesn't match with the red line. All the expected straight lines are bulged out. Visit [Distortion (optics)](https://en.wikipedia.org/wiki/Distortion_%28optics%29) for more details.

![calib-radial](../../data/calib-radial.jpg)

This distortion is represented as follows:

$$ 
x_{distorted} = x( 1 + k_1 r^2 + k_2 r^4 + k_3 r^6) \\ y_{distorted} = y( 1 + k_1 r^2 + k_2 r^4 + k_3 r^6)
$$

Similarly, another distortion is the tangential distortion which occurs because image taking lense is not aligned perfectly parallel to the imaging plane. So some areas in image may look nearer than expected. It is represented as below:

$$
x_{distorted} = x + [ 2p_1xy + p_2(r^2+2x^2)] \\ y_{distorted} = y + [ p_1(r^2+ 2y^2)+ 2p_2xy]
$$

In short, we need to find five parameters, known as distortion coefficients given by:

$$
Distortion \; coefficients=(k_1 \hspace{10pt} k_2 \hspace{10pt} p_1 \hspace{10pt} p_2 \hspace{10pt} k_3)
$$

In addition to this, we need to find a few more information, like intrinsic and extrinsic parameters of a camera. Intrinsic parameters are specific to a camera. It includes information like focal length $ (f_x, f_y) $, optical centers $ (c_x, c_y) $ etc. It is also called camera matrix. It depends on the camera only, so once calculated, it can be stored for future purposes. It is expressed as a 3x3 matrix:

$$
camera \; matrix = \left [ \begin{matrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{matrix} \right ]
$$

Extrinsic parameters corresponds to rotation and translation vectors which translates a coordinates of a 3D point to a coordinate system.

For stereo applications, these distortions need to be corrected first. To find all these parameters, what we have to do is to provide some sample images of a well defined pattern (eg, chess board). We find some specific points in it ( square corners in chess board). We know its coordinates in real world space and we know its coordinates in image. With these data, some mathematical problem is solved in background to get the distortion coefficients. That is the summary of the whole story. For better results, we need atleast 10 test patterns.

## Code

As mentioned above, we need atleast 10 test patterns for camera calibration. OpenCV comes with some images of chess board (see [opencv/samples/data/left01.jpg – left14.jpg](https://github.com/opencv/opencv/tree/master/samples/data)), so we will utilize it. For sake of understanding, consider just one image of a chess board. Important input datas needed for camera calibration is a set of 3D real world points and its corresponding 2D image points. 2D image points are OK which we can easily find from the image (these image points are locations where two black squares touch each other in the chess boards).

What about the 3D points from real world space? Those images are taken from a static camera and chess boards are placed at different locations and orientations. So we need to know $ (X,Y,Z) $ values. But for simplicity, we can say chess board was kept stationary at XY plane, (so Z=0 always) and camera was moved accordingly. This consideration helps us to find only X,Y values. Now for X,Y values, we can simply pass the points as (0,0), (1,0), (2,0), ... which denotes the location of points. In this case, the results we get will be in the scale of size of chess board square. But if we know the square size, (say 30 mm), and we can pass the values as (0,0), (30,0), (60,0), ..., we get the results in mm. (In this case, we don't know square size since we didn't take those images, so we pass in terms of square size).

3D points are called _object points_ and 2D image points are called _image points_.

### Setup

So to find pattern in chess board, we use the function, [cv.findChessboardCorners()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a). We also need to pass what kind of pattern we are looking, like 8x8 grid, 5x5 grid etc. In this example, we use 7x6 grid. (Normally a chess board has 8x8 squares and 7x7 internal corners). It returns the corner points and retval which will be True if pattern is obtained. These corners will be placed in an order (from left-to-right, top-to-bottom)

#### See also

> This function may not be able to find the required pattern in all the images. So one good option is to [write](https://docs.opencv.org/3.4.1/da/d56/classcv_1_1FileStorage.html#a26447446dd3fa0644684a045e16399fe) the code such that, it starts the camera and check each frame for required pattern. Once pattern is obtained, find the corners and store it in a list. Also provides some interval before reading next frame so that we can adjust our chess board in different direction. Continue this process until required number of good patterns are obtained. Even in the example provided here, we are not sure out of 14 images given, how many are good. So we [read](https://docs.opencv.org/3.4.1/de/dd9/classcv_1_1FileNode.html#ab24433dde37f770766481a91983e5f44) all the images and take the good ones.
    Instead of chess board, we can use some circular grid, but then use the function [cv.findCirclesGrid()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#gad1205c4b803a21597c7d6035f5efd775) to find the pattern. It is said that less number of images are enough when using circular grid.

Once we find the corners, we can increase their accuracy using [cv.cornerSubPix()](https://docs.opencv.org/3.4.1/dd/d1a/group__imgproc__feature.html#ga354e0d7c86d0d9da75de9b9701a9a87e). We can also draw the pattern using [cv.drawChessboardCorners()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga6a10b0bb120c4907e5eabbcd22319022). All these steps are included in below code:

```python
import numpy as np
import cv2 as cv
import glob
import re

# Termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0), ... , (6,5,0)
objp = np.zeros((6 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d points in real world space
imgpoints = []  # 2d points in image plane
images = glob.glob("../../data/left*.jpg")

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)

    # If found, add object points, image points (after refining them)
    if ret is True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 6), corners2, ret)
        cv.imshow("Image", img)
        cv.waitKey(500)
cv.destroyAllWindows()
```

Three images with pattern drawn on it are shown below:

![calib-res](../../data/calib-result-1.png)

### Calibration

So now we have our object points and image points we are ready to go for calibration. For that we use the function, [cv.calibrateCamera()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga3207604e4b1a1758aa66acb6ed5aa65d). It returns the camera matrix, distortion coefficients, rotation and translation vectors etc.

```python
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
```

### Undistortion

We have got what we were trying. Now we can take an image and undistort it. OpenCV comes with two methods, we will see both. But before that, we can refine the camera matrix based on a free scaling parameter using [cv.getOptimalNewCameraMatrix()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga7a6c4e032c97f03ba747966e6ad862b1). If the scaling parameter _alpha=0_, it returns undistorted image with minimum unwanted pixels. So it may even remove some pixels at image corners. If _alpha=1_, all pixels are retained with some extra black images. It also returns an image ROI which can be used to crop the result.

So we take a new image (left12.jpg in this case, that is the first image in this chapter).

```python
img = cv.imread("../../data/left12.jpg")
h, w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
```
#### 1. Using [cv.undistort()](https://docs.opencv.org/3.4.1/da/d54/group__imgproc__transform.html#ga69f2545a8b62a6b0fc2ee060dc30559d)

This is the shortest path. Just call the function and use ROI obtained above to crop the result.

```python
# undistort using cv.undistort()
dst = cv.undistort(img, mtx, dist, None, newcameramtx)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite("output-files/calib-result.png", dst)
```

#### 2. Using remapping

This is curved path. First find a mapping function from distorted image to undistorted image. Then use the remap function.

```python
# undistort using remapping
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx,
                                        (w, h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite("output-files/calib-result.png", dst)
```

Both the methods give the same result. See the result below:

![calib-result](../../data/calib-result-2.png)

You can see in the result that all the edges are straight.

Now you can store the camera matrix and distortion coefficients using write functions in Numpy (np.savez, np.savetxt etc) for future uses.

## Re-projection Error

Re-projection error gives a good estimation of just how exact is the found parameters. This should be as close to zero as possible. Given the intrinsic, distortion, rotation and translation matrices, we first transform the object point to image point using [cv.projectPoints()](https://docs.opencv.org/3.4.1/d9/d0c/group__calib3d.html#ga1019495a2c8d1743ed5cc23fa0daff8c). Then we calculate the absolute norm between what we got with our transformation and the corner finding algorithm. To find the average error we calculate the arithmetical mean of the errors calculate for all the calibration images.

```python
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i],
                                     tvecs[i], mtx, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
    mean_error += error
print("total error: {}".format(mean_error/len(objpoints)))
```

## Exercises 

1. Try camera calibration with circular grid.