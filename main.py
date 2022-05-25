import sys
import gaapp
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from solution_panel import *
from gacvm import *
import numpy as np
from __feature__ import snake_case, true_property


 
if __name__ == '__main__':
    
    QApplication.set_attribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    ga_app = gaapp.QGAApp()
 
    # ajout de vos stratégies
    # -------------------------------------------------------- par exemple
    # ga_app.add_crossover_strategy(my_awesome_strategy)
    # ga_app.add_mutation_strategy(ma_spectaculaire_strategie)
    
    # ajout de vos panneaux de résolution de problème
    # -------------------------------------------------------- par exemple
    # range = np.zeros((1,2), dtype=np.float64)
    # domaine = Domains()
    # algo = ProblemDefinition()
    # range = np.zeros((1,2), dtype=np.float64)
    # tab_param = np.array([42, 420])
    
    open_box_solution_panel = OpenBoxSolutionPanel()

    # domain_names = np.array([["Translation X:"], ["Translation Y:"], ["Rotation:"], ["Scaling:"]])
    # print(domain_names)
    shape_transformation_optimizer = ShapeTransformationOptimizerSolutionPanel()
    cell_tower_coverage_optimizer = CellTowerCoverageOptimizerSolutionPanel()
    #cell_tower_coverage_optimizer.find_total_nb_of_each_tower()
    ga_app.add_solution_panel(open_box_solution_panel)
    ga_app.add_solution_panel(shape_transformation_optimizer)
    ga_app.add_solution_panel(cell_tower_coverage_optimizer)

    ga_app.show()
    sys.exit(app.exec_())

