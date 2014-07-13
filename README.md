# Captchonka

Captchonka is a pentesting tool to brute force captchas

## Init

Run help to see available options `python captchonka -h` or `python captchonka --help`.

You can also run it as `./captchonka` on Unix systems.

All commands should be run within a module (mod) `python captchonka --mod=violet` _(this will do nothing)_.

To see the list of available modules do `python captchonka --list`.

## Training

Before cracking you have to train your algorithm. To do so do:
* Run `python captchonka --mod=violet --train="input/example.png"`
* If process is successful then a list of characters will be saved in `output/char/`
* Now move manually each characted from `output/char/` to `core/mods/violet/char/LETTER`

You can run training in verbose mode to see processed image at each step `python captchonka --mod=violet --train="input/example.png" -v`.

Detected characters may be automatically moved into their corresponding folders. For this:
* Name your image file so that it will contain the code in square brackets: `example-[GPCKC].png`. Square brackets can be placed anywhere in name
* Run training in auto-mode `python captchonka --mod=violet --train "input/example-[GPCKC].png" -v -a`

If code will be found in image name and its length will correspond to number of found characters then they will be moved into according folders.

## Cracking

Crack a captcha by running `python captchonka --mod=violet --crack="input/example.png"`.

Run in verbose mode to see what happend under the hood and what are the guess probabilities `python captchonka --mod=violet --crack="input/example.png" -v`.

## Using your own module

You can create your own module by creating a folder in `core/mods/`. This folder should have a file with the same name as folder name. In best case scenario you have to implement only `cleanImage` method. It should return a black-and-white image with no noise. Use `core/mods/violet/violet.py` as an example.

If overriding `cleanImage` is not enough you may look also override following methods:
* `cleanImage` - get a raw PIL Image and return one without noise
* `getCharacters` - extract a list of PIL Images ordered by their position in original image
* `checkCharacterSizes` - test if character size matches requirements
* `getCodeFromString` - get code from image title
* `computeSimilarity` - compare similarity between two 2D binarry lists, return a float between 0 and 100

## Running over multiple files

If you have multiple PNG files in a folder (lets say `input/test/`) than you could run
`for f in input/test/*.png; do echo $f; python captchonka --mod=violet --crack="$f"; done`

If you have multiple PNG files for training and each file has its code in name than you could run
`for f in input/violet/*.png; do python captchonka --mod=violet --train="$f" -a; done`

## Console colors

* *Red* - error
* *Green* - success
* *Blue* - info
* *Yellow* - warning

## Prerequisites

### List of prerequisites

* Python 2.7
* NumPy
* SciPy
* OpenCV

### Installing prerequisites on OS X
* [Brew](http://brew.sh/) with Science `brew tap homebrew/science`
* Python `brew install python --framework --universal`
* Python pip (if it is not installed with Python) `easy_install pip`
* NumPy `pip install numpy`
* SciPy `brew install homebrew/python/scipy`
* OpenCV `brew install opencv`

## Useful resources
* [SciPy Advanced image processing](http://scipy-lectures.github.io/advanced/image_processing/)

## Credits

Based on [CIntruder](https://github.com/epsylon/cintruder).

## License

General Public License v3
