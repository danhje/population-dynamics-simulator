#!/usr/env/bin python
"""
This module provides the animal classes.

Animal() serves as a superclass for specific animal types. It should usually
not be instantiated directly. Instead, the subclasses Herbivore() and 
Carnivore() should be instantiated. 
"""

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import slump as sl
import fitness as ft 

class Animal(object):
    """
    Represents an animal. 
    
    Superclass for specific animal types.
    """
        
    def __init__(self, weight, age=0):
        """
        Initialize an animal object. 
    
        Parameters:
        weight (required)
        age (optional)
        """
        
        if age < 0 or type(age) != int:
            raise ValueError('Age must be non-negative int')
        if weight < self.params['w_min']:
            raise ValueError("Animal weight can't be smaller than min_weight")
        
        self._weight = weight
        self._age = age
        self._last_moved = 0
        self._fitness = None
        self.update_fitness()
    
    def __str__(self):
        """Return a simple string representation of the animal."""
        
        return self.__class__.__name__
    
    def __repr__(self):
        """
        Return a string representation of the animal.
        
        The returned string can be used to generate a clone, and is in the form
        Animal(<weight>, <age>).
        """
        
        return (self.__class__.__name__ + 
                "({0}, {1})".format(self.weight(), self.age()))

    @staticmethod
    def update_params(params):
        """
        Static method for updating parameters of the Animal class.
             
        This method is not really needed, as subclasses have their own 
        static methods for updating parameters. It is here just to keep
        pylint from complaining.
        """
        
        Animal.params = params        
        
    def weight(self):
        """Return animals weight."""
        
        return self._weight
    
    def age(self):
        """Return animals age."""
        
        return self._age
    
    def fitness(self):
        """Return animals fitness."""
        
        return self._fitness
    
    def last_moved(self):
        """Return when animal was last moved."""
        
        return self._last_moved
        
    def update_fitness(self):
        """
        Update animals _fitness variable.
        
        This method will call the method new_fitness() in the cython 
        module fitness.pyx. 
        
        Should be called every time age or weight is changed.
        """
      
        self._fitness = ft.new_fitness(self)
        
    def birth(self, animal_count_in_region):
        """
        Determine if animal will give birth.
                
        Parameters:
        animal_count_in_region (# of herbivores in the same region, required)
        """
        
        if (self.weight() < (self.params['w_min'] + 
                             self.params['zeta'] * 
                             self.params['w_birth']) or
            self.age() == 0):
            return False
        else:
            gives_birth = sl.random() < (self.params['gamma'] * 
                                         self.fitness() * 
                                         (animal_count_in_region-1))
            if gives_birth:
                self.birthloss()
                return True
            else: 
                return False
            
    def weightloss(self):
        """Cause animal to loose weight."""

        self._weight -= self.params['sigma'] * self._weight
        self.update_fitness()
        
    def birthloss(self):
        """Cause animal to loose weight after giving birth."""

        self._weight -= self.params['zeta'] * self.params['w_birth']
        self.update_fitness()
        
    def weightgain(self, weight):
        """
        Cause animal to gain weight.
        
        Parameters:
        weight (weight to gain, required)
        """
        if weight < 0:
            raise ValueError('weight cannot be negative.')
        self._weight += weight
        self.update_fitness()
        
    def aging(self):
        """Age the animal by one year."""

        self._age += 1
        self.update_fitness()
        
    def death(self):
        """Determine if animal dies."""
        
        if self.weight() < self.params['w_min']:
            return True
        else:
            return sl.random() < self.params['omega'] * (1-self.fitness())
        
    def migrate(self):
        """Determine if animal is able to migrate."""

        if sl.random() < self.params['mu'] * self.fitness():
            return True
        else:
            return False


class Herbivore(Animal):
    """Represents a herbivore."""

    def __init__(self, weight, age=0):
        """
        Initialize a herbivore object. 
    
        Parameters:
        weight (required)
        age (optional, default = 0)
        """ 
        
        Animal.__init__(self, weight, age)
    
    @staticmethod
    def update_params(params):
        """
        Static method for updating parameters of the Herbivore class.
             
        Parameters:
        params (dictionary with all herbivore parameters, required)
        """
        
        Herbivore.params = params
    
    def eat(self, amount):
        """
        The animal will eat, increasing its weight.
        
        Parameters:
        amount (amount to eat in int/float, required)
        """
        
        self.weightgain(self.params['beta'] * amount)
        return amount


class Carnivore(Animal):
    """Represents a carnivore."""

    def __init__(self, weight, age=0):
        """
        Initialize a carnivore object. 
    
        Parameters:
        weight (required)
        age (optional, default = 0)
        """ 
        
        Animal.__init__(self, weight, age)
        
    @staticmethod
    def update_params(params):
        """
        Static method for updating parameters of the Carnivore class.
             
        Parameters:
        params (dictionary with all carnivore parameters, required)
        """
        
        Carnivore.params = params
    
    def _eat(self, prey, eaten_this_year, herbivores):
        """
        The animal will eat, increasing its weight.
        
        Return value is the amount eaten.
        
        Parameters:
        prey (pointer to prey to feed off, required)
        eaten_this_year (amount eaten so far this year, required)
        herbivores (pointer to herbivores list, required)
        """
        
        if prey.weight() >= self.params['F'] - eaten_this_year:
            self.weightgain((self.params['beta'] * 
                            (self.params['F'] - eaten_this_year)))
            herbivores.remove(prey)
            return self.params['F'] - eaten_this_year
        else:
            self.weightgain(self.params['beta'] * prey.weight())
            herbivores.remove(prey)
            return prey.weight()
            
    def hunt(self, herbivores):
        """
        Hunt herbivores in the region.
        
        Parameters: 
        herbivores (list of herbivores in the region, required)
        """

        eaten_this_year = 0
        huntingground = sorted(herbivores, 
                               key=lambda herbivore: herbivore.fitness())
        for prey in huntingground:
            if eaten_this_year >= self.params['F']:
                break
            fit_diff = self.fitness() - prey.fitness()
            if fit_diff <= 0:
                break
            elif 0 < fit_diff < self.params['DeltaPhiMax']:
                prob = (fit_diff / self.params['DeltaPhiMax'])
                if sl.random() < prob:
                    eaten_this_year += self._eat(prey, 
                                                 eaten_this_year, 
                                                 herbivores)
            else:
                eaten_this_year += self._eat(prey, eaten_this_year, herbivores)


