#!/usr/env/bin python
"""
This module provides a function that will return the fitness of an animal.
"""

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import numpy as np

cdef float _e 
_e = np.e

cpdef float _fitness_helper(float att1, float att2, float phi):
    """
    Helper method for the _fitness method.
    
    Parameters:
    att1 (int/float, required)
    att2 (int/float, required)
    phi (int/float, required)
    
    Return value:
    1 / (1 + e**(phi*(att1-att2)))
    """
    
    return 1.0 / (1 + _e**(phi*(att1-att2))) 

cpdef float new_fitness(animal):
    """Return new fitness for animal."""

    if animal._weight < animal.params['w_min']:
        return 0
    else:
        return (_fitness_helper(animal._age, 
                                animal.params['a_half'], 
                                animal.params['phi_age']) *
                _fitness_helper(animal._weight, 
                                animal.params['w_half_low'], 
                                -animal.params['phi_low']) *
                _fitness_helper(animal._weight, 
                                animal.params['w_half_high'], 
                                animal.params['phi_high']))
    
    

