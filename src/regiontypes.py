#!/usr/env/bin python
"""
This module provides the region classes.

Region() serves as a superclass for specific animal types. It should usually
not be instantiated directly. Instead, the subclasses should be instantiated.
"""

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import numpy as np
import slump as sl
import animaltypes as ani

class Region(object):
    """
    Represents a square region in the terrain.
    
    Superclass for specific region types.
    """
    
    def __init__(self, herbivores=None, carnivores=None):
        """
        Initialize a region.
        
        Parameters:
        herbivores (list of herbivore objects, optional)
        carnivores (list of carnivore objects, optional)
        """
        
        if herbivores == None:
            self._herbivores = []
        else:
            self._herbivores = herbivores
        
        if carnivores == None:
            self._carnivores = []
        else:
            self._carnivores = carnivores
        
        self._food = 0
        self._livable = False   
        self._color = None 
        
    def __str__(self):
        """Return a simple string representation of the region."""

        return self.__class__.__name__
    
    def __repr__(self):
        """
        Return a representation of the region.
        
        Return string can be used to generate clone of region, and is in the
        form <Region type>(<herbivores>, <carnivores>, <_food>)
        """
        
        return (self.__class__.__name__ + 
                "({0}, {1}, {2})".format(self._herbivores, 
                                         self._carnivores, 
                                         self._food))
        
    def color(self):
        """Return color to represent region in map."""
        
        return self._color
    
    def herbivores(self):
        """Return list of herbivores in region."""

        return self._herbivores

    def carnivores(self):
        """Return list of carnivores in region."""

        return self._carnivores
        
    def move(self, animal, current_year):
        """
        Accept new animal if possible.
        
        Return True if animal was accepted, False otherwise.
        """
        
        if animal.last_moved() == current_year:
            return False
        if not self._livable:
            return False
        if animal.__class__ == ani.Herbivore:
            self._herbivores.append(animal)
        elif animal.__class__ == ani.Carnivore:
            self._carnivores.append(animal)
        animal._last_moved = current_year
        return True    
    
    def deploy(self, animal):
        """
        Deploy animal if possible.
        
        Will raise an error if animal was not accepted.        
        """
        
        if not self._livable:
            raise AttributeError('Cannot place animals in {}'.format(self))
        if animal.__class__ == ani.Herbivore:
            self._herbivores.append(animal)
        elif animal.__class__ == ani.Carnivore:
            self._carnivores.append(animal)
        
    def dispatch(self, animal):
        """Remove animal from region."""
        
        if animal.__class__ == ani.Herbivore:
            self._herbivores.remove(animal)
        else:
            self._carnivores.remove(animal)
            
    def regrowth_cycle(self):
        """
        Do one cycle (one year) of regrowth.
        
        This method is overloaded in certain subclasses.
        """
        
        pass

    def nutrition_cycle(self):
        """
        Do one cycle (one year) of nutrition uptake.
        
        This method is overloaded in certain subclasses.
        """

        for herbivore in sorted(self._herbivores, 
                                key=lambda herbivore: herbivore.fitness(), 
                                reverse=True):
            if herbivore.params['F'] <= self._food:
                self._food -= herbivore.eat(herbivore.params['F'])
            elif 0 < self._food < herbivore.params['F']:
                self._food -= herbivore.eat(self._food)
        for carnivore in sorted(self._carnivores, 
                                key=lambda carnivore: carnivore.fitness(), 
                                reverse=True):
            carnivore.hunt(self._herbivores)
    
    def breeding_cycle(self):   
        """Do one cycle (one year) of breeding."""
 
        # Variables that count the number of mature animals in the region.
        mature_herbs = len([herb for herb in self._herbivores 
                            if herb.age() > 0])
        mature_carns = len([carn for carn in self._carnivores 
                            if carn.age() > 0])
        for herbivore in self._herbivores:
            if herbivore.birth(mature_herbs):
                self.deploy(ani.Herbivore(herbivore.params['w_birth']))
        for carnivore in self._carnivores:
            if carnivore.birth(mature_carns):
                self.deploy(ani.Carnivore(carnivore.params['w_birth']))
    
    def aging_cycle(self):
        """Do one cycle (one year) of aging."""

        for animal in self._herbivores + self._carnivores:
            animal.aging()
    
    def weightloss_cycle(self):
        """Do one cycle (one year) of weightloss."""

        for animal in self._herbivores + self._carnivores:
            animal.weightloss()
    
    def death_cycle(self):
        """Do one cycle (one year) of death."""

        self._herbivores[:] = [herbivore for herbivore in self._herbivores 
                              if not herbivore.death()]
        self._carnivores[:] = [carnivore for carnivore in self._carnivores 
                              if not carnivore.death()]
        
    def migration_cycle(self, terrain, current_year):
        """
        Do one cycle (one year) of migration.
        
        Parameters:
        terrain object (pointer to terrain object, required)
        current_year (curent year, required)
        """

        current_cell = (np.where(terrain.terrain_map() == self))
        current_cell = [current_cell[0][0], current_cell[1][0]]
        # Placeholder array for adjacent cells.
        adjacent_cells = np.array(4*[current_cell])
        # Finds adjacent cells
        adjacent_cells[0][0] += 1
        adjacent_cells[1][0] -= 1
        adjacent_cells[2][1] += 1
        adjacent_cells[3][1] -= 1
        for animal in self._herbivores + self._carnivores:
            if animal.migrate():
                randomint = sl.randint(4)
                # Checks the cell designated in the list.
                check_cell = adjacent_cells[randomint]
                coord = (check_cell[0], check_cell[1])
                if terrain.terrain_map()[coord].move(animal, current_year):
                    self.dispatch(animal)


class Desert(Region):
    """Represents a square dessert region in the terrain."""

    def __init__(self):
        """Initialize a dessert region."""

        Region.__init__(self)
        self._livable = True
        self._color = (1, 0.9, 0.8)

    def nutrition_cycle(self):
        """Do one cycle (one year) of nutrition uptake."""

        pass
    

class Savannah(Region):
    """Represents a square savannah region in the terrain."""

    def __init__(self, herbivores=None, carnivores=None, food=None):
        """
        Initialize a savannah region.
        
        Parameters:
        herbivores (list of herbivore objects, optional)
        carnivores (list of carnivore objects, optional)
        food (amount of _food, optional)
        """
        
        Region.__init__(self, herbivores, carnivores)
        self._livable = True
        self._color = (0.8, 1, 0.1)
        if food == None:
            self._food = self.params['fmax']
        else:
            self._food = food
        
    @staticmethod
    def update_params(params):
        """
        Static method for updating parameters of the Savannah class.
        
        Parameters:
        params (dictionary containing parameters, required)
        """
        
        Savannah.params = params
        Savannah._food = Savannah.params['fmax']
    
    def regrowth_cycle(self):
        """Do one cycle (one year) of regrowth."""

        self._food = (self._food + 
                     self.params['alpha'] * 
                     (self.params['fmax'] - self._food))


class Jungle(Region):
    """Represents a square jungle region in the terrain."""

    def __init__(self, herbivores=None, carnivores=None, food=None):
        """
        Initialize a jungle region.
                
        Parameters:
        herbivores (list of herbivore objects, optional)
        carnivores (list of carnivore objects, optional)
        food (amount of _food, optional)
        """
        
        Region.__init__(self, herbivores, carnivores)
        self._livable = True
        self._color = (0, 0.90, 0.20)
        if food == None:
            self._food = self.params['fmax']
        else:
            self._food = food
        
    @staticmethod
    def update_params(params):
        """
        Static method for updating parameters of the Savannah class.
        
        Parameters:
        params (dictionary containing parameters, required)
        """
        
        Jungle.params = params
        Jungle._food = Jungle.params['fmax']
    
    def regrowth_cycle(self):
        """Do one cycle (one year) of regrowth."""

        self._food = self.params['fmax']    


class Mountain(Region):
    """Represents a square mountain region in the terrain."""

    def __init__(self):
        """Initialize a savannah region."""
        
        Region.__init__(self)
        self._livable = False
        self._color = (0.5, 0.5, 0.5) #grey

    def nutrition_cycle(self):
        """Do one cycle (one year) of nutrition uptake."""

        pass


class Ocean(Region):
    """Represents a square ocean region in the terrain."""

    def __init__(self):
        """Initialize a ocean region."""

        Region.__init__(self)
        self._livable = False
        self._color = (0.10, 0.20, 0.8) #blue

    def nutrition_cycle(self):
        """Do one cycle (one year) of nutrition uptake."""

        pass


