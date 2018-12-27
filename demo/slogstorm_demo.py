"""
Demonstrates the usage of slogstorm. 
"""

import slogstormpakke.slogstorm as slog
    
if __name__ == "__main__":
    STRMAP = """OOOOOOOOOOOOOOOOO
                OSJSJOJDMMJJSJOOO
                OSMJJJJSSMMMMODDO
                OJSJSMDJJJJSJSMMO
                OJDSSMJSSSSSJSSMO
                OSOSJSJDMJJJJJSJO
                OJMJSOSJJMMOJOJMO
                ODSJJMJDSMMSJOMJO
                OJDJMSJDJSSMJOMSO
                OOOOOOOOOOOOOOOOO
                """
    SIM = slog.InputHandler(mapstr=STRMAP)
    SIM.set_graph_ylim(3000)
    SIM.set_plot_update_interval(50)
    
    SIM.deploy_animals(
        [{'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 12.5}]}])
    SIM.run_simulation(years=50)
    
    SIM.deploy_animals(
        [{'loc': (2, 2), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 12.5}]},
         {'loc': (2, 2), 
          'pop': [{'species': 'Carnivore', 'age': 10, 'weight': 12.5}]}])
    SIM.run_simulation(years=100)
    
    SIM.set_herbivore_parameters({'w_birth': 10., 'beta': 0.5})
    SIM.set_carnivore_parameters({'F': 25, 'beta': 0.8, 'mu': 0.8})
    SIM.set_plot_update_interval(50)
    SIM.run_simulation(years=150)
    SIM.set_carnivore_parameters({'DeltaPhiMax': 0.3})
    SIM.set_jungle_parameters({'fmax': 100})
    SIM.set_savannah_parameters({'fmax': 50})
    SIM.run_simulation(years=150)
    SIM.set_carnivore_parameters({'F': 15, 'beta': 0.9, 'mu': 0.8})
    SIM.set_jungle_parameters({'fmax': 30})
    SIM.set_savannah_parameters({'fmax': 20})
    SIM.run_simulation(years=150)

