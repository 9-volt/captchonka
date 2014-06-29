#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import os, sys
from core.options import CaptchonkaOptions

class captchonka():
  def __init__(self):
    self.captchaPath = ""
    self.options = None

  def create_options(self, args=None):
    self.options = CaptchonkaOptions().get_options(args)

    if self.options.verbose:
      print "Options", self.options

  def get_OCR(self, captcha):
    options = self.options

    if options.mod:
      if options.verbose:
        print "Loading module:", options.mod
        print "==============="

      try:
        sys.path.append('core/mods/%s/'%(options.mod))
        exec("from " + options.mod + " import CaptchonkaOCR")
      except Exception:
        print "This module: '", options.mod, "' exists?. Try --list to view available modules\n"
        sys.exit(2)
      OCR = CaptchonkaOCR(captcha, options)

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

  def run(self):
    options = self.options

    if options.listmods:
      if options.verbose:
        print "======================================="
        print "List of specific OCR exploiting modules"
        print "======================================="

      top = 'core/mods/'
      for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
          if name == 'ocr.py':
            folder = os.path.basename(os.path.normpath(root))
            print folder
      print "run with --mod [modname]"
      sys.exit(2)


if __name__ == "__main__":
  app = captchonka()
  app.create_options()
  app.run()
