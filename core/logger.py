from termcolor import colored
from core.options import CaptchonkaOptions

_options = CaptchonkaOptions().get_options()

def log(message, bypass_options=False):
  if _options.verbose or bypass_options:
    print message

def error(message, bypass_options=False):
  if _options.verbose or bypass_options:
    print colored(message, 'red')

def success(message, bypass_options=False):
  if _options.verbose or bypass_options:
    print colored(message, 'green')

def info(message, bypass_options=False):
  if _options.verbose or bypass_options:
    print colored(message, 'cyan')

def warning(message, bypass_options=False):
  if _options.verbose or bypass_options:
    print colored(message, 'yellow')

def header(message, bypass_options=False):
  log('', bypass_options)
  log('='*20, bypass_options)
  log(message, bypass_options)
  log('='*20, bypass_options)

def subheader(message, bypass_options=False):
  log('', bypass_options)
  log(message, bypass_options)
  log('='*20, bypass_options)

def line(bypass_options=False):
  log('\n' + '='*20, bypass_options)
