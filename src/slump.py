#!/usr/env/bin python
"""
This module provides a random generator interface.

NumPy's random generators is used by default, but may be replaced by another.
"""

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import numpy.random as nrandom

def seed(seedvalue):
    """Set the seed value for the random generator."""
    
    nrandom.seed(seedvalue)

def random():
    """Return a (pseudo)random float in the interval [0, 1)."""
    
    return nrandom.random()

def randint(vmax):
    """Return a (pseudo)randomly selected int between 0 and vmax."""
    
    return nrandom.randint(vmax)        