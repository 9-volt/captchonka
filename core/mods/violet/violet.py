#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from core.ocr import CaptchonkaOCR

from PIL import Image
import cv2, numpy

class CaptchonkaOCRMod(CaptchonkaOCR):
  def train(self):
    self.cleanImage()
    self.divideIntoCharacters()

  def crack(self):
    pass

  def cleanImage(self):
    options = self.options

    self.processed.save(options.output_dir + '/1-processed.png')

    self.cleanDenoise()
    # self.erodeAndDilate()
    self.blackAndWhite()
    # self.divideIntoCharacters()

  def cleanDenoise(self):
    options = self.options

    clean = cv2.fastNlMeansDenoising(numpy.array(self.processed), None, 30, 6, 14) # Moldcell
    self.processed = Image.fromarray(numpy.uint8(clean))

    self.processed.save(options.output_dir + '/2-denoise.png')
