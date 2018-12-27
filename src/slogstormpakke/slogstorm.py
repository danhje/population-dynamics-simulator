#!/usr/env/bin python
'''
This module provides the main simulation classes.

InputHandler() provides the main user interface. It can be used to start a 
simulation, generate a terrain, deploy animals, modify parameters etc. 

See the docstrings from the different classes and methods for more detailed
documentation. 
'''

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import os
import numpy as np
import matplotlib.pyplot as plt
import regiontypes as lnd
import animaltypes as ani


class Terrain(object):
    """Represents the entire terrain."""

    def __init__(self, STRMAP=None, mapfile=None):
        """
        Initialize a terrain object.
        
        Parameters:
        mapstr (string describing the map)
        mapfile (location of file containing mapstr)
        
        One of the parameters must be given.
        """
        
        letter_value = {'O': lnd.Ocean,
                        'M': lnd.Mountain,
                        'D': lnd.Desert,
                        'J': lnd.Jungle,
                        'S': lnd.Savannah}
        
        if (STRMAP == None and mapfile == None):
            raise AttributeError('Need map input')
        elif (STRMAP != None and mapfile != None):
            raise AttributeError('Can only handle single input')
        
        if mapfile != None:
            if not os.path.isfile(mapfile):
                raise IOError('File not found')
            STRMAP = open(mapfile).read() 
            
        STRMAP = np.array([[cell for cell in row] for row in STRMAP.split()])
        map_dims = np.shape(STRMAP)
        
        # Make sure all lines have the same length.
        # If they do not, map_dims will only contain one int, not two.
        if len(map_dims) != 2:
            raise ValueError('All rows in map must have the same length')
        
        # Make sure map is big enough
        if map_dims[0] < 3 or map_dims[1] < 3:
            raise ValueError('Map is too small')
        
        # Make sure edges are ocean
        if (not all(STRMAP[0, :] == np.array(map_dims[1]*['O'])) or
            not all(STRMAP[-1, :] == np.array(map_dims[1]*['O'])) or
            not all(STRMAP[:, 0] == np.array(map_dims[0]*['O'])) or
            not all(STRMAP[:, -1] == np.array(map_dims[0]*['O']))):
            raise ValueError('Edges in map must be ocean')        
        
        self._strmap = STRMAP
        
        # Make sure all letters in STRMAP are valid, and 
        # convert STRMAP to matrix of region objects.
        try:
            self._mapmat = np.array([[letter_value[cell]() for cell in row]
                                     for row in STRMAP])
        except KeyError:
            raise ValueError("Invalid letter in map. These are valid: {}"
                             .format(letter_value.keys()))

        self._map_dims = map_dims
        
    def terrain_map(self):
        """Return terrain map."""
        
        return self._mapmat
    
    def terrain_dimensions(self):
        """
        Return terrain dimensions.
        
        Format: (<rows>, <columns>)
        """

        return self._map_dims
    
    def growth(self):
        """Perform regrowth, nutrition and breeding cycles."""
        
        for row in self.terrain_map():
            for celle in row:
                celle.regrowth_cycle()
                celle.nutrition_cycle()
                celle.breeding_cycle()
        
    def migration(self, year):
        """Perform migration cycle."""
        
        for row in self.terrain_map():
            for celle in row:
                celle.migration_cycle(self, year)

    def decay(self):
        """Perform aging, weightloss and death cycles."""
        
        for row in self.terrain_map():
            for celle in row:
                celle.aging_cycle()
                celle.weightloss_cycle()
                celle.death_cycle()
    
    def animal_counts(self):
        "Count herbivores and carnivores this year."""
        
        h_this_y = 0
        c_this_y = 0
        for row in self.terrain_map():
            for celle in row:
                h_this_y += len(celle.herbivores())
                c_this_y += len(celle.carnivores())
        
        return (h_this_y, c_this_y)
        

class Graphics(object):
    """Handles the graphics display."""

    def __init__(self):
        """Initialize a graphics object."""
        
        plt.ion()
        # plt.show()
        
        # Constants used to determine coloring of density maps:
        self._min_colormap_h = 0
        self._max_colormap_h = 60
        self._min_colormap_c = 0
        self._max_colormap_c = 20
        
        # Graphing update interval
        self._update_interval = 1
        
        # Graph y-axis upper limit
        self._ylim = 4000
        
        # Lists that will later be used to hold data on animal counts
        # between graphics updates. 
        self._antall_h = []
        self._antall_c = []
        
        # Variables used for saving images
        self._img_counter = 0
        self._img_base = 'fig'
        self._img_format = 'png'
        
        # Path to ffmpeg, change path if needed.
        self._ffmpeg_binary = "/opt/local/bin/ffmpeg"
        # self._ffmpeg_binary = r"i:\\tools\ffmpeg-git-win64-static\bin\ffmpeg"
        
        # Figures and subplots
        self._fig = plt.figure(figsize=(14, 9))
        self._graph_subplot = self._fig.add_subplot(2, 2, 1)
        self._terrain_subplot = self._fig.add_subplot(2, 2, 2)
        self._herbivore_subplot = self._fig.add_subplot(2, 2, 3)
        self._carnivore_subplot = self._fig.add_subplot(2, 2, 4)
        
        # Place holder names for plotting
        self._terrain_img_ax = None
        self._h_img_ax = None
        self._c_img_ax = None
        self._h_graphline = None
        self._c_graphline = None
        self._h_colorbar = None
        self._c_colorbar = None
        
    def update_interval(self, interval=None):
        """
        Set / get update interval for the graphics.
        
        Parameters:
        interval (new update interval, in years, optional.
                  If omitted, interval remains unchanged.)
                  
        Return value: current update interval.       
        """
        
        if interval != None:
            if interval <= 0:
                raise ValueError('Update interval must be positive')
            if type(interval) != int:
                raise ValueError('Update interval must be an integer')
            self._update_interval = interval
            
        return self._update_interval
        
    def set_ylim(self, ylim):
        """
        Set _graph_subplot y-axis upper limit.
        
        Parameters:
        ylim (y-axis upper limit, required)
        """
        
        if ylim < 0:
            raise ValueError('Y-axis upper limit must be non-negative')
        self._ylim = ylim
        plt.subplot(self._graph_subplot)
        plt.ylim(0, self._ylim)
        self.update_graphics()
               
    def draw_terrain(self, terrain):
        """
        Draw a map of the terrain.
        
        Parameters:
        terrain (terrain object, required)
        """
        if self._terrain_img_ax == None:
            # Draw terrain
            plt.subplot(self._terrain_subplot)
            map_rgb = [[cell.color() for cell in row] 
                       for row in terrain.terrain_map()]
            self._terrain_img_ax = self._terrain_subplot.imshow(map_rgb, 
                                                interpolation='nearest')
            
            # Make ticks start from 1 instead of 0
            plt.xticks(np.arange(0, terrain.terrain_dimensions()[1]), 
                       np.arange(1, terrain.terrain_dimensions()[1] + 1))
            plt.yticks(np.arange(0, terrain.terrain_dimensions()[0]), 
                       np.arange(1, terrain.terrain_dimensions()[0] + 1)) 

    def graph_setup(self, current_year, xlim):
        """
        Set up the _graph_subplot and plot the first data.
        
        Parameters:
        current_year (the current year, required)
        xlim (upper x-limit for _graph_subplot)
        """
        
        plt.subplot(self._graph_subplot)
        
        # Set axis limits
        plt.xlim(0, xlim)
        plt.ylim(0, self._ylim)
        
        # Create x-values and plot
        xval_h = range(current_year+1-len(self._antall_h), current_year+1)
        xval_c = range(current_year+1-len(self._antall_c), current_year+1)
        self._h_graphline = self._graph_subplot.plot(xval_h, 
                                                     self._antall_h, 'g-') 
        self._c_graphline = self._graph_subplot.plot(xval_c, 
                                                     self._antall_c, 'r-')
        
        # Draw legend
        plt.legend((self._h_graphline, self._c_graphline), 
                   ('Herbivores', 'Carnivores'), loc=2)
        
        # Set labels
        plt.xlabel('Year')
        plt.ylabel('Total number of animals')
        
        # Clear temporary lists
        self._antall_h = []
        self._antall_c = []
                
        
    def hmap_setup(self, terrain_matrix, vmin=None, vmax=None):
        """
        Set up and draw herbivore intensity map.
        
        Parameters:
        tarrain_matrix (matrix containing terrain regions, required)
        vmin (lower colorbar value, optional)
        vmax (upper colorbar value, optional)
        """
        
        plt.subplot(self._herbivore_subplot)
        
        if vmin != None: 
            self._min_colormap_h = vmin
        if vmax != None: 
            self._max_colormap_h = vmax
        if vmin >= vmax and vmin is not None and vmax is not None:
            raise ValueError('vmax cannot be less or equal to vmin')
        # Create matrix of animal counts
        herbilen = []
        for row in terrain_matrix:
            row_counter = []
            for celle in row:
                row_counter.append(len(celle.herbivores()))
            herbilen.append(row_counter)
        
        # Draw map
        self._h_img_ax = self._herbivore_subplot.imshow(herbilen, 
                                               interpolation='nearest',
                                               vmin=self._min_colormap_h, 
                                               vmax=self._max_colormap_h)
        
        # Make ticks start from 1 instead of 0
        plt.xticks(np.arange(0, np.shape(terrain_matrix)[1]), 
                   np.arange(1, np.shape(terrain_matrix)[1]+1))
        plt.yticks(np.arange(0, np.shape(terrain_matrix)[0]), 
                   np.arange(1, np.shape(terrain_matrix)[0]+1))
        
        # Draw colorbar
        if self._h_colorbar == None:
            self._h_colorbar = plt.colorbar(self._h_img_ax)
        else:
            self._h_colorbar.update_bruteforce(self._h_img_ax)
        
    def cmap_setup(self, terrain_matrix, vmin=None, vmax=None):
        """
        Set up and draw carnivore intensity map.
        
        Parameters:
        tarrain_matrix (matrix containing terrain regions, required)
        vmin (lower colorbar value, optional)
        vmax (upper colorbar value, optional)
        """
        
        plt.subplot(self._carnivore_subplot)

        if vmin != None: 
            self._min_colormap_c = vmin
        if vmax != None: 
            self._max_colormap_c = vmax
        if vmin >= vmax and vmin is not None and vmax is not None:
            raise ValueError('vmax cannot be less or equal to vmin')
        # Create matrix of animal counts
        carnilen = []
        for row in terrain_matrix:
            row_counter = []
            for celle in row:
                row_counter.append(len(celle.carnivores()))
            carnilen.append(row_counter)
            
        # Draw map
        self._c_img_ax = self._carnivore_subplot.imshow(carnilen, 
                                               interpolation='nearest', 
                                               vmin=self._min_colormap_c, 
                                               vmax=self._max_colormap_c)
        
        # Make ticks start from 1 instead of 0
        plt.xticks(np.arange(0, np.shape(terrain_matrix)[1]), 
                   np.arange(1, np.shape(terrain_matrix)[1]+1))
        plt.yticks(np.arange(0, np.shape(terrain_matrix)[0]), 
                   np.arange(1, np.shape(terrain_matrix)[0]+1))
        
        # Draw colorbar
        if self._c_colorbar == None:
            self._c_colorbar = plt.colorbar(self._c_img_ax)
        else:
            self._c_colorbar.update_bruteforce(self._c_img_ax)
    
    def draw_graph(self, herbivore_count, carnivore_count, current_year, xlim):
        """
        Plot total herbivore and carnivore counts vs. time.
        
        Parameters:
        herbivore_count (total number of herbivores this year, required)
        carnivore_count (total number of carnivores this year, required)
        current_year (the current year, required)
        xlim (x-axis upper limit, required)
        """
        
        plt.subplot(self._graph_subplot)
    
        # Animal counts are stored temporary in lists until it is 
        # time to update the _graph_subplot.
        self._antall_h.append(herbivore_count)
        self._antall_c.append(carnivore_count)
        
        if current_year % self._update_interval == 0:
            if self._h_graphline is None:
                self.graph_setup(current_year, xlim)
            else:
                yvals_h = np.hstack((self._h_graphline[0].get_ydata(), 
                                     np.array(self._antall_h)))
                yvals_c = np.hstack((self._c_graphline[0].get_ydata(), 
                                    np.array(self._antall_c)))
                
                xvals_h = range(1, len(yvals_h) + 1)
                xvals_c = range(1, len(yvals_c) + 1)
                                
                self._h_graphline[0].set_data(xvals_h, yvals_h)
                self._c_graphline[0].set_data(xvals_c, yvals_c) 
                
                plt.xlim(0, xlim)
                plt.ylim(0, self._ylim)
                
                # Clear temporary lists.
                self._antall_h = [] 
                self._antall_c = []
    
    def draw_herbivores(self, terrain_matrix):
        """
        Draw herbivore intensity map.
        
        Parameters:
        terrain_matrix (matrix containing terrain regions, required)
        year (the current year, required)
        """
        
        plt.subplot(self._herbivore_subplot)
        
        if self._h_img_ax is None:
            self.hmap_setup(terrain_matrix)
        else:
            herbilen = []
            for row in terrain_matrix:
                row_counter = []
                for celle in row:
                    row_counter.append(len(celle.herbivores()))
                herbilen.append(row_counter)
            
            self._h_img_ax.set_data(herbilen)

    def draw_carnivores(self, terrain_matrix, year):
        """
        Draw carnivore intensity map.
        
        Parameters:
        terrain_matrix (matrix containing terrain regions, required)
        year (the current year, required)
        """
        
        plt.subplot(self._carnivore_subplot)
        
        if self._c_img_ax is None:
            self.cmap_setup(terrain_matrix)
        else:
            carnilen = []
            for row in terrain_matrix:
                row_counter = []
                for celle in row:
                    row_counter.append(len(celle.carnivores()))
                carnilen.append(row_counter)
            
            self._c_img_ax.set_data(carnilen)
            
            # Show current year
            plt.xlabel("Year: {}".format(year))

    def update_graphics(self):
        """Update the graphics display."""
        
        plt.draw()

    def save_image(self, file_name_base=None):
        """
        Save figure to file.
        
        Parameters:
        file_name_base (str containing base of image file name, optional.
                        If omitted, default is used.)
        """
        
        if file_name_base is not None:
            self._img_base = file_name_base
        plt.savefig('{0}_{1:05d}.{2}'.format(self._img_base, 
                                             self._img_counter, 
                                             self._img_format))
        self._img_counter += 1   
        
    def make_film(self, filename=None):
        """
        Make movie from saved figures.
        
        Parameters:
        filename (name of movie file, optional)
        """
        
        if filename == None: 
            filename = self._img_base
        ffmpeg_cmd = ('{0} -y -i {1}_%05d.png {2}.mp4'
                      .format(self._ffmpeg_binary, self._img_base, filename))

        os.system(ffmpeg_cmd) 


class Simulator(object):
    """Handles the _simulation."""

    def __init__(self, terrain, graphics):
        """
        Initialize simulator object.
        
        Parameters:
        terrain (terrain object to use in simulation, required)
        graphics (graphics object to use in simulation, required)
        """
        
        self._graphics = graphics
        self._terrain = terrain
        self._h_this_y = 0
        self._c_this_y = 0
        self._year = 0
        
    def run_simulation(self, years, file_name_base=None):
        """
        Run the main simulation loop.
        
        Parameters:
        years (number of years to simulate, required)
        file_name_base (str containing base of image file name, optional.
                        If omitted, images are not saved.)
        """
        
        if self._graphics.update_interval() > years:
            raise ValueError(
                    "Simulation period cannot be less than plot interval")
        if years < 0:
            raise ValueError('Cannot simulate negative years')
        if type(years) != int:
            raise TypeError('Years must be integer')
        
        xlim = self._year + years
        for self._year in range(self._year + 1, self._year + 1 + years):      
            self._terrain.growth()
            self._terrain.migration(self._year)
            self._terrain.decay()
            
            (h_this_y, c_this_y) = self._terrain.animal_counts()

            self._graphics.draw_graph(h_this_y, 
                                      c_this_y, 
                                      self._year, 
                                      xlim)
            if (self._year) % self._graphics.update_interval() == 0: 
                self._graphics.draw_terrain(self._terrain)
                self._graphics.draw_herbivores(self._terrain.terrain_map())
                self._graphics.draw_carnivores(self._terrain.terrain_map(), 
                                               self._year)
                self._graphics.update_graphics()  
                if file_name_base is not None:
                    self._graphics.save_image(file_name_base)
                if h_this_y == 0 and c_this_y == 0:
                    break
              
    def current_year(self):
        """Return the current year."""
        
        return self._year
        
    def animal_count(self):
        """Return total animal count."""
        
        return self._h_this_y + self._c_this_y
    
    def count_by_species(self):
        """Return animal count by species."""
        
        return {'herbivores': self._h_this_y, 'carnivores': self._c_this_y}
    
    def count_by_cell(self):
        """Return herbivore and carnivore counts for each cell."""
        
        herbmat = np.zeros(np.shape(self._terrain.terrain_map()))
        carnmat = np.zeros(np.shape(self._terrain.terrain_map()))
        for row in range(np.shape(self._terrain.terrain_map())[0]):
            for column in range(np.shape(self._terrain.terrain_map())[1]):
                herbcount = len(self._terrain.terrain_map()[row, column]
                                .herbivores())
                carncount = len(self._terrain.terrain_map()[row, column]
                                .carnivores()) 
                herbmat[row, column] = herbcount
                carnmat[row, column] = carncount
        return {'herbivores': herbmat, 'carnivores': carnmat}


class InputHandler(object):
    """Handles the user input and serves as the main user interface."""
    
    def __init__(self, mapstr=None, mapfile=None):
        """
        Initialize InputHandler object.
        
        Parameters:
        mapstr (string describing the map. See below)
        mapfile (location of file containing mapstr)
        
        One of the parameters must be given.
        
        mapstr should be a multiline string containing upper case letters
        O, J, S, D and M, representing the different region types. All lines
        must have the same number of letters. Along the edge, there should be
        only O's. 
        
        Example mapstr:
        
        "OOOOOO
         OJSJSO
         OSSSSO
         OSDDSO
         OMMDMO
         OOOOOO"
        """
        
        self._default_params_h = {'w_birth': 8., 
                             'beta': 0.4,
                             'sigma': 0.05,
                             'w_min': 5.,
                             'a_half': 40.,
                             'phi_age': 0.1,
                             'w_half_low': 10.,
                             'w_half_high': 60.,
                             'phi_low': 0.5,
                             'phi_high': 0.2,
                             'mu': 0.15,
                             'gamma': 0.1,
                             'zeta': 2.,
                             'omega': 0.01,
                             'F': 10}
        ani.Herbivore.update_params(self._default_params_h)
        
        self._default_params_c = {'w_birth': 6., 
                             'beta': 0.75,
                             'sigma': 0.1,
                             'w_min': 3.,
                             'a_half': 40.,
                             'phi_age': 0.15,
                             'w_half_low': 6.,
                             'w_half_high': 40.,
                             'phi_low': 0.3,
                             'phi_high': 0.1,
                             'mu': 0.4,
                             'gamma': 0.25,
                             'zeta': 2.5,
                             'omega': 0.01,
                             'F': 15,
                             'DeltaPhiMax': 0.75}
        ani.Carnivore.update_params(self._default_params_c)
        
        self._default_params_j = {'fmax': 300}
        lnd.Jungle.update_params(self._default_params_j)
        
        self._default_params_s = {'fmax': 150, 'alpha': 0.8}
        lnd.Savannah.update_params(self._default_params_s)
        
        # Initialize Graphics() and Terrain() objects and deliver them to 
        # the Simulator() 
        self._graphics = Graphics()
        self._terrain = Terrain(mapstr, mapfile)
        self._simulation = Simulator(self._terrain, self._graphics)

    def _convert_indices(self, indices):
        """
        Convert user-friendly indices to Python indices.
        
        Return tuple with the converted indices.
        
        Parameters:
        indices (tuple, list or numpy array with two integers, required)
        """
        
        return (indices[0]-1, indices[1]-1)

    def run_simulation(self, years, file_name_base=None):
        """
        Run the main _simulation loop in the simulator object.
        
        Parameters:
        years (number of years to simulate, required)
        file_name_base (str containing base of image file name, optional.
                        If omitted, images are not saved.)
        """
        
        self._simulation.run_simulation(years, file_name_base)
        
    def deploy_animals(self, deployments):
        """
        Deploy animals on the terrain.

        Parameters:
        deployments (list containing deployments (see example below), optional)
        
        Example:
        deploy_animals([{'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 18.0}]},
                        {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 3, 'weight': 22.5}]},
                        {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 15.2}]},
                        {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 11, 'weight': 10.7}]}])
        """
        
        for deployment in deployments:
            for k in deployment:
                if k not in ['loc', 'pop']:
                    raise KeyError('No parameter called {}'.format(k))
            coord = self._convert_indices(deployment['loc'])
            for animal in deployment['pop']:
                for k in animal:
                    if k not in ['species', 'age', 'weight']:
                        raise KeyError('No parameter called {}'.
                                             format(k))
                if animal['species'] == 'Herbivore':
                    self._terrain.terrain_map()[coord].deploy(
                            ani.Herbivore(animal['weight'], animal['age']))
                elif animal['species'] == 'Carnivore':
                    self._terrain.terrain_map()[coord].deploy(
                            ani.Carnivore(animal['weight'], animal['age']))
                else:
                    raise ValueError('No species called {}'.
                                     format(animal['species']))

    def set_herbivore_parameters(self, parameters):
        """
        Set herbivore parameters.
        
        Parameters:
        parameters (dict containing parameters to change from default values, 
                    optional)
        """
        
        for k in parameters.keys():
            if k not in self._default_params_h:
                raise KeyError('Unknown parameter name')
        if any(value < 0 for value in parameters.values()):
            raise ValueError('Only non-negative numbers')

        self._default_params_h.update(parameters)    
        ani.Herbivore.update_params(self._default_params_h)
        
    def set_carnivore_parameters(self, parameters):
        """
        Set carnivore parameters.
        
        Parameters:
        parameters (dict containing parameters to change from default values, 
                    optional)
        """
        
        for k in parameters.keys():
            if k not in self._default_params_c:
                raise KeyError('Unknown parameter name')
        if any(value < 0 for value in parameters.values()):
            raise ValueError('Only non-negative numbers')

        self._default_params_c.update(parameters)  
        ani.Carnivore.update_params(self._default_params_c)
        
    def set_jungle_parameters(self, parameters):
        """
        Set jungle parameters.
        
        Parameters:
        parameters (dict containing parameters to change from default values, 
                    optional)
        """
        
        for k in parameters.keys():
            if k not in self._default_params_j:
                raise KeyError('Unknown parameter name')
        if any(value < 0 for value in parameters.values()):
            raise ValueError('Only non-negative numbers')
        
        self._default_params_j.update(parameters)   
        lnd.Jungle.update_params(self._default_params_j)
        
    def set_savannah_parameters(self, parameters):
        """
        Set savannah parameters.
        
        Parameters:
        parameters (dict containing parameters to change from default values,
                    optional)
        """
        
        for k in parameters.keys():
            if k not in self._default_params_s:
                raise KeyError('Unknown parameter name')
        if any(value < 0 for value in parameters.values()):
            raise ValueError('Only non-negative numbers')
        
        self._default_params_s.update(parameters)
        lnd.Savannah.update_params(self._default_params_s)

    def set_graph_ylim(self, ylim):
        """
        Set the y-axis limit in the _graph_subplot.
        
        Parameters:
        _ylim (y-axis upper limit, required)
        """
        
        self._graphics.set_ylim(ylim)
    
    def set_herbivore_luminance_scale(self, vmax, vmin=0):
        """
        Set the colorbar restraints for the herbivore map.
        
        Parameters:
        vmax (max value, required)
        vmin (min value, optional, default = 0)
        
        vmax should be set approximately to the expected maximum number
        of herbivores in any single cell / region.
        vmin should usually be set to 0.
        """

        self._graphics.hmap_setup(self._terrain.terrain_map(), 
                                  vmin, vmax)
    
    def set_carnivore_luminance_scale(self, vmax, vmin=0):
        """
        Set the colorbar restraints for the carnivore map.
                
        Parameters:
        vmax (max value, required)
        vmin (min value, optional, default = 0)
        
        vmax should be set approximately to the expected maximum number
        of carnivores in any single cell / region.
        vmin should usually be set to 0.
        """
        
        self._graphics.cmap_setup(self._terrain.terrain_map(), 
                                  vmin, vmax)

    def set_plot_update_interval(self, interval):
        """Set update interval for the _graphics."""
        
        self._graphics.update_interval(interval)
                    
    def make_film(self, filename=None):
        """
        Make movie from saved figures.
        
        Parameters:
        filename (name of movie file, optional)
        """
        
        self._graphics.make_film(filename)
        

if __name__ == "__main__":
    pass
