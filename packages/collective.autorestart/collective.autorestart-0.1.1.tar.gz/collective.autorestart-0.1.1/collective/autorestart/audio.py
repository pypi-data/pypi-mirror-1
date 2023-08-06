"""

    WAV audio playback via pygame mixer

"""

__license__ = "GPL"
__author__  = "Mikko Ohtamaa <mikko@redinnovation.com>"
__copyright__ = "2008 Red Innovation Ltd."
__docformat__ = "epytext"

import os, sys

import pygame.mixer as pgmixer
import pygame.time as pgtime

def get_sound(fname):
    file = sys.modules[__name__].__file__
    return os.path.abspath(os.path.join(os.path.dirname(file), fname))
    

def play(file):
    
    pgmixer.init(11025)
    sound = pgmixer.Sound(file)
    channel = sound.play()
    while channel.get_busy():
        pgtime.wait(1000)

    sound.stop()
    pgmixer.quit()
