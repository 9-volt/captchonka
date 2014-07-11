#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from PIL import Image
from operator import itemgetter
from termcolor import colored
import os, hashlib, time, re, numpy, string, math
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

    # Grayscale colors as an array of arrays
    processed_colors = numpy.array(processed)

    for y in range(processed.size[0]):
      for x in range(processed.size[1]):
        if processed_colors[x][y] != 255:
          inletter = True

      if foundletter == False and inletter == True:
        foundletter = True
        start = y

      if foundletter == True and inletter == False:
        foundletter = False
        end = y

        # Find vertical bound
        top = -1
        bottom = -1

        for vx in range(processed.size[1]):
          for vy in range(start, end + 1):
            if processed_colors[vx][vy] == 0:
              # For top save only first occurence
              if top == -1:
                top = vx
              # For bottom save all occurences, so the last one will be the bottom
              bottom = vx

        if top >= 0 and top <= bottom:
          characters.append(processed.crop((start, top, end, bottom + 1)))
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
        print colored("Error! Training found {0} chars while in file name are specified {1} chars.".format(len(characters), len(code)), "red")
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
    options = self.options

    if not options.mod:
      print "Error! Can't crack without a mod"
      return None

    processed = self.getImage()
    processed = self.cleanImage(processed)

    # List of images
    characters = self.getCharacters(processed)

    # Check for characters proximity and return most probable value
    vectorCompare = VectorCompare()
    iconset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    imageset = []
    last_letter = None

    print "Loading dictionary... "
    for letter in iconset:
      char_dir = os.path.join(options.mod_dir, 'char', letter)

      for img in os.listdir(char_dir):
        temp = []
        if img != "Thumbs.db" and img != ".DS_Store":
          if options.verbose:
            if last_letter != letter:
              print "-----------------"
              print "Word:", letter
              print "-----------------"
            print img
            last_letter = letter
          temp.append(self.buildVector(Image.open(os.path.join(char_dir, img))))
        imageset.append({letter:temp})

    try:
      im = self.getImage()
      im2 = Image.new("P", im.size, 255)
      im = im.convert("P")
    except:
      print "\nError during Cracking process!. is that captcha supported?\n"
      return None

    count = 0
    countid = 1
    word_sug = None

    for letter in characters:
      print "----------------------------\n"
      im3 = letter
      guess = []
      for image in imageset:
        for x, y in image.iteritems():
          if len(y) != 0:
            guess.append((vectorCompare.relation(y[0], self.buildVector(im3)), x))
      guess.sort(reverse=True)
      word_per = guess[0][0] * 100
      if str(word_per) == "100.0":
        print "Image position   :", countid
        print "Broken Percent   :", int(round(float(word_per))), "%", "[+]"
      else:
        print "Image position   :", countid
        print "Broken Percent   :", "%.4f" % word_per, "%"
      print "------------------"
      print "Word suggested   :", guess[0][1]

      if word_sug == None:
        word_sug = str(guess[0][1])
      else:
        word_sug = word_sug + str(guess[0][1])
      count += 1
      countid = countid + 1

    print "\n=================="
    if word_sug is None:
      print "Possible Solution: ", "[ No idea!. Maybe, you need to train more...]"
    else:
      print "Possible Solution: ", "[", word_sug, "]"
    print "==================\n"

    return word_sug

  def buildVector(self, img):
    dct = {}
    count = 0
    for i in img.getdata():
      dct[count] = i
      count += 1
    return dct


class VectorCompare:

  def magnitude(self, concordance):
    total = 0
    for word, count in concordance.iteritems():
      # print concordance
      total += count ** 2
    return math.sqrt(total)

  def relation(self, concordance1, concordance2):
    topvalue = 0
    for word, count in concordance1.iteritems():
      if concordance2.has_key(word):
        topvalue += count * concordance2[word]
    return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))
