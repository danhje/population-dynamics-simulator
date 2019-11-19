This is a population dynamics simulator, exploring the exciting lives of herbivores and carnivores on an island with limited resources. 

Written by Aleksander Hykkerud and Daniel Hjertholm in 2012, as an exercise in the cours INF200 - Anvanced Programming at the NMBU. 

In the graphic below, from top left to bottom right: Plot of population sizes, the island with its different terrain types, and two heat maps showing the density of herbivores and carnivores, respectively. 

![Simulation](https://github.com/danhje/population-dynamics-simulator/blob/master/presentation/Example.gif?raw=true)

Even thought the simulator is relatively primitive, it is able to reproduce a lot of the phenomenon that are actually observed in nature, like periodic population cycles, lag effects and the overshoot-and-collapse effect.

The course in which this simulator was develiped focused on unit testing and performance optimization. Thus, almost every method is regorously tested. Optimization of code was done by fist profiling with cProfile. This revealed that a single method, the method that calculated and returned the fitness of a given individual, was called 47 million times, and accounted for 60% of the total CPU time. Based on this, the method was replaced with a fitness variable, which was only re-calculated when it neede to change. This change resulted in a factor 4 decrease in the CPU time used to calculate fitness. The calculation still used about 15% of the total CPU time, but by "cythonizing" it, i.e. transpiling it to C with the use of Cython, this was further decreased to 3.7% CPU time.

The update_fitness method before cythonization:

![Before Cython](https://github.com/danhje/population-dynamics-simulator/blob/master/presentation/Before%20cython%20(update_fitness).png?raw=true)

The update_fitness method after cythonization:

![After Cython](https://github.com/danhje/population-dynamics-simulator/blob/master/presentation/After%20cython%20(update_fitness).png?raw=true)

Profiling done using cProfile:

![Profiling done using cProfile](https://github.com/danhje/population-dynamics-simulator/blob/master/presentation/After%20cython.png?raw=true)

Documentation for the project was automatically generated through the use of Sphinx and docstrings.


