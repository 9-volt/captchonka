#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from PIL import Image, ImageEnhance
from operator import itemgetter
import os, hashlib, time, sys, subprocess, platform, cv2, numpy, cv2.cv as cv
import helpers as ImageHelpers

class CaptchonkaOCR(object):
  def __init__(self, captcha, options):
    self.options = options
    self.options.output_char_dir = os.path.join(self.options.output_dir, "char")

    self.initDirs()

    self.initImage(captcha)

  # Create necessary dirs if they do not exist
  def initDirs(self):
    options = self.options

    if not os.path.exists(options.output_dir):
      os.makedirs(options.output_dir)

    if not os.path.exists(options.output_char_dir):
      os.makedirs(options.output_char_dir)

    # Clean chars dir from previous chars
    for the_file in os.listdir(options.output_char_dir):
      file_path = os.path.join(options.output_char_dir, the_file)
      try:
        if os.path.isfile(file_path):
          os.unlink(file_path)
      except Exception, e:
        print e

  def initImage(self, captcha):
    try:
      self.original = Image.open(captcha)
      self.processed = Image.open(captcha).convert("P")
      self.draft = Image.new("P", self.original.size, 255)
    except:
      print "Error during OCR process!. Captcha not found or image format not supported\n"

  def train(self):
    self.cleanImage()
    self.divideIntoCharacters()

  def crack(self):
    pass

  def cleanImage(self):
    options = self.options

    self.processed.save(options.output_dir + '/1-processed.png')

    self.cleanDenoise()
    self.erodeAndDilate()
    self.blackAndWhite()

  def cleanDenoise(self):
    options = self.options

    clean = cv2.fastNlMeansDenoising(numpy.array(self.processed), None, 30, 6, 14) # Moldcell
    self.processed = Image.fromarray(numpy.uint8(clean))

    self.processed.save(options.output_dir + '/2-denoise.png')

  def erodeAndDilate(self):
    options = self.options

    # contr = ImageEnhance.Contrast(self.processed)
    # contr = contr.enhance(2)
    # processed = cv.fromarray(numpy.array(contr))

    processed = cv.fromarray(numpy.array(self.processed))

    # res = cv.CreateImage(cv.GetSize(processed), 8, 1)
    # cv.CvtColor(processed, res, cv.CV_BGR2GRAY)

    ImageHelpers.dilateImage(processed, 1)
    ImageHelpers.erodeImage(processed, 1)

    cv.SaveImage(options.output_dir + "/3-erode-and-dilate.png", processed)

    self.processed = Image.fromarray(numpy.uint8(processed))

  def blackAndWhite(self):
    options = self.options

    colourid = []
    hist = self.processed.histogram()
    values = {}

    for i in range(256):
      values[i] = hist[i]

    for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
      colourid.append(j)

    for x in range(self.processed.size[1]):
      for y in range(self.processed.size[0]):
        pix = self.processed.getpixel((y, x))
        if pix < 140:
          self.draft.putpixel((y, x), 0)

    self.draft.save(options.output_dir + '/4-black-and-white.png')

  def divideIntoCharacters(self):
    im2 = self.draft

    inletter = False
    foundletter = False
    start = 0
    end = 0

    letters = []

    for y in range(im2.size[0]):
      for x in range(im2.size[1]):
        pix = im2.getpixel((y, x))
        if pix != 255:
          inletter = True

      if foundletter == False and inletter == True:
        foundletter = True
        start = y

      if foundletter == True and inletter == False:
        foundletter = False
        end = y
        letters.append((start, end))
      inletter = False

    count = 0
    for letter in letters:
      m = hashlib.md5()
      im3 = im2.crop(( letter[0], 0, letter[1], im2.size[1] ))
      m.update("%s%s"%(time.time(), count))
      im3.save(self.options.output_char_dir + "/%s.gif"%(m.hexdigest()))
      count += 1

    print "Training Results:"
    print "================="
    print "Number of 'words' extracted: ", count
    if count == 0:
      print "\nOuch!. Looks like this type of captcha is resisting to our OCR methods... by the moment ;)\n"
    else:
      print "Output folder              : ", self.options.output_char_dir
      print "Generated %d characters"%count

      print "\nNow, move each image to the correct folder on your dictionary: '/iconset/'\n"
