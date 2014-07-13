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

  def batch(self, captcha_folder):
    OCR = self.get_OCR("")
    for root, dirs, filenames in os.walk(captcha_folder):
        for captcha in filenames:
          OCR._captcha = captcha_folder+captcha
          # OCR.options.output_dir = OCR.options.output_dir+'/'+captcha.split('.')[0]
          OCR.train()

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

    # Train in Batches
    if options.batch:
      captcha_folder = options.batch
      self.batch(captcha_folder)

if __name__ == "__main__":
  app = captchonka()
  app.create_options()
  app.run()
