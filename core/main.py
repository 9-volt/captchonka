#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import os, sys
from core.options import CaptchonkaOptions
import core.logger as Logger

# Make core modules available to mods
sys.path.append('core/')

class captchonka():
  def __init__(self):
    self.captchaPath = ""
    self.options = None

  def create_options(self, args=None):
    self.options = CaptchonkaOptions().get_options(args)

    Logger.header('Options')
    for key, value in self.options.__dict__.items():
      Logger.log('  ' + key + ': ' + str(value))

    project_folder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    self.options.output_dir = os.path.join(project_folder, 'output')

    if self.options.mod:
      self.options.mod_dir = os.path.join(project_folder, 'core', 'mods', self.options.mod)

  def get_OCR(self, captcha):
    options = self.options

    if options.mod:
      Logger.info("\nLoading module: " + options.mod)

      # Did not add try/catch because if an error is in
      sys.path.append('core/mods/%s/'%(options.mod))
      exec("from " + options.mod + " import CaptchonkaOCRMod")

      OCR = CaptchonkaOCRMod(captcha, options)

    else:
      from core.ocr import CaptchonkaOCR
      OCR = CaptchonkaOCR(captcha, options)

    return OCR

  def train(self, captcha):
    OCR = self.get_OCR(captcha)
    OCR.train()

  def crack(self, captcha):
    OCR = self.get_OCR(captcha)
    OCR.crack()

  def batch_train(self, folder):
    OCR = self.get_OCR("")
    total_trained = 0
    total_success = 0

    for file_name in os.listdir(folder):
      OCR._captcha = os.path.join(folder, file_name)
      (root, ext) = os.path.splitext(OCR._captcha)
      if ext in ['.png', '.gif', '.jpg', '.jpeg']:
        total_trained += 1
        if OCR.train():
          total_success += 1
    self.show_batch_results(total_success,total_trained)

  def batch_crack(self, folder):
    OCR = self.get_OCR("")
    test_for_code = True
    first_crack = True
    total_cracked = 0
    total_success = 0

    for file_name in os.listdir(folder):
      OCR._captcha = os.path.join(folder, file_name)
      (root, ext) = os.path.splitext(OCR._captcha)

      if ext in ['.png', '.gif', '.jpg', '.jpeg']:
        # Detect if we should look for codes in titles
        if first_crack:
          first_crack = False
          real_code = OCR.getCodeFromString(file_name)

          if not real_code:
            test_for_code = False

        if not self.options.verbose:
          Logger.info("File {}".format(file_name), True)

        code = OCR.crack()

        if test_for_code:
          real_code = OCR.getCodeFromString(file_name)
          total_cracked += 1
          if code and real_code and code.upper() == real_code.upper():
            total_success += 1

    if test_for_code:
      self.show_batch_results(total_success,total_cracked)

  def show_batch_results(self, ideal_result, real_result):
    if ideal_result == real_result:
      Logger.success("{}/{} - 100%".format(ideal_result, real_result), True)
    elif ideal_result == 0:
      Logger.error("0/{} - 0%".format(real_result), True)
    else:
      Logger.warning("{}/{} - {}%".format(ideal_result, real_result, round(100.0 * ideal_result / real_result, 2)), True)

  def run(self):
    options = self.options

    # List mods
    if options.listmods:
      Logger.header("List of mods", True)

      mods_dir = "core/mods/"

      for dir in os.listdir(mods_dir):
        if os.path.isdir(os.path.join(mods_dir, dir)):
          Logger.log(dir, True)

      sys.exit(2)

    # Train
    if options.train:
      captcha = options.train
      self.train(captcha)

    # Crack
    if options.crack:
      captcha = options.crack
      self.crack(captcha)

    # Batch train with percentage
    if options.batch_train:
      self.batch_train(options.batch_train)

    # Batch crack with percentage
    if options.batch_crack:
      self.batch_crack(options.batch_crack)

if __name__ == "__main__":
  app = captchonka()
  app.create_options()
  app.run()
