#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from core.ocr import CaptchonkaOCR

from PIL import Image
import cv2, cv2.cv as cv, numpy
import helpers as ImageHelpers

class CaptchonkaOCRMod(CaptchonkaOCR):
  def cleanImage(self, processed):
    self.newStep()
    options = self.options

    if options.verbose:
      processed.save(options.output_dir + '/{}-processed.png'.format(self.getStep()))

    processed = self.cleanDenoise(processed)
    processed = self.erodeAndDilate(processed)
    processed = self.blackAndWhite(processed, 145)

    return processed

  def cleanDenoise(self, processed):
    self.newStep()
    options = self.options

    clean = cv2.fastNlMeansDenoising(numpy.array(processed), None, 32, 8, 14) # Moldcell

    processed = Image.fromarray(numpy.uint8(clean))

    if options.verbose:
      processed.save(options.output_dir + '/{}-denoise.png'.format(self.getStep()))

    return processed

  def erodeAndDilate(self, processed):
    self.newStep()
    options = self.options

    # contr = ImageEnhance.Contrast(self.processed)
    # contr = contr.enhance(2)
    # processed = cv.fromarray(numpy.array(contr))

    _processed = cv.fromarray(numpy.array(processed))

    # res = cv.CreateImage(cv.GetSize(processed), 8, 1)
    # cv.CvtColor(processed, res, cv.CV_BGR2GRAY)

    ImageHelpers.dilateImage(_processed, 1)
    ImageHelpers.erodeImage(_processed, 1)

    processed = Image.fromarray(numpy.uint8(_processed))

    if options.verbose:
      processed.save(options.output_dir + '/{}-erode-and-dilate.png'.format(self.getStep()))

    return processed
