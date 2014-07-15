#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from core.ocr import CaptchonkaOCR

from PIL import Image, ImageEnhance
import cv2, cv2.cv as cv, numpy
import helpers as ImageHelpers

class CaptchonkaOCRMod(CaptchonkaOCR):
  def checkCharacterSizes(self, width=0, height=0):
    return (width > 2 or width * height >= 16) and height > 3 and width < 20 and height < 20

  def cleanImage(self, processed):
    self.newStep()
    options = self.options

    if options.verbose:
      processed.save(options.output_dir + '/{}-processed.png'.format(self.getStep()))

    processed = processed.convert("RGBA")
    processed = self.deleteBackground(processed)
    processed = self.cleanSpecificDenoise(processed)
    processed = self.fillMissingPixels(processed)
    processed = self.cleanGeneralDenoise(processed)

    processed = self.erodeAndDilate(processed)
    processed = self.blackAndWhite(processed, 140)

    return processed

  def deleteBackground(self, processed):
    self.newStep()
    options = self.options

    pix = processed.load()

    background_color = self.__getBackgroundColor(pix,processed)

    for y in xrange(processed.size[1]):
      for x in xrange(processed.size[0]):
        if pix[x, y] == background_color:
          pix[x, y] = (255, 255, 255, 255)

    if options.verbose:
      processed.save(options.output_dir + '/{}-delete-background.png'.format(self.getStep()))

    return processed

  def __getBackgroundColor(self, pix, processed):
    background_color = {}
    for y in xrange(processed.size[1]):
      for x in xrange(processed.size[0]):
        if pix[x, y] != (0, 0, 0, 255):
          if pix[x, y] in background_color:
            background_color[pix[x, y]] += 1
          else:
            background_color[pix[x, y]] = 1
    result = sorted(background_color, key = background_color.get, reverse = True)
    return result[0]

  def cleanSpecificDenoise(self, processed):
    self.newStep()
    options = self.options

    pix = processed.load()
    self.__deleteSpecificNoise(pix,processed)

    if options.verbose:
      processed.save(options.output_dir + '/{}-specific-denoise.png'.format(self.getStep()))

    return processed

  def __deleteSpecificNoise(self, pix, processed):
    for y in xrange(processed.size[1]):
      for x in xrange(processed.size[0]):
        # Moldcell color
        if (pix[x, y] == (102, 51, 153, 255)) or (pix[x, y] == (153, 153, 153, 255)):
          pix[x, y] = (255, 255, 255, 255)

  def fillMissingPixels(self, processed):
    self.newStep()
    options = self.options

    pix = processed.load()
    self.__fillPixelsAround(pix,processed)

    if options.verbose:
      processed.save(options.output_dir + '/{}-fill-pixies.png'.format(self.getStep()))

    return processed

  def __fillPixelsAround(self, pix, processed):
    for y in xrange(processed.size[1]):
      for x in xrange(processed.size[0]):
        try:
          if (pix[x-1, y] != (255, 255, 255, 255)) and (pix[x+1, y] != (255, 255, 255, 255)) \
            or (pix[x, y-1] != (255, 255, 255, 255)) and (pix[x, y+1] != (255, 255, 255, 255)):

            pix[x, y] = (0, 0, 0, 255)
        except:
          pass
  def cleanGeneralDenoise(self, processed):
    self.newStep()
    options = self.options

    processed = processed.convert("LA")
    processed = processed.convert("P")
    clean = cv2.fastNlMeansDenoising(numpy.array(processed), None, 17, 5, 7)

    processed = Image.fromarray(numpy.uint8(clean))

    if options.verbose:
      processed.save(options.output_dir + '/{}-general-denoise.png'.format(self.getStep()))

    return processed

  def erodeAndDilate(self, processed):
    self.newStep()
    options = self.options

    contr = ImageEnhance.Contrast(processed)
    processed = contr.enhance(1.2)

    sharp = ImageEnhance.Sharpness(processed)
    processed = sharp.enhance(1.1)

    clean = cv2.fastNlMeansDenoising(numpy.array(processed), None, 33, 3, 7)
    processed = Image.fromarray(numpy.uint8(clean))

    if options.verbose:
      processed.save(options.output_dir + '/{}-erode-and-dilate.png'.format(self.getStep()))

    return processed
