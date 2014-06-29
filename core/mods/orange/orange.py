#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from core.ocr import CaptchonkaOCR

from PIL import Image
import cv2, numpy

class CaptchonkaOCRMod(CaptchonkaOCR):
  def cleanImage(self):
    options = self.options

    self.processed.save(options.output_dir + '/1-processed.png')

    self.cleanDenoise()
    self.erodeAndDilate()
    self.blackAndWhite()
