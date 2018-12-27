'''
:mod:`profile_sim` runs a BioSim simulation 
and illustrates how to use the resulting information.

Original code written by Hans E Plesser. 
Slight modification by Aleksander Hykkerud and Daniel Hjertholm.

.. seealso::

  - http://docs.python.org/library/profile.html
  - http://www.doughellmann.com/PyMOTW/profile
'''

__author__ = "Hans E Plesser, UMB"

import cProfile
import pstats
import os

from slogstorm import InputHandler

# HEP's laptop
_GPROF2DOT = '/Library/Frameworks/EPD64.framework/Versions/Current/bin/gprof2dot'
_DOT = '/usr/local/bin/dot'

# TF02
#_GPROF2DOT = 'gprof2dot'
#_DOT = r'I:\tools\Graphviz\bin\dot'

if __name__ == '__main__':

    # turn off all graphics by replacing graphics functions
    # with mock functions
    
    # run_simulation._setup_graphics = Mock()
    # run_simulation._update_graphics = Mock()
    # run_simulation._save_graphics = Mock()

    # initialize setup
    sim = InputHandler(mapfile="mapfile.txt")
    sim.set_plot_update_interval(40)
    sim.deploy_animals(
        [{'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])

    # profile with direct output to console, short run
    cProfile.run('sim.run_simulation(100)')
    
    sim.deploy_animals(
        [{'loc': (3, 3), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 22.5}]},
         {'loc': (3, 3), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 22.5}]},
         {'loc': (3, 3), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 22.5}]},
         {'loc': (3, 3), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 22.5}]}])

    # profile with output to file, longer run
    prof_file = 'biosim.prof'
    cProfile.run('sim.run_simulation(100)', prof_file)

    # read profile data from file, output statistics in different orders
    prof = pstats.Stats(prof_file).strip_dirs()


#    print '=' * 80
#    prof.sort_stats('name').print_stats()
#    
#    print '=' * 80
#    prof.sort_stats('cum').print_stats()
#
#    print '=' * 80
#    prof.sort_stats('time').print_stats()
#
#    print '=' * 80
#    prof.sort_stats('calls').print_stats()
#
#    print '=' * 80
#    prof.print_callers()
#
#    print '=' * 80
#    prof.print_callees()

    
    # finally, invoke gprof2dot and dot to create a figure
    os.system('{gprof2dot} -f pstats -o {file}.dot {file}'
              .format(gprof2dot=_GPROF2DOT, file=prof_file))
    os.system('{dot} -Tpdf -o {file}.pdf {file}.dot'
              .format(dot=_DOT, file=prof_file))
    print "Profile graph stored as {file}.pdf".format(file=prof_file)


