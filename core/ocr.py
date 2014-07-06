#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from PIL import Image
from operator import itemgetter
import os, hashlib, time, re, numpy, string
import helpers as ImageHelpers

'''
# Use Denoising
clean = cv2.fastNlMeansDenoising(numpy.array(im), None, 17, 4, 7)
im = Image.fromarray(numpy.uint8(clean))

# Contrast
contr = ImageEnhance.Contrast(im)
im = contr.enhance(1.3)

# Sharpness
sharp = ImageEnhance.Sharpness(im)
im = sharp.enhance(1.1)

# Dilate and Erode image
_processed = cv.fromarray(numpy.array(processed))
ImageHelpers.dilateImage(_processed, 1)
ImageHelpers.erodeImage(_processed, 1)

processed = Image.fromarray(numpy.uint8(_processed))
'''

class CaptchonkaOCR(object):
  def __init__(self, captcha, options):
    self.options = options
    self.options.output_char_dir = os.path.join(self.options.output_dir, "char")
    self._step = 0
    self._captcha = captcha

    self.initDirs()

  def newStep(self):
    self._step += 1

  def getStep(self):
    return self._step

  # Create necessary dirs if they do not exist
  def initDirs(self):
    options = self.options

    if not os.path.exists(options.output_dir):
      os.makedirs(options.output_dir)

    if not os.path.exists(options.output_char_dir):
      os.makedirs(options.output_char_dir)

    # Clean output dir from previous preview files
    for the_file in os.listdir(options.output_dir):
      if re.match("^[0-9]\-", the_file):
        file_path = os.path.join(options.output_dir, the_file)

        try:
          if os.path.isfile(file_path):
            os.unlink(file_path)

            if options.verbose:
              print "Removed preview file {}".format(the_file)

        except Exception, e:
          print e

    # Clean chars dir from previous chars
    for the_file in os.listdir(options.output_char_dir):
      file_path = os.path.join(options.output_char_dir, the_file)
      try:
        if os.path.isfile(file_path):
          os.unlink(file_path)
      except Exception, e:
        print e

    if options.mod:
      chars_dir = os.path.join(options.mod_dir, 'char')

      # Create root chars dir
      if not os.path.exists(chars_dir):
        os.makedirs(chars_dir)

      # Create numbers dir
      for i in range(10):
        char_dir = os.path.join(chars_dir, str(i))
        if not os.path.exists(char_dir):
          os.makedirs(char_dir)

      # Create letters dir
      for l in string.lowercase[:26]:
        char_dir = os.path.join(chars_dir, l)
        if not os.path.exists(char_dir):
          os.makedirs(char_dir)

  # ###############
  # Train part
  # ###############

  def train(self):
    processed = self.getImage()
    processed = self.cleanImage(processed)

    # List of images
    characters = self.getCharacters(processed)

    # Save characters on hard disc
    self.saveCharacters(characters)

    return self.isTrainingSuccessful(characters)

  # Returns image to work with
  def getImage(self):
    original = None
    try:
      original = Image.open(self._captcha)
    except:
      print "Error during reading captcha. Either path is wrond or file format is not supported"

    return original

  def cleanImage(self, processed):
    self.newStep()
    options = self.options

    if options.verbose:
      processed.save(options.output_dir + '/{}-preprocessed.png'.format(self.getStep()))

    return self.blackAndWhite(processed)

  # Colors from 0 to colorBorder => black, from colorBorder to 255 => white
  def blackAndWhite(self, processed, colorBorder = 127):
    self.newStep()
    options = self.options
    blank = Image.new("P", processed.size, 255)

    colourid = []
    hist = processed.histogram()
    values = {}

    for i in range(256):
      values[i] = hist[i]

    for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
      colourid.append(j)

    for x in range(processed.size[1]):
      for y in range(processed.size[0]):
        pix = processed.getpixel((y, x))
        if pix < colorBorder:
          blank.putpixel((y, x), 0)

    if options.verbose:
      blank.save(options.output_dir + '/{}-black-and-white.png'.format(self.getStep()))

    return blank

  # Returns a list of images ordered by their position in original image
  def getCharacters(self, processed):
    characters = []

    inletter = False
    foundletter = False
    start = 0
    end = 0

    for y in range(processed.size[0]):
      for x in range(processed.size[1]):
        pix = processed.getpixel((y, x))
        if pix != 255:
          inletter = True

      if foundletter == False and inletter == True:
        foundletter = True
        start = y

      if foundletter == True and inletter == False:
        foundletter = False
        end = y

        # Add character to list
        characters.append(processed.crop((start, 0, end, processed.size[1])))
      inletter = False

    return characters

  def saveCharacters(self, characters):
    characters_hashes = []

    # Get characters' hashes
    for character in characters:
      m = hashlib.md5()

      # Get image as a string of 0 and 1 (for 255) and n (for new line)
      ones_array = map(lambda lst: map(lambda x: '0' if x == 0 else '1', lst), numpy.array(character))
      ones_string = 'n'.join(map(lambda lst: ''.join(lst), ones_array))

      m.update(ones_string)

      characters_hashes.append(m.hexdigest())

    saveAsCategorized = False

    if self.options.auto_train:
      # Parse file name and find code
      basename = os.path.basename(self._captcha)
      code = self.getCodeFromString(basename)

      if len(code) != len(characters):
        saveAsCategorized = False
        print "Error! Training found {0} chars while in file name are specified {1} chars.".format(len(characters), len(code))
      else:
        saveAsCategorized = True

    if self.options.verbose:
      if saveAsCategorized:
        print "\nSaving characters into categorized folders"
      else:
        print "\nSaving characters into output folder"
      print "="*15

    i = 0
    for character in characters:
      character_hash = characters_hashes[i]

      if saveAsCategorized:
        character_symbol = code[i]
        dst = os.path.join(self.options.mod_dir, 'char', character_symbol.lower(), character_hash + '.gif')
      else:
        dst = os.path.join(self.options.output_char_dir, character_hash + '.gif')

      character.save(dst)

      if self.options.verbose and saveAsCategorized:
        print "Saving {0} into mod folder".format(character_symbol)

      i += 1

  def isTrainingSuccessful(self, characters):
    if self.options.auto_train:
      # Parse file name and find code
      basename = os.path.basename(self._captcha)
      code = self.getCodeFromString(basename)

      return len(code) == len(characters)
    else:
      return len(characters) > 0

  def getCodeFromString(self, str):
    codes = re.findall("\[(.*)\]", str)
    code = None

    if len(codes) == 0:
      print "Error! No code found in image name"
    elif len(codes) == 1:
      code = codes[0]
    else:
      print "Warning! Found more than one code in image name"
      code = codes[0]

    return code

  # ###############
  # Crack part
  # ###############

  def crack(self):
    pass
