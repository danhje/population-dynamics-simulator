#!/usr/bin/env python
'''Tests for BioSim project.'''

__author__ = "Aleksander Hykkerud and Daniel Hjertholm"

import unittest
import mock

import slogstormpakke.slogstorm as slog


class BioSimTests(unittest.TestCase):
    """Test suite for the BioSim project."""
    
    def __init__(self, methodName):
        """Initialize test case."""
        unittest.TestCase.__init__(self, methodName)
        
        # save original reference to slump random generator
        self.orig_random = slog.sl.random
        self.orig_randint = slog.sl.randint

        
    def setUp(self):
        """Reset everything before next test."""
        # restore original reference to slump random generator
        
        slog.sl.random = self.orig_random
        slog.sl.randint = self.orig_randint
        
        slog.plt.close()
        
        # generate default InputHandler for use in tests
        self.hi = slog.InputHandler(mapstr="OOO\nOJO\nOMO\nOOO")
        self.hi.set_carnivore_parameters({'w_birth': 6.,
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
                             'DeltaPhiMax': 0.75})
        self.hi.set_herbivore_parameters({'w_birth': 8., 
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
                             'F': 10})
    
    def test_create_input_handler(self):
        """Ensure that we can create a input handler object."""
        self.assertIsInstance(self.hi, slog.InputHandler)
        
    def test_input_handler_has_objects(self):
        """Ensure that input handler has created instance of Graphics(), Terrain() and Simulator()."""
        self.assertIsInstance(self.hi._graphics, slog.Graphics)
        self.assertIsInstance(self.hi._terrain, slog.Terrain)
        self.assertIsInstance(self.hi._simulation, slog.Simulator)
        
    def test_map_creation(self):
        """Ensure that map is generated correctly and map dimensions are correct."""
        # test with map in string format
        mapmat = self.hi._terrain.terrain_map()
        for row in mapmat:
            for cell in row:
                self.assertTrue(issubclass(cell.__class__, slog.lnd.Region), 'Bad map was created.')
        self.assertIsInstance(mapmat[0, 0], slog.lnd.Ocean)
        self.assertIsInstance(mapmat[1, 1], slog.lnd.Jungle)
        self.assertIsInstance(mapmat[2, 1], slog.lnd.Mountain)
        self.assertEqual(self.hi._terrain.terrain_dimensions(), (4, 3))

        # test with map generated from file
        outfile = open("testmapfile.txt", 'w')
        outfile.write("OOO\nOJO\nOMO\nOOO")
        outfile.close()
        hi2 = slog.InputHandler(mapfile="testmapfile.txt")
        slog.os.remove('testmapfile.txt')
        mapmat = hi2._terrain.terrain_map()
        for row in mapmat:
            for cell in row:
                self.assertTrue(issubclass(cell.__class__, slog.lnd.Region), 'Bad map was created.')
        self.assertIsInstance(mapmat[0, 0], slog.lnd.Ocean)
        self.assertIsInstance(mapmat[1, 1], slog.lnd.Jungle)
        self.assertIsInstance(mapmat[2, 1], slog.lnd.Mountain)
        self.assertEqual(hi2._terrain.terrain_dimensions(), (4, 3))
        
    def test_bad_mapstr_raises_exception(self):
        """Ensure that bad mapstrings are handled correctly."""
        self.assertRaises(ValueError, slog.InputHandler, mapstr="OOO\nOJO\nOOOO")
        self.assertRaises(ValueError, slog.InputHandler, mapstr="BOO\nOJO\nOOO")
        self.assertRaises(ValueError, slog.InputHandler, mapstr="oOO\nOJO\nOOOO")
        self.assertRaises(ValueError, slog.InputHandler, mapstr="DOO\nOJO\nOOOO")

    def test_changing_parameters(self):
        """Ensure that the InputHandler's methods for changing parameters work."""
        
        # test with bad keys
        self.assertRaises(KeyError, self.hi.set_carnivore_parameters, {'w_mon' : 20})
        self.assertRaises(KeyError, self.hi.set_herbivore_parameters, {'w_minimum' : 20})
        self.assertRaises(KeyError, self.hi.set_jungle_parameters, {'lotoffood' : 20})
        self.assertRaises(KeyError, self.hi.set_savannah_parameters, {'maxfood' : 20})
        
        # test for negative parameter setting
        for param in self.hi._default_params_c:
            self.assertRaises(ValueError, self.hi.set_carnivore_parameters, {param : -20})
        
        # test for negative parameter setting
        for param in self.hi._default_params_h:
            self.assertRaises(ValueError, self.hi.set_herbivore_parameters, {param : -20})
        
        # test for negative parameter setting
        for param in self.hi._default_params_j:
            self.assertRaises(ValueError, self.hi.set_jungle_parameters, {param : -20})
    
        # test for negative parameter setting
        for param in self.hi._default_params_s:
            self.assertRaises(ValueError, self.hi.set_savannah_parameters, {param : -20})
        
        # test if parameter is stored in dict
        carni = slog.ani.Carnivore(12.5, 3) 
        for param in self.hi._default_params_c:
            self.hi.set_carnivore_parameters({param : 9})
            self.assertEqual(carni.params[param], 9)
        herbi = slog.ani.Herbivore(12.5, 3) 
        for param in self.hi._default_params_h:
            self.hi.set_herbivore_parameters({param : 9})
            self.assertEqual(herbi.params[param], 9)
        jungle = slog.lnd.Jungle() 
        for param in self.hi._default_params_j:
            self.hi.set_jungle_parameters({param : 9})
            self.assertEqual(jungle.params[param], 9)
        savannah = slog.lnd.Savannah() 
        for param in self.hi._default_params_s:
            self.hi.set_savannah_parameters({param : 9})
            self.assertEqual(savannah.params[param], 9)
        
        self.assertRaises(ValueError, self.hi.set_graph_ylim, -300)
        self.hi.set_graph_ylim(1337)
        self.assertEqual(1337, self.hi._graphics._ylim)
        
        self.assertRaises(ValueError, self.hi.set_herbivore_luminance_scale, vmin=1000, vmax=0)
        self.hi.set_herbivore_luminance_scale(vmin=0, vmax=1000)
        self.assertEqual(0, self.hi._graphics._min_colormap_h)
        self.assertEqual(1000, self.hi._graphics._max_colormap_h)
        
        self.assertRaises(ValueError, self.hi.set_carnivore_luminance_scale, vmin=1000, vmax=0)
        self.hi.set_carnivore_luminance_scale(vmin=0, vmax=1000)
        self.assertEqual(0, self.hi._graphics._min_colormap_c)
        self.assertEqual(1000, self.hi._graphics._max_colormap_c)
        
        self.assertRaises(ValueError, self.hi.set_plot_update_interval, 0)
        self.assertRaises(ValueError, self.hi.set_plot_update_interval, -10)
        self.assertRaises(ValueError, self.hi.set_plot_update_interval, 0.5)
        self.hi.set_plot_update_interval(20)
        self.assertEqual(20, self.hi._graphics._update_interval)
        self.assertEqual(11, self.hi._graphics.update_interval(11))
    
    def test_run_simulation(self):
        """Ensure that run_simulation() starts and runs for the specified number of years."""   
        slog.sl.seed(154789)   
        self.hi.deploy_animals(
            [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
             {'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
             {'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
             {'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        
        def f(ar1=None, ar2=None, ar3=None, ar4=None):
            pass
        
        # turn off plotting
        self.hi._graphics.draw_carnivores = f
        self.hi._graphics.draw_herbivores = f
        self.hi._graphics.draw_graph = f
        self.hi._graphics.draw_terrain = f
        self.hi._graphics.update_graphics = f

        self.assertRaises(ValueError, self.hi.run_simulation, -40)
        self.assertRaises(TypeError, self.hi.run_simulation, 4.5)
        self.hi.run_simulation(40)
        self.assertEqual(40, self.hi._simulation.current_year())
        
    def test_region_move(self):
        """Ensure that Region.move() works."""
        hi = slog.InputHandler("OOO\nOJO\nOJO\nOOO") 
        hi.deploy_animals(
            [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        self.assertTrue(hi._terrain.terrain_map()[2,1].move(
                        hi._terrain.terrain_map()[1,1].herbivores()[0],5))
        self.assertEqual(hi._terrain.terrain_map()[1,1].herbivores()[0], 
                         hi._terrain.terrain_map()[2,1].herbivores()[0])
        
        self.assertFalse(hi._terrain.terrain_map()[2,1].move(
                         hi._terrain.terrain_map()[1,1].herbivores()[0],5))
    
        self.assertFalse(hi._terrain.terrain_map()[0,0].move(
                         hi._terrain.terrain_map()[1,1].herbivores()[0],6))
        self.assertEqual(len(hi._terrain.terrain_map()[0,0].herbivores()), 0)
    
    def test_simulator_methods(self):
        """
        Ensure that Simulator's methods returns data in the expected format.
        Does not test whether the data is correct. 
        """
        hi = slog.InputHandler("OOO\nOJO\nOJO\nOOO") 
        self.assertEqual(type(hi._simulation.current_year()), int)
        self.assertEqual(type(hi._simulation.animal_count()), int)
        self.assertEqual(type(hi._simulation.count_by_species()), dict)
        self.assertEqual(type(hi._simulation.count_by_cell()), dict)
        
    def test_deploy_animals(self):
        """Ensure that we can deploy animals."""
        ih = slog.InputHandler(mapstr="OOO\nOJO\nOJO\nOOO")
        ih.deploy_animals(
            [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
             {'loc': (3, 2), 
              'pop': [{'species': 'Carnivore', 'age': 0, 'weight': 24.5}]}])
        
        self.assertEqual(ih._terrain.terrain_map()[1, 1].herbivores()[0].age(), 10)
        self.assertEqual(ih._terrain.terrain_map()[1, 1].herbivores()[0].weight(), 12.5)
        self.assertEqual(ih._terrain.terrain_map()[2, 1].carnivores()[0].age(), 0)
        self.assertEqual(ih._terrain.terrain_map()[2, 1].carnivores()[0].weight(), 24.5)
        
    def test_bad_animal_deployment_raises_exception(self):
        """Ensure that bad deployment are handled."""
        
        # bad location
        self.assertRaises(AttributeError, self.hi.deploy_animals, [{'loc': (1, 1), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        self.assertRaises(AttributeError, self.hi.deploy_animals, [{'loc': (-1, 1), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        
        # keyerrors
        self.assertRaises(KeyError, self.hi.deploy_animals, [{'loc': (2, 2), 
              'pp': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        self.assertRaises(KeyError, self.hi.deploy_animals, [{'lc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
        self.assertRaises(KeyError, self.hi.deploy_animals, [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'wight': 12.5}]}])
        
        # negative age and weight values
        self.assertRaises(ValueError, self.hi.deploy_animals, [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': 10, 'weight': -12.5}]}])
        self.assertRaises(ValueError, self.hi.deploy_animals, [{'loc': (2, 2), 
              'pop': [{'species': 'Herbivore', 'age': -10, 'weight': 12.5}]}])

    def test_fitness_function(self):
        """Ensure return value of fitness function is correct."""
        bjertulf = slog.ani.Carnivore(12, 10)
        self.assertAlmostEqual(bjertulf.fitness(), 0.800068298637, 5)
        arntulf = slog.ani.Herbivore(15, 12)
        self.assertAlmostEqual(arntulf.fitness(), 0.871058654557, 5)
    
    def test_animal_eat(self):
        """Ensure that Animal.eat() works."""
        arnt = slog.ani.Herbivore(10, 15)
        self.assertEqual(50, arnt.eat(50))
        self.assertAlmostEqual(10 + arnt.params['beta']*50.0, arnt.weight(), 5)
        
    def test_convert_indices(self):
        """Test if indices converter returns correct result."""
        for times in range(10):
            xnum = slog.sl.randint(50)
            ynum = slog.sl.randint(50)
            self.assertEqual((xnum,ynum), self.hi._convert_indices((xnum+1,ynum+1)))
            
    def test_birth_calls_slump(self):
        """Test if birth calls slump."""
        slog.sl.random = mock.Mock(return_value=0.)
        agnes = slog.ani.Herbivore(30, 5)
        agnes.birth(10)
        self.assertTrue(slog.sl.random.called)
        
    def prob_birth(self, animal, animal_count_in_region):  
        """Calculate expected probability of giving birth."""      
        if (animal.weight() < (animal.params['w_min'] + 
                               animal.params['zeta'] * 
                               animal.params['w_birth']) or
            animal.age() == 0):
            return 0
        else:
            return (animal.params['gamma'] * 
                    animal.fitness() * 
                    (animal_count_in_region-1))
              
    def test_birth_return_values(self):
        """Test the birth functions return values."""
        gunnar = slog.ani.Herbivore(30, 5)
        for i in range(10):
            gunnar.eat(self.orig_randint(20))
            gunnar.aging()
            animal_count = i+3
            probbirth = self.prob_birth(gunnar, animal_count)
            for rtest, expected in [(0.99*probbirth, True), (1.01*probbirth, False)]:
                slog.sl.random = mock.Mock(return_value=rtest)
                gunnar._weight = 30
                self.assertEqual(gunnar.birth(animal_count), expected)
               
    def test_herbivore_eat(self):
        """Test herbivore.eat()."""
        lars = slog.ani.Herbivore(30, 5)
        lars.eat(30)
        self.assertAlmostEqual(30 + lars.params['beta'] * 30, lars.weight(), 5)
        
    def test_carnivore_eat(self):
        """Test carnivore.eat()."""
        # eat tiny animal
        ulf = slog.ani.Carnivore(10, 5)
        geir = slog.ani.Herbivore(ulf.params['F']*0.5,3)
        herbilist = [geir]
        ulf._eat(geir, 0, herbilist)
        self.assertAlmostEqual(ulf.weight(), (10 + ulf.params['beta'] * geir.weight()))
        
        # eat medium animal
        ulf = slog.ani.Carnivore(10, 5)
        geir = slog.ani.Herbivore(ulf.params['F'],3)
        herbilist = [geir]
        ulf._eat(geir, 0, herbilist)
        self.assertAlmostEqual(ulf.weight(), (10 + ulf.params['beta'] * geir.weight()))
        
        # eat big animal
        ulf = slog.ani.Carnivore(10, 5)
        geir = slog.ani.Herbivore(ulf.params['F']*1.5,3)
        herbilist = [geir]
        ulf._eat(geir, 0, herbilist)
        self.assertAlmostEqual(ulf.weight(), 10 + ulf.params['F']*ulf.params['beta'])
        
    def test_carnivore_hunt(self):
        """Test carnivore.hunt()."""
        self.hi.set_carnivore_parameters({'F': 13.5})
        self.hi.deploy_animals([{'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 6.0}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 7.5}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 8.2}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 9.2}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 10.7}]}])
                
        for htest, expected in [(0.0, 2), (1.0, 2), (0.5, 1)]:
            slog.sl.random = mock.Mock(return_value=htest)
            self.hi._terrain.terrain_map()[1,1].carnivores()[0].hunt(self.hi._terrain.terrain_map()[1,1].herbivores()) 
            self.assertEqual(len(self.hi._terrain.terrain_map()[1,1].herbivores()), expected)       
            
     
   
        
    def test_weightloss(self):
        """test weightloss function"""
        self.hi.deploy_animals([{'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 6.0}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 8}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 30}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 100}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 9001}]}])   
        
        for animal in self.hi._terrain.terrain_map()[1,1].herbivores() + self.hi._terrain.terrain_map()[1,1].carnivores():
            old_weight = animal.weight()
            animal.weightloss()
            self.assertAlmostEqual(old_weight-old_weight*animal.params['sigma'], animal.weight(), 5)

    def test_birthloss(self):
        """test birthloss function"""
        self.hi.deploy_animals([{'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 6.0}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 8}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 30}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 100}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 9001}]}])   
        
        for animal in self.hi._terrain.terrain_map()[1,1].herbivores() + self.hi._terrain.terrain_map()[1,1].carnivores():
            old_weight = animal.weight()
            animal.birthloss()
            self.assertAlmostEqual(old_weight-animal.params['w_birth']*animal.params['zeta'], animal.weight(), 5)

    def test_weightgain(self):
        """test weightgain function"""
        self.hi.deploy_animals([{'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 6.0}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 8}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 30}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 100}]},
                       {'loc': (2, 2), 'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 9001}]}])   

        for animal in self.hi._terrain.terrain_map()[1,1].herbivores() + self.hi._terrain.terrain_map()[1,1].carnivores():
            old_weight = animal.weight()
            amount = slog.sl.randint(40)
            animal.weightgain(amount)
            self.assertAlmostEqual(old_weight+amount, animal.weight(), 5)
        
        self.assertRaises(ValueError, self.hi._terrain.terrain_map()[1,1].herbivores()[0].weightgain, -10)
    
    def test_age(self):
        """test age function returns"""
        martine = slog.ani.Herbivore(14, 23)
        martin = slog.ani.Carnivore(10, 24)
        self.assertEqual(martine.age(), 23)
        self.assertEqual(martin.age(), 24)
        
    def test_weight(self):
        """test weight function returns."""
        martine = slog.ani.Herbivore(14, 23)
        martin = slog.ani.Carnivore(10, 24)
        self.assertEqual(martine.weight(), 14)
        self.assertEqual(martin.weight(), 10)
        
    def test_update_fitness_is_called(self):
        """test if update fitness is called"""
        martine = slog.ani.Herbivore(14, 23)
        martin = slog.ani.Carnivore(10, 24)
        martini = slog.ani.Carnivore(8, 25)
        martonio = slog.ani.Carnivore(8, 25)

        martine.update_fitness = mock.Mock(return_value=None)
        martin.update_fitness = mock.Mock(return_value=None)
        martini.update_fitness = mock.Mock(return_value=None)
        martonio.update_fitness = mock.Mock(return_value=None)
        
        martine.aging()
        martin.weightloss()
        martini.weightgain(5)
        martonio.birthloss()
        
        self.assertTrue(martine.update_fitness.called)
        self.assertTrue(martin.update_fitness.called)
        self.assertTrue(martini.update_fitness.called)
        self.assertTrue(martonio.update_fitness.called)
        
    def test_last_moved_update(self):
        """test last moved function in animal."""
        eilert = slog.ani.Herbivore(14, 23)
        hundremeterskogen = slog.lnd.Jungle()
        self.assertEqual(eilert.last_moved(), 0)
        hundremeterskogen.move(eilert, 5)
        self.assertEqual(hundremeterskogen.herbivores()[0].last_moved(), 5)

    def prob_migrate(self, animal):
        """calculate probability for migration."""
        return animal.params['mu']*animal.fitness()
        
    def test_animal_migrate(self):
        """test animal migrate function."""
        self.hi.set_herbivore_parameters({'mu': 0.15})
        fivel = slog.ani.Herbivore(14, 14)
        for i in range(10):
            fivel.aging()
            probmigrate = self.prob_migrate(fivel)
            for rtest, expected in [(0.99*probmigrate, True), (1.01*probmigrate, False)]:
                slog.sl.random = mock.Mock(return_value=rtest)
                self.assertEqual(fivel.migrate(), expected)
                
        
if __name__ == '__main__':
    unittest.main(verbosity=2)

