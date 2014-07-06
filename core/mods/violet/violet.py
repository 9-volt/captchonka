#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from core.ocr import CaptchonkaOCR

from PIL import Image, ImageEnhance
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
    processed = self.blackAndWhite(processed, 132)

    return processed

  def cleanDenoise(self, processed):
    self.newStep()
    options = self.options

    clean = cv2.fastNlMeansDenoising(numpy.array(processed), None, 17, 4, 7) # Moldcell

    processed = Image.fromarray(numpy.uint8(clean))

    if options.verbose:
      processed.save(options.output_dir + '/{}-denoise.png'.format(self.getStep()))

    return processed

  def erodeAndDilate(self, processed):
    self.newStep()
    options = self.options

    contr = ImageEnhance.Contrast(processed)
    processed = contr.enhance(1.3)

    sharp = ImageEnhance.Sharpness(processed)
    processed = sharp.enhance(1.1)

    clean = cv2.fastNlMeansDenoising(numpy.array(processed), None, 33, 3, 7)
    processed = Image.fromarray(numpy.uint8(clean))

    if options.verbose:
      processed.save(options.output_dir + '/{}-erode-and-dilate.png'.format(self.getStep()))

    return processed
