#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import optparse

class CaptchonkaOptions(optparse.OptionParser):
  def __init__(self, *args):
    optparse.OptionParser.__init__(self,
      description='Captchonka is a pentesting tool to brute force captchas',
      prog='captchonka',
      usage= '\n\ncaptchonka [OPTIONS]')

    self.add_option("-v", "--verbose", action="store_true", dest="verbose", help="active verbose mode output results")
    self.add_option("--train", action="store", dest="train", help="apply common OCR techniques to captcha")
    self.add_option("-a", "--auto-train", action="store_true", dest="auto_train", help="move decoded chars into corresponding folders")
    self.add_option("--crack", action="store", dest="crack", help="brute force using local dictionary (from: 'iconset/')")

    group1 = optparse.OptionGroup(self, "Modules (training)")
    group1.add_option("--list", action="store_true", dest="listmods", help="list available modules (from: 'core/mods/')")
    group1.add_option("--mod", action="store", dest="mod", help="train using a specific OCR exploiting module")
    self.add_option_group(group1)

  def get_options(self, user_args=None):
    (options, args) = self.parse_args(user_args)
    options.args = args

    return options
