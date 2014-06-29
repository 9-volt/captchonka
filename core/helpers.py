import cv2.cv as cv

# class ImageHelpers(object):
def smoothImage(im, nbiter=0, filter=cv.CV_GAUSSIAN):
  for i in range(nbiter):
    cv.Smooth(im, im, filter)

def openCloseImage(im, nbiter=0):
  for i in range(nbiter):
    cv.MorphologyEx(im, im, None, None, cv.CV_MOP_OPEN) #Open and close to make appear contours
    cv.MorphologyEx(im, im, None, None, cv.CV_MOP_CLOSE)

def dilateImage(im, nbiter=0):
  element = cv.CreateStructuringElementEx(2, 2, 1, 1, cv.CV_SHAPE_RECT)
  for i in range(nbiter):
    cv.Dilate(im, im, element)
  # cv.ReleaseStructuringElement(&element)

def erodeImage(im, nbiter=0):
  element = cv.CreateStructuringElementEx(2, 2, 1, 1, cv.CV_SHAPE_RECT)
  for i in range(nbiter):
    cv.Erode(im, im, element)
