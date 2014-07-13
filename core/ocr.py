#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from PIL import Image
from operator import itemgetter
import os, hashlib, time, re, numpy, string, math
import helpers as ImageHelpers
import core.logger as Logger

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

            Logger.log("Removed preview file {}".format(the_file))

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

      # Create numbers and letters dir
      char_folders = range(10) + list(string.lowercase[:26])
      for i in char_folders:
        char_dir = os.path.join(chars_dir, str(i))
        if not os.path.exists(char_dir):
          os.makedirs(char_dir)

  # ###############
  # Train part
  # ###############

  def train(self):
    Logger.log("Train on " + self._captcha)

    processed = self.getImage()
    processed = self.cleanImage(processed)
    # Ensure that image is in black and white
    processed = self.blackAndWhite(processed)

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
      Logger.error("Error during reading captcha. Either path is wrond or file format is not supported", True)

    return original

  # Method that takes a raw PIL Image instance and returns a processed one
  # Resulting image should be in white and black (colors 0 and 255)
  # self.blackAndWhite method may be used to do this
  # If it is not black and white then it will be automatically transformed to black and white
  # with 127 as middle color
  #
  # @override
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

  # Returns a list of PIL Images ordered by their position in original image
  # Each image is a character
  #
  # @override
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

      if foundletter == True and (inletter == False or y == processed.size[0] - 1):
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

        if top >= 0 and top <= bottom and self.checkCharacterSizes(end - start, bottom + 1 - top):
          characters.append(processed.crop((start, top, end, bottom + 1)))
      inletter = False

    return characters

  # Check if found character matches minimal requirements of size
  #
  # @override
  def checkCharacterSizes(self, width=0, height=0):
    return True

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
        Logger.error("Error! Training found {0} chars while in file name are specified {1} chars.".format(len(characters), len(code)), 1)
      else:
        saveAsCategorized = True

    if self.options.verbose:
      if saveAsCategorized:
        Logger.subheader("Saving characters into categorized folders")
      else:
        Logger.log("Saving characters into output folder")

    i = 0
    for character in characters:
      character_hash = characters_hashes[i]

      if saveAsCategorized:
        character_symbol = code[i]
        dst = os.path.join(self.options.mod_dir, 'char', character_symbol.lower(), character_hash + '.gif')
      else:
        dst = os.path.join(self.options.output_char_dir, character_hash + '.gif')

      character.save(dst)

      if saveAsCategorized:
        Logger.log("Saving {0} into mod folder".format(character_symbol))

      i += 1

  def isTrainingSuccessful(self, characters):
    if self.options.auto_train:
      # Parse file name and find code
      basename = os.path.basename(self._captcha)
      code = self.getCodeFromString(basename)

      return len(code) == len(characters)
    else:
      return len(characters) > 0

  # Parses a file name to look for code in it
  # Ex. m01-[ABCDE].png -> ABCDE
  def getCodeFromString(self, str):
    codes = re.findall("\[(.*)\]", str)
    code = None

    if len(codes) == 0:
      Logger.error("No code found in image name: " + str)
    elif len(codes) == 1:
      code = codes[0]
    else:
      Logger.warning("Found more than one code in image name: " + str)
      code = codes[0]

    return code

  # ###############
  # Crack part
  # ###############

  def crack(self):
    Logger.info("\nTrain on " + self._captcha)

    options = self.options

    if not options.mod:
      Logger.error("Can't crack without a mod")
      return None

    supposed_words = []

    processed = self.getImage()
    processed = self.cleanImage(processed)
    # Ensure that image is in black and white
    processed = self.blackAndWhite(processed)

    # List of images
    characters = self.getCharacters(processed)
    trained_chars = self.loadTrainedChars()

    Logger.subheader("Detected characters")

    # Go through each character
    for character in characters:
      # Transform image to list of lists
      a_char = self.imageTo2DBinaryList(character)

      similarity_best = 0.0
      similarity_letter = None

      for char, chars_list in trained_chars.iteritems():
        for a_trained_char in chars_list:
          similarity = self.computeSimilarity(a_char, a_trained_char)

          if similarity > similarity_best:
            similarity_best = similarity
            similarity_letter = char

      supposed_words.append((similarity_best, similarity_letter))

      Logger.log("{} {}%".format(similarity_letter, round(similarity_best, 2)))

    guess = ''
    multiple_probability = 1.0
    average_probability = 0
    all_guesed = True
    for probability, letter in supposed_words:
      if letter:
        guess += letter
      else:
        guess += '_'
        all_guesed = False

      multiple_probability *= probability / 100
      average_probability += probability

    average_probability /= len(guess)

    Logger.subheader("Results")

    if all_guesed:
      Logger.success(guess)
    else:
      Logger.info("characters marked with _ are the ones that are not guessed:")
      Logger.error(guess)

    Logger.info("{}% Overall probability".format(round(multiple_probability * 100, 2)))
    Logger.info("{}% Average probability".format(round(average_probability, 2)))

    return guess

  # Load all available trained characters
  # Return an object with chars as keys
  # Each value is a list of images representations
  # Each image representation is a list of lists with 0s and 1s
  #
  # chars = {
  #   0: []
  #   1: []
  #   ...
  #   a: []
  #   b: [
  #     [[0,1],[1,0]]
  #   ]
  # }
  def loadTrainedChars(self):
    options = self.options
    chars = {}

    chars_dir = os.path.join(options.mod_dir, 'char')

    if not os.path.exists(chars_dir):
      Logger.error("It seems that you did not train this module", True)
      return None
    else:
      Logger.info("\nLoading trained characters")

    # Create numbers and letters dir
    char_folders = range(10) + list(string.lowercase[:26])
    for i in char_folders:
      char_dir = os.path.join(chars_dir, str(i))
      if not os.path.exists(char_dir):
        Logger.warning("It seems that there is no folder for char {}".format(i))
      else:
        chars[i] = []

        # Read and load letters
        for img in os.listdir(char_dir):
          (root, ext) = os.path.splitext(img)

          # Work only with gifs
          if ext == '.gif':
            chars[i].append(self.imageTo2DBinaryList(Image.open(os.path.join(char_dir, img))))

    return chars

  def imageTo2DBinaryList(self, image):
    # Transform it into an array of 0s and 1s
    return map(lambda lst: map(lambda x: 0 if x == 0 else 1, lst), numpy.array(image))

  # Compare two 2D binarry lists
  # Returns a float from 0 to 100
  #
  # @override
  def computeSimilarity(self, image1, image2):
    if len(image1) == 0 or len(image2) == 0 or len(image1[0]) == 0 or len(image2[0]) == 0:
      return 0

    width = max(len(image1[0]), len(image2[0]))
    height = max(len(image1), len(image2))
    width_small = min(len(image1[0]), len(image2[0]))
    height_small = min(len(image1), len(image2))
    area = width * height
    matches = 0

    for h in range(height_small):
      for w in range(width_small):
        if image1[h][w] == image2[h][w]:
          matches += 1

    return 100.0 * matches / area
